# FastAPI Integration Guide - Spring Boot ↔ Medical RAG Pipeline

## Overview

This guide explains how the Spring Boot ANC Service integrates with the FastAPI Medical RAG Pipeline for AI-powered risk assessment.

## Architecture

```
React Frontend
      ↓
Spring Boot (Port 8080)
      ↓ HTTP POST
FastAPI Medical RAG (Port 8000)
      ↓
PostgreSQL (Spring Boot stores results)
```

## FastAPI Endpoints

### Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/query` | POST | Simple text query |
| `/assess` | POST | Simplified risk assessment |
| `/assess-structured` | POST | **Structured JSON input** (Used by Spring Boot) |

## Integration Point: `/assess-structured`

### Spring Boot → FastAPI Request

**Endpoint:** `POST http://localhost:8000/assess-structured`

**Headers:**
```
Content-Type: application/json
X-API-KEY: your-fastapi-secret-key
```

**Request Body (from Spring Boot):**
```json
{
  "clinical_summary": "38-year-old at 34 weeks gestation with severe hypertension...",
  "structured_data": {
    "patient_info": {
      "age": 38,
      "gestationalWeeks": 34
    },
    "medical_history": {
      "previousLSCS": true,
      "chronicHypertension": true,
      "diabetes": false,
      "smoking": false,
      "tobaccoUse": false,
      "alcoholUse": false
    },
    "vitals": {
      "heightCm": 152.0,
      "bmi": 28.5,
      "bpSystolic": 165,
      "bpDiastolic": 110
    },
    "lab_reports": {
      "hemoglobin": 9.8,
      "rhNegative": false,
      "hivPositive": false,
      "syphilisPositive": false,
      "urineProtein": true,
      "urineSugar": false
    },
    "obstetric_history": {
      "birthOrder": 3,
      "interPregnancyInterval": 24,
      "stillbirthCount": 0,
      "abortionCount": 1,
      "pretermHistory": false
    },
    "pregnancy_details": {
      "twinPregnancy": false,
      "malpresentation": false,
      "placentaPrevia": false,
      "reducedFetalMovement": false,
      "amnioticFluidNormal": true,
      "umbilicalDopplerAbnormal": false
    },
    "current_symptoms": {
      "headache": true,
      "visualDisturbance": true,
      "epigastricPain": false,
      "decreasedUrineOutput": false,
      "bleedingPerVagina": false,
      "convulsions": false
    }
  },
  "care_level": "PHC",
  "verbose": false
}
```

### FastAPI → Spring Boot Response

**Response Body (to Spring Boot):**
```json
{
  "isHighRisk": true,
  "riskLevel": "CRITICAL",
  "detectedRisks": [
    "Severe Anaemia",
    "Severe Pre Eclampsia",
    "GDM Screening Overdue",
    "Elderly Gravida",
    "Twin Pregnancy"
  ],
  "explanation": "Risk Assessment: CRITICAL. Patient presents with 5 significant risk factors including severe anaemia (Hb 6.5 g/dL), severe pre-eclampsia (BP 165/110 with proteinuria), advanced maternal age (38 years), twin pregnancy, and overdue GDM screening at 30 weeks. Immediate referral to CEmOC/District Hospital is required for comprehensive management.",
  "confidence": 0.7,
  "recommendation": "URGENT: Immediate referral to CEmOC/District Hospital required.",
  "patientId": "P12345",
  "patientName": "Test Patient",
  "age": 38,
  "gestationalWeeks": 30,
  "visitMetadata": null
}
```

## Field Mapping

### Spring Boot DTO → FastAPI Request

| Spring Boot Field | FastAPI Field | Notes |
|-------------------|---------------|-------|
| `PatientInfoDTO.age` | `patient_info.age` | Direct mapping |
| `PatientInfoDTO.gestationalWeeks` | `patient_info.gestationalWeeks` | Direct mapping |
| `MedicalHistoryDTO.previousLscs` | `medical_history.previousLSCS` | Case difference |
| `VitalsDTO.heightCm` | `vitals.heightCm` | Direct mapping |
| `VitalsDTO.bmi` | `vitals.bmi` | Direct mapping |
| `VitalsDTO.bpSystolic` | `vitals.bpSystolic` | Direct mapping |
| `LabReportsDTO.hemoglobin` | `lab_reports.hemoglobin` | Direct mapping |
| `ObstetricHistoryDTO.birthOrder` | `obstetric_history.birthOrder` | Direct mapping |
| `PregnancyDetailsDTO.twinPregnancy` | `pregnancy_details.twinPregnancy` | Direct mapping |
| `CurrentSymptomsDTO.headache` | `current_symptoms.headache` | Direct mapping |

