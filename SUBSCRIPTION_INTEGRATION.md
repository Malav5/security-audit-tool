# Subscription System Integration Guide

## Overview
This guide explains how to integrate the subscription system into your existing App.jsx.

## Files Created

1. **`backend/subscription.py`** - Subscription management logic
2. **`frontend/src/PricingPage.jsx`** - Beautiful pricing page component
3. **`frontend/src/api.js`** - Updated with subscription API calls

## Integration Steps

### Step 1: Import PricingPage in App.jsx

Add to the imports at the top of `App.jsx`:

```javascript
import PricingPage from './PricingPage';
import { getSubscription, upgradeSubscription } from './api';
import { Crown } from 'lucide-react';
```

### Step 2: Add Subscription State

Add these state variables after the existing state declarations (around line 35):

```javascript
// Subscription State
const [subscription, setSubscription] = useState(null);
const [showPricing, setShowPricing] = useState(false);
```

### Step 3: Fetch Subscription on Login

Add this useEffect after the existing useEffects (around line 82):

```javascript
useEffect(() => {
  if (session) {
    fetchSubscription();
  }
}, [session]);

const fetchSubscription = async () => {
  try {
    const subData = await getSubscription(session.access_token);
    setSubscription(subData);
  } catch (err) {
    console.error('Error fetching subscription:', err);
  }
};
```

### Step 4: Add Upgrade Handler

Add this function after `handleToggleAutomation` (around line 242):

```javascript
const handleUpgrade = async (tier) => {
  if (!session) {
    setShowAuth(true);
    return;
  }

  if (tier === 'enterprise') {
    // Open contact sales
    window.open('mailto:sales@cybersecure.com?subject=Enterprise Plan Inquiry', '_blank');
    return;
  }

  try {
    await upgradeSubscription(tier, session.access_token);
    await fetchSubscription(); // Refresh subscription data
    setShowPricing(false);
    alert(`Successfully upgraded to ${tier} plan!`);
  } catch (err) {
    alert(err.message);
  }
};
```

### Step 5: Add Upgrade Button to Navbar

Update the navbar section (around line 260) to include an upgrade button:

```javascript
<div className="flex items-center gap-4">
  {!isInitialLoading && (
    session ? (
      <div className="flex items-center gap-3">
        {/* Subscription Badge */}
        {subscription && subscription.tier !== 'free' && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30">
            <Crown className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-semibold text-cyan-400">
              {subscription.tier_name}
            </span>
          </div>
        )}
        
        {/* Upgrade Button (show for free users) */}
        {subscription && subscription.tier === 'free' && (
          <button
            onClick={() => setShowPricing(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold hover:shadow-lg hover:shadow-cyan-500/20 transition"
          >
            <Crown className="w-4 h-4" />
            <span className="hidden md:inline">Upgrade</span>
          </button>
        )}
        
        {/* Existing Dashboard Button */}
        <button
          onClick={() => setView(view === 'dashboard' ? 'home' : 'dashboard')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 hover:bg-slate-700 transition"
        >
          {view === 'dashboard' ? <Globe className="w-4 h-4" /> : <LayoutDashboard className="w-4 h-4" />}
          <span className="hidden md:inline">{view === 'dashboard' ? 'Home' : 'Dashboard'}</span>
        </button>
        
        {/* Existing Sign Out Button */}
        <button
          onClick={handleSignOut}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-900/20 border border-red-900/50 hover:bg-red-900/40 text-red-400 transition"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden md:inline">Sign Out</span>
        </button>
      </div>
    ) : (
      <button
        onClick={() => setShowAuth(true)}
        className="flex items-center gap-2 px-6 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-600 text-white font-semibold transition shadow-lg shadow-cyan-500/20"
      >
        <User className="w-4 h-4" />
        <span>Sign In</span>
      </button>
    )
  )}
</div>
```

### Step 6: Add Pricing Modal

Add this before the closing `</div>` of the main container (around line 776):

```javascript
{/* Pricing Modal */}
<AnimatePresence>
  {showPricing && (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={() => setShowPricing(false)}
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
      />
      <div className="relative min-h-screen">
        <button
          onClick={() => setShowPricing(false)}
          className="absolute top-6 right-6 z-50 p-2 rounded-lg bg-slate-800 text-white hover:bg-slate-700 transition"
        >
          <X className="w-6 h-6" />
        </button>
        <PricingPage 
          session={session} 
          onUpgrade={handleUpgrade}
          onClose={() => setShowPricing(false)}
        />
      </div>
    </div>
  )}
</AnimatePresence>
```

### Step 7: Add Scan Limit Check

Update the `handleScan` function to check subscription limits (around line 136):

