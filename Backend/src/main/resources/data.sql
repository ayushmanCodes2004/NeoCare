-- Fix NULL values in doctors table
UPDATE doctors SET is_active = TRUE WHERE is_active IS NULL;
UPDATE doctors SET is_available = TRUE WHERE is_available IS NULL;
