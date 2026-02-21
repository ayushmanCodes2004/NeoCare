# Structured API Guide - /assess-structured Endpoint

## Overview

The `/assess-structured` endpoint accepts detailed structured JSON data (patient demographics, vitals, labs, medical history, etc.) and returns a simplified risk assessment.

This is ideal for:
- Electronic Medical Record (EMR) systems
- Hospital Information Systems (HIS)
- Mobile health apps with structured data collection
- Integration with existing patient databases

---

## Endpoint

```
POST http://localhost:8000/assess-structured
```

---

## Request Format

### Complete Structure

```json
{
  "clinical_summary": "Brief clinical summary",
  "structured_data": {
    "patient_info": { ... },
    "medical_history": { ... },
    "vitals": { ... },
    "lab_reports": { ... },
    "pregnancy_details": { ... },
    "current_symptoms": { ... },
    "visit_metadata": { ... }
  },
  "care_level": "PHC",
  "verbose": false
}
```

### Detailed Field Descriptions

#### patient_info (Required)
```json
{
  "patientId": "ANC-2025-00123",
  "name": "Sita Devi",
  "age": 36,                      // Required
  "gravida": 3,
  "para": 1,
  "livingChildren": 1,
  "gestationalWeeks": 30,
  "lmpDate": "2025-07-15",
  "estimatedDueDate": "2026-04-22"
}
```

#### medical_history (Required)
```json
{
  "previousLSCS": true,
  "badObstetricHistory": false,
  "previousStillbirth": false,
  "previousPretermDelivery": false,
  "previousAbortion": true,
  "systemicIllness": "None",
  "chronicHypertension": false,
  "diabetes": false,
  "thyroidDisorder": false
}
```

#### vitals (Required)
```json
{
  "weightKg": 78,
  "heightCm": 158,
  "bmi": 31.2,
  "bpSystolic": 150,              // Required
  "bpDiastolic": 100,             // Required
  "pulseRate": 96,
  "respiratoryRate": 20,
  "temperatureCelsius": 36.9,
  "pallor": true,
  "pedalEdema": true
}
```

#### lab_reports (Required)
```json
{
  "hemoglobin": 6.5,              // Required
  "plateletCount": 150000,
  "bloodGroup": "B+",
  "rhNegative": false,
  "urineProtein": true,
  "urineSugar": false,
  "fastingBloodSugar": 92,
  "hivPositive": false,
  "syphilisPositive": false,
  "serumCreatinine": 0.8,
  "ast": 32,
  "alt": 28
}
```

#### pregnancy_details (Required)
```json
{
  "twinPregnancy": true,
  "malpresentation": false,
  "placentaPrevia": false,
  "reducedFetalMovement": true,
  "amnioticFluidNormal": true,
  "umbilicalDopplerAbnormal": false
}
```

#### current_symptoms (Required)
```json
{
  "headache": false,
  "visualDisturbance": false,
  "epigastricPain": false,
  "decreasedUrineOutput": false,
  "bleedingPerVagina": false,
  "convulsions": false
}
```

#### visit_metadata (Optional)
```json
{
  "visitType": "Routine ANC",
  "visitNumber": 5,
  "healthWorkerId": "ASHA-234",
  "subCenterId": "SC-12",
  "district": "Kalahandi",
  "state": "Odisha",
  "timestamp": "2026-02-20T10:30:00Z"
}
```

---

## Response Format

