# V1 vs V2 - Quick Comparison

## FastAPI Response Structure

### V1 (Old - Hypothetical)
```json
{
  "risk_level": "HIGH",
  "risk_score": 85,
  "flags": ["Severe Anaemia", "Hypertension"],
  "recommended_actions": ["Refer to hospital", "Monitor BP"],
  "rag_context_used": "Retrieved 3 relevant guidelines...",
  "error": null
}
```

### V2 (New - Actual FastAPI)
```json
{
  "isHighRisk": true,
  "riskLevel": "CRITICAL",
  "detectedRisks": ["Severe Anaemia", "Severe Pre Eclampsia", "Twin Pregnancy"],
  "explanation": "Risk Assessment: CRITICAL. Patient presents with 5 significant risk factors...",
  "confidence": 0.7,
  "recommendation": "URGENT: Immediate referral to CEmOC/District Hospital required.",
  "patientId": "P12345",
  "patientName": "Test Patient",
  "age": 38,
  "gestationalWeeks": 30,
  "visitMetadata": null
}
```

## Database Schema

### V1 Columns
```sql
patient_id          VARCHAR(255) NOT NULL
worker_id           VARCHAR(255)
phc_id              VARCHAR(255)
clinical_summary    TEXT
structured_data     JSONB NOT NULL
risk_level          VARCHAR(10)
risk_score          INTEGER
ai_flags            JSONB
ai_recommendations  JSONB
rag_context_used    TEXT
ai_error_message    TEXT
status              VARCHAR(30)
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### V2 Columns
```sql
patient_id          VARCHAR(255)        -- NOT NULL removed
patient_name        VARCHAR(255)        -- NEW
worker_id           VARCHAR(255)
phc_id              VARCHAR(255)
clinical_summary    TEXT
structured_data     JSONB NOT NULL
is_high_risk        BOOLEAN             -- NEW
risk_level          VARCHAR(20)         -- Expanded size
detected_risks      JSONB               -- NEW (replaces ai_flags)
explanation         TEXT                -- NEW
confidence          NUMERIC(4,3)        -- NEW (replaces risk_score)
recommendation      TEXT                -- NEW (replaces ai_recommendations)
visit_metadata      JSONB               -- NEW
ai_error_message    TEXT
status              VARCHAR(30)
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

## API Endpoints

### V1 Endpoints
```
POST   /api/anc/register-visit
GET    /api/anc/visits/{visitId}
GET    /api/anc/patients/{patientId}/visits
GET    /api/anc/visits/high-risk
```

### V2 Endpoints (Added)
```
POST   /api/anc/register-visit
GET    /api/anc/visits/{visitId}
GET    /api/anc/patients/{patientId}/visits
GET    /api/anc/visits/high-risk              -- Updated logic
GET    /api/anc/visits/critical                -- NEW
GET    /api/anc/visits/risk-level/{riskLevel}  -- NEW
```

## Repository Methods

### V1 Methods
```java
findByPatientIdOrderByCreatedAtDesc(String patientId)
findByWorkerIdOrderByCreatedAtDesc(String workerId)
findByRiskLevel(String riskLevel)
findLatestByPatientId(String patientId)
countHighRiskVisits()
```

### V2 Methods (Added)
```java
findByPatientIdOrderByCreatedAtDesc(String patientId)
findByWorkerIdOrderByCreatedAtDesc(String workerId)
findByIsHighRiskTrueOrderByCreatedAtDesc()           -- NEW
findByRiskLevelOrderByCreatedAtDesc(String riskLevel) -- Updated
findAllCriticalVisits()                               -- NEW
findLatestByPatientId(String patientId)
countHighRiskVisits()                                 -- Updated logic
countCriticalVisits()                                 -- NEW
```

## Field Mapping Changes

| V1 Field | V2 Field | Notes |
|----------|----------|-------|
| `risk_score` (Integer 0-100) | `confidence` (Double 0.0-1.0) | Changed to confidence score |
| `ai_flags` (JSONB array) | `detectedRisks` (JSONB array) | Renamed for clarity |
| `ai_recommendations` (JSONB array) | `recommendation` (TEXT) | Single string instead of array |
| `rag_context_used` (TEXT) | ❌ Removed | Not in FastAPI response |
| ❌ Not present | `isHighRisk` (Boolean) | NEW - Quick filter flag |
| ❌ Not present | `explanation` (TEXT) | NEW - Full LLM explanation |
| ❌ Not present | `patient_name` (VARCHAR) | NEW - Patient name |
| ❌ Not present | `visitMetadata` (JSONB) | NEW - Optional metadata |

## Response Message Changes

### V1 Messages
```
"Visit registered successfully"
"Visit registered and risk analysis completed successfully"
"Visit registered but AI analysis failed. Please retry."
```

### V2 Messages (Enhanced)
```
"Visit registered successfully. Risk level: LOW"
"ALERT: High risk pregnancy detected — CRITICAL. Immediate action required."
"ALERT: High risk pregnancy detected — HIGH. Immediate action required."
"Visit registered but AI analysis failed. Please retry."
```

## Risk Level Values

### V1
```
HIGH
MEDIUM
LOW
```

### V2
```
CRITICAL  -- NEW highest priority
HIGH
MEDIUM
LOW
```

## Key Advantages of V2

| Feature | V1 | V2 |
|---------|----|----|
| FastAPI Match | ❌ Hypothetical | ✅ Exact match |
| Boolean Filter | ❌ No | ✅ `isHighRisk` flag |
| Confidence Score | ❌ Integer 0-100 | ✅ Double 0.0-1.0 |
| Explanation | ❌ No | ✅ Full LLM text |
| Critical Alerts | ❌ No separate level | ✅ CRITICAL level |
| Patient Name | ❌ No | ✅ Included |
| Metadata Support | ❌ No | ✅ Flexible JSONB |
| Query Performance | ⚠️ String comparison | ✅ Boolean index |

## Migration Complexity

| Aspect | Complexity | Notes |
|--------|-----------|-------|
| Database Schema | 🟡 Medium | Add columns, migrate data, drop old columns |
| Backend Code | 🟢 Low | Mostly field renames |
| API Contract | 🔴 High | Breaking changes for frontend |
| Data Migration | 🟡 Medium | Can map most fields automatically |

## Backward Compatibility

❌ **Not backward compatible**

Breaking changes:
1. Database schema changed
2. API response structure changed
3. Field names changed
4. Data types changed (risk_score → confidence)

## Recommended Upgrade Path

1. ✅ Backup database
2. ✅ Deploy V2 backend
3. ✅ Run migration script
4. ✅ Update frontend to V2 API
5. ✅ Test thoroughly
6. ✅ Monitor for issues
7. ✅ Drop old columns after verification

## Testing Checklist

- [ ] V2 backend starts successfully
- [ ] Database migration completes
- [ ] New endpoints return data
- [ ] FastAPI integration works
- [ ] Response structure matches V2
- [ ] High-risk filtering works
- [ ] Critical filtering works
- [ ] Confidence scores display correctly
- [ ] Detected risks array populates
- [ ] Explanation text appears
- [ ] Frontend displays new fields

## Summary

V2 is a **major upgrade** that aligns the backend with the actual FastAPI response structure, providing:
- ✅ Exact API match
- ✅ Better performance
- ✅ Richer data
- ✅ Enhanced filtering
- ✅ Critical alerts
- ✅ Confidence scores
- ✅ Full explanations

The upgrade requires database migration and frontend updates but provides significant improvements in functionality and accuracy.
