# Integration Testing Guide - Spring Boot + FastAPI

## Prerequisites

Before testing, ensure you have:
- ✅ Java 17+ installed
- ✅ Maven 3.6+ installed
- ✅ PostgreSQL 12+ running
- ✅ Python 3.10+ installed
- ✅ FastAPI dependencies installed

## Step-by-Step Testing

### Step 1: Setup PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE anc_db;
\c anc_db;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

# Run schema
\i Backend/src/main/resources/schema.sql

# Verify
\dt
# Should show: anc_visits table

\q
```

### Step 2: Configure Spring Boot

Edit `Backend/src/main/resources/application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/anc_db
    username: postgres
    password: YOUR_POSTGRES_PASSWORD  # Update this!

fastapi:
  base-url: http://localhost:8000
  api-key: your-fastapi-secret-key  # Optional, can be any value
```

### Step 3: Start FastAPI Server

```bash
# Navigate to Medical RAG Pipeline folder
cd "Medical RAG Pipeline"

# Install dependencies (first time only)
pip install -r requirements_api.txt

# Start FastAPI server
python api_server.py
```

**Expected Output:**
```
🚀 Starting Medical RAG API...
📦 Loading production pipeline...
✅ Pipeline loaded successfully
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Verify FastAPI is running:**
```bash
# In a new terminal
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "system": "Medical RAG - High-Risk Pregnancy Detection",
  "timestamp": "2026-02-21T..."
}
```

### Step 4: Build Spring Boot Application

```bash
# Navigate to Backend folder
cd Backend

# Clean and compile
mvn clean compile

# Package (optional)
mvn clean package
```

**Expected Output:**
```
[INFO] BUILD SUCCESS
[INFO] Total time: XX.XXX s
```

### Step 5: Start Spring Boot Application

```bash
# From Backend folder
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
Started AncServiceApplication in X.XXX seconds (JVM running for X.XXX)
```

### Step 6: Test Complete Integration

#### Test 1: Health Check

```bash
# Test Spring Boot
curl http://localhost:8080/actuator/health

# Test FastAPI
curl http://localhost:8000/health
```

#### Test 2: Register Visit (Complete Flow)

```bash
# Using the test payload
curl -X POST http://localhost:8080/api/anc/register-visit \
  -H "Content-Type: application/json" \
  -d @Backend/test-payload.json
```

**Expected Response:**
```json
{
  "visitId": "uuid-here",
  "patientId": "P12345",
  "patientName": "Test Patient",
  "status": "AI_ANALYZED",
  "riskAssessment": {
    "isHighRisk": true,
    "riskLevel": "CRITICAL",
    "detectedRisks": [
      "Severe Pre Eclampsia",
      "Elderly Gravida",
      "Mild Anaemia"
    ],
    "explanation": "Risk Assessment: CRITICAL. Patient presents with...",
    "confidence": 0.7,
    "recommendation": "URGENT: Immediate referral to CEmOC/District Hospital required.",
    "patientId": "P12345",
    "patientName": "Test Patient",
    "age": 38,
    "gestationalWeeks": 34,
    "visitMetadata": null
  },
  "savedAt": "2026-02-21T...",
  "message": "ALERT: High risk pregnancy detected — CRITICAL. Immediate action required."
}
```

#### Test 3: Retrieve Visit

```bash
# Get the visitId from previous response
curl http://localhost:8080/api/anc/visits/{visitId}
```

#### Test 4: Get High-Risk Visits

```bash
curl http://localhost:8080/api/anc/visits/high-risk
```

#### Test 5: Get Critical Visits

```bash
curl http://localhost:8080/api/anc/visits/critical
```

#### Test 6: Get Patient History

```bash
curl http://localhost:8080/api/anc/patients/P12345/visits
```

## Verification Checklist

### FastAPI Verification
- [ ] FastAPI server starts without errors
- [ ] Health endpoint returns 200 OK
- [ ] `/assess-structured` endpoint accepts requests
- [ ] Response includes all required fields
- [ ] Confidence scores are between 0.0 and 1.0
- [ ] Risk levels are valid (CRITICAL/HIGH/MEDIUM/LOW)