```json
{
  "isHighRisk": true,
  "riskLevel": "HIGH",
  "detectedRisks": [
    "Advanced Maternal Age",
    "Severe Anaemia",
    "Hypertension",
    "Twin Pregnancy"
  ],
  "explanation": "Patient presents with multiple high-risk factors including severe anemia (Hb 6.5), advanced maternal age (36 years), hypertension (BP 150/100), and twin pregnancy.",
  "confidence": 0.87,
  "recommendation": "Immediate obstetric consultation recommended.",
  "patientId": "ANC-2025-00123",
  "patientName": "Sita Devi",
  "age": 36,
  "gestationalWeeks": 30,
  "visitMetadata": {
    "visitType": "Routine ANC",
    "visitNumber": 5,
    "healthWorkerId": "ASHA-234",
    "subCenterId": "SC-12",
    "district": "Kalahandi",
    "state": "Odisha",
    "timestamp": "2026-02-20T10:30:00Z"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `isHighRisk` | boolean | `true` if risk level is HIGH or CRITICAL |
| `riskLevel` | string | "LOW", "MODERATE", "HIGH", "CRITICAL", or "UNKNOWN" |
| `detectedRisks` | array | List of detected risk conditions |
| `explanation` | string | Brief explanation of the assessment |
| `confidence` | float | Confidence score 0.0-1.0 |
| `recommendation` | string | Clinical recommendation |
| `patientId` | string | Patient identifier (from input) |
| `patientName` | string | Patient name (from input) |
| `age` | int | Patient age (from input) |
| `gestationalWeeks` | int | Gestational age (from input) |
| `visitMetadata` | object | Visit information (from input) |

---

## Complete Example

### Request

```json
{
  "clinical_summary": "Pregnant woman aged 36, 30 weeks gestation, Hb 6.5 g/dL, BP 150/100 mmHg, previous LSCS, twin pregnancy. Complains of pedal edema and reduced fetal movements.",
  "structured_data": {
    "patient_info": {
      "patientId": "ANC-2025-00123",
      "name": "Sita Devi",
      "age": 36,
      "gravida": 3,
      "para": 1,
      "livingChildren": 1,
      "gestationalWeeks": 30,
      "lmpDate": "2025-07-15",
      "estimatedDueDate": "2026-04-22"
    },
    "medical_history": {
      "previousLSCS": true,
      "badObstetricHistory": false,
      "previousStillbirth": false,
      "previousPretermDelivery": false,
      "previousAbortion": true,
      "systemicIllness": "None",
      "chronicHypertension": false,
      "diabetes": false,
      "thyroidDisorder": false
    },
    "vitals": {
      "weightKg": 78,
      "heightCm": 158,
      "bmi": 31.2,
      "bpSystolic": 150,
      "bpDiastolic": 100,
      "pulseRate": 96,
      "respiratoryRate": 20,
      "temperatureCelsius": 36.9,
      "pallor": true,
      "pedalEdema": true
    },
    "lab_reports": {
      "hemoglobin": 6.5,
      "plateletCount": 150000,
      "bloodGroup": "B+",
      "rhNegative": false,
      "urineProtein": true,
      "urineSugar": false,
      "fastingBloodSugar": 92,
      "hivPositive": false,
      "syphilisPositive": false,
      "serumCreatinine": 0.8,
      "ast": 32,
      "alt": 28
    },
    "pregnancy_details": {
      "twinPregnancy": true,
      "malpresentation": false,
      "placentaPrevia": false,
      "reducedFetalMovement": true,
      "amnioticFluidNormal": true,
      "umbilicalDopplerAbnormal": false
    },
    "current_symptoms": {
      "headache": false,
      "visualDisturbance": false,
      "epigastricPain": false,
      "decreasedUrineOutput": false,
      "bleedingPerVagina": false,
      "convulsions": false
    },
    "visit_metadata": {
      "visitType": "Routine ANC",
      "visitNumber": 5,
      "healthWorkerId": "ASHA-234",
      "subCenterId": "SC-12",
      "district": "Kalahandi",
      "state": "Odisha",
      "timestamp": "2026-02-20T10:30:00Z"
    }
  },
  "care_level": "PHC",
  "verbose": false
}
```

### Response

```json
{
  "isHighRisk": true,
  "riskLevel": "HIGH",
  "detectedRisks": [
    "Advanced Maternal Age",
    "Severe Anaemia",
    "Hypertension",
    "Twin Pregnancy"
  ],
  "explanation": "Patient presents with multiple high-risk factors including severe anemia (Hb 6.5), advanced maternal age (36 years), hypertension (BP 150/100), and twin pregnancy.",
  "confidence": 0.87,
  "recommendation": "Immediate obstetric consultation recommended.",
  "patientId": "ANC-2025-00123",
  "patientName": "Sita Devi",
  "age": 36,
  "gestationalWeeks": 30,
  "visitMetadata": {
    "visitType": "Routine ANC",
    "visitNumber": 5,
    "healthWorkerId": "ASHA-234",
    "subCenterId": "SC-12",
    "district": "Kalahandi",
    "state": "Odisha",
    "timestamp": "2026-02-20T10:30:00Z"
  }
}
```

---

## Integration Examples

### Python

```python
import requests

