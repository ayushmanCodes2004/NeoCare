# API JSON Input/Output Formats

## 📥 INPUT FORMAT

### POST /query

**Endpoint:** `http://localhost:8000/query`

**Method:** POST

**Content-Type:** application/json

### Minimal Input
```json
{
  "query": "38-year-old pregnant woman with BP 150/95, Hb 10.5, twin pregnancy"
}
```

### Full Input (All Options)
```json
{
  "query": "38-year-old pregnant woman with BP 150/95, Hb 10.5, twin pregnancy",
  "care_level": "PHC",
  "verbose": false
}
```

### Input Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Clinical query (min 10 characters) |
| `care_level` | string | ❌ No | "PHC" | Care level: "ASHA", "PHC", "CHC", or "DISTRICT" |
| `verbose` | boolean | ❌ No | false | Include debug information |

### Input Examples

**Example 1: High-Risk Case**
```json
{
  "query": "38-year-old with BP 150/95, Hb 10.5, twin pregnancy",
  "care_level": "PHC"
}
```

**Example 2: Young Maternal Age**
```json
{
  "query": "19-year-old at 8 weeks with Hb 7.5, BP 145/95",
  "care_level": "PHC"
}
```

**Example 3: Moderate Risk**
```json
{
  "query": "28-year-old with Hb 10.5",
  "care_level": "PHC"
}
```

**Example 4: ASHA Worker Level**
```json
{
  "query": "Pregnant woman with swelling in legs and headache",
  "care_level": "ASHA"
}
```

**Example 5: District Hospital**
```json
{
  "query": "38-year-old at 30 weeks with twin pregnancy, placenta previa, BP 165/110",
  "care_level": "DISTRICT"
}
```

---

## 📤 OUTPUT FORMAT

### Success Response

```json
{
  "success": true,
  "query": "38-year-old with BP 150/95, Hb 10.5, twin pregnancy",
  "answer": "[CLINICAL DECISION SUPPORT — NOT A DIAGNOSIS]\nThis is an AI-powered clinical decision support tool for frontline health workers.\nAll recommendations must be verified by a qualified healthcare professional before any clinical action is taken.\nThis system provides guidance, not authority. Final management decisions should be made by a qualified doctor.\n\nCare Level: Primary Health Center\n\n⚠️ URGENT: Refer to obstetric specialist immediately\n⚠️ HIGH-RISK PREGNANCY — Requires enhanced surveillance\n\n======================================================================\n\nRisk Classification:\n- Advanced Maternal Age: Present (38 years)\n- Hypertension: Present (BP 150/95 mmHg)\n- Mild Anaemia: Present (Hb 10.5 g/dL)\n- Multiple Gestation: Present (Twin pregnancy)\n\nOverall Risk: CRITICAL (rule-based)\nRisk Score: 10\n\nEvidence:\n- Page 14: Advanced maternal age definition and risk factors\n- Page 13: Hypertension management in pregnancy\n- Page 15: Anaemia classification and treatment\n- Page 22: Multiple pregnancy complications\n\nClinical Recommendations:\n- Immediate referral to District Hospital for specialist care\n- Antihypertensive therapy: Tab Alpha Methyl Dopa 250mg BD/TDS\n- Iron and folic acid supplementation for anaemia\n- Enhanced ANC monitoring with frequent visits\n- Ultrasound for fetal growth monitoring\n- Blood pressure monitoring twice weekly\n\n======================================================================\n\nEvidence Grounding: 0.95\n  - Grounded claims: 18/19\n\nConfidence: 0.75 (MEDIUM)\n\nConfidence Breakdown:\n  - Retrieval Quality: 0.80\n  - Rule Coverage: 1.00\n  - Chunk Agreement: 0.70\n  - Extractor Confidence: 0.95\n\nRetrieval Statistics:\n  - FAISS chunks: 30\n  - BM25 chunks: 10\n  - Final chunks: 8\n\n[Consult qualified physician for all clinical decisions]",
  "blocked": false,
  "care_level": "PHC",
  "confidence": {
    "score": 0.75,
    "level": "MEDIUM",
    "original_score": 0.82,
    "ceiling_applied": [
      "weak_retrieval (quality=0.35)"
    ],
    "breakdown": {
      "retrieval_quality": 0.80,
      "rule_coverage": 1.0,
      "chunk_agreement": 0.70,
      "extractor_confidence": 0.95
    }
  },
  "features": {
    "age": 38,
    "gestational_age_weeks": null,
    "systolic_bp": 150,
    "diastolic_bp": 95,
    "hemoglobin": 10.5,
    "fbs": null,
    "twin_pregnancy": true,
    "prior_cesarean": false,
    "placenta_previa": false,
    "comorbidities": [],
    "extraction_confidence": 0.95,
    "missing_fields": [
      "gestational_age",
      "glucose"
    ]
  },
  "rule_output": {
    "overall_risk": "CRITICAL",
    "total_score": 10,
    "rule_coverage": 1.0,
    "triggered_rules": [
      "advanced_maternal_age",
      "hypertension",
      "mild_anemia",
      "twin_pregnancy"
    ],
    "risk_flags": [
      {
        "condition": "Advanced Maternal Age",
        "present": true,
        "severity": "major",
        "value": "38 years",
        "threshold": "≥35 years",
        "rationale": "Age ≥35 increases risk of chromosomal abnormalities, GDM, hypertension, cesarean delivery",
        "score": 3
      },
      {
        "condition": "Hypertension",
        "present": true,
        "severity": "major",
        "value": "BP 150/95 mmHg",
        "threshold": "≥140/90 mmHg",
        "rationale": "Hypertension (≥140/90) - risk of pre-eclampsia, IUGR, preterm delivery, requires antihypertensive therapy",
        "score": 3
      },
      {
        "condition": "Mild Anaemia",
        "present": true,
        "severity": "moderate",
        "value": "Hb 10.5 g/dL",
        "threshold": "<11 g/dL",
        "rationale": "Mild anaemia (Hb 10-11) - requires iron and folic acid supplementation",
        "score": 1
      },
      {
        "condition": "Multiple Gestation (Twins)",
        "present": true,
        "severity": "major",
        "value": "Twin pregnancy",
        "threshold": "N/A",
        "rationale": "Twin pregnancy increases risk of preterm birth, IUGR, pre-eclampsia, requires enhanced surveillance",
        "score": 3
      }
    ]
  },
  "retrieval_stats": {
    "rewritten_query": "Advanced maternal age pregnancy risk classification India guidelines Hypertension BP 150/95 management pregnancy pre-eclampsia Anaemia Hb 10.5 anemia threshold pregnancy iron supplementation Twin pregnancy multiple gestation high risk management 38-year-old with BP 150/95, Hb 10.5, twin pregnancy",
    "faiss_count": 30,
    "bm25_count": 10,
    "final_count": 8,
    "retrieval_quality": 0.80,
    "chunk_agreement": 0.70
  },
  "timestamp": "2024-01-15T10:30:45.123Z",
  "processing_time_ms": 8542.35
}
```