### FastAPI Response → Spring Boot Entity

| FastAPI Field | Spring Boot Entity Field | Type |
|---------------|-------------------------|------|
| `isHighRisk` | `isHighRisk` | Boolean |
| `riskLevel` | `riskLevel` | String (CRITICAL/HIGH/MEDIUM/LOW) |
| `detectedRisks` | `detectedRisks` | List<String> (JSONB) |
| `explanation` | `explanation` | TEXT |
| `confidence` | `confidence` | Double (0.0-1.0) |
| `recommendation` | `recommendation` | TEXT |
| `visitMetadata` | `visitMetadata` | Map<String, Object> (JSONB) |

## Configuration

### Spring Boot `application.yml`

```yaml
fastapi:
  base-url: http://localhost:8000
  connect-timeout: 5000
  read-timeout: 30000
  api-key: your-fastapi-secret-key
```

### FastAPI Configuration

**Start FastAPI Server:**
```bash
cd "Medical RAG Pipeline"
python api_server.py
```

**Server will start on:** `http://localhost:8000`

**Check health:**
```bash
curl http://localhost:8000/health
```

## Testing the Integration

### 1. Start FastAPI
```bash
cd "Medical RAG Pipeline"
python api_server.py
```

Expected output:
```
🚀 Starting Medical RAG API...
📦 Loading production pipeline...
✅ Pipeline loaded successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test FastAPI Directly
```bash
curl -X POST http://localhost:8000/assess-structured \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-fastapi-secret-key" \
  -d @Backend/test-payload-fastapi.json
```

### 3. Start Spring Boot
```bash
cd Backend
mvn spring-boot:run
```

Expected output:
```
Started AncServiceApplication in X.XXX seconds
```

### 4. Test Complete Flow
```bash
curl -X POST http://localhost:8080/api/anc/register-visit \
  -H "Content-Type: application/json" \
  -d @Backend/test-payload.json
```

## Error Handling

### FastAPI Unavailable

**Scenario:** FastAPI is not running or unreachable

**Spring Boot Behavior:**
- Visit is still saved to database (status=REGISTERED)
- `aiErrorMessage` is set
- Response includes error message
- HTTP 201 Created (visit saved successfully)

**Response:**
```json
{
  "visitId": "uuid",
  "patientId": "P12345",
  "status": "AI_FAILED",
  "riskAssessment": null,
  "message": "Visit registered but AI analysis failed. Please retry."
}
```

### FastAPI Timeout

**Configuration:**
```yaml
fastapi:
  connect-timeout: 5000  # 5 seconds to connect
  read-timeout: 30000    # 30 seconds to read response
```

**Behavior:** Same as unavailable - visit saved, error logged

### Invalid Response

**Scenario:** FastAPI returns unexpected format

**Spring Boot Behavior:**
- Logs error with details
- Sets status=AI_FAILED
- Visit still saved

## Data Flow Diagram

```
┌─────────────┐
│   React     │
│  Frontend   │
└──────┬──────┘
       │ POST /api/anc/register-visit
       │ (AncVisitRequestDTO)
       ↓
┌─────────────────────────────────────┐
│      Spring Boot Controller         │
│   AncVisitController.registerVisit()│
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│       Spring Boot Service           │
│   AncVisitService.registerVisit()   │
│                                     │
│  1. Auto-generate clinical summary │
│  2. Map DTO → Entity                │
│  3. Save to PostgreSQL (REGISTERED) │
└──────┬──────────────────────────────┘
       │
       │ Build FastApiRequestDTO
       ↓
┌─────────────────────────────────────┐
│      FastAPI Client                 │
│   FastApiClient.analyzeRisk()       │
│                                     │
│  POST /assess-structured            │
│  Headers: X-API-KEY                 │
│  Body: clinical_summary +           │
│        structured_data              │
└──────┬──────────────────────────────┘
       │
       │ HTTP POST
       ↓
┌─────────────────────────────────────┐
│      FastAPI Server                 │
│   Medical RAG Pipeline              │
│                                     │
│  1. Extract clinical features       │
│  2. Run rule engine                 │
│  3. Retrieve relevant guidelines    │
│  4. Generate LLM explanation        │
│  5. Calculate confidence            │
└──────┬──────────────────────────────┘
       │
       │ FastApiResponseDTO
       ↓
