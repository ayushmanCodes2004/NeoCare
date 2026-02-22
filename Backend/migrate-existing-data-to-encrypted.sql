-- Migration Script: Encrypt Existing Unencrypted Data
-- WARNING: This script is for reference only. 
-- PostgreSQL cannot directly call Java encryption methods.
-- Use the Java migration tool instead: MigrateExistingDataToEncrypted.java

-- This script shows what needs to be migrated:

-- 1. Check for unencrypted data (Base64 strings are typically 40+ chars)
SELECT 
    'anc_workers' as table_name,
    COUNT(*) as potentially_unencrypted
FROM anc_workers 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40;

SELECT 
    'patients' as table_name,
    COUNT(*) as potentially_unencrypted
FROM patients 
WHERE LENGTH(full_name) < 40 OR LENGTH(address) < 40;

SELECT 
    'doctors' as table_name,
    COUNT(*) as potentially_unencrypted
FROM doctors 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40;

-- 2. List unencrypted records
SELECT id, full_name, email, created_at 
FROM anc_workers 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40
ORDER BY created_at;

SELECT id, full_name, address, created_at 
FROM patients 
WHERE LENGTH(full_name) < 40 OR LENGTH(address) < 40
ORDER BY created_at;

SELECT id, full_name, email, created_at 
FROM doctors 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40
ORDER BY created_at;

-- NOTE: To actually encrypt the data, use the Java migration tool
-- which can call the EncryptionService to encrypt each field properly.
