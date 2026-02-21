# Version 2 Updates - Matching Actual FastAPI Response

## Overview
Updated the Spring Boot backend to match the actual FastAPI `/analyze` endpoint response structure.

## Key Changes

### 1. FastApiResponseDTO - Complete Restructure
**Old Structure:**
```java
- risk_level (String)
- risk_score (Integer)
- flags (List<String>)
- recommended_actions (List<String>)
- rag_context_used (String)
- error (String)
```

**New Structure (Matches Actual FastAPI):**
```java
- isHighRisk (Boolean)           // Quick boolean flag
- riskLevel (String)             // CRITICAL / HIGH / MEDIUM / LOW
- detectedRisks (List<String>)   // ["Severe Anaemia", "Twin Pregnancy", ...]
- explanation (String)           // Full LLM explanation
- confidence (Double)            // 0.0 to 1.0
- recommendation (String)        // Primary action
- patientId (String)             // Echoed back
- patientName (String)           // Echoed back
- age (Integer)                  // Echoed back
- gestationalWeeks (Integer)     // Echoed back
- visitMetadata (Map)            // Optional metadata
```

### 2. Database Schema Updates

**New Columns:**
- `patient_name` VARCHAR(255) - Added patient name field
- `is_high_risk` BOOLEAN - Quick boolean flag for filtering
- `detected_risks` JSONB - Array of detected risk conditions
- `explanation` TEXT - Full LLM explanation
- `confidence` NUMERIC(4,3) - Model confidence score
- `recommendation` TEXT - Primary clinical recommendation
- `visit_metadata` JSONB - Optional metadata from FastAPI

**Removed Columns:**
- `risk_score` INTEGER - Replaced by confidence
- `ai_flags` JSONB - Replaced by detectedRisks
- `ai_recommendations` JSONB - Replaced by recommendation
- `rag_context_used` TEXT - No longer in FastAPI response

**New Indexes:**
- `idx_anc_is_high_risk` - For quick high-risk filtering
- `idx_anc_detected_risks` - GIN index on detected risks array

### 3. Entity Updates (AncVisitEntity.java)
- Added `patientName` field
- Replaced old AI fields with new FastAPI response fields
- Updated column mappings to match new schema
- Better documentation with field descriptions

### 4. Repository Updates (AncVisitRepository.java)

**New Query Methods:**
```java
// Find all high-risk visits (isHighRisk = true)
findByIsHighRiskTrueOrderByCreatedAtDesc()

// Find by specific risk level
findByRiskLevelOrderByCreatedAtDesc(String riskLevel)

// Find only CRITICAL visits
findAllCriticalVisits()

// Count high-risk visits
countHighRiskVisits()

// Count critical visits
countCriticalVisits()
```

### 5. Mapper Updates (AncVisitMapper.java)
- Added `patientName` mapping in `toEntity()`
- Updated `enrichWithAiResponse()` to map all new FastAPI fields
- Enhanced `buildMessage()` with risk-level-specific messages
- Added detailed logging of AI response fields

### 6. Service Updates (AncVisitService.java)
- Added `getCriticalVisits()` method
- Added `getVisitsByRiskLevel(String riskLevel)` method
- Updated logging to use new field names
- Better error handling for FastAPI failures

### 7. Controller Updates (AncVisitController.java)

**New Endpoints:**
```
GET /api/anc/visits/critical
    - Returns only CRITICAL risk level visits

GET /api/anc/visits/risk-level/{riskLevel}
    - Filter by specific risk level (CRITICAL/HIGH/MEDIUM/LOW)
```

**Updated Endpoint:**
```
GET /api/anc/visits/high-risk
    - Now uses isHighRisk boolean flag (covers CRITICAL + HIGH)
```

### 8. DTO Updates
- `AncVisitRequestDTO`: Added `patientName` field
- `AncVisitResponseDTO`: Added `patientName` field
- `FastApiResponseDTO`: Complete restructure to match actual API

## Migration Guide

### Database Migration
If you have existing data, run this migration:

