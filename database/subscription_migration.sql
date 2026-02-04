-- =====================================================
-- SUBSCRIPTION SYSTEM DATABASE MIGRATION
-- Run this in Supabase SQL Editor
-- =====================================================

-- 1. Create subscriptions table
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Subscription details
    tier TEXT NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'basic', 'professional', 'enterprise')),
    tier_name TEXT NOT NULL DEFAULT 'Free',
    
    -- Usage tracking
    scans_this_month INTEGER DEFAULT 0,
    scans_limit INTEGER DEFAULT 5,
    
    -- Features (stored as JSONB for flexibility)
    features JSONB DEFAULT '{
        "pdf_download": false,
        "selenium_enabled": false,
        "code_snippets": false,
        "automated_scans": false,
        "api_access": false,
        "priority_support": false,
        "custom_branding": false
    }'::jsonb,
    
    -- Stripe integration (for future use)
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    stripe_price_id TEXT,
    
    -- Billing
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one subscription per user
    UNIQUE(user_id)
);

-- 2. Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tier ON public.subscriptions(tier);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer ON public.subscriptions(stripe_customer_id);

-- 3. Enable Row Level Security (RLS)
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- 4. Create RLS policies
-- Users can view their own subscription
CREATE POLICY "Users can view own subscription"
    ON public.subscriptions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own subscription (for initial creation)
CREATE POLICY "Users can insert own subscription"
    ON public.subscriptions
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own subscription
CREATE POLICY "Users can update own subscription"
    ON public.subscriptions
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Service role can do everything (for backend operations)
CREATE POLICY "Service role has full access"
    ON public.subscriptions
    FOR ALL
    USING (auth.role() = 'service_role');

-- 5. Create function to auto-create free subscription on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user_subscription()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.subscriptions (
        user_id,
        tier,
        tier_name,
        scans_this_month,
        scans_limit,
        features,
        current_period_start,
        current_period_end
    )
    VALUES (
        NEW.id,
        'free',
        'Free',
        0,
        5,
        '{
            "pdf_download": false,
            "selenium_enabled": false,
            "code_snippets": false,
            "automated_scans": false,
            "api_access": false,
            "priority_support": false,
            "custom_branding": false
        }'::jsonb,
        NOW(),
        NOW() + INTERVAL '1 month'
    );
    RETURN NEW;
END;
$$;

-- 6. Create trigger to auto-create subscription on user signup
DROP TRIGGER IF EXISTS on_auth_user_created_subscription ON auth.users;
CREATE TRIGGER on_auth_user_created_subscription
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user_subscription();

-- 7. Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- 8. Create trigger to auto-update updated_at
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- 9. Create function to reset monthly scan count
CREATE OR REPLACE FUNCTION public.reset_monthly_scans()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.subscriptions
    SET scans_this_month = 0,
        current_period_start = NOW(),
        current_period_end = NOW() + INTERVAL '1 month'
    WHERE current_period_end < NOW();
END;
$$;

