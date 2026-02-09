import os
import asyncio
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from fastapi.responses import FileResponse
from pydantic import BaseModel
from supabase import create_client, Client
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Import the scanner class from your existing script
from audit_tool import SecurityScanner 

load_dotenv()

# --- SUPABASE CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- PAYPAL CONFIG ---
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox") # 'sandbox' or 'live'

PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# --- AUTOMATION SCHEDULER ---
scheduler = BackgroundScheduler()
scheduler.start()

def run_automated_scan(user_id: str, url: str, token: str):
    """Function called by the scheduler to run a 24hr scan."""
    print(f"[AUTO-SCAN] Starting scheduled scan for {url} (User: {user_id})")
    scanner = SecurityScanner(url)
    results = scanner.run(is_premium=True)
    
    scan_data = {
        "user_id": user_id,
        "hostname": scanner.hostname,
        "risk_score": results["grade"],
        "issue_count": len(results["issues"]),
        "pdf_url": results["pdf_filename"],
        "findings": results["issues"],
        "is_automated": True
    }
    
    try:
        # Save results to DB
        supabase.table("scans").insert(scan_data).execute()
        print(f"[AUTO-SCAN] Completed & Saved for {url}")
    except Exception as e:
        print(f"[AUTO-SCAN] Error: {e}")

app = FastAPI(
    title="CyberSecure Audit API",
    description="A White-Label API that generates PDF security reports.",
    version="1.0"
)

# --- SCHEDULER INITIALIZATION (Already started above) ---

def run_scheduled_scan(user_id: str, url: str):
    """Execution logic for automated scans."""
    print(f"[AUTO-PILOT] Starting automated scan for {url} (User: {user_id})")
    try:
        scanner = SecurityScanner(url)
        # Automated scans always use Premium logic since they are an enterprise feature
        results = scanner.run(is_premium=True)
        
        scan_data = {
            "user_id": user_id,
            "hostname": scanner.hostname,
            "risk_score": results["grade"],
            "issue_count": len(results["issues"]),
            "pdf_url": results["pdf_filename"],
            "findings": results["issues"],
            "created_at": datetime.now().isoformat()
        }
        # In a real app we'd need a service key to bypass RLS for background jobs
        # For now, we interact with the DB directly
        supabase.table("scans").insert(scan_data).execute()
        print(f"[AUTO-PILOT] Completed scan for {url}. Result saved.")
    except Exception as e:
        print(f"[AUTO-PILOT] ERROR: Failed automated scan for {url}: {e}")

def process_subscription_billing():
    """Scheduled task to handle monthly renewals and cancellations"""
    print("[BILLING] Running automated subscription check...")
    try:
        # Find all active subscriptions that have expired
        now = datetime.now()
        # Use admin client to check all subscriptions
        result = supabase.table("subscriptions").select("*").lt("current_period_end", now.isoformat()).execute()
        
        for sub in result.data:
            user_id = sub["user_id"]
            tier = sub["tier"]
            cancel_at_period_end = sub.get("cancel_at_period_end", False)
            
            if cancel_at_period_end:
                # Downgrade to free tier
                print(f"[BILLING] Subscription for {user_id} expired and canceled. Downgrading to free.")
                supabase.table("subscriptions").update({
                    "tier": "free",
                    "tier_name": "Free",
                    "scans_limit": 5,
                    "scans_this_month": 0,
                    "features": {
                        "pdf_download": False, "selenium_enabled": False, "code_snippets": False,
                        "automated_scans": False, "api_access": False
                    },
                    "current_period_start": now.isoformat(),
                    "current_period_end": (now + relativedelta(months=1)).isoformat(),
                    "cancel_at_period_end": False,
                    "updated_at": now.isoformat()
                }).eq("user_id", user_id).execute()
            else:
                # Renew for another month (reset scan count)
                # In a real app, this would trigger a payment charge
                print(f"[BILLING] Renewing subscription for {user_id} ({tier})")
                supabase.table("subscriptions").update({
                    "scans_this_month": 0,
                    "current_period_start": now.isoformat(),
                    "current_period_end": (now + relativedelta(months=1)).isoformat(),
                    "updated_at": now.isoformat()
                }).eq("user_id", user_id).execute()
                
    except Exception as e:
        print(f"[BILLING] Critical error in billing job: {e}")

