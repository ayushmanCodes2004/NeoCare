# PostgreSQL Encryption Check Queries

## Quick Check Scripts

### Option 1: PowerShell Script (Easiest)
```powershell
./check-encryption.ps1
```

### Option 2: SQL File (Most Detailed)
```bash
psql -U postgres -d NeoSure -f check-encryption-status.sql
```

### Option 3: Direct psql Commands (Copy-Paste)

## Essential Queries

### 1. Quick Overview - Encrypted vs Unencrypted Count
```sql
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
```

**Expected Output:**
```
 table_name | total | encrypted | unencrypted 
------------+-------+-----------+-------------
 Workers    |     1 |         1 |           0
 Patients   |     1 |         1 |           0
 Doctors    |     0 |         0 |           0
```

### 2. Encryption Percentage
```sql
SELECT 
    'Workers' as table_name,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / 
          NULLIF(COUNT(*), 0), 2) as encrypted_percentage
FROM anc_workers
UNION ALL
SELECT 'Patients', COUNT(*),
    ROUND(100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / 
          NULLIF(COUNT(*), 0), 2)
FROM patients
UNION ALL
SELECT 'Doctors', COUNT(*),
    ROUND(100.0 * COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) / 
          NULLIF(COUNT(*), 0), 2)
FROM doctors;
```

**Expected Output:**
```
 table_name | total | encrypted_percentage 
------------+-------+---------------------
 Workers    |     1 |              100.00
 Patients   |     1 |              100.00
 Doctors    |     0 |                NULL
```

### 3. See Actual Encrypted Data
```sql
-- Workers
SELECT 
    id,
    full_name,
    LENGTH(full_name) as name_length,
    phone,
    email,
    LENGTH(email) as email_length
FROM anc_workers
ORDER BY created_at DESC
LIMIT 5;
```

**Expected Output:**
```
                  id                  |                    full_name                     | name_length |   phone    |                      email                       | email_length
--------------------------------------+--------------------------------------------------+-------------+------------+--------------------------------------------------+--------------
 f38f168c-9b9e-4338-bb3a-8c2a370b407f | 52yMdOTs2F8/5ceIqINO/qzXcuvbhCD1Lja/pOze+Hc... |          64 | 9998887776 | Fr/a6Ers5eDI1oAiDM2orxJ8QmetoUOeBIrGFsRMl4z... |           76
```

### 4. See Patient Encrypted Data
```sql
SELECT 
    id,
    full_name,
    LENGTH(full_name) as name_length,
    phone,
    address,
    LENGTH(address) as address_length
FROM patients
ORDER BY created_at DESC
LIMIT 5;
```

**Expected Output:**
```
                  id                  |                    full_name                     | name_length |   phone    |                     address                      | address_length
--------------------------------------+--------------------------------------------------+-------------+------------+--------------------------------------------------+----------------
 c5f1a5b5-3fb2-46c2-900d-b1c2236014ca | WbAza+/rsiLSwE1aToMHIaVZZqgVfs86CdS7UxVgFSf... |          64 | 8887776665 | T8feLFtDdIWOtEZRMZ49LKLb+b6cSnj+leVnJGwWmtn... |            120
```

### 5. Find Unencrypted Workers (Need Migration)
```sql
SELECT 
    id,
    full_name,
    email,
    created_at
FROM anc_workers 
WHERE LENGTH(full_name) < 40 OR LENGTH(email) < 40
ORDER BY created_at;
```

**Expected Output (if all encrypted):**
```
 id | full_name | email | created_at 
----+-----------+-------+------------
(0 rows)
```

### 6. Find Unencrypted Patients (Need Migration)
```sql
SELECT 
    id,
    full_name,
    address,
    created_at
FROM patients 
WHERE LENGTH(full_name) < 40 OR LENGTH(address) < 40
ORDER BY created_at;
```

**Expected Output (if all encrypted):**
```
 id | full_name | address | created_at 
----+-----------+---------+------------
(0 rows)
```