# Your structured patient data
patient_data = {
    "clinical_summary": "36-year-old with severe anemia and hypertension",
    "structured_data": {
        "patient_info": {
            "patientId": "ANC-2025-00123",
            "age": 36,
            "gestationalWeeks": 30
        },
        "medical_history": {
            "previousLSCS": True
        },
        "vitals": {
            "bpSystolic": 150,
            "bpDiastolic": 100
        },
        "lab_reports": {
            "hemoglobin": 6.5
        },
        "pregnancy_details": {
            "twinPregnancy": True
        },
        "current_symptoms": {}
    },
    "care_level": "PHC"
}

response = requests.post(
    "http://localhost:8000/assess-structured",
    json=patient_data
)

result = response.json()
print(f"Patient: {result['patientName']}")
print(f"High Risk: {result['isHighRisk']}")
print(f"Risk Level: {result['riskLevel']}")
print(f"Detected Risks: {', '.join(result['detectedRisks'])}")
```

### JavaScript/Node.js

```javascript
const patientData = {
  clinical_summary: "36-year-old with severe anemia and hypertension",
  structured_data: {
    patient_info: {
      patientId: "ANC-2025-00123",
      age: 36,
      gestationalWeeks: 30
    },
    medical_history: {
      previousLSCS: true
    },
    vitals: {
      bpSystolic: 150,
      bpDiastolic: 100
    },
    lab_reports: {
      hemoglobin: 6.5
    },
    pregnancy_details: {
      twinPregnancy: true
    },
    current_symptoms: {}
  },
  care_level: "PHC"
};

const response = await fetch('http://localhost:8000/assess-structured', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(patientData)
});

const result = await response.json();
console.log(`Patient: ${result.patientName}`);
console.log(`High Risk: ${result.isHighRisk}`);
console.log(`Risk Level: ${result.riskLevel}`);
```

---

## How It Works

1. **Structured Data Conversion**: The endpoint converts your structured JSON into a clinical query text
2. **RAG Processing**: The query is processed through the production RAG pipeline
3. **Risk Assessment**: Clinical rules engine evaluates risk factors
4. **Response Generation**: LLM generates evidence-based recommendations
5. **Simplified Output**: Results are formatted into clean JSON with patient context

---

## Benefits

✅ **Type-safe**: Pydantic models validate all input fields
✅ **Comprehensive**: Captures all relevant clinical data
✅ **Traceable**: Includes patient ID and visit metadata
✅ **Consistent**: Structured format ensures data quality
✅ **Integration-ready**: Easy to integrate with EMR/HIS systems

---

## Testing

Run the test script:

```bash
python test_structured_api.py
```

This will:
1. Show the expected input format
2. Send your example structured data
3. Display the complete response
4. Validate all fields

---

## API Comparison

| Feature | /assess | /assess-structured | /query |
|---------|---------|-------------------|--------|
| Input | Text query | Structured JSON | Text query |
| Patient Context | No | Yes (ID, name, metadata) | No |
| Data Validation | Basic | Comprehensive | Basic |
| EMR Integration | Difficult | Easy | Difficult |
| Response Size | Small | Medium | Large |
| Use Case | Simple queries | EMR/HIS integration | Debugging |

---

## Notes

- All boolean fields default to `false` if not provided
- Optional fields can be omitted
- The `clinical_summary` is used as additional context
- Patient ID and visit metadata are returned in the response for traceability
- All safety features (hallucination guard, evidence attribution) are active

---

*Last Updated: 2026-02-20*
*Version: 1.0.0*
