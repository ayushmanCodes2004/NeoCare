# Quick Start Guide - ANC Service

## 🚀 5-Minute Setup

### 1. Prerequisites Check
```bash
java -version    # Need Java 17+
mvn -version     # Need Maven 3.6+
psql --version   # Need PostgreSQL 12+
```

### 2. Database Setup (2 minutes)
```sql
-- Open psql or pgAdmin
CREATE DATABASE anc_db;
\c anc_db;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Run schema
\i src/main/resources/schema.sql
```

### 3. Configure (1 minute)
Edit `src/main/resources/application.yml`:
```yaml
spring:
  datasource:
    password: YOUR_PASSWORD  # Change this line only!
```

### 4. Run (2 minutes)
```bash
# Option A: Direct run
mvn spring-boot:run

# Option B: Windows
run.bat

# Option C: Build JAR first
mvn clean package
java -jar target/anc-service-1.0.0.jar
```

### 5. Test
```bash
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8080/api/anc/register-visit" `
  -Method Post -ContentType "application/json" -InFile "test-payload.json"

# Curl
curl -X POST http://localhost:8080/api/anc/register-visit \
  -H "Content-Type: application/json" -d @test-payload.json
```

## 📍 Endpoints

| Method | URL | Purpose |
|--------|-----|---------|
| POST | `/api/anc/register-visit` | Register new visit |
| GET | `/api/anc/visits/{id}` | Get visit by ID |
| GET | `/api/anc/patients/{id}/visits` | Patient history |
| GET | `/api/anc/visits/high-risk` | High-risk visits |

## 🔧 Common Issues

**Port 8080 in use?**
```yaml
# Change in application.yml
server:
  port: 8081
```

**Can't connect to DB?**
```bash
# Test connection
psql -U postgres -d anc_db
```

**FastAPI not running?**
- Non-fatal! Visit still saves
- Start FastAPI service separately

## 📚 More Help

- Full setup: See `SETUP.md`
- Implementation details: See `IMPLEMENTATION_SUMMARY.md`
- API docs: See `README.md`

## ✅ Success Indicators

Console shows:
```
Started AncServiceApplication in X.XXX seconds
```

Test returns:
```json
{
  "visitId": "uuid-here",
  "status": "AI_ANALYZED",
  "message": "Visit registered and risk analysis completed successfully"
}
```

## 🎯 What's Next?

1. ✅ Backend running on http://localhost:8080
2. ⏭️ Start FastAPI service (port 8000)
3. ⏭️ Start React frontend (port 3000)
4. ⏭️ Test complete flow

---

**Need help?** Check the detailed guides:
- `SETUP.md` - Step-by-step setup
- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details
