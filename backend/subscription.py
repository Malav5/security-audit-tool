"""
Subscription management and pricing plans
"""

from enum import Enum
from typing import Optional
from datetime import datetime, timedelta

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class SubscriptionPlan:
    """Defines subscription plans and their features"""
    
    PLANS = {
        SubscriptionTier.FREE: {
            "name": "Free",
            "price": 0,
            "price_id": None,  # No Stripe price ID for free
            "features": {
                "scans_per_month": 5,
                "selenium_enabled": False,
                "pdf_download": False,
                "detailed_fixes": False,
                "compliance_mapping": False,
                "code_snippets": False,
                "automated_scans": False,
                "api_access": False,
                "priority_support": False,
                "custom_branding": False,
                "findings_limit": 3,  # Show only 3 findings
                "severity_filter": ["HIGH"],  # Only show high severity
            },
            "description": "Perfect for trying out the platform",
            "cta": "Get Started Free"
        },
        SubscriptionTier.BASIC: {
            "name": "Basic",
            "price": 29,
            "price_id": "price_basic_monthly",  # Replace with actual Stripe price ID
            "features": {
                "scans_per_month": 50,
                "selenium_enabled": True,
                "pdf_download": True,
                "detailed_fixes": True,
                "compliance_mapping": True,
                "code_snippets": False,
                "automated_scans": False,
                "api_access": False,
                "priority_support": False,
                "custom_branding": False,
                "findings_limit": None,  # Show all findings
                "severity_filter": None,  # Show all severities
            },
            "description": "Great for small teams and startups",
            "cta": "Upgrade to Basic"
        },
        SubscriptionTier.PROFESSIONAL: {
            "name": "Professional",
            "price": 99,
            "price_id": "price_professional_monthly",  # Replace with actual Stripe price ID
            "features": {
                "scans_per_month": 200,
                "selenium_enabled": True,
                "pdf_download": True,
                "detailed_fixes": True,
                "compliance_mapping": True,
                "code_snippets": True,
                "automated_scans": True,
                "api_access": True,
                "priority_support": False,
                "custom_branding": False,
                "findings_limit": None,
                "severity_filter": None,
            },
            "description": "Perfect for growing businesses",
            "cta": "Upgrade to Professional"
        },
        SubscriptionTier.ENTERPRISE: {
            "name": "Enterprise",
            "price": 299,
            "price_id": "price_enterprise_monthly",  # Replace with actual Stripe price ID
            "features": {
                "scans_per_month": -1,  # Unlimited
                "selenium_enabled": True,
                "pdf_download": True,
                "detailed_fixes": True,
                "compliance_mapping": True,
                "code_snippets": True,
                "automated_scans": True,
                "api_access": True,
                "priority_support": True,
                "custom_branding": True,
                "findings_limit": None,
                "severity_filter": None,
            },
            "description": "For large organizations with advanced needs",
            "cta": "Contact Sales"
        }
    }
    
    @classmethod
    def get_plan(cls, tier: SubscriptionTier) -> dict:
        """Get plan details by tier"""
        return cls.PLANS.get(tier, cls.PLANS[SubscriptionTier.FREE])
    
    @classmethod
    def get_feature(cls, tier: SubscriptionTier, feature: str):
        """Get specific feature value for a tier"""
        plan = cls.get_plan(tier)
        return plan["features"].get(feature)
    
    @classmethod
    def can_use_feature(cls, tier: SubscriptionTier, feature: str) -> bool:
        """Check if tier has access to a feature"""
        feature_value = cls.get_feature(tier, feature)
        if isinstance(feature_value, bool):
            return feature_value
        return feature_value is not None
    
    @classmethod
    def filter_findings_by_plan(cls, findings: list, tier: SubscriptionTier) -> list:
        """Filter findings based on subscription tier"""
        plan = cls.get_plan(tier)
        
        # Filter by severity if restricted
        severity_filter = plan["features"]["severity_filter"]
        if severity_filter:
            findings = [f for f in findings if f.get("severity") in severity_filter]
        
        # Limit number of findings if restricted
        findings_limit = plan["features"]["findings_limit"]
        if findings_limit:
            findings = findings[:findings_limit]
        
        return findings
    
    @classmethod
    def get_pdf_content_level(cls, tier: SubscriptionTier) -> str:
        """Determine what content to show in PDF"""
        plan = cls.get_plan(tier)
        features = plan["features"]
        
        if not features["pdf_download"]:
            return "preview"  # Very limited preview
        elif not features["code_snippets"]:
            return "basic"  # No code snippets
        elif not features["custom_branding"]:
            return "professional"  # Full content, no branding
        else:
            return "enterprise"  # Everything including custom branding


class UserSubscription:
    """Manages user subscription state"""
    
    def __init__(self, user_id: str, tier: SubscriptionTier = SubscriptionTier.FREE,
                 stripe_customer_id: Optional[str] = None,
                 stripe_subscription_id: Optional[str] = None,
                 current_period_end: Optional[datetime] = None):
        self.user_id = user_id
        self.tier = tier
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.current_period_end = current_period_end or datetime.utcnow()
        self.scans_this_month = 0
    
    def is_active(self) -> bool:
        """Check if subscription is active"""
        if self.tier == SubscriptionTier.FREE:
            return True
        return datetime.utcnow() < self.current_period_end
    
    def can_scan(self) -> bool:
        """Check if user can perform another scan"""
        if not self.is_active():
            return False
        
        max_scans = SubscriptionPlan.get_feature(self.tier, "scans_per_month")
        if max_scans == -1:  # Unlimited
            return True
        
        return self.scans_this_month < max_scans
    
    def increment_scan_count(self):
        """Increment monthly scan count"""
        self.scans_this_month += 1
    
    def get_scans_remaining(self) -> int:
        """Get remaining scans for the month"""
        max_scans = SubscriptionPlan.get_feature(self.tier, "scans_per_month")
        if max_scans == -1:
            return -1  # Unlimited
        return max(0, max_scans - self.scans_this_month)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "user_id": self.user_id,
            "tier": self.tier.value,
            "tier_name": SubscriptionPlan.get_plan(self.tier)["name"],
            "is_active": self.is_active(),
            "scans_this_month": self.scans_this_month,
            "scans_remaining": self.get_scans_remaining(),
            "current_period_end": self.current_period_end.isoformat(),
            "features": SubscriptionPlan.get_plan(self.tier)["features"]
        }
