# 🗄️ Database Setup Guide for Subscription System

## Overview
This guide will help you set up the database tables needed for the subscription system in Supabase.

---

## 📋 Prerequisites

- Supabase project created
- Access to Supabase SQL Editor
- Supabase URL and API keys configured in `.env`

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Open Supabase SQL Editor

1. Go to your Supabase Dashboard: https://app.supabase.com
2. Select your project
3. Click on **SQL Editor** in the left sidebar
4. Click **"New query"**

### Step 2: Run the Migration

1. Open the file: `database/subscription_migration.sql`
2. Copy the **entire contents** of the file
3. Paste into the Supabase SQL Editor
4. Click **"Run"** button (or press Ctrl/Cmd + Enter)

### Step 3: Verify Setup

Run these verification queries in the SQL Editor:

```sql
-- Check if subscriptions table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'subscriptions'
) AS subscriptions_table_exists;

-- Should return: true
```

```sql
-- View subscription tiers
SELECT * FROM public.subscription_tiers ORDER BY price_monthly;

-- Should show 4 tiers: free, basic, professional, enterprise
```

```sql
-- Check if trigger exists
SELECT tgname FROM pg_trigger WHERE tgname = 'on_auth_user_created_subscription';

-- Should return: on_auth_user_created_subscription
```

---

## 📊 What Gets Created

### 1. **subscriptions** Table
Stores user subscription data:
- `id` - Unique subscription ID
- `user_id` - Reference to auth.users
- `tier` - Subscription tier (free, basic, professional, enterprise)
- `scans_this_month` - Current month's scan count
- `scans_limit` - Maximum scans allowed per month
- `features` - JSONB of enabled features
- `stripe_customer_id` - For Stripe integration
- `current_period_end` - Billing period end date

### 2. **subscription_tiers** Table
Reference table with tier definitions:
- Tier names and prices
- Feature lists
- Scan limits

### 3. **Triggers**
- `on_auth_user_created_subscription` - Auto-creates free subscription for new users
- `update_subscriptions_updated_at` - Auto-updates timestamp

### 4. **Functions**
- `handle_new_user_subscription()` - Creates free subscription on signup
- `reset_monthly_scans()` - Resets scan counts monthly
- `increment_scan_count(user_id)` - Increments user's scan count
- `can_user_scan(user_id)` - Checks if user can perform scan

### 5. **RLS Policies**
- Users can view their own subscription
- Users can update their own subscription
- Service role has full access

---

## 🧪 Testing the Setup

### Test 1: Create a New User

1. Sign up in your app
2. Check if subscription was auto-created:

```sql
SELECT u.email, s.tier, s.scans_limit
FROM auth.users u
LEFT JOIN public.subscriptions s ON s.user_id = u.id
ORDER BY u.created_at DESC
LIMIT 5;
```

You should see the new user with `tier = 'free'` and `scans_limit = 5`.

### Test 2: Manually Create Subscription

```sql
-- Replace with your actual user ID
INSERT INTO public.subscriptions (user_id, tier, tier_name, scans_limit)
VALUES ('YOUR_USER_ID_HERE', 'basic', 'Basic', 50);
```

### Test 3: Check Scan Limit Function

```sql
-- Replace with your actual user ID
SELECT public.can_user_scan('YOUR_USER_ID_HERE');

-- Should return: true (if under limit)
```

### Test 4: Increment Scan Count

```sql
-- Replace with your actual user ID
SELECT public.increment_scan_count('YOUR_USER_ID_HERE');

-- Then check the count
SELECT scans_this_month FROM public.subscriptions 
WHERE user_id = 'YOUR_USER_ID_HERE';
```

---

## 🔄 Monthly Maintenance

### Reset Scan Counts

At the start of each month, run this to reset all scan counts:

```sql
SELECT public.reset_monthly_scans();
```

**Recommended**: Set up a cron job or use Supabase Edge Functions to run this automatically.

### Using Supabase Cron (pg_cron extension)

```sql
-- Enable pg_cron extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule monthly reset (runs on 1st of each month at midnight)
SELECT cron.schedule(
    'reset-monthly-scans',
    '0 0 1 * *',
    $$SELECT public.reset_monthly_scans()$$
);
```

---

## 📈 Monitoring Queries

### View All Subscriptions

```sql
SELECT 
    u.email,
    s.tier,
    s.tier_name,
    s.scans_this_month,
    s.scans_limit,
    (s.scans_limit - s.scans_this_month) as scans_remaining,
    s.created_at
FROM public.subscriptions s
JOIN auth.users u ON u.id = s.user_id
ORDER BY s.created_at DESC;
```

### Subscription Distribution

```sql
SELECT 
    tier,
    COUNT(*) as user_count,
    SUM(scans_this_month) as total_scans
FROM public.subscriptions
GROUP BY tier
ORDER BY 
    CASE tier
        WHEN 'free' THEN 1
        WHEN 'basic' THEN 2
        WHEN 'professional' THEN 3
        WHEN 'enterprise' THEN 4
    END;
```

