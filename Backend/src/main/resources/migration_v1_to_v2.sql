-- Migration Script: V1 to V2
-- Updates database schema to match actual FastAPI response structure
-- Run this if you have existing data from V1

-- ============================================================================
-- STEP 1: Add new columns
-- ============================================================================

ALTER TABLE anc_visits ADD COLUMN IF NOT EXISTS patient_name VARCHAR(255);
ALTER TABLE anc_visits ADD COLUMN IF NOT EXISTS is_high_risk BOOLEAN;
ALTER TABLE anc_visits ADD COLUMN IF NOT EXISTS detected_risks JSONB;
ALTER TABLE anc_visits ADD COLUMN IF NOT EXISTS explanation TEXT;
ALTER TABLE anc_visits ADD COLUMN IF NOT EXISTS confidence NUMERIC(4,3);
ALTER TABLE anc_visits ADD COLUMN IF NOT EXISTS recommendation TEXT;
ALTER TABLE anc_visits ADD COLUMN IF NOT EXISTS visit_metadata JSONB;

-- ============================================================================
-- STEP 2: Migrate existing data (if any)
-- ============================================================================

-- Map old risk_level to new is_high_risk boolean
UPDATE anc_visits 
SET is_high_risk = CASE 
    WHEN risk_level IN ('HIGH', 'CRITICAL') THEN true 
    ELSE false 
END
WHERE is_high_risk IS NULL;

-- Map old ai_flags to new detected_risks
UPDATE anc_visits 
SET detected_risks = ai_flags
WHERE detected_risks IS NULL AND ai_flags IS NOT NULL;

-- Map old ai_recommendations to new recommendation (take first item)
UPDATE anc_visits 
SET recommendation = ai_recommendations->>0
WHERE recommendation IS NULL AND ai_recommendations IS NOT NULL;

-- Set default confidence for existing records
UPDATE anc_visits 
SET confidence = 0.5
WHERE confidence IS NULL AND status = 'AI_ANALYZED';

-- ============================================================================
-- STEP 3: Update column types
-- ============================================================================

-- Expand risk_level column to accommodate longer values
ALTER TABLE anc_visits ALTER COLUMN risk_level TYPE VARCHAR(20);

-- Remove NOT NULL constraint from patient_id if it exists
ALTER TABLE anc_visits ALTER COLUMN patient_id DROP NOT NULL;

-- ============================================================================
-- STEP 4: Drop old columns (CAUTION: Data will be lost!)
-- ============================================================================

-- Uncomment these lines only after verifying migration was successful
-- ALTER TABLE anc_visits DROP COLUMN IF EXISTS risk_score;
-- ALTER TABLE anc_visits DROP COLUMN IF EXISTS ai_flags;
-- ALTER TABLE anc_visits DROP COLUMN IF EXISTS ai_recommendations;
-- ALTER TABLE anc_visits DROP COLUMN IF EXISTS rag_context_used;

-- ============================================================================
-- STEP 5: Add new indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_anc_is_high_risk ON anc_visits(is_high_risk);
CREATE INDEX IF NOT EXISTS idx_anc_detected_risks ON anc_visits USING GIN(detected_risks);

-- ============================================================================
-- STEP 6: Drop old indexes
-- ============================================================================

DROP INDEX IF EXISTS idx_anc_visits_ai_flags;

-- ============================================================================
-- STEP 7: Verify migration
-- ============================================================================

-- Check column existence
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'anc_visits'
ORDER BY ordinal_position;

-- Check data migration
SELECT 
    COUNT(*) as total_visits,
    COUNT(is_high_risk) as has_is_high_risk,
    COUNT(detected_risks) as has_detected_risks,
    COUNT(confidence) as has_confidence,
    COUNT(recommendation) as has_recommendation
FROM anc_visits;

-- Check high-risk distribution
SELECT 
    is_high_risk,
    risk_level,
    COUNT(*) as count
FROM anc_visits
GROUP BY is_high_risk, risk_level
ORDER BY is_high_risk DESC, risk_level;

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. Backup your database before running this migration!
-- 2. Old columns are NOT dropped by default - uncomment Step 4 after verification
-- 3. Existing data will have default/migrated values for new fields
-- 4. New visits will have proper values from FastAPI
-- 5. Consider re-running AI analysis on old visits to get full new data
