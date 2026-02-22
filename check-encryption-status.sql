-- ============================================
-- ENCRYPTION STATUS CHECK QUERIES
-- Run these in PostgreSQL to verify encryption
-- ============================================

-- 1. QUICK OVERVIEW - Encrypted vs Unencrypted Count
-- Encrypted data is Base64 encoded (typically 40+ characters)
-- ============================================
SELECT 
    'Workers' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) as encrypted,
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END) as unencrypted
FROM anc_workers

UNION ALL

SELECT 
    'Patients',
    COUNT(*),
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END),
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END)
FROM patients

UNION ALL

SELECT 
    'Doctors',
    COUNT(*),
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END),
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END)
FROM doctors;


-- 2. DETAILED VIEW - See Actual Data
-- ============================================

-- Workers - Check encryption
SELECT 
    id,
    full_name,
    LENGTH(full_name) as name_length,
    phone,
    email,
    LENGTH(email) as email_length,
    CASE 
        WHEN LENGTH(full_name) >= 40 THEN '✓ Encrypted'
        ELSE '✗ Plain Text'
    END as name_status,
    CASE 
        WHEN LENGTH(email) >= 40 THEN '✓ Encrypted'
        ELSE '✗ Plain Text'
    END as email_status,
    created_at
FROM anc_workers
ORDER BY created_at DESC;


-- Patients - Check encryption
SELECT 
    id,
    full_name,
    LENGTH(full_name) as name_length,
    phone,
    address,
    LENGTH(address) as address_length,
    CASE 
        WHEN LENGTH(full_name) >= 40 THEN '✓ Encrypted'
        ELSE '✗ Plain Text'
    END as name_status,
    CASE 
        WHEN LENGTH(address) >= 40 THEN '✓ Encrypted'
        ELSE '✗ Plain Text'
    END as address_status,
    created_at
FROM patients
ORDER BY created_at DESC;


-- Doctors - Check encryption
SELECT 
    id,
    full_name,
    LENGTH(full_name) as name_length,
    phone,
    email,
    LENGTH(email) as email_length,
    CASE 
        WHEN LENGTH(full_name) >= 40 THEN '✓ Encrypted'
        ELSE '✗ Plain Text'
    END as name_status,
    CASE 
        WHEN LENGTH(email) >= 40 THEN '✓ Encrypted'
        ELSE '✗ Plain Text'
    END as email_status,
    created_at
FROM doctors
ORDER BY created_at DESC;


-- 3. FIND UNENCRYPTED RECORDS (Need Migration)
-- ============================================

-- Unencrypted Workers
SELECT 
    'WORKER' as type,
    id,
    full_name,
    email,
    created_at
FROM anc_workers 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40
ORDER BY created_at;


-- Unencrypted Patients
SELECT 
    'PATIENT' as type,
    id,
    full_name,
    address,
    created_at
FROM patients 
WHERE LENGTH(full_name) < 40 OR LENGTH(address) < 40
ORDER BY created_at;


-- Unencrypted Doctors
SELECT 
    'DOCTOR' as type,
    id,
    full_name,
    email,
    created_at
FROM doctors 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40
ORDER BY created_at;


-- 4. SAMPLE ENCRYPTED DATA - See What Encryption Looks Like
-- ============================================

-- Show first 3 workers with encrypted data
SELECT 
    'Worker' as type,
    SUBSTRING(full_name, 1, 50) || '...' as encrypted_name_sample,
    phone as plain_phone,
    SUBSTRING(email, 1, 50) || '...' as encrypted_email_sample
FROM anc_workers
WHERE LENGTH(full_name) >= 40
LIMIT 3;


-- Show first 3 patients with encrypted data
SELECT 
    'Patient' as type,
    SUBSTRING(full_name, 1, 50) || '...' as encrypted_name_sample,
    phone as plain_phone,
    SUBSTRING(address, 1, 50) || '...' as encrypted_address_sample
FROM patients
WHERE LENGTH(full_name) >= 40
LIMIT 3;


-- 5. ENCRYPTION PERCENTAGE BY TABLE
-- ============================================