### Output Fields Explained

#### Top Level
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `query` | string | Original query |
| `answer` | string | Full clinical response with recommendations |
| `blocked` | boolean | Whether output was blocked by hallucination guard |
| `care_level` | string | Care level used (ASHA/PHC/CHC/DISTRICT) |
| `timestamp` | string | ISO 8601 timestamp |
| `processing_time_ms` | number | Processing time in milliseconds |

#### Confidence Object
| Field | Type | Description |
|-------|------|-------------|
| `score` | number | Overall confidence (0-1) |
| `level` | string | Confidence label (HIGH/MEDIUM/LOW/VERY_LOW) |
| `original_score` | number | Score before ceiling applied |
| `ceiling_applied` | array | List of ceilings applied |
| `breakdown` | object | Component scores |

#### Features Object
| Field | Type | Description |
|-------|------|-------------|
| `age` | number/null | Patient age in years |
| `gestational_age_weeks` | number/null | Gestational age |
| `systolic_bp` | number/null | Systolic blood pressure |
| `diastolic_bp` | number/null | Diastolic blood pressure |
| `hemoglobin` | number/null | Hemoglobin level (g/dL) |
| `fbs` | number/null | Fasting blood sugar (mg/dL) |
| `twin_pregnancy` | boolean | Twin pregnancy flag |
| `prior_cesarean` | boolean | Previous cesarean flag |
| `placenta_previa` | boolean | Placenta previa flag |
| `comorbidities` | array | List of comorbidities |
| `extraction_confidence` | number | Feature extraction quality (0-1) |
| `missing_fields` | array | List of fields not extracted |

#### Rule Output Object
| Field | Type | Description |
|-------|------|-------------|
| `overall_risk` | string | Risk level (LOW/MODERATE/HIGH/CRITICAL) |
| `total_score` | number | Numeric risk score |
| `rule_coverage` | number | % of features with rules (0-1) |
| `triggered_rules` | array | List of triggered rule names |
| `risk_flags` | array | Detailed risk flag objects |

#### Risk Flag Object
| Field | Type | Description |
|-------|------|-------------|
| `condition` | string | Condition name |
| `present` | boolean | Whether condition is present |
| `severity` | string | Severity level (minor/moderate/major/critical) |
| `value` | string | Actual value |
| `threshold` | string | Threshold value |
| `rationale` | string | Clinical rationale |
| `score` | number | Risk score contribution |

#### Retrieval Stats Object
| Field | Type | Description |
|-------|------|-------------|
| `rewritten_query` | string | Query after rewriting |
| `faiss_count` | number | Chunks from FAISS |
| `bm25_count` | number | Chunks from BM25 |
| `final_count` | number | Final chunks after reranking |
| `retrieval_quality` | number | Quality score (0-1) |
| `chunk_agreement` | number | Multi-chunk agreement (0-1) |

