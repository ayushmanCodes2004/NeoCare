# 🔧 RAG Pipeline Integration Fix

## ❌ Current Issue

**Error:** `422 Unprocessable Content` when backend calls `/assess-structured`

**Root Cause:** The backend is sending data that doesn't match the RAG Pipeline's expected format. The Pydantic validation in FastAPI is rejecting the request.

---

## 🔍 What's Happening

### Backend Sends:
```json
{
  "clinical_summary": "...",
  "structured_data": {
    "patient_info": { ... },
    "medical_history": { ... },
    "vitals": { ... },
    "lab_reports": { ... },
    "obstetric_history": { ... },
    "pregnancy_details": { ... },
    "current_symptoms": { ... }
  }
}
```

### RAG Pipeline Expects:
All fields in `structured_data` must be present and match the Pydantic models exactly. Missing or null fields cause validation errors.

---

## ✅ Solution Options

### Option 1: Fix Backend to Send Complete Data (Recommended)

Ensure all required fields are populated before sending to RAG Pipeline.

**File:** `Backend/src/main/java/com/anc/service/AncVisitService.java`

Make sure the `StructuredDataDTO` is fully populated with all nested objects:
- `patient_info` - Required
- `medical_history` - Required
- `vitals` - Required
- `lab_reports` - Required
- `pregnancy_details` - Required
- `current_symptoms` - Required
- `obstetric_history` - Optional (but should be present)

### Option 2: Make RAG Pipeline Fields Optional

Modify the RAG Pipeline to accept optional fields.

**File:** `Medical RAG Pipeline/api_server.py`

Change the `StructuredData` model to make fields optional:

```python
class StructuredData(BaseModel):
    """Complete structured patient data."""
    patient_info: PatientInfo
    medical_history: MedicalHistory
    vitals: Vitals
    lab_reports: LabReports
    obstetric_history: Optional[ObstetricHistoryDTO] = None  # Already optional
    pregnancy_details: PregnancyDetails
    current_symptoms: CurrentSymptoms
    visit_metadata: Optional[VisitMetadata] = None  # Already optional
```

---

## 🔧 Quick Fix (Immediate)

### Step 1: Check Backend Logs

Look at what the backend is actually sending:

```bash
# In Backend logs, look for:
"FastAPI Request: {...}"
```

### Step 2: Check RAG Pipeline Logs

```bash
# In RAG Pipeline terminal (Terminal 4), look for validation errors
```

### Step 3: Test with API Tester

Use the API Tester to manually test the endpoint:

**URL:** http://localhost:8080/api-tester.html

Try registering a visit and see the exact error.

---

## 📋 Required Fields Checklist

### PatientInfo
- ✅ `age` (required, integer)
- ⚠️ `gravida` (optional, integer)
- ⚠️ `para` (optional, integer)
- ⚠️ `gestationalWeeks` (optional, integer)

### MedicalHistory
- ✅ `previousLSCS` (required, boolean, default: false)
- ✅ `chronicHypertension` (required, boolean, default: false)
- ✅ `diabetes` (required, boolean, default: false)
- ✅ `thyroidDisorder` (required, boolean, default: false)
- ✅ `badObstetricHistory` (required, boolean, default: false)

### Vitals
- ✅ `bpSystolic` (required, integer)
- ✅ `bpDiastolic` (required, integer)
- ⚠️ `pallor` (required, boolean, default: false)
- ⚠️ `pedalEdema` (required, boolean, default: false)

### LabReports
- ✅ `hemoglobin` (required, float)
- ⚠️ `urineProtein` (required, boolean, default: false)
- ⚠️ `fastingBloodSugar` (optional, float)

### PregnancyDetails
- ✅ `twinPregnancy` (required, boolean, default: false)
- ✅ `placentaPrevia` (required, boolean, default: false)
- ✅ `reducedFetalMovement` (required, boolean, default: false)
- ✅ `malpresentation` (required, boolean, default: false)