┌─────────────────────────────────────┐
│      Spring Boot Mapper             │
│   AncVisitMapper.enrichWithAiResponse()│
│                                     │
│  Map FastAPI response to Entity:    │
│  - isHighRisk                       │
│  - riskLevel                        │
│  - detectedRisks                    │
│  - explanation                      │
│  - confidence                       │
│  - recommendation                   │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│      PostgreSQL Database            │
│   Update visit (AI_ANALYZED)        │
└──────┬──────────────────────────────┘
       │
       │ AncVisitResponseDTO
       ↓
┌─────────────┐
│   React     │
│  Frontend   │
│             │
│  Display:   │
│  - Risk level badge                 │
│  - Detected risks list              │
│  - Explanation text                 │
│  - Confidence score                 │
│  - Recommendation                   │
└─────────────┘
```

## Troubleshooting

### Issue: FastAPI not responding

**Check:**
```bash
# Is FastAPI running?
curl http://localhost:8000/health

# Check FastAPI logs
cd "Medical RAG Pipeline"
python api_server.py
```

**Solution:** Start FastAPI server

### Issue: Connection refused

**Check:**
```yaml
# application.yml
fastapi:
  base-url: http://localhost:8000  # Correct URL?
```

**Solution:** Verify FastAPI URL and port

### Issue: API key mismatch

**Check:**
```yaml
# application.yml
fastapi:
  api-key: your-fastapi-secret-key  # Matches FastAPI?
```

**Solution:** Ensure API keys match (or remove if not configured)

### Issue: Timeout errors

**Check:**
```yaml
# application.yml
fastapi:
  read-timeout: 30000  # Increase if needed
```

**Solution:** Increase timeout for slow responses

### Issue: Field mapping errors

**Check Spring Boot logs:**
```
ERROR: Failed to map FastAPI response
```

**Solution:** Verify FastAPI response matches expected structure

## Performance Considerations

### Typical Response Times

| Component | Time |
|-----------|------|
| Spring Boot processing | < 100ms |
| FastAPI feature extraction | < 1s |
| FastAPI retrieval | 1-2s |
| FastAPI LLM reasoning | 5-10s |
| **Total** | **6-13s** |

### Optimization Tips

1. **FastAPI Side:**
   - Use GPU for embeddings (if available)
   - Cache FAISS index in memory
   - Use connection pooling for Ollama

2. **Spring Boot Side:**
   - Async processing (future enhancement)
   - Connection pooling (already configured)
   - Timeout configuration

3. **Database:**
   - Indexed queries
   - Connection pooling (HikariCP)

## Security Considerations

### Production Checklist

- [ ] Use HTTPS for FastAPI
- [ ] Secure API key (environment variable)
- [ ] Network isolation (internal network only)
- [ ] Rate limiting on both services
- [ ] Input validation
- [ ] Error message sanitization
- [ ] Audit logging

### Example: Secure Configuration

```yaml
# application.yml (production)
fastapi:
  base-url: https://internal-fastapi.yourdomain.com
  api-key: ${FASTAPI_API_KEY}  # From environment
  connect-timeout: 5000
  read-timeout: 30000
```

## Monitoring

### Key Metrics to Monitor

1. **FastAPI Availability:**
   - Health check endpoint
   - Response time
   - Error rate

2. **Integration Success Rate:**
   - AI_ANALYZED vs AI_FAILED ratio
   - Average processing time
   - Timeout frequency

3. **Data Quality:**
   - Confidence score distribution
   - Detected risks frequency
   - Risk level distribution

### Logging

**Spring Boot logs:**
```
INFO: Calling FastAPI at: http://localhost:8000/assess-structured
INFO: AI analysis completed: isHighRisk=true, riskLevel=CRITICAL, confidence=0.7
```

**FastAPI logs:**
```
INFO: Received structured assessment request
INFO: Extracted features: age=38, BP=165/110, Hb=9.8
INFO: Risk assessment: CRITICAL (score=15)
```

## Next Steps

1. ✅ FastAPI running on port 8000
2. ✅ Spring Boot configured to call FastAPI
3. ⏭️ Test complete integration
4. ⏭️ Deploy to production
5. ⏭️ Monitor performance
6. ⏭️ Optimize as needed

## Support

**FastAPI Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API Guide: `Medical RAG Pipeline/API_DOCUMENTATION.md`

**Spring Boot Documentation:**
- README: `Backend/README.md`
- Setup Guide: `Backend/SETUP.md`
- V2 Changes: `Backend/CHANGES_V2.md`

---

**Integration Version:** 2.0.0  
**Last Updated:** February 2026  
**Status:** ✅ Ready for Testing