### 7. Check Consultation Notes Encryption
```sql
SELECT 
    id,
    patient_id,
    doctor_id,
    LENGTH(doctor_notes) as notes_length,
    LENGTH(diagnosis) as diagnosis_length,
    LENGTH(action_plan) as action_plan_length,
    status
FROM consultations
WHERE doctor_notes IS NOT NULL
ORDER BY created_at DESC
LIMIT 5;
```

### 8. Check Visit Patient Names Encryption
```sql
SELECT 
    id,
    patient_id,
    patient_name,
    LENGTH(patient_name) as name_length,
    risk_level,
    status
FROM anc_visits
WHERE patient_name IS NOT NULL
ORDER BY created_at DESC
LIMIT 5;
```

### 9. Column Sizes Verification
```sql
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_name IN ('anc_workers', 'patients', 'doctors')
    AND column_name IN ('full_name', 'phone', 'email', 'address')
ORDER BY table_name, column_name;
```

**Expected Output:**
```
 table_name  | column_name |     data_type     | character_maximum_length 
-------------+-------------+-------------------+--------------------------
 anc_workers | email       | character varying |                      500
 anc_workers | full_name   | character varying |                      500
 anc_workers | phone       | character varying |                       15
 doctors     | email       | character varying |                      500
 doctors     | full_name   | character varying |                      500
 doctors     | phone       | character varying |                       15
 patients    | address     | character varying |                     1000
 patients    | full_name   | character varying |                      500
 patients    | phone       | character varying |                       15
```

### 10. Complete Summary
```sql
SELECT 
    'Total Workers' as metric,
    COUNT(*)::text as value
FROM anc_workers
UNION ALL
SELECT 'Encrypted Workers',
    COUNT(*)::text
FROM anc_workers WHERE LENGTH(full_name) >= 40
UNION ALL
SELECT 'Total Patients',
    COUNT(*)::text
FROM patients
UNION ALL
SELECT 'Encrypted Patients',
    COUNT(*)::text
FROM patients WHERE LENGTH(full_name) >= 40
UNION ALL
SELECT 'Total Doctors',
    COUNT(*)::text
FROM doctors
UNION ALL
SELECT 'Encrypted Doctors',
    COUNT(*)::text
FROM doctors WHERE LENGTH(full_name) >= 40;
```

## How to Run These Queries

### Method 1: pgAdmin
1. Open pgAdmin
2. Connect to NeoSure database
3. Open Query Tool
4. Copy-paste any query above
5. Click Execute (F5)

### Method 2: psql Command Line
```bash
# Connect to database
psql -U postgres -d NeoSure

# Run query
SELECT * FROM anc_workers;

# Exit
\q
```

### Method 3: PowerShell
```powershell
$env:PGPASSWORD = "ayushman@2004"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d NeoSure -c "SELECT * FROM anc_workers;"
```

## Understanding the Results

### Encrypted Data Characteristics
- **Length:** 40+ characters (Base64 encoded)
- **Format:** Random alphanumeric with +, /, = characters
- **Example:** `WbAza+/rsiLSwE1aToMHIaVZZqgVfs86CdS7UxVgFSfbMTMNjeH3tbWdhOcemrv396Gf`

### Plain Text Data Characteristics
- **Length:** Usually < 40 characters
- **Format:** Readable text
- **Example:** `John Doe`, `john@example.com`, `123 Main Street`

### Phone Numbers
- **Always plain text** (used for login and search)
- **Length:** 10-15 characters
- **Example:** `9998887776`

## Your Current Status

Based on the check:
```
✅ Workers: 1 total, 1 encrypted (100%)
✅ Patients: 1 total, 1 encrypted (100%)
✅ Doctors: 0 total, 0 encrypted (N/A)
```

**Result:** All data is encrypted! No migration needed.

## If You Find Unencrypted Data

1. **Check the count:**
```sql
SELECT COUNT(*) FROM anc_workers WHERE LENGTH(full_name) < 40;
```

2. **If count > 0, run migration:**
   - Uncomment `@Component` in `MigrateExistingDataToEncrypted.java`
   - Restart backend
   - Check logs for migration results
   - Comment out `@Component` again

3. **Verify after migration:**
```sql
SELECT COUNT(*) FROM anc_workers WHERE LENGTH(full_name) < 40;
-- Should return 0
```