### CurrentSymptoms
- ✅ `headache` (required, boolean, default: false)
- ✅ `visualDisturbance` (required, boolean, default: false)
- ✅ `epigastricPain` (required, boolean, default: false)
- ✅ `decreasedUrineOutput` (required, boolean, default: false)
- ✅ `bleedingPerVagina` (required, boolean, default: false)
- ✅ `convulsions` (required, boolean, default: false)

---

## 🐛 Debugging Steps

### 1. Check Backend Request
```bash
# Look at Backend logs (Terminal 2)
# Find the line: "FastAPI Request: {...}"
# Copy the JSON and validate it
```

### 2. Test RAG Pipeline Directly
```bash
curl -X POST http://localhost:8000/assess-structured \
  -H "Content-Type: application/json" \
  -d '{
    "clinical_summary": "Test patient",
    "structured_data": {
      "patient_info": {
        "age": 26,
        "gravida": 2,
        "para": 1,
        "gestationalWeeks": 24
      },
      "medical_history": {
        "previousLSCS": false,
        "chronicHypertension": false,
        "diabetes": false,
        "thyroidDisorder": false,
        "badObstetricHistory": false
      },
      "vitals": {
        "bpSystolic": 120,
        "bpDiastolic": 80,
        "pallor": false,
        "pedalEdema": false
      },
      "lab_reports": {
        "hemoglobin": 11.5,
        "urineProtein": false
      },
      "pregnancy_details": {
        "twinPregnancy": false,
        "placentaPrevia": false,
        "reducedFetalMovement": false,
        "malpresentation": false
      },
      "current_symptoms": {
        "headache": false,
        "visualDisturbance": false,
        "epigastricPain": false,
        "decreasedUrineOutput": false,
        "bleedingPerVagina": false,
        "convulsions": false
      }
    }
  }'
```

### 3. Check Response
If you get 422, the response will show which field is invalid:
```json
{
  "detail": [
    {
      "loc": ["body", "structured_data", "vitals", "bpSystolic"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🎯 Recommended Fix

### Update Backend DTOs to Include Default Values

**File:** `Backend/src/main/java/com/anc/dto/MedicalHistoryDTO.java`

```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MedicalHistoryDTO {
    
    @JsonProperty("previousLSCS")
    @Builder.Default
    private Boolean previousLSCS = false;
    
    @JsonProperty("chronicHypertension")
    @Builder.Default
    private Boolean chronicHypertension = false;
    
    @JsonProperty("diabetes")
    @Builder.Default
    private Boolean diabetes = false;
    
    @JsonProperty("thyroidDisorder")
    @Builder.Default
    private Boolean thyroidDisorder = false;
    
    @JsonProperty("badObstetricHistory")
    @Builder.Default
    private Boolean badObstetricHistory = false;
    
    // Add other fields with defaults...
}
```

Do the same for:
- `VitalsDTO`
- `PregnancyDetailsDTO`
- `CurrentSymptomsDTO`
- `LabReportsDTO`

---

## 📊 Testing

### Test 1: Simple Visit Registration
1. Open frontend: http://localhost:5173
2. Login as worker
3. Create a patient
4. Register an ANC visit
5. Fill ALL required fields
6. Submit
7. Check if AI analysis works

### Test 2: Check Logs
```bash
# Backend logs (Terminal 2)
# Should show: "FastAPI responded with HTTP status: 200"

# RAG Pipeline logs (Terminal 4)
# Should show: "POST /assess-structured HTTP/1.1" 200
```

---

## 🚀 Quick Workaround

If you need to test immediately, use the `/assess` endpoint instead of `/assess-structured`:

**Backend Change:**
```java
// In FastApiClient.java
String url = fastApiBaseUrl + "/assess";  // Instead of /assess-structured

// Send simple query instead of structured data
String query = buildSimpleQuery(request);
```

This endpoint accepts a simple text query and is more forgiving.

---

## 📞 Need Help?

1. Check Backend logs (Terminal 2)
2. Check RAG Pipeline logs (Terminal 4)
3. Use API Tester: http://localhost:8080/api-tester.html
4. Test RAG directly: http://localhost:8000/docs

The error message will tell you exactly which field is missing or invalid!