```javascript
const handleScan = async (e) => {
  e.preventDefault();
  if (!url) {
    setError("Please enter a valid URL");
    return;
  }

  // Check subscription limits
  if (session && subscription) {
    if (subscription.scans_remaining === 0) {
      setError(`You've reached your monthly scan limit (${subscription.scans_limit} scans). Please upgrade your plan.`);
      setShowPricing(true);
      return;
    }
  }

  try {
    new URL(url.startsWith('http') ? url : `https://${url}`);
  } catch (_) {
    setError("Please enter a valid URL (e.g., example.com)");
    return;
  }

  // ... rest of existing handleScan code ...
};
```

### Step 8: Show Scans Remaining

Add a scan counter in the dashboard view (around line 610):

```javascript
<div className="flex justify-between items-end border-b border-slate-800 pb-6">
  <div>
    <h2 className="text-3xl font-bold text-white">Security Dashboard</h2>
    <p className="text-slate-400 mt-1">Manage and review your organization's scan history.</p>
    
    {/* Scans Remaining */}
    {subscription && (
      <div className="mt-3 flex items-center gap-2">
        <Activity className="w-4 h-4 text-cyan-400" />
        <span className="text-sm text-slate-300">
          {subscription.scans_remaining === -1 
            ? 'Unlimited scans remaining' 
            : `${subscription.scans_remaining} scans remaining this month`}
        </span>
      </div>
    )}
  </div>
  
  <div className="flex gap-3">
    {subscription && subscription.tier === 'free' && (
      <button
        onClick={() => setShowPricing(true)}
        className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold hover:shadow-lg transition flex items-center gap-2"
      >
        <Crown className="w-4 h-4" />
        Upgrade Plan
      </button>
    )}
    <button
      onClick={() => setView('home')}
      className="px-4 py-2 rounded-lg bg-cyan-500/10 text-cyan-400 text-sm font-semibold hover:bg-cyan-500/20 transition flex items-center gap-2"
    >
      <ArrowLeft className="w-4 h-4" /> New Scan
    </button>
  </div>
</div>
```

---

## Database Setup

### Create Subscriptions Table in Supabase

Run this SQL in Supabase SQL Editor:

```sql
-- Create subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    tier TEXT NOT NULL DEFAULT 'free',
    tier_name TEXT NOT NULL DEFAULT 'Free',
    scans_this_month INTEGER DEFAULT 0,
    scans_limit INTEGER DEFAULT 5,
    features JSONB DEFAULT '{}',
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    current_period_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Enable RLS
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Create policy for users to read their own subscription
CREATE POLICY "Users can view own subscription"
    ON subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Create policy for users to insert their own subscription
CREATE POLICY "Users can insert own subscription"
    ON subscriptions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create policy for users to update their own subscription
CREATE POLICY "Users can update own subscription"
    ON subscriptions FOR UPDATE
    USING (auth.uid() = user_id);

-- Create index for faster lookups
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);

-- Create function to auto-create free subscription on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.subscriptions (user_id, tier, tier_name, scans_limit)
    VALUES (NEW.id, 'free', 'Free', 5);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to auto-create subscription
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
```

---

## Testing

### 1. Test Free Tier
- Sign up with new account
- Verify "Upgrade" button appears in navbar
- Click upgrade button
- Verify pricing page opens

### 2. Test Upgrade
- Click on "Upgrade to Basic" button
- Verify subscription updates
- Verify navbar shows "Basic" badge
- Verify "Upgrade" button disappears

### 3. Test Scan Limits
- As free user, run 5 scans
- Try to run 6th scan
- Verify error message and pricing modal opens

### 4. Test Dashboard
- Verify scans remaining counter shows
- Verify upgrade button shows for free users
- Verify badge shows for paid users

---

## Stripe Integration (Optional)

To add real payment processing:

### 1. Install Stripe
```bash
pip install stripe
```

### 2. Update backend/main.py

Add Stripe initialization:
```python
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
```

### 3. Create Checkout Session
```python
@app.post("/create-checkout-session")
async def create_checkout_session(data: dict, authorization: Optional[str] = Header(None)):
    # Verify user
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    
    tier = data.get("tier")
    price_id = get_stripe_price_id(tier)  # Map tier to Stripe price ID
    
    session = stripe.checkout.Session.create(
        customer_email=user.email,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url='https://your-frontend.com/success',
        cancel_url='https://your-frontend.com/pricing',
    )
    
    return {"checkout_url": session.url}
```

### 4. Update Frontend
```javascript
const handleUpgrade = async (tier) => {
  const response = await api.post('/create-checkout-session', { tier });
  window.location.href = response.data.checkout_url;
};
```

---

## Summary

You now have:
- ✅ 4-tier subscription system (Free, Basic, Professional, Enterprise)
- ✅ Beautiful pricing page with feature comparison
- ✅ Upgrade button in navbar
- ✅ Subscription badge for paid users
- ✅ Scan limit enforcement
- ✅ Scans remaining counter
- ✅ Database schema for subscriptions
- ✅ API endpoints for subscription management

**Next Steps**:
1. Follow integration steps above
2. Create subscriptions table in Supabase
3. Test the flow
4. (Optional) Add Stripe for real payments

---

**Last Updated**: February 4, 2026  
**Version**: 1.0
