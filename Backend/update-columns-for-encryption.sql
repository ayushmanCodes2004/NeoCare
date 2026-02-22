-- SQL Migration: Update column lengths for encrypted data
-- Run this BEFORE enabling encryption to avoid data truncation

-- Patients table
ALTER TABLE patients 
    ALTER COLUMN full_name TYPE VARCHAR(500),
    ALTER COLUMN phone TYPE VARCHAR(500),
    ALTER COLUMN address TYPE VARCHAR(1000);

-- ANC Visits table
ALTER TABLE anc_visits 
    ALTER COLUMN patient_name TYPE VARCHAR(500);

-- Doctors table
ALTER TABLE doctors 
    ALTER COLUMN full_name TYPE VARCHAR(500),
    ALTER COLUMN phone TYPE VARCHAR(500),
    ALTER COLUMN email TYPE VARCHAR(500);

-- ANC Workers table
ALTER TABLE anc_workers 
    ALTER COLUMN full_name TYPE VARCHAR(500),
    ALTER COLUMN phone TYPE VARCHAR(500),
    ALTER COLUMN email TYPE VARCHAR(500);

-- Note: Consultations table TEXT columns don't need length changes
-- TEXT columns can store encrypted data without modification

-- Verify changes
SELECT 
    table_name, 
    column_name, 
    data_type, 
    character_maximum_length
FROM information_schema.columns
WHERE table_name IN ('patients', 'anc_visits', 'doctors', 'anc_workers')
    AND column_name IN ('full_name', 'phone', 'email', 'address', 'patient_name')
ORDER BY table_name, column_name;
