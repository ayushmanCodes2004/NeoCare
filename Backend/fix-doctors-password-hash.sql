-- ═══════════════════════════════════════════════════════════════════════════════
-- FIX: Add password_hash column to doctors table
-- ═══════════════════════════════════════════════════════════════════════════════

-- Check if column exists, if not add it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'doctors' 
        AND column_name = 'password_hash'
    ) THEN
        ALTER TABLE doctors ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '';
        RAISE NOTICE 'Added password_hash column to doctors table';
    ELSE
        RAISE NOTICE 'password_hash column already exists in doctors table';
    END IF;
END $$;

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'doctors' 
AND column_name = 'password_hash';