### Spring Boot Verification
- [ ] Application starts without errors
- [ ] Database connection successful
- [ ] Can save visit to database
- [ ] FastAPI client successfully calls endpoint
- [ ] Response mapping works correctly
- [ ] All fields populated in database
- [ ] Queries return correct data

### Integration Verification
- [ ] Complete flow works end-to-end
- [ ] Visit saved with status=REGISTERED
- [ ] FastAPI called successfully
- [ ] Visit updated with status=AI_ANALYZED
- [ ] All AI fields populated correctly
- [ ] Response returned to client
- [ ] Error handling works (FastAPI down)

## Common Issues and Solutions

### Issue 1: FastAPI Not Starting

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
cd "Medical RAG Pipeline"
pip install -r requirements_api.txt
```

### Issue 2: FAISS Index Missing

**Error:**
```
FileNotFoundError: FAISS index not found
```

**Solution:**
```bash
cd "Medical RAG Pipeline"
python main.py --ingest
```

### Issue 3: PostgreSQL Connection Failed

**Error:**
```
Connection refused: localhost:5432
```

**Solution:**
```bash
# Check if PostgreSQL is running
Get-Service -Name "*postgres*"

# Start if not running
Start-Service postgresql-x64-17
```

### Issue 4: Port Already in Use

**Error:**
```
Address already in use: 8080
```

**Solution:**
```yaml
# Change port in application.yml
server:
  port: 8081
```

### Issue 5: FastAPI Timeout

**Error:**
```
Read timed out
```

**Solution:**
```yaml
# Increase timeout in application.yml
fastapi:
  read-timeout: 60000  # 60 seconds
```

### Issue 6: Field Mapping Error

**Error:**
```
Failed to map FastAPI response
```

**Solution:**
- Check FastAPI response format
- Verify DTO field names match
- Check logs for detailed error

## Testing Different Scenarios

### Scenario 1: Low Risk Patient

```json
{
  "patientId": "P001",
  "patientName": "Low Risk Patient",
  "structured_data": {
    "patient_info": {
      "age": 25,
      "gestationalWeeks": 20
    },
    "vitals": {
      "bpSystolic": 110,
      "bpDiastolic": 70
    },
    "lab_reports": {
      "hemoglobin": 12.5
    }
  }
}
```

**Expected:** `riskLevel: "LOW"`, `isHighRisk: false`

### Scenario 2: High Risk Patient

```json
{
  "patientId": "P002",
  "patientName": "High Risk Patient",
  "structured_data": {
    "patient_info": {
      "age": 38,
      "gestationalWeeks": 30
    },
    "medical_history": {
      "previousLSCS": true,
      "chronicHypertension": true
    },
    "vitals": {
      "bpSystolic": 150,
      "bpDiastolic": 100
    },
    "lab_reports": {
      "hemoglobin": 10.0
    },
    "pregnancy_details": {
      "twinPregnancy": true
    }
  }
}
```

**Expected:** `riskLevel: "HIGH"`, `isHighRisk: true`

### Scenario 3: Critical Risk Patient

```json
{
  "patientId": "P003",
  "patientName": "Critical Risk Patient",
  "structured_data": {
    "patient_info": {
      "age": 40,
      "gestationalWeeks": 34
    },
    "medical_history": {
      "previousLSCS": true,
      "diabetes": true
    },
    "vitals": {
      "bpSystolic": 170,
      "bpDiastolic": 115
    },
    "lab_reports": {
      "hemoglobin": 6.5,
      "urineProtein": true
    },
    "pregnancy_details": {
      "twinPregnancy": true,
      "placentaPrevia": true
    },
    "current_symptoms": {
      "headache": true,
      "visualDisturbance": true,
      "convulsions": true
    }
  }
}
```

**Expected:** `riskLevel: "CRITICAL"`, `isHighRisk: true`, multiple `detectedRisks`

### Scenario 4: FastAPI Unavailable

**Test:**
1. Stop FastAPI server
2. Try to register visit
3. Verify graceful degradation

**Expected:**
- Visit still saved (status=REGISTERED)
- `aiErrorMessage` populated
- Response includes error message
- HTTP 201 Created (not 500 error)

## Performance Testing

### Measure Response Times

```bash
# Using curl with timing
curl -X POST http://localhost:8080/api/anc/register-visit \
  -H "Content-Type: application/json" \
  -d @Backend/test-payload.json \
  -w "\nTotal time: %{time_total}s\n"