### Users Near Scan Limit

```sql
SELECT 
    u.email,
    s.tier,
    s.scans_this_month,
    s.scans_limit,
    ROUND((s.scans_this_month::FLOAT / s.scans_limit) * 100, 2) as usage_percentage
FROM public.subscriptions s
JOIN auth.users u ON u.id = s.user_id
WHERE s.tier != 'enterprise'
AND s.scans_this_month >= (s.scans_limit * 0.8)
ORDER BY usage_percentage DESC;
```

### Revenue Calculation

```sql
SELECT 
    tier,
    COUNT(*) as subscribers,
    CASE tier
        WHEN 'basic' THEN 29
        WHEN 'professional' THEN 99
        WHEN 'enterprise' THEN 299
        ELSE 0
    END as monthly_price,
    COUNT(*) * CASE tier
        WHEN 'basic' THEN 29
        WHEN 'professional' THEN 99
        WHEN 'enterprise' THEN 299
        ELSE 0
    END as monthly_revenue
FROM public.subscriptions
GROUP BY tier
ORDER BY monthly_revenue DESC;
```

---

## 🔧 Common Operations

### Upgrade a User Manually

```sql
UPDATE public.subscriptions
SET 
    tier = 'professional',
    tier_name = 'Professional',
    scans_limit = 200,
    features = '{
        "pdf_download": true,
        "selenium_enabled": true,
        "code_snippets": true,
        "automated_scans": true,
        "api_access": true
    }'::jsonb
WHERE user_id = 'USER_ID_HERE';
```

### Reset a User's Scan Count

```sql
UPDATE public.subscriptions
SET scans_this_month = 0
WHERE user_id = 'USER_ID_HERE';
```

### Give a User Bonus Scans

```sql
UPDATE public.subscriptions
SET scans_limit = scans_limit + 10
WHERE user_id = 'USER_ID_HERE';
```

### View User's Subscription Details

```sql
SELECT 
    u.email,
    s.*
FROM public.subscriptions s
JOIN auth.users u ON u.id = s.user_id
WHERE u.email = 'user@example.com';
```

---

## 🐛 Troubleshooting

### Issue: Trigger not creating subscriptions for new users

**Check if trigger exists:**
```sql
SELECT * FROM pg_trigger WHERE tgname = 'on_auth_user_created_subscription';
```

**Recreate trigger:**
```sql
DROP TRIGGER IF EXISTS on_auth_user_created_subscription ON auth.users;
CREATE TRIGGER on_auth_user_created_subscription
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user_subscription();
```

### Issue: RLS blocking queries

**Check RLS policies:**
```sql
SELECT * FROM pg_policies WHERE tablename = 'subscriptions';
```

**Temporarily disable RLS (for testing only):**
```sql
ALTER TABLE public.subscriptions DISABLE ROW LEVEL SECURITY;
-- Remember to re-enable: ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
```

### Issue: Scan count not incrementing

**Check current count:**
```sql
SELECT scans_this_month FROM public.subscriptions WHERE user_id = 'USER_ID';
```

**Manually increment:**
```sql
UPDATE public.subscriptions 
SET scans_this_month = scans_this_month + 1 
WHERE user_id = 'USER_ID';
```

---

## 🔒 Security Best Practices

1. **Never expose service_role key** in frontend
2. **Always use RLS policies** for user data
3. **Validate subscription tier** on backend before granting access
4. **Log subscription changes** for audit trail
5. **Encrypt sensitive data** (Stripe IDs, etc.)

---

## 📝 Schema Diagram

```
auth.users (Supabase Auth)
    ↓ (one-to-one)
subscriptions
    - id (UUID, PK)
    - user_id (UUID, FK → auth.users.id)
    - tier (TEXT)
    - scans_this_month (INTEGER)
    - scans_limit (INTEGER)
    - features (JSONB)
    - stripe_customer_id (TEXT)
    - created_at (TIMESTAMP)
    - updated_at (TIMESTAMP)

subscription_tiers (Reference)
    - tier (TEXT, PK)
    - name (TEXT)
    - price_monthly (INTEGER)
    - features (JSONB)
```

---

## ✅ Checklist

After running the migration, verify:

- [ ] `subscriptions` table exists
- [ ] `subscription_tiers` table exists
- [ ] Trigger `on_auth_user_created_subscription` exists
- [ ] RLS policies are enabled
- [ ] Test user signup creates free subscription
- [ ] Can query subscription data
- [ ] Scan count increments correctly
- [ ] Monthly reset function works

---

## 🆘 Need Help?

- **Supabase Docs**: https://supabase.com/docs/guides/database
- **SQL Reference**: https://www.postgresql.org/docs/
- **RLS Guide**: https://supabase.com/docs/guides/auth/row-level-security

---

**Last Updated**: February 4, 2026  
**Version**: 1.0  
**Migration File**: `database/subscription_migration.sql`
