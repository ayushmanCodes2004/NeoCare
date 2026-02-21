# ANC Service - Complete Setup Guide

## Prerequisites Installation

### 1. Install Java 17
Download and install Java 17 JDK from:
- Oracle: https://www.oracle.com/java/technologies/downloads/#java17
- OpenJDK: https://adoptium.net/

Verify installation:
```bash
java -version
# Should show: java version "17.x.x"
```

### 2. Install Maven
Download from: https://maven.apache.org/download.cgi

Add to PATH and verify:
```bash
mvn -version
```

### 3. Install PostgreSQL
Download from: https://www.postgresql.org/download/

During installation:
- Set password for postgres user
- Note the port (default: 5432)

## Database Setup

### Step 1: Create Database
Open PostgreSQL command line (psql) or pgAdmin:

```sql
-- Connect as postgres user
CREATE DATABASE anc_db;

-- Connect to the new database
\c anc_db;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### Step 2: Run Schema
```bash
# From Backend directory
psql -U postgres -d anc_db -f src/main/resources/schema.sql
```

Or manually run the SQL from `src/main/resources/schema.sql`

### Step 3: Verify Tables
```sql
\c anc_db
\dt
# Should show: anc_visits table
```

## Application Configuration

### Update Database Credentials
Edit `src/main/resources/application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/anc_db
    username: postgres
    password: YOUR_POSTGRES_PASSWORD  # Change this!
```

### Update FastAPI Configuration
```yaml
fastapi:
  base-url: http://localhost:8000  # Your FastAPI server URL
  api-key: your-fastapi-secret-key  # Match with FastAPI config
```

## Build and Run

### Option 1: Using Maven (Recommended)
```bash
# Build
mvn clean install

# Run
mvn spring-boot:run
```

### Option 2: Using JAR
```bash
# Build JAR
mvn clean package

# Run JAR
java -jar target/anc-service-1.0.0.jar
```

### Option 3: Using Windows Batch Script
```bash
# Simply double-click or run:
run.bat
```

## Verify Installation

### 1. Check Server Started
Look for this in console:
```
Started AncServiceApplication in X.XXX seconds
```

### 2. Test Health
Open browser: http://localhost:8080

### 3. Test API Endpoint
```bash
# Using curl
curl -X POST http://localhost:8080/api/anc/register-visit \
  -H "Content-Type: application/json" \
  -d @test-payload.json

# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:8080/api/anc/register-visit" `
  -Method Post `
  -ContentType "application/json" `
  -InFile "test-payload.json"
```

## Troubleshooting

### Issue: Port 8080 already in use
Solution: Change port in `application.yml`:
```yaml
server:
  port: 8081  # Or any available port
```

### Issue: Cannot connect to PostgreSQL
1. Check PostgreSQL is running:
   ```bash
   # Windows
   services.msc  # Look for postgresql service
   ```

2. Verify connection details in `application.yml`

3. Test connection:
   ```bash
   psql -U postgres -d anc_db
   ```

### Issue: FastAPI connection failed
- This is non-fatal - visit will still be saved
- Check FastAPI is running on configured URL
- Verify API key matches

### Issue: Maven build fails
1. Clear Maven cache:
   ```bash
   mvn clean
   ```

2. Delete `.m2/repository` folder and rebuild

3. Check internet connection (Maven downloads dependencies)

## Development Tips

### Hot Reload
Use Spring Boot DevTools for automatic restart:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
</dependency>
```

### View Logs
Logs are in console. To save to file, add to `application.yml`:
```yaml
logging:
  file:
    name: logs/anc-service.log
```

### Database GUI Tools
- pgAdmin (comes with PostgreSQL)
- DBeaver (free, cross-platform)
- DataGrip (JetBrains, paid)

## Next Steps

1. Start FastAPI service (see Medical RAG Pipeline folder)
2. Test complete flow with test-payload.json
3. Integrate with React frontend
4. Configure production settings

## Production Checklist

- [ ] Change `ddl-auto` to `validate` in application.yml
- [ ] Set strong database password
- [ ] Configure CORS to specific origins
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure connection pooling
- [ ] Set up monitoring (Actuator)
- [ ] Use environment variables for secrets