```

**Expected Times:**
- Spring Boot processing: < 100ms
- FastAPI analysis: 6-13 seconds
- Total: 6-13 seconds

### Load Testing (Optional)

```bash
# Install Apache Bench
# Windows: Download from Apache website
# Linux: sudo apt-get install apache2-utils

# Run load test (10 requests, 2 concurrent)
ab -n 10 -c 2 -p Backend/test-payload.json \
  -T application/json \
  http://localhost:8080/api/anc/register-visit
```

## Database Verification

```sql
-- Connect to database
psql -U postgres -d anc_db

-- Check visits
SELECT 
    id,
    patient_id,
    patient_name,
    is_high_risk,
    risk_level,
    status,
    created_at
FROM anc_visits
ORDER BY created_at DESC
LIMIT 10;

-- Check AI fields
SELECT 
    id,
    patient_id,
    detected_risks,
    confidence,
    recommendation
FROM anc_visits
WHERE status = 'AI_ANALYZED'
LIMIT 5;

-- Count by risk level
SELECT 
    risk_level,
    COUNT(*) as count
FROM anc_visits
GROUP BY risk_level;

-- Count by status
SELECT 
    status,
    COUNT(*) as count
FROM anc_visits
GROUP BY status;
```

## Logs to Monitor

### Spring Boot Logs

**Look for:**
```
INFO: Registering ANC visit for patient: P12345
INFO: Auto-generated clinical summary: ...
INFO: Visit saved with ID: uuid
INFO: Calling FastAPI at: http://localhost:8000/assess-structured
INFO: AI analysis completed: isHighRisk=true, riskLevel=CRITICAL, confidence=0.7
INFO: Enriched — isHighRisk: true, riskLevel: CRITICAL, detectedRisks count: 5, confidence: 0.7
```

**Watch for errors:**
```
ERROR: FastAPI call failed: ...
ERROR: Failed to map FastAPI response: ...
```

### FastAPI Logs

**Look for:**
```
INFO: Received structured assessment request
INFO: Extracted features: age=38, BP=165/110, Hb=9.8
INFO: Risk assessment: CRITICAL (score=15)
```

## Success Criteria

✅ **Integration is successful if:**

1. FastAPI server starts and responds to health checks
2. Spring Boot application starts without errors
3. Visit registration saves to database
4. FastAPI is called successfully
5. Response is mapped correctly
6. All fields are populated in database
7. Queries return correct data
8. Error handling works when FastAPI is down
9. Response times are acceptable (< 15 seconds)
10. No data loss or corruption

## Next Steps After Successful Testing

1. ✅ Integration tested and working
2. ⏭️ Deploy to staging environment
3. ⏭️ Perform user acceptance testing
4. ⏭️ Configure production settings
5. ⏭️ Set up monitoring and alerts
6. ⏭️ Deploy to production

## Support

**If you encounter issues:**

1. Check logs in both Spring Boot and FastAPI
2. Verify all services are running
3. Test each component individually
4. Review configuration files
5. Check database connectivity
6. Verify network connectivity between services

**Documentation:**
- FastAPI Integration: `Backend/FASTAPI_INTEGRATION_GUIDE.md`
- Spring Boot Setup: `Backend/SETUP.md`
- API Documentation: `Medical RAG Pipeline/API_DOCUMENTATION.md`

---

**Test Version:** 2.0.0  
**Last Updated:** February 2026  
**Status:** Ready for Testing 🧪