-- 10. Create function to increment scan count
CREATE OR REPLACE FUNCTION public.increment_scan_count(p_user_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE public.subscriptions
    SET scans_this_month = scans_this_month + 1
    WHERE user_id = p_user_id;
END;
$$;

-- 11. Create function to check if user can scan
CREATE OR REPLACE FUNCTION public.can_user_scan(p_user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_scans_this_month INTEGER;
    v_scans_limit INTEGER;
    v_tier TEXT;
BEGIN
    SELECT scans_this_month, scans_limit, tier
    INTO v_scans_this_month, v_scans_limit, v_tier
    FROM public.subscriptions
    WHERE user_id = p_user_id;
    
    -- If no subscription found, return false
    IF NOT FOUND THEN
        RETURN false;
    END IF;
    
    -- Enterprise has unlimited scans
    IF v_tier = 'enterprise' THEN
        RETURN true;
    END IF;
    
    -- Check if under limit
    RETURN v_scans_this_month < v_scans_limit;
END;
$$;

-- 12. Insert default subscription tiers reference table (optional, for documentation)
CREATE TABLE IF NOT EXISTS public.subscription_tiers (
    tier TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price_monthly INTEGER NOT NULL,
    price_yearly INTEGER NOT NULL,
    scans_limit INTEGER NOT NULL,
    features JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert tier definitions
INSERT INTO public.subscription_tiers (tier, name, price_monthly, price_yearly, scans_limit, features, description)
VALUES
    ('free', 'Free', 0, 0, 5, '{
        "pdf_download": false,
        "selenium_enabled": false,
        "code_snippets": false,
        "automated_scans": false,
        "api_access": false,
        "priority_support": false,
        "custom_branding": false
    }'::jsonb, 'Perfect for trying out the platform'),
    
    ('basic', 'Basic', 29, 278, 50, '{
        "pdf_download": true,
        "selenium_enabled": true,
        "code_snippets": false,
        "automated_scans": false,
        "api_access": false,
        "priority_support": false,
        "custom_branding": false
    }'::jsonb, 'Great for small teams and startups'),
    
    ('professional', 'Professional', 99, 950, 200, '{
        "pdf_download": true,
        "selenium_enabled": true,
        "code_snippets": true,
        "automated_scans": true,
        "api_access": true,
        "priority_support": false,
        "custom_branding": false
    }'::jsonb, 'Perfect for growing businesses'),
    
    ('enterprise', 'Enterprise', 299, 2870, -1, '{
        "pdf_download": true,
        "selenium_enabled": true,
        "code_snippets": true,
        "automated_scans": true,
        "api_access": true,
        "priority_support": true,
        "custom_branding": true
    }'::jsonb, 'For large organizations with advanced needs')
ON CONFLICT (tier) DO NOTHING;

-- 13. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON public.subscription_tiers TO anon, authenticated;
GRANT ALL ON public.subscriptions TO authenticated;

-- =====================================================
-- VERIFICATION QUERIES
-- Run these to verify the setup
-- =====================================================

-- Check if subscriptions table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'subscriptions'
) AS subscriptions_table_exists;

-- Check if trigger exists
SELECT EXISTS (
    SELECT FROM pg_trigger 
    WHERE tgname = 'on_auth_user_created_subscription'
) AS trigger_exists;

-- View all subscription tiers
SELECT * FROM public.subscription_tiers ORDER BY price_monthly;

-- Count existing subscriptions
SELECT COUNT(*) as total_subscriptions FROM public.subscriptions;

-- View subscriptions by tier
SELECT tier, COUNT(*) as count 
FROM public.subscriptions 
GROUP BY tier 
ORDER BY tier;

-- =====================================================
-- MAINTENANCE QUERIES
-- =====================================================

-- Manually reset all monthly scans (run at start of each month)
-- SELECT public.reset_monthly_scans();

-- Check users who are near their scan limit
-- SELECT 
--     u.email,
--     s.tier,
--     s.scans_this_month,
--     s.scans_limit,
--     (s.scans_limit - s.scans_this_month) as scans_remaining
-- FROM public.subscriptions s
-- JOIN auth.users u ON u.id = s.user_id
-- WHERE s.scans_this_month >= (s.scans_limit * 0.8)
-- AND s.tier != 'enterprise'
-- ORDER BY scans_remaining;

-- =====================================================
-- ROLLBACK (if needed)
-- =====================================================

-- DROP TRIGGER IF EXISTS on_auth_user_created_subscription ON auth.users;
-- DROP FUNCTION IF EXISTS public.handle_new_user_subscription();
-- DROP FUNCTION IF EXISTS public.reset_monthly_scans();
-- DROP FUNCTION IF EXISTS public.increment_scan_count(UUID);
-- DROP FUNCTION IF EXISTS public.can_user_scan(UUID);
-- DROP FUNCTION IF EXISTS public.update_updated_at_column();
-- DROP TABLE IF EXISTS public.subscriptions CASCADE;
-- DROP TABLE IF EXISTS public.subscription_tiers CASCADE;
