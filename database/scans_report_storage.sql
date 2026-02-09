-- =====================================================
-- SCANS REPORT STORAGE MIGRATION
-- Run this in Supabase SQL Editor to enable report storage
-- =====================================================

-- 1. Add pdf_content column to scans table
-- This allows storing the base64 encoded PDF directly in the database
-- to prevent the "Report Expired" issue when the server restarts.
ALTER TABLE public.scans 
ADD COLUMN IF NOT EXISTS pdf_content TEXT;

-- 2. Add an index for performance (optional)
-- CREATE INDEX IF NOT EXISTS idx_scans_pdf_url ON public.scans(pdf_url);

-- 3. Verify the column exists
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='scans' AND column_name='pdf_content'
    ) THEN
        RAISE NOTICE 'Column pdf_content created successfully.';
    ELSE
        RAISE NOTICE 'Failed to create column pdf_content.';
    END IF;
END $$;