---

## 🚫 ERROR RESPONSES

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid care_level. Must be one of: ASHA, PHC, CHC, DISTRICT",
  "detail": null,
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "detail": "Error processing query: Connection timeout",
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

### 503 Service Unavailable
```json
{
  "success": false,
  "error": "Pipeline not initialized",
  "detail": null,
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

---

## 📋 BLOCKED OUTPUT EXAMPLE

When confidence is too low, output is blocked:

```json
{
  "success": true,
  "query": "pregnant woman",
  "answer": "[CLINICAL DECISION SUPPORT — NOT A DIAGNOSIS]\n\n⚠️ LOW CONFIDENCE — INSUFFICIENT DOCUMENT EVIDENCE\n\nThe system cannot provide a reliable answer for this query due to:\n\n  • Overall confidence (0.32) below threshold (0.35)\n  • Retrieval quality (0.18) below threshold (0.35)\n\nThis may occur when:\n- The query is outside the scope of the clinical document\n- Insufficient relevant information was retrieved\n- The extracted clinical features are incomplete\n\nPlease:\n1. Rephrase your query with more specific clinical details\n2. Ensure the query relates to high-risk pregnancy topics covered in the document\n3. Consult a qualified healthcare professional for clinical guidance\n\n[Consult qualified physician for all clinical decisions]",
  "blocked": true,
  "care_level": "PHC",
  "confidence": {
    "score": 0.32,
    "level": "LOW",
    "breakdown": {
      "retrieval_quality": 0.18,
      "rule_coverage": 0.0,
      "chunk_agreement": 0.50,
      "extractor_confidence": 0.30
    }
  },
  "features": {
    "age": null,
    "gestational_age_weeks": null,
    "systolic_bp": null,
    "diastolic_bp": null,
    "hemoglobin": null,
    "fbs": null,
    "twin_pregnancy": false,
    "prior_cesarean": false,
    "placenta_previa": false,
    "comorbidities": [],
    "extraction_confidence": 0.30,
    "missing_fields": [
      "age",
      "gestational_age",
      "blood_pressure",
      "hemoglobin",
      "glucose"
    ]
  },
  "rule_output": {
    "overall_risk": "LOW",
    "total_score": 0,
    "rule_coverage": 0.0,
    "triggered_rules": [],
    "risk_flags": []
  },
  "retrieval_stats": {
    "rewritten_query": "pregnant woman",
    "faiss_count": 30,
    "bm25_count": 5,
    "final_count": 8,
    "retrieval_quality": 0.18,
    "chunk_agreement": 0.50
  },
  "timestamp": "2024-01-15T10:30:45.123Z",
  "processing_time_ms": 3245.67
}
```

---

## 💡 USAGE TIPS

### Extracting Key Information

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "38-year-old with BP 150/95, Hb 10.5, twin pregnancy"}
)

data = response.json()

# Check if successful
if data['success'] and not data['blocked']:
    # Get risk assessment
    risk = data['rule_output']['overall_risk']
    score = data['rule_output']['total_score']
    
    # Get confidence
    confidence = data['confidence']['level']
    
    # Get clinical features
    age = data['features']['age']
    bp = f"{data['features']['systolic_bp']}/{data['features']['diastolic_bp']}"
    
    # Get answer
    answer = data['answer']
    
    print(f"Risk: {risk} (Score: {score})")
    print(f"Confidence: {confidence}")
    print(f"Patient: {age} years, BP {bp}")
else:
    print(f"Error or blocked: {data.get('answer', 'Unknown error')}")
```

### JavaScript Example
```javascript
fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: '38-year-old with BP 150/95, Hb 10.5, twin pregnancy',
    care_level: 'PHC'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success && !data.blocked) {
    console.log('Risk:', data.rule_output.overall_risk);
    console.log('Score:', data.rule_output.total_score);
    console.log('Confidence:', data.confidence.level);
  }
});
```

---

## 📊 SAMPLE RESPONSES BY RISK LEVEL

### LOW RISK
```json
{
  "rule_output": {
    "overall_risk": "LOW",
    "total_score": 0,
    "triggered_rules": []
  }
}
```

### MODERATE RISK
```json
{
  "rule_output": {
    "overall_risk": "MODERATE",
    "total_score": 3,
    "triggered_rules": ["mild_anemia"]
  }
}
```

### HIGH RISK
```json
{
  "rule_output": {
    "overall_risk": "HIGH",
    "total_score": 6,
    "triggered_rules": ["advanced_maternal_age", "hypertension"]
  }
}
```

### CRITICAL RISK
```json
{
  "rule_output": {
    "overall_risk": "CRITICAL",
    "total_score": 10,
    "triggered_rules": ["advanced_maternal_age", "hypertension", "mild_anemia", "twin_pregnancy"]
  }
}
```

---

**API Version:** 1.0.0  
**Last Updated:** 2024-01-15
