from fastapi import FastAPI, BackgroundTasks, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Import the scanner class from your existing script
from audit_tool import SecurityScanner 

load_dotenv()

# --- SUPABASE CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="CyberSecure Audit API",
    description="A White-Label API that generates PDF security reports.",
    version="1.0"
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

    # Check for authentication
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user = await verify_user(token)
        if user:
            is_premium = True
            user_id = user.id

    # 1. Initialize the Scanner
    scanner = SecurityScanner(target_url)
    
    # 2. Run all checks
    results = scanner.run(is_premium=is_premium)
    pdf_filename = results["pdf_filename"]
    
    # 3. Save to Supabase if the user is logged in
    if is_premium and user_id:
        risk_score = results["grade"]
        issue_count = len(results["issues"])

        scan_data = {
            "user_id": str(user_id),
            "hostname": scanner.hostname,
            "risk_score": risk_score,
            "issue_count": issue_count,
            "pdf_url": pdf_filename
        }
        try:
            supabase.postgrest.auth(token).table("scans").insert(scan_data).execute()
        except Exception as e:
            print(f"CRITICAL: Error saving scan to Supabase: {e}")

    return results

@app.get("/download-pdf/{filename}")
async def download_pdf(filename: str, background_tasks: BackgroundTasks):
    """Returns the generated PDF file."""
    if os.path.exists(filename):
        background_tasks.add_task(cleanup_file, filename)
        return FileResponse(
            path=filename, 
            filename=filename, 
            media_type='application/pdf'
        )
    raise HTTPException(status_code=404, detail="File not found or already deleted.")

@app.post("/save-scan")
async def save_scan(data: dict):
    """Explicitly save a scan record (optional)"""
    try:
        supabase.table("scans").insert(data).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "CyberSecure API with Supabase is Running."}