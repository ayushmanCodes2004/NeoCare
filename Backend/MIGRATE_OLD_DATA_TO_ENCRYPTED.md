# Migrating Old Unencrypted Data to Encrypted Format

## Current Status

✅ **Your current data is already encrypted!**

Checked your database:
- 1 worker: Already encrypted (Base64 format)
- 1 patient: Already encrypted (Base64 format)
- 0 doctors, 0 visits, 0 consultations

## What Happens to Old Data?

When you enable encryption on existing unencrypted data, you have 3 options:

### Option 1: Start Fresh (Recommended for Development)
**Best for:** Development/testing environments

```sql
-- Clear all data and start fresh
TRUNCATE TABLE anc_visits, consultations, patients, anc_workers, doctors CASCADE;
```

**Pros:**
- Clean slate
- No migration needed
- All new data is encrypted

**Cons:**
- Loses existing data

### Option 2: Migrate Existing Data (Production)
**Best for:** Production with existing users

Use the Java migration tool provided:

#### Step 1: Check for Unencrypted Data
```bash
psql -U postgres -d NeoSure -f Backend/migrate-existing-data-to-encrypted.sql
```

This shows which records need encryption.

#### Step 2: Run Java Migration Tool

1. Open `Backend/src/main/java/com/anc/util/MigrateExistingDataToEncrypted.java`

2. Uncomment the `@Component` annotation:
```java
@Component  // UNCOMMENT THIS TO RUN MIGRATION
public class MigrateExistingDataToEncrypted implements CommandLineRunner {
```

3. Start the backend:
```bash
cd Backend
./run.bat
```

4. The migration runs automatically on startup and logs:
```
========================================
STARTING DATA ENCRYPTION MIGRATION
========================================
Migrating ANC Workers...
Encrypting worker abc-123 full_name: John Doe
Encrypting worker abc-123 email: john@example.com
✅ Worker abc-123 encrypted
Workers: 5 encrypted, 2 already encrypted

Migrating Patients...
Encrypting patient xyz-456 full_name: Jane Smith
Encrypting patient xyz-456 address: 123 Main St
✅ Patient xyz-456 encrypted
Patients: 10 encrypted, 3 already encrypted

========================================
MIGRATION COMPLETE
========================================
```

5. After migration completes, comment out `@Component` again to prevent re-running:
```java
// @Component  // UNCOMMENT THIS TO RUN MIGRATION
```

6. Restart backend

#### Step 3: Verify Migration
```sql
-- Check that all data is now encrypted (Base64 strings are 40+ chars)
SELECT 
    id, 
    LENGTH(full_name) as name_length,
    LENGTH(email) as email_length
FROM anc_workers;

-- Should show lengths > 40 for encrypted fields
```

### Option 3: Manual Migration (Small Datasets)
**Best for:** Very small datasets (< 10 records)

For each record:
1. Read the plain text value
2. Encrypt it using the EncryptionService
3. Update the database

This is what the Java tool does automatically.

## How the Migration Tool Works

### Detection Logic
```java
// Encrypted data is Base64 encoded (typically 40+ characters)
// Unencrypted data is shorter (e.g., "John Doe" = 8 chars)
if (fullName.length() < 40) {
    // Probably unencrypted - encrypt it
    fullName = encryptionService.encrypt(fullName);
}
```

### Safety Features
1. **Non-destructive:** Only encrypts fields that appear unencrypted
2. **Idempotent:** Can run multiple times safely
3. **Logged:** All operations are logged
4. **Skips encrypted:** Already encrypted data is not re-encrypted

### What Gets Encrypted
- ✅ Worker: `full_name`, `email`
- ✅ Patient: `full_name`, `address`
- ✅ Doctor: `full_name`, `email`
- ❌ Phone numbers: NOT encrypted (used for login/search)

## Handling Decryption Errors

If you try to decrypt already-encrypted data, you'll get errors like:
```
javax.crypto.AEADBadTagException: Tag mismatch!
```

This happens when:
1. Encryption key changed
2. Data was encrypted with different key
3. Data is corrupted

**Solution:** Use the migration tool which detects and skips already-encrypted data.

## Production Deployment Strategy

### Before Deployment
1. **Backup database:**
```bash
pg_dump -U postgres NeoSure > backup_before_encryption.sql
```

2. **Test migration on staging:**
   - Clone production database to staging
   - Run migration tool
   - Verify all data is accessible
   - Test application functionality

### During Deployment
1. **Enable maintenance mode** (optional)
2. **Deploy new code** with encryption
3. **Run migration tool** (if needed)
4. **Verify encryption** in database
5. **Test API endpoints**
6. **Disable maintenance mode**

### Rollback Plan
If something goes wrong:
```bash
# Restore from backup
psql -U postgres NeoSure < backup_before_encryption.sql

# Deploy previous version without encryption
git checkout previous-version
cd Backend
./run.bat
```

## Monitoring After Migration

### Check Encryption Status
```sql
-- Count encrypted vs unencrypted records
SELECT 
    'Workers' as table_name,
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END) as encrypted,
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END) as unencrypted
FROM anc_workers

UNION ALL

SELECT 
    'Patients',
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END),
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END)
FROM patients

UNION ALL

SELECT 
    'Doctors',
    COUNT(CASE WHEN LENGTH(full_name) >= 40 THEN 1 END),
    COUNT(CASE WHEN LENGTH(full_name) < 40 THEN 1 END)
FROM doctors;
```

### Test API Responses
```bash
# Create new record - should be encrypted
curl -X POST http://localhost:8080/api/patients \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"fullName":"Test Patient",...}'

# Fetch record - should return decrypted
curl -X GET http://localhost:8080/api/patients/{id} \
  -H "Authorization: Bearer $TOKEN"
```

## FAQ

### Q: Will old data cause errors?
**A:** Yes, if you try to decrypt unencrypted data, you'll get decryption errors. Use the migration tool first.

### Q: Can I run the migration multiple times?
**A:** Yes, it's safe. The tool skips already-encrypted data.

### Q: What if I change the encryption key?
**A:** All existing encrypted data becomes unreadable. You'd need to:
1. Decrypt with old key
2. Re-encrypt with new key
This is why key management is critical!

### Q: How do I know if data is encrypted?
**A:** Encrypted data is Base64 encoded and looks like:
```
WbAza+/rsiLSwE1aToMHIaVZZqgVfs86CdS7UxVgFSfbMTMNjeH3tbWdhOcemrv396Gf
```
Unencrypted data looks like:
```
John Doe
```

### Q: Can I search encrypted fields?
**A:** No, encrypted fields cannot be searched directly. That's why phone numbers are NOT encrypted - they're used for login and search.

## Your Current Situation

✅ **You're all set!** Your existing data is already encrypted:

```
Worker full_name: 52yMdOTs2F8/5ceIqINO/qzXcuvbhCD1Lja/pOze+Hc... (encrypted)
Worker email: Fr/a6Ers5eDI1oAiDM2orxJ8QmetoUOeBIrGFsRMl4z... (encrypted)
Patient full_name: WbAza+/rsiLSwE1aToMHIaVZZqgVfs86CdS7UxVgFSf... (encrypted)
Patient address: T8feLFtDdIWOtEZRMZ49LKLb+b6cSnj+leVnJGwWmtn... (encrypted)
```

No migration needed! All new data will be automatically encrypted.

## Files Created

1. `Backend/src/main/java/com/anc/util/MigrateExistingDataToEncrypted.java` - Java migration tool
2. `Backend/migrate-existing-data-to-encrypted.sql` - SQL detection script
3. This guide - Complete migration documentation