```sql
-- Add new columns
ALTER TABLE anc_visits ADD COLUMN patient_name VARCHAR(255);
ALTER TABLE anc_visits ADD COLUMN is_high_risk BOOLEAN;
ALTER TABLE anc_visits ADD COLUMN detected_risks JSONB;
ALTER TABLE anc_visits ADD COLUMN explanation TEXT;
ALTER TABLE anc_visits ADD COLUMN confidence NUMERIC(4,3);
ALTER TABLE anc_visits ADD COLUMN recommendation TEXT;
ALTER TABLE anc_visits ADD COLUMN visit_metadata JSONB;

-- Drop old columns
ALTER TABLE anc_visits DROP COLUMN risk_score;
ALTER TABLE anc_visits DROP COLUMN ai_flags;
ALTER TABLE anc_visits DROP COLUMN ai_recommendations;
ALTER TABLE anc_visits DROP COLUMN rag_context_used;

-- Update risk_level column size
ALTER TABLE anc_visits ALTER COLUMN risk_level TYPE VARCHAR(20);

-- Add new indexes
CREATE INDEX idx_anc_is_high_risk ON anc_visits(is_high_risk);
CREATE INDEX idx_anc_detected_risks ON anc_visits USING GIN(detected_risks);

-- Drop old indexes
DROP INDEX IF EXISTS idx_anc_visits_ai_flags;
```

### Or Fresh Install
For new installations, just run the updated `schema.sql` file.

## API Response Example

### Old Response Format:
```json
{
  "visitId": "uuid",
  "patientId": "P12345",
  "status": "AI_ANALYZED",
  "riskAssessment": {
    "risk_level": "HIGH",
    "risk_score": 85,
    "flags": ["Severe Anaemia", "Hypertension"],
    "recommended_actions": ["Refer to hospital"],
    "rag_context_used": "...",
    "error": null
  },
  "savedAt": "2024-01-01T10:00:00",
  "message": "Visit registered successfully"
}
```

### New Response Format:
```json
{
  "visitId": "uuid",
  "patientId": "P12345",
  "patientName": "Test Patient",
  "status": "AI_ANALYZED",
  "riskAssessment": {
    "isHighRisk": true,
    "riskLevel": "CRITICAL",
    "detectedRisks": [
      "Severe Anaemia",
      "Severe Pre Eclampsia",
      "GDM Screening Overdue",
      "Elderly Gravida",
      "Twin Pregnancy"
    ],
    "explanation": "Risk Assessment: CRITICAL. Patient presents with 5 significant risk factors...",
    "confidence": 0.7,
    "recommendation": "URGENT: Immediate referral to CEmOC/District Hospital required.",
    "patientId": "P12345",
    "patientName": "Test Patient",
    "age": 38,
    "gestationalWeeks": 30,
    "visitMetadata": null
  },
  "savedAt": "2024-01-01T10:00:00",
  "message": "ALERT: High risk pregnancy detected — CRITICAL. Immediate action required."
}
```

## Benefits of V2

1. **Exact FastAPI Match**: No more field mapping issues
2. **Better Risk Filtering**: Boolean `isHighRisk` flag for quick queries
3. **Richer Data**: Full LLM explanation and confidence scores
4. **Better UX**: Risk-level-specific messages for React frontend
5. **More Flexible**: Metadata field for future extensions
6. **Better Queries**: New repository methods for dashboard stats
7. **CRITICAL Alerts**: Separate endpoint for urgent cases

## Testing

### Test High-Risk Endpoint:
```bash
curl http://localhost:8080/api/anc/visits/high-risk
```

### Test Critical Endpoint:
```bash
curl http://localhost:8080/api/anc/visits/critical
```

### Test Risk Level Filter:
```bash
curl http://localhost:8080/api/anc/visits/risk-level/CRITICAL
curl http://localhost:8080/api/anc/visits/risk-level/HIGH
curl http://localhost:8080/api/anc/visits/risk-level/MEDIUM
curl http://localhost:8080/api/anc/visits/risk-level/LOW
```

## Backward Compatibility

⚠️ **Breaking Changes**: This is a major version update with breaking changes:
- Database schema changed
- API response structure changed
- Frontend will need updates to handle new response format

## Next Steps

1. Update React frontend to use new response structure
2. Update dashboard to use new query endpoints
3. Add CRITICAL alert notifications
4. Implement confidence score visualization
5. Add detected risks badge display
