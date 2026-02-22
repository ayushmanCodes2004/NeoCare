-- Fix NULL values in doctors table before adding NOT NULL constraints
UPDATE doctors SET is_active = TRUE WHERE is_active IS NULL;
UPDATE doctors SET is_available = TRUE WHERE is_available IS NULL;

-- Verify
SELECT COUNT(*) as null_is_active FROM doctors WHERE is_active IS NULL;
SELECT COUNT(*) as null_is_available FROM doctors WHERE is_available IS NULL;