# Register the billing check to run every 12 hours
scheduler.add_job(
    process_subscription_billing,
    trigger=IntervalTrigger(hours=12),
    id="billing_check",
    replace_existing=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This defines the data we expect from the frontend
class ScanRequest(BaseModel):
    url: str

def cleanup_file(path: str):
    """Deletes the PDF after sending it to save space."""
    if os.path.exists(path):
        os.remove(path)

async def verify_user(token: str):
    """Verifies the Supabase user token."""
    try:
        user = supabase.auth.get_user(token)
        return user.user if user else None
    except Exception:
        return None

@app.post("/generate-audit")
async def generate_audit(
    request: ScanRequest, 
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    """
    Takes a URL, runs the scan, returns JSON results and a pdf link.
    """
    target_url = request.url
    is_premium = False
    user_id = None
    token = None
    user_tier = "free"

    # Check for authentication
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user = await verify_user(token)
        if user:
            is_premium = True
            user_id = user.id
            print(f"DEBUG: Authenticated user detected: {user_id}")
            
            # Get user's subscription
            try:
                sub_result = supabase.table("subscriptions").select("*").eq("user_id", str(user_id)).execute()
                
                if sub_result.data and len(sub_result.data) > 0:
                    subscription = sub_result.data[0]
                    user_tier = subscription.get("tier", "free")
                    scans_this_month = subscription.get("scans_this_month", 0)
                    scans_limit = subscription.get("scans_limit", 5)
                    period_end_str = subscription.get("current_period_end")
                    
                    # --- Proactive Period Reset Check ---
                    now = datetime.now()
                    if period_end_str:
                        period_end = datetime.fromisoformat(period_end_str.replace("Z", "+00:00")).replace(tzinfo=None)
                        if now > period_end:
                            print(f"DEBUG: Period expired for {user_id}. Resetting scans.")
                            # Reset period for exactly one calendar month
                            new_start = now
                            new_end = now + relativedelta(months=1)
                            
                            supabase.table("subscriptions").update({
                                "scans_this_month": 0,
                                "current_period_start": new_start.isoformat(),
                                "current_period_end": new_end.isoformat(),
                                "updated_at": now.isoformat()
                            }).eq("user_id", str(user_id)).execute()
                            
                            scans_this_month = 0 # Update local variable for subsequent check
                    
                    # Check if user has scans remaining (unless enterprise)
                    if user_tier != "enterprise" and scans_this_month >= scans_limit:
                        raise HTTPException(
                            status_code=403,
                            detail=f"Monthly scan limit reached ({scans_limit} scans). Please upgrade your plan."
                        )
                    
                    print(f"DEBUG: User tier: {user_tier}, Scans: {scans_this_month}/{scans_limit}")
                else:
                    # No subscription found, create free tier using auth token
                    print(f"DEBUG: No subscription found, creating free tier for user {user_id}")
                    now = datetime.now()
                    supabase.postgrest.auth(token).table("subscriptions").insert({
                        "user_id": str(user_id),
                        "tier": "free",
                        "tier_name": "Free",
                        "scans_this_month": 0,
                        "scans_limit": 5,
                        "current_period_start": now.isoformat(),
                        "current_period_end": (now + relativedelta(months=1)).isoformat()
                    }).execute()
                    
            except HTTPException:
                raise  # Re-raise HTTP exceptions
            except Exception as e:
                print(f"WARNING: Error fetching subscription: {e}")
                # Continue with free tier as fallback

    # 1. Initialize the Scanner
    scanner = SecurityScanner(target_url)
    
    # 2. Run all checks
    results = scanner.run(is_premium=is_premium)
    
    # 3. Generate tier-based PDF
    from tiered_pdf import generate_tiered_pdf
    try:
        pdf_filename = generate_tiered_pdf(
            hostname=scanner.hostname,
            grade=results["grade"],
            findings=results["issues"],
            tier=user_tier
        )
        results["pdf_filename"] = pdf_filename
    except Exception as e:
        print(f"ERROR: Tiered PDF generation failed: {e}")
        # Fallback to original PDF
        pdf_filename = results["pdf_filename"]
    
    # 4. Save to Supabase and increment scan count if user is logged in
    if is_premium and user_id:
        risk_score = results["grade"]
        issue_count = len(results["issues"])

        scan_data = {
            "user_id": str(user_id),
            "hostname": scanner.hostname,
            "risk_score": risk_score,
            "issue_count": issue_count,
            "pdf_url": pdf_filename,
            "findings": results["issues"] # Save the full research for the portal
        }
        try:
            # Use the authenticated client to bypass RLS properly
            supabase.postgrest.auth(token).table("scans").insert(scan_data).execute()
            print(f"SUCCESS: Scan saved for {scanner.hostname}")
            
            # Increment scan count using user's token for RLS
            current_count = supabase.postgrest.auth(token).table("subscriptions").select("scans_this_month").eq("user_id", str(user_id)).execute().data[0]["scans_this_month"]
            supabase.postgrest.auth(token).table("subscriptions").update({
                "scans_this_month": current_count + 1
            }).eq("user_id", str(user_id)).execute()
            print(f"SUCCESS: Scan count incremented for user {user_id}")
            
        except Exception as e:
            print(f"CRITICAL: Error saving scan to Supabase: {e}")
            # Fallback for local testing if token auth fails
            try:
                supabase.table("scans").insert(scan_data).execute()
                print("FALLBACK SUCCESS: Saved without token header")
            except Exception as e2:
                print(f"ULTIMATE FAILURE: {e2}")

    return results

@app.get("/download-pdf/{filename}")
async def download_pdf(
    filename: str, 
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    """Returns the generated PDF file. Requires authentication."""
    # Verify user is authenticated
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required to download PDF reports")
    
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")
    
    # Check if file exists
    if os.path.exists(filename):
        background_tasks.add_task(cleanup_file, filename)
        return FileResponse(
            path=filename, 
            filename=filename, 
            media_type='application/pdf'
        )
    raise HTTPException(status_code=404, detail="File not found or already deleted.")

@app.delete("/delete-scan/{scan_id}")
async def delete_scan(scan_id: str, authorization: Optional[str] = Header(None)):
    """Deletes a specific scan record if it belongs to the authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        print(f"DEBUG: Attempting to delete scan {scan_id} for user {user.id}")
        
        # 1. Try deleting with strict user_id filtering using the main client (bypass RLS potential issues)
        # This is more stable as it doesn't rely on the schema cache of the auth client
        result = supabase.table("scans").delete().eq("id", scan_id).eq("user_id", str(user.id)).execute()
        
        # 2. If no data was deleted, try with integer casting
        if not result.data and scan_id.isdigit():
            print("DEBUG: UUID match failed, trying as integer ID...")
            result = supabase.table("scans").delete().eq("id", int(scan_id)).eq("user_id", str(user.id)).execute()

        # 3. Final verification
        if result.data:
            print(f"DEBUG: Successfully deleted scan {scan_id}")
            return {"status": "success", "message": "Scan deleted successfully"}
        else:
            print(f"DEBUG: No scan found to delete with ID {scan_id} for user {user.id}")
            return {"status": "error", "message": "No matching scan found in database"}

    except Exception as e:
        print(f"CRITICAL DELETE ERROR: {e}")
        # Log to Supabase directly if the above fails
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/toggle-automation")
async def toggle_automation(data: dict, authorization: Optional[str] = Header(None)):
    """Enables/Disables 24hr automated scanning for a host."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Session")

    hostname = data.get("hostname")
    enable = data.get("enable", True)
    job_id = f"auto_{user.id}_{hostname}"

    if enable:
        # Add job to run every 24 hours
        scheduler.add_job(
            run_automated_scan,
            trigger=IntervalTrigger(hours=24),
            args=[str(user.id), hostname, token],
            id=job_id,
            replace_existing=True
        )
        msg = f"Automation enabled for {hostname}"
    else:
        # Remove job
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        msg = f"Automation disabled for {hostname}"

    return {"status": "success", "message": msg, "is_automated": enable}

@app.get("/subscription")
async def get_subscription(authorization: Optional[str] = Header(None)):
    """Get user's current subscription details"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Use auth(token) to respect RLS
        result = supabase.postgrest.auth(token).table("subscriptions").select("*").eq("user_id", str(user.id)).execute()
        
        if result.data and len(result.data) > 0:
            sub_data = result.data[0]
            # Calculate scans remaining
            tier = sub_data.get("tier", "free")
            scans_this_month = sub_data.get("scans_this_month", 0)
            scans_limit = sub_data.get("scans_limit", 5)
            scans_remaining = -1 if tier == "enterprise" else max(0, scans_limit - scans_this_month)

            return {
                "tier": sub_data.get("tier", "free"),
                "tier_name": sub_data.get("tier_name", "Free"),
                "scans_this_month": scans_this_month,
                "scans_limit": scans_limit,
                "scans_remaining": scans_remaining,
                "features": sub_data.get("features", {}),
                "current_period_end": sub_data.get("current_period_end")
            }
        else:
            # Handle case where trigger might not have run yet
            return {
                "tier": "free",
                "tier_name": "Free",
                "scans_this_month": 0,
                "scans_limit": 5,
                "scans_remaining": 5
            }
    except Exception as e:
        print(f"Error fetching subscription: {e}")
        return {"tier": "free", "tier_name": "Free", "scans_this_month": 0, "scans_limit": 5}

@app.post("/upgrade-subscription")
async def upgrade_subscription(data: dict, authorization: Optional[str] = Header(None)):
    """Upgrade user subscription using user's token for RLS"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    tier = data.get("tier", "free").lower()
    
    # Map tier to limit and features
    plan_meta = {
        "free": {
            "limit": 5,
            "features": {
                "pdf_download": False, "selenium_enabled": False, "code_snippets": False,
                "automated_scans": False, "api_access": False
            }
        },
        "basic": {
            "limit": 50,
            "features": {
                "pdf_download": True, "selenium_enabled": True, "code_snippets": False,
                "automated_scans": False, "api_access": False
            }
        },
        "professional": {
            "limit": 200,
            "features": {
                "pdf_download": True, "selenium_enabled": True, "code_snippets": True,
                "automated_scans": True, "api_access": True
            }
        },
        "enterprise": {
            "limit": -1,
            "features": {
                "pdf_download": True, "selenium_enabled": True, "code_snippets": True,
                "automated_scans": True, "api_access": True, "priority_support": True, "custom_branding": True
            }
        }
    }
    
    meta = plan_meta.get(tier, plan_meta["free"])
    
    try:
        # Check if subscription exists using admin client for check
        result = supabase.table("subscriptions").select("*").eq("user_id", str(user.id)).execute()
        
        now = datetime.now()
        subscription_data = {
            "user_id": str(user.id),
            "tier": tier,
            "tier_name": tier.capitalize(),
            "scans_limit": meta["limit"],
            "features": meta["features"],
            "scans_this_month": 0, # Reset count on upgrade/change
            "current_period_start": now.isoformat(),
            "current_period_end": (now + relativedelta(months=1)).isoformat(),
            "updated_at": now.isoformat()
        }
        
        # Use admin client with user_id check to ensure stability
        if result.data and len(result.data) > 0:
            # Update existing
            supabase.table("subscriptions").update(subscription_data).eq("user_id", str(user.id)).execute()
        else:
            # Create new
            supabase.table("subscriptions").insert(subscription_data).execute()
        
        return {
            "status": "success",
            "message": f"Successfully upgraded to {tier} plan",
            "tier": tier
        }
    except Exception as e:
        print(f"Error upgrading subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_paypal_access_token():
    """Get PayPal OAuth2 access token."""
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET))
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"PAYPAL AUTH ERROR: {response.text}")
        return None