SELECT 
    'Workers' as table_name,
    COUNT(*) as total,
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) as encrypted,
    ROUND(
        100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / 
        NULLIF(COUNT(*), 0), 
        2
    ) as encryption_percentage
FROM anc_workers

UNION ALL

SELECT 
    'Patients',
    COUNT(*),
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END),
    ROUND(
        100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / 
        NULLIF(COUNT(*), 0), 
        2
    )
FROM patients

UNION ALL

SELECT 
    'Doctors',
    COUNT(*),
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END),
    ROUND(
        100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / 
        NULLIF(COUNT(*), 0), 
        2
    )
FROM doctors;


-- 6. RECENT RECORDS - Check Latest Data
-- ============================================

-- Last 5 workers created
SELECT 
    'Worker' as type,
    id,
    CASE 
        WHEN LENGTH(full_name) >= 40 THEN '✓ ENCRYPTED'
        ELSE '✗ PLAIN: ' || full_name
    END as name_status,
    phone,
    CASE 
        WHEN LENGTH(email) >= 40 THEN '✓ ENCRYPTED'
        ELSE '✗ PLAIN: ' || email
    END as email_status,
    created_at
FROM anc_workers
ORDER BY created_at DESC
LIMIT 5;


-- Last 5 patients created
SELECT 
    'Patient' as type,
    id,
    CASE 
        WHEN LENGTH(full_name) >= 40 THEN '✓ ENCRYPTED'
        ELSE '✗ PLAIN: ' || full_name
    END as name_status,
    phone,
    CASE 
        WHEN LENGTH(address) >= 40 THEN '✓ ENCRYPTED'
        ELSE '✗ PLAIN: ' || address
    END as address_status,
    created_at
FROM patients
ORDER BY created_at DESC
LIMIT 5;


-- 7. COLUMN LENGTHS - Verify Column Sizes
-- ============================================

SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_name IN ('anc_workers', 'patients', 'doctors')
    AND column_name IN ('full_name', 'phone', 'email', 'address')
ORDER BY table_name, column_name;


-- 8. CONSULTATIONS - Check Encrypted Notes
-- ============================================

SELECT 
    id,
    patient_id,
    doctor_id,
    CASE 
        WHEN doctor_notes IS NULL THEN 'NULL'
        WHEN LENGTH(doctor_notes) >= 40 THEN '✓ ENCRYPTED'
        ELSE '✗ PLAIN: ' || SUBSTRING(doctor_notes, 1, 30)
    END as notes_status,
    CASE 
        WHEN diagnosis IS NULL THEN 'NULL'
        WHEN LENGTH(diagnosis) >= 40 THEN '✓ ENCRYPTED'
        ELSE '✗ PLAIN: ' || SUBSTRING(diagnosis, 1, 30)
    END as diagnosis_status,
    status,
    created_at
FROM consultations
ORDER BY created_at DESC
LIMIT 10;


-- 9. VISITS - Check Patient Name Encryption
-- ============================================

SELECT 
    id,
    patient_id,
    CASE 
        WHEN patient_name IS NULL THEN 'NULL'
        WHEN LENGTH(patient_name) >= 40 THEN '✓ ENCRYPTED'
        ELSE '✗ PLAIN: ' || patient_name
    END as patient_name_status,
    risk_level,
    status,
    created_at
FROM anc_visits
ORDER BY created_at DESC
LIMIT 10;


-- 10. SUMMARY REPORT - Complete Overview
-- ============================================

SELECT 
    'ENCRYPTION STATUS SUMMARY' as report_title,
    (SELECT COUNT(*) FROM anc_workers) as total_workers,
    (SELECT COUNT(*) FROM anc_workers WHERE LENGTH(full_name) >= 40) as encrypted_workers,
    (SELECT COUNT(*) FROM patients) as total_patients,
    (SELECT COUNT(*) FROM patients WHERE LENGTH(full_name) >= 40) as encrypted_patients,
    (SELECT COUNT(*) FROM doctors) as total_doctors,
    (SELECT COUNT(*) FROM doctors WHERE LENGTH(full_name) >= 40) as encrypted_doctors,
    (SELECT COUNT(*) FROM consultations) as total_consultations,
    (SELECT COUNT(*) FROM anc_visits) as total_visits;
