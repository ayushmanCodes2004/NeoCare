# Quick Encryption Status Check
# Run this to verify encryption in your database

$env:PGPASSWORD = "ayushman@2004"
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ENCRYPTION STATUS CHECK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Quick Overview
Write-Host "1. QUICK OVERVIEW" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
& $psql -U postgres -d NeoSure -c "
SELECT 
    'Workers' as table_name,
    COUNT(*) as total,
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) as encrypted,
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END) as unencrypted
FROM anc_workers
UNION ALL
SELECT 'Patients', COUNT(*), 
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END),
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END)
FROM patients
UNION ALL
SELECT 'Doctors', COUNT(*), 
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END),
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END)
FROM doctors;
"

Write-Host ""
Write-Host "2. ENCRYPTION PERCENTAGE" -ForegroundColor Yellow
Write-Host "========================" -ForegroundColor Yellow
& $psql -U postgres -d NeoSure -c "
SELECT 
    'Workers' as table_name,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / NULLIF(COUNT(*), 0), 2) as encrypted_pct
FROM anc_workers
UNION ALL
SELECT 'Patients', COUNT(*),
    ROUND(100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / NULLIF(COUNT(*), 0), 2)
FROM patients
UNION ALL
SELECT 'Doctors', COUNT(*),
    ROUND(100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / NULLIF(COUNT(*), 0), 2)
FROM doctors;
"

Write-Host ""
Write-Host "3. SAMPLE ENCRYPTED DATA" -ForegroundColor Yellow
Write-Host "========================" -ForegroundColor Yellow
& $psql -U postgres -d NeoSure -c "
SELECT 
    'Worker' as type,
    SUBSTRING(full_name, 1, 60) as encrypted_sample,
    phone
FROM anc_workers
WHERE LENGTH(full_name) >= 40
LIMIT 2;
"

Write-Host ""
& $psql -U postgres -d NeoSure -c "
SELECT 
    'Patient' as type,
    SUBSTRING(full_name, 1, 60) as encrypted_sample,
    phone
FROM patients
WHERE LENGTH(full_name) >= 40
LIMIT 2;
"

Write-Host ""
Write-Host "4. UNENCRYPTED RECORDS (Need Migration)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
& $psql -U postgres -d NeoSure -c "
SELECT 'Worker' as type, id, full_name, email
FROM anc_workers 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40
UNION ALL
SELECT 'Patient', id, full_name, address
FROM patients 
WHERE LENGTH(full_name) < 40 OR LENGTH(address) < 40
UNION ALL
SELECT 'Doctor', id, full_name, email
FROM doctors 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40;
"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CHECK COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Encrypted data looks like: WbAza+/rsiLSwE1aToMHIaVZZqgVfs86..." -ForegroundColor Gray
Write-Host "Plain text looks like: John Doe" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed queries, run:" -ForegroundColor White
Write-Host "  psql -U postgres -d NeoSure -f check-encryption-status.sql" -ForegroundColor Cyan
Write-Host ""