@app.post("/create-paypal-order")
async def create_paypal_order(data: dict, authorization: Optional[str] = Header(None)):
    """Creates a PayPal order for subscription upgrade."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    tier = data.get("tier", "basic").lower()
    
    # Prices as defined in PricingPage
    price_map = {
        "basic": 29,
        "professional": 99,
        "enterprise": 299
    }
    
    amount = price_map.get(tier)
    if not amount:
        raise HTTPException(status_code=400, detail="Invalid tier")

    access_token = get_paypal_access_token()
    if not access_token:
        raise HTTPException(status_code=500, detail="PayPal Authentication Failed")

    url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": str(amount)
            },
            "description": f"CyberSecure {tier.capitalize()} Plan",
            "reference_id": f"{user.id}_{tier}"
        }],
        "application_context": {
            "brand_name": "CyberSecure India",
            "return_url": f"{FRONTEND_URL}/payment-success",
            "cancel_url": f"{FRONTEND_URL}/pricing"
        }
    }

    response = requests.post(url, headers=headers, json=order_data)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"PAYPAL ORDER ERROR: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/webhook")
async def paypal_webhook(request: Request):
    """PayPal webhook to handle asynchronous events."""
    # For simplicity in local dev, we skip strict signature verification 
    # unless PAYPAL_WEBHOOK_ID is provided and we implement verification.
    # In production, ALWAYS verify the signature.
    
    data = await request.json()
    event_type = data.get("event_type")
    
    if event_type == "CHECKOUT.ORDER.COMPLETED" or event_type == "PAYMENT.CAPTURE.COMPLETED":
        resource = data.get("resource", {})
        
        # Try to extract user_id and tier from custom description or metadata
        # In PayPal V2 Orders, reference_id is used for this
        reference_id = resource.get("reference_id")
        if not reference_id:
            # If order level, it might be deeper
            purchase_units = resource.get("purchase_units", [])
            if purchase_units:
                reference_id = purchase_units[0].get("reference_id")
                
        if reference_id and "_" in reference_id:
            user_id, tier = reference_id.split("_")
            print(f"WEBHOOK: PayPal payment completed for user {user_id}, upgrading to {tier}")
            await perform_upgrade(user_id, tier)

    return {"status": "success"}

async def perform_upgrade(user_id: str, tier: str):
    """Helper function to perform database upgrade."""
    plan_meta = {
        "free": {"limit": 5, "features": {"pdf_download": False, "selenium_enabled": False, "code_snippets": False, "automated_scans": False, "api_access": False}},
        "basic": {"limit": 50, "features": {"pdf_download": True, "selenium_enabled": True, "code_snippets": False, "automated_scans": False, "api_access": False}},
        "professional": {"limit": 200, "features": {"pdf_download": True, "selenium_enabled": True, "code_snippets": True, "automated_scans": True, "api_access": True}},
        "enterprise": {"limit": -1, "features": {"pdf_download": True, "selenium_enabled": True, "code_snippets": True, "automated_scans": True, "api_access": True, "priority_support": True, "custom_branding": True}}
    }
    meta = plan_meta.get(tier, plan_meta["free"])
    now = datetime.now()
    
    subscription_data = {
        "user_id": user_id,
        "tier": tier,
        "tier_name": tier.capitalize(),
        "scans_limit": meta["limit"],
        "features": meta["features"],
        "scans_this_month": 0,
        "current_period_start": now.isoformat(),
        "current_period_end": (now + relativedelta(months=1)).isoformat(),
        "updated_at": now.isoformat()
    }

    # Use admin client to update the DB
    result = supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
    if result.data:
        supabase.table("subscriptions").update(subscription_data).eq("user_id", user_id).execute()
    else:
        supabase.table("subscriptions").insert(subscription_data).execute()

@app.post("/cancel-subscription")
async def cancel_subscription(authorization: Optional[str] = Header(None)):
    """Sets the subscription to cancel at the end of the current period."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        supabase.table("subscriptions").update({
            "cancel_at_period_end": True,
            "updated_at": datetime.now().isoformat()
        }).eq("user_id", str(user.id)).execute()
        
        return {"status": "success", "message": "Subscription will be canceled at the end of the period."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pricing-plans")
def get_pricing_plans():
    """Get all available pricing plans"""
    return {
        "plans": [
            {
                "tier": "free",
                "name": "Free",
                "price": 0,
                "features": {
                    "scans_per_month": 5,
                    "pdf_download": False,
                    "selenium_enabled": False,
                    "code_snippets": False,
                    "automated_scans": False
                }
            },
            {
                "tier": "basic",
                "name": "Basic",
                "price": 29,
                "features": {
                    "scans_per_month": 50,
                    "pdf_download": True,
                    "selenium_enabled": True,
                    "code_snippets": False,
                    "automated_scans": False
                }
            },
            {
                "tier": "professional",
                "name": "Professional",
                "price": 99,
                "features": {
                    "scans_per_month": 200,
                    "pdf_download": True,
                    "selenium_enabled": True,
                    "code_snippets": True,
                    "automated_scans": True
                }
            },
            {
                "tier": "enterprise",
                "name": "Enterprise",
                "price": 299,
                "features": {
                    "scans_per_month": -1,
                    "pdf_download": True,
                    "selenium_enabled": True,
                    "code_snippets": True,
                    "automated_scans": True,
                    "priority_support": True,
                    "custom_branding": True
                }
            }
        ]
    }

@app.get("/")
def home():
    return {"message": "CyberSecure API with Supabase is Running."}