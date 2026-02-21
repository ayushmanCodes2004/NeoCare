# Simplified API Guide - /assess Endpoint

## Overview

The `/assess` endpoint provides a clean, simplified JSON output for risk assessment. Perfect for mobile apps, dashboards, and integrations.

---

## Endpoint

```
POST http://localhost:8000/assess
```

---

## Request Format

```json
{
  "query": "Clinical description of the pregnancy case",
  "care_level": "PHC",
  "verbose": false
}
```

### Parameters

- `query` (required): Clinical description including age, gestational age, BP, Hb, symptoms, etc.
- `care_level` (optional): One of "ASHA", "PHC", "CHC", "DISTRICT" (default: "PHC")
- `verbose` (optional): Include debug info (default: false)

---

## Response Format

```json
{
  "isHighRisk": true,
  "riskLevel": "HIGH",
  "detectedRisks": [
    "Severe anemia",
    "Advanced maternal age",
    "Hypertension"
  ],
  "explanation": "Patient has Hb < 7 indicating severe anemia, age > 35, and elevated BP suggesting preeclampsia risk.",
  "confidence": 0.93,
  "recommendation": "Immediate obstetric consultation recommended."
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `isHighRisk` | boolean | `true` if risk level is HIGH or CRITICAL |
| `riskLevel` | string | One of: "LOW", "MODERATE", "HIGH", "CRITICAL", "UNKNOWN" |
| `detectedRisks` | array | List of detected risk conditions |
| `explanation` | string | Brief explanation of the assessment (max 250 chars) |
| `confidence` | float | Confidence score 0.0-1.0 |
| `recommendation` | string | Clinical recommendation |

---

## Risk Levels

| Level | Score | Meaning |
|-------|-------|---------|
| LOW | 0 | No significant risk factors detected |
| MODERATE | 1-3 | Minor risk factors present, routine monitoring |
| HIGH | 4-6 | Major risk factors, referral recommended |
| CRITICAL | 7+ | Multiple severe risks, urgent referral required |
| UNKNOWN | - | Unable to assess (insufficient data) |

---

## Example Use Cases

### Example 1: Severe Anemia + Advanced Age + Hypertension

**Request:**
```json
{
  "query": "A 38-year-old pregnant woman at 32 weeks with BP 155/98 mmHg and Hb 6.2 g/dL. She has severe headache and pedal edema.",
  "care_level": "PHC"
}
```

**Response:**
```json
{
  "isHighRisk": true,
  "riskLevel": "HIGH",
  "detectedRisks": [
    "Advanced Maternal Age",
    "Severe Anaemia",
    "Hypertension"
  ],
  "explanation": "Patient presents with multiple high-risk factors including severe anemia (Hb 6.2), advanced maternal age (38 years), and hypertension (BP 155/98).",
  "confidence": 0.87,
  "recommendation": "Immediate obstetric consultation recommended."
}
```

---

### Example 2: Normal Pregnancy

**Request:**
```json
{
  "query": "A 26-year-old G2P1 at 28 weeks with BP 118/76 mmHg, Hb 11.5 g/dL, no complaints. Previous delivery was normal.",
  "care_level": "PHC"
}
```

**Response:**
```json
{
  "isHighRisk": false,
  "riskLevel": "LOW",
  "detectedRisks": [],
  "explanation": "Patient has normal vital signs and no significant risk factors detected. Continue routine antenatal care.",
  "confidence": 0.82,
  "recommendation": "Continue routine antenatal care."
}
```

---

### Example 3: Teenage Pregnancy with Mild Anemia

**Request:**
```json
{
  "query": "A 17-year-old primigravida at 24 weeks with BP 110/70 mmHg and Hb 10.2 g/dL. No other complications.",
  "care_level": "ASHA"
}
```

**Response:**
```json
{
  "isHighRisk": false,
  "riskLevel": "MODERATE",
  "detectedRisks": [
    "Teenage Pregnancy",
    "Mild Anaemia"
  ],
  "explanation": "Young maternal age (17 years) and mild anemia (Hb 10.2) require monitoring. Ensure iron supplementation and regular ANC visits.",
  "confidence": 0.79,
  "recommendation": "Continue routine antenatal care."
}
```

---

### Example 4: Twin Pregnancy + GDM

**Request:**
```json
{
  "query": "A 30-year-old woman at 30 weeks with twin pregnancy. FBS is 98 mg/dL. BP 130/85 mmHg, Hb 10.8 g/dL.",
  "care_level": "CHC"
}
```

**Response:**
```json
{
  "isHighRisk": true,
  "riskLevel": "HIGH",
  "detectedRisks": [
    "Twin Pregnancy",
    "GDM"
  ],
  "explanation": "Twin pregnancy with gestational diabetes (FBS 98) requires specialized monitoring and delivery planning at higher facility.",
  "confidence": 0.85,
  "recommendation": "Referral to higher facility recommended for specialized care."
}
```

---

## Integration Examples

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/assess",
    json={
        "query": "38-year-old with BP 155/98, Hb 6.2 at 32 weeks",
        "care_level": "PHC"
    }
)

result = response.json()
print(f"High Risk: {result['isHighRisk']}")
print(f"Risk Level: {result['riskLevel']}")
print(f"Confidence: {result['confidence']}")
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8000/assess', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "38-year-old with BP 155/98, Hb 6.2 at 32 weeks",
    care_level: "PHC"
  })
});

const result = await response.json();
console.log(`High Risk: ${result.isHighRisk}`);
console.log(`Risk Level: ${result.riskLevel}`);
console.log(`Confidence: ${result.confidence}`);
```

### cURL

```bash
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "query": "38-year-old with BP 155/98, Hb 6.2 at 32 weeks",
    "care_level": "PHC"
  }'
```

---

## Error Handling

### Insufficient Data

If the system cannot assess risk due to insufficient data:

```json
{
  "isHighRisk": false,
  "riskLevel": "UNKNOWN",
  "detectedRisks": [],
  "explanation": "Unable to assess risk due to insufficient evidence. Please provide more clinical details or consult a healthcare professional.",
  "confidence": 0.0,
  "recommendation": "Consult qualified healthcare professional for clinical assessment."
}
```

### Server Error

```json
{
  "detail": "Error processing query: [error message]"
}
```

---

## Comparison: /assess vs /query

| Feature | /assess | /query |
|---------|---------|--------|
| Output Format | Simple, clean JSON | Detailed, verbose JSON |
| Response Size | Small (~200 bytes) | Large (~2-5 KB) |
| Fields | 6 essential fields | 15+ detailed fields |
| Use Case | Mobile apps, dashboards | Clinical workstations, debugging |
| Processing Time | Same | Same |
| Confidence Info | Single score | Full breakdown |
| Retrieval Stats | Not included | Included |
| Answer Text | Brief explanation | Full clinical answer |

---

## Testing

Run the test script:

```bash
python test_simple_api.py
```

This will:
1. Show expected output format
2. Test 4 different clinical scenarios
3. Validate response structure
4. Display key metrics

---

## API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Notes

- The `/assess` endpoint uses the same production pipeline as `/query`
- All safety features (hallucination guard, evidence attribution, etc.) are active
- Confidence scores reflect retrieval quality, rule coverage, and evidence strength
- Risk levels are based on clinical rule engine with 12 medical rules
- Recommendations are care-level aware (ASHA/PHC/CHC/DISTRICT)

---

*Last Updated: 2026-02-20*
*Version: 1.0.0*
