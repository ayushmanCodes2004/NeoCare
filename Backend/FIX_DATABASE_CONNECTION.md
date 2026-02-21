# Fix PostgreSQL Connection - Quick Guide

## Problem
Spring Boot cannot connect to PostgreSQL because the password is incorrect.

**Error:**
```
FATAL: password authentication failed for user "postgres"
```

## Solution

You have 3 options to fix this:

### Option 1: Update Password in application.yml (Quickest)

1. Open `Backend/src/main/resources/application.yml`
2. Find the datasource section:
   ```yaml
   spring:
     datasource:
       url: jdbc:postgresql://localhost:5432/anc_db
       username: postgres
       password: yourpassword  # ← Change this line
   ```
3. Replace `yourpassword` with your actual PostgreSQL password
4. Save the file

### Option 2: Use Environment Variable (Recommended for Production)

1. Open `Backend/src/main/resources/application.yml`
2. Change the password line to:
   ```yaml
   spring:
     datasource:
       password: ${POSTGRES_PASSWORD:postgres}
   ```
3. Set environment variable before running:
   ```bash
   # Windows PowerShell
   $env:POSTGRES_PASSWORD="your_actual_password"
   mvn spring-boot:run
   
   # Windows CMD
   set POSTGRES_PASSWORD=your_actual_password
   mvn spring-boot:run
   
   # Bash
   export POSTGRES_PASSWORD=your_actual_password
   mvn spring-boot:run
   ```

### Option 3: Reset PostgreSQL Password (If You Forgot It)

1. Open Command Prompt as Administrator
2. Stop PostgreSQL service:
   ```bash
   net stop postgresql-x64-17
   ```
3. Edit `pg_hba.conf` file (usually in `C:\Program Files\PostgreSQL\17\data\`)
4. Change authentication method from `md5` to `trust` temporarily:
   ```
   # TYPE  DATABASE        USER            ADDRESS                 METHOD
   host    all             all             127.0.0.1/32            trust
   ```
5. Start PostgreSQL service:
   ```bash
   net start postgresql-x64-17
   ```
6. Connect without password and reset:
   ```bash
   psql -U postgres
   ALTER USER postgres PASSWORD 'new_password';
   \q
   ```
7. Change `pg_hba.conf` back to `md5`
8. Restart PostgreSQL service
9. Update `application.yml` with the new password

## After Fixing Password

### Step 1: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Enter your password when prompted

# Create database
CREATE DATABASE anc_db;

# Connect to the database
\c anc_db;

# Create extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

# Exit
\q
```

### Step 2: Run Schema (Optional - Hibernate will create tables)

The schema will be created automatically by Hibernate (`ddl-auto: update`), but you can also run it manually:

```bash
psql -U postgres -d anc_db -f Backend/src/main/resources/schema.sql
```

### Step 3: Start Spring Boot

```bash
cd Backend
mvn spring-boot:run
```

**Expected Output:**
```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.2.0)

...
Hikari pool started
Hibernate: create table if not exists anc_visits ...
Started AncServiceApplication in X.XXX seconds (JVM running for X.XXX)
```

### Step 4: Verify Connection

```bash
# Test health endpoint
curl http://localhost:8080/actuator/health
```

**Expected Response:**
```json
{
  "status": "UP"
}
```

## Common PostgreSQL Passwords

If you're not sure what password you set during installation, try these common defaults:
- `postgres` (most common)
- `admin`
- `password`
- `root`
- Empty password (just press Enter)

## Verify PostgreSQL is Running

```bash
# Check service status
Get-Service -Name "*postgres*"

# Should show:
# Status   Name               DisplayName
# ------   ----               -----------
# Running  postgresql-x64-17  postgresql-x64-17 - PostgreSQL Server 17
```

If not running:
```bash
Start-Service postgresql-x64-17
```

## Quick Test Connection

```bash
# Try to connect (will prompt for password)
psql -U postgres -h localhost -p 5432

# If successful, you'll see:
# psql (17.x)
# Type "help" for help.
# postgres=#
```

## Next Steps After Fixing

1. ✅ Fix PostgreSQL password
2. ✅ Create `anc_db` database
3. ✅ Start Spring Boot application
4. ⏭️ Start FastAPI server (see `Backend/TEST_INTEGRATION.md`)
5. ⏭️ Test complete integration

## Need Help?

**Check PostgreSQL logs:**
- Windows: `C:\Program Files\PostgreSQL\17\data\log\`

**Check Spring Boot logs:**
- Look for connection errors in console output

**Still stuck?**
- Verify PostgreSQL version: `psql --version`
- Check port 5432 is not blocked: `netstat -an | findstr 5432`
- Ensure PostgreSQL service is running

---

**Quick Reference:**
- PostgreSQL Port: 5432
- Database Name: anc_db
- Username: postgres
- Password: ← YOU NEED TO SET THIS
- Spring Boot Port: 8080
- FastAPI Port: 8000
