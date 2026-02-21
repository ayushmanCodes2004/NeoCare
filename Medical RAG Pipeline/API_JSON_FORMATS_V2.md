# API JSON Input/Output Formats - V2

## 🆕 What's New in V2

V2 adds support for 16 new HPR conditions from PMSMA + JOGH + Extended PMSMA guidelines:

**New Anthropometric Fields:**
- `height` - Height in cm (threshold: <140 cm)
- `bmi` - BMI in kg/m² (threshold: ≥30)

**New Lifestyle Risk Fields:**
- `smoking` - Current smoker (boolean)
- `tobacco_use` - Tobacco use (boolean)
- `alcohol_use` - Alcohol consumption (boolean)

**New Obstetric History Fields:**
- `birth_order` - Birth order/parity (threshold: ≥5)
- `inter_pregnancy_interval` - Months between pregnancies (threshold: <18 or >59)
- `stillbirth_count` - Number of previous stillbirths
- `abortion_count` - Number of previous abortions
- `preterm_history` - History of preterm delivery (boolean)

**New Serology Fields:**
- `rh_negative` - Rh negative blood group (boolean)
- `hiv_positive` - HIV positive status (boolean)
- `syphilis_positive` - Syphilis positive status (boolean)

**New Pregnancy Complications:**
- `malpresentation` - Abnormal fetal presentation (boolean)
- `systemic_illness` - Current or past systemic illness (boolean)

**New Output Fields:**
- `is_hpr` - Composite HPR flag (boolean) based on Section 19 logic
- `borderline_flags` - Array of borderline values needing monitoring

---

## 📥 INPUT FORMAT

### POST /query (Simple Text Query)

**Endpoint:** `http://localhost:8000/query`

**Method:** POST

**Content-Type:** application/json

### V2 Input Example
```json
{
  "query": "28-year-old woman at 20 weeks, height 135 cm, BMI 32, smoker, Hb 10.5, BP 110/70, birth order 6, previous pregnancy 10 months ago",
  "care_level": "PHC",
  "verbose": false
}
```

### Input Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Clinical query with V2 fields (min 10 characters) |
| `care_level` | string | ❌ No | "PHC" | Care level: "ASHA", "PHC", "CHC", or "DISTRICT" |
| `verbose` | boolean | ❌ No | false | Include debug information |

---

### POST /assess-structured (Structured JSON Input)

**Endpoint:** `http://localhost:8000/assess-structured`

**Method:** POST

**Content-Type:** application/json

### V2 Structured Input Example
```json
{
  "clinical_summary": "28-year-old G6P5 at 20 weeks with short stature, high BMI, smoking, mild anaemia",
  "structured_data": {
    "patient_info": {
      "patientId": "ANC-2024-001",
      "name": "Patient Name",
      "age": 28,
      "gravida": 6,
      "para": 5,
      "livingChildren": 5,
      "gestationalWeeks": 20,
      "lmpDate": "2024-09-01",
      "estimatedDueDate": "2025-06-08"
    },
    "medical_history": {
      "previousLSCS": false,
      "badObstetricHistory": false,
      "previousStillbirth": true,
      "previousPretermDelivery": true,
      "previousAbortion": true,
      "systemicIllness": "Asthma",
      "chronicHypertension": false,
      "diabetes": false,
      "thyroidDisorder": false
    },
    "vitals": {
      "weightKg": 75,
      "heightCm": 135,
      "bmi": 32.0,
      "bpSystolic": 110,
      "bpDiastolic": 70,
      "pulseRate": 80,
      "respiratoryRate": 18,
      "temperatureCelsius": 37.0,
      "pallor": true,
      "pedalEdema": false
    },
    "lab_reports": {
      "hemoglobin": 10.5,
      "plateletCount": 200000,
      "bloodGroup": "B+",
      "rhNegative": false,
      "urineProtein": false,
      "urineSugar": false,
      "fastingBloodSugar": 85,
      "hivPositive": false,
      "syphilisPositive": false,
      "serumCreatinine": 0.8,
      "ast": 25,
      "alt": 30
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
      "headache": false,
      "visualDisturbance": false,
      "epigastricPain": false,
      "decreasedUrineOutput": false,
      "bleedingPerVagina": false,
      "convulsions": false
    },
    "visit_metadata": {
      "visitType": "Routine ANC",
      "visitNumber": 3,
      "healthWorkerId": "ANM-115",
      "subCenterId": "SC-033",
      "district": "Jaipur",
      "state": "Rajasthan",
      "timestamp": "2025-02-21T10:30:00Z"
    }
  },
  "care_level": "PHC",
  "verbose": false
}
```

### V2 Structured Input Fields

#### patient_info (NEW FIELDS: None - existing fields sufficient)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patientId` | string | ❌ | Patient identifier |
| `name` | string | ❌ | Patient name |
| `age` | number | ✅ | Age in years |
| `gravida` | number | ❌ | Number of pregnancies |
| `para` | number | ❌ | Number of deliveries |
| `livingChildren` | number | ❌ | Number of living children |
| `gestationalWeeks` | number | ❌ | Gestational age in weeks |
| `lmpDate` | string | ❌ | Last menstrual period (ISO 8601) |
| `estimatedDueDate` | string | ❌ | Estimated due date (ISO 8601) |

#### medical_history (🆕 V2 ENHANCED)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `previousLSCS` | boolean | ❌ | Previous cesarean section |
| `badObstetricHistory` | boolean | ❌ | Bad obstetric history |
| `previousStillbirth` | boolean | ❌ | 🆕 Previous stillbirth |
| `previousPretermDelivery` | boolean | ❌ | 🆕 Previous preterm delivery |
| `previousAbortion` | boolean | ❌ | 🆕 Previous abortion |
| `systemicIllness` | string | ❌ | 🆕 Current or past systemic illness |
| `chronicHypertension` | boolean | ❌ | Chronic hypertension |
| `diabetes` | boolean | ❌ | Diabetes |
| `thyroidDisorder` | boolean | ❌ | Thyroid disorder |
| `smoking` | boolean | ❌ | 🆕 Current smoker |
| `tobaccoUse` | boolean | ❌ | 🆕 Tobacco use |
| `alcoholUse` | boolean | ❌ | 🆕 Alcohol consumption |

#### vitals (🆕 V2 ENHANCED)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `weightKg` | number | ❌ | Weight in kg |
| `heightCm` | number | ❌ | 🆕 Height in cm (threshold: <140) |
| `bmi` | number | ❌ | 🆕 BMI in kg/m² (threshold: ≥30) |
| `bpSystolic` | number | ✅ | Systolic BP in mmHg |
| `bpDiastolic` | number | ✅ | Diastolic BP in mmHg |
| `pulseRate` | number | ❌ | Pulse rate per minute |
| `respiratoryRate` | number | ❌ | Respiratory rate per minute |
| `temperatureCelsius` | number | ❌ | Temperature in Celsius |
| `pallor` | boolean | ❌ | Pallor present |
| `pedalEdema` | boolean | ❌ | Pedal edema present |

#### lab_reports (🆕 V2 ENHANCED)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hemoglobin` | number | ✅ | Hemoglobin in g/dL |
| `plateletCount` | number | ❌ | Platelet count |
| `bloodGroup` | string | ❌ | Blood group (A+, B+, AB+, O+, A-, B-, AB-, O-) |
| `rhNegative` | boolean | ❌ | 🆕 Rh negative blood group |
| `urineProtein` | boolean | ❌ | Urine protein positive |
| `urineSugar` | boolean | ❌ | Urine sugar positive |
| `fastingBloodSugar` | number | ❌ | FBS in mg/dL |
| `hivPositive` | boolean | ❌ | 🆕 HIV positive status |
| `syphilisPositive` | boolean | ❌ | 🆕 Syphilis positive status |
| `serumCreatinine` | number | ❌ | Serum creatinine |
| `ast` | number | ❌ | AST level |
| `alt` | number | ❌ | ALT level |

#### pregnancy_details (🆕 V2 ENHANCED)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `twinPregnancy` | boolean | ❌ | Twin/multiple pregnancy |
| `malpresentation` | boolean | ❌ | 🆕 Abnormal fetal presentation |
| `placentaPrevia` | boolean | ❌ | Placenta previa |
| `reducedFetalMovement` | boolean | ❌ | Reduced fetal movement |
| `amnioticFluidNormal` | boolean | ❌ | Amniotic fluid normal |
| `umbilicalDopplerAbnormal` | boolean | ❌ | Umbilical Doppler abnormal |

#### obstetric_history (🆕 NEW SECTION)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `birthOrder` | number | ❌ | 🆕 Birth order/parity (threshold: ≥5) |
| `interPregnancyInterval` | number | ❌ | 🆕 Months between pregnancies (threshold: <18 or >59) |
| `stillbirthCount` | number | ❌ | 🆕 Number of previous stillbirths |
| `abortionCount` | number | ❌ | 🆕 Number of previous abortions |
| `pretermHistory` | boolean | ❌ | 🆕 History of preterm delivery |

---

## 📤 OUTPUT FORMAT (V2)

### Success Response with V2 Fields

```json
{
  "success": true,
  "query": "28-year-old at 20 weeks, height 135 cm, BMI 32, smoker, Hb 10.5, birth order 6",
  "answer": "[Full clinical response with V2 conditions...]",
  "blocked": false,
  "care_level": "PHC",
  "confidence": {
    "score": 0.85,
    "level": "HIGH",
    "breakdown": {
      "retrieval_quality": 0.90,
      "rule_coverage": 1.0,
      "chunk_agreement": 0.80,
      "extractor_confidence": 0.95
    }
  },
  "features": {
    "age": 28,
    "gestational_age_weeks": 20,
    "systolic_bp": 110,
    "diastolic_bp": 70,
    "hemoglobin": 10.5,
    "fbs": null,
    "height": 135,
    "bmi": 32,
    "smoking": true,
    "tobacco_use": false,
    "alcohol_use": false,
    "birth_order": 6,
    "inter_pregnancy_interval": 10,
    "stillbirth_count": 0,
    "abortion_count": 0,
    "preterm_history": false,
    "rh_negative": false,
    "hiv_positive": false,
    "syphilis_positive": false,
    "twin_pregnancy": false,
    "prior_cesarean": false,
    "placenta_previa": false,
    "malpresentation": false,
    "systemic_illness": false,
    "comorbidities": [],
    "extraction_confidence": 0.95,
    "missing_fields": []
  },
  "rule_output": {
    "overall_risk": "HIGH",
    "total_score": 8,
    "rule_coverage": 1.0,
    "is_hpr": true,
    "triggered_rules": [
      "mild_anaemia",
      "gdm_screening_pending",
      "short_stature",
      "high_bmi",
      "smoking",
      "high_birth_order",
      "short_birth_spacing"
    ],
    "risk_flags": [
      {
        "condition": "Mild Anaemia",
        "present": true,
        "severity": "minor",
        "value": "Hb 10.5 g/dL",
        "threshold": "< 11 g/dL",
        "score": 1
      },
      {
        "condition": "GDM First Screening Pending",
        "present": true,
        "severity": "minor",
        "value": "GA 20 weeks, no OGTT done",
        "threshold": "OGTT required at 14-28 weeks",
        "score": 1
      },
      {
        "condition": "Short Stature",
        "present": true,
        "severity": "moderate",
        "value": "135 cm",
        "threshold": "< 140 cm",
        "score": 2
      },
      {
        "condition": "High BMI",
        "present": true,
        "severity": "moderate",
        "value": "32 kg/m²",
        "threshold": ">= 30 kg/m²",
        "score": 2
      },
      {
        "condition": "Smoking",
        "present": true,
        "severity": "moderate",
        "value": "Current smoker",
        "score": 2
      },
      {
        "condition": "High Birth Order",
        "present": true,
        "severity": "moderate",
        "value": "Birth order 6",
        "threshold": ">= 5",
        "score": 2
      },
      {
        "condition": "Short Birth Spacing",
        "present": true,
        "severity": "moderate",
        "value": "10 months",
        "threshold": "< 18 months",
        "score": 2
      }
    ],
    "borderline_flags": [
      {
        "condition": "Borderline Anaemia",
        "value": "Hb 10.5 g/dL",
        "action": "IFA twice daily, monitor monthly",
        "severity": "watch"
      }
    ],
    "confirmed_conditions": [
      "mild_anaemia",
      "short_stature",
      "high_bmi",
      "smoking",
      "high_birth_order",
      "short_birth_spacing"
    ],
    "suspected_conditions": [
      "gdm_screening_pending"
    ],
    "referral_facility": "CHC/PHC",
    "immediate_referral": false,
    "diagnosis_notes": [
      "GDM First Screening Pending - 75g OGTT required (14-28 weeks)"
    ]
  },
  "retrieval_stats": {
    "rewritten_query": "Short stature pregnancy risk height 135 cm High BMI obesity pregnancy BMI 32 Smoking tobacco pregnancy complications High birth order grand multipara Birth spacing short interval Mild anaemia Hb 10.5 28-year-old at 20 weeks",
    "faiss_count": 30,
    "bm25_count": 10,
    "final_count": 8,
    "retrieval_quality": 0.90,
    "chunk_agreement": 0.80
  },
  "timestamp": "2025-02-21T10:30:45.123Z",
  "processing_time_ms": 8542.35
}
```

### V2 Output Fields Explained

#### New Features Object Fields (🆕 V2)
| Field | Type | Description |
|-------|------|-------------|
| `height` | number/null | 🆕 Height in cm |
| `bmi` | number/null | 🆕 BMI in kg/m² |
| `smoking` | boolean | 🆕 Current smoker |
| `tobacco_use` | boolean | 🆕 Tobacco use |
| `alcohol_use` | boolean | 🆕 Alcohol consumption |
| `birth_order` | number/null | 🆕 Birth order/parity |
| `inter_pregnancy_interval` | number/null | 🆕 Months between pregnancies |
| `stillbirth_count` | number | 🆕 Number of previous stillbirths |
| `abortion_count` | number | 🆕 Number of previous abortions |
| `preterm_history` | boolean | 🆕 History of preterm delivery |
| `rh_negative` | boolean | 🆕 Rh negative blood group |
| `hiv_positive` | boolean | 🆕 HIV positive status |
| `syphilis_positive` | boolean | 🆕 Syphilis positive status |
| `malpresentation` | boolean | 🆕 Abnormal fetal presentation |
| `systemic_illness` | boolean | 🆕 Current or past systemic illness |

#### New Rule Output Fields (🆕 V2)
| Field | Type | Description |
|-------|------|-------------|
| `is_hpr` | boolean | 🆕 Composite HPR flag (Section 19 logic) |
| `borderline_flags` | array | 🆕 Borderline values needing monitoring |
| `confirmed_conditions` | array | 🆕 Lab-confirmed conditions |
| `suspected_conditions` | array | 🆕 Conditions needing confirmatory tests |
| `referral_facility` | string | 🆕 Recommended facility level |
| `immediate_referral` | boolean | 🆕 Urgent referral needed |
| `diagnosis_notes` | array | 🆕 Clinical notes |

#### Borderline Flag Object (🆕 V2)
| Field | Type | Description |
|-------|------|-------------|
| `condition` | string | Borderline condition name |
| `value` | string | Actual value |
| `action` | string | Recommended monitoring action |
| `severity` | string | Always "watch" |

---

## 🆕 V2 TRIGGERED RULES

### New V2 Conditions in triggered_rules Array

| Rule Name | Threshold | Score | Severity |
|-----------|-----------|-------|----------|
| `short_stature` | Height <140 cm | 2 | moderate |
| `high_bmi` | BMI ≥30 kg/m² | 2 | moderate |
| `smoking` | Current smoker | 2 | moderate |
| `tobacco_use` | Tobacco use | 2 | moderate |
| `alcohol_use` | Alcohol consumption | 2 | moderate |
| `high_birth_order` | Birth order ≥5 | 2 | moderate |
| `short_birth_spacing` | Interval <18 months | 2 | moderate |
| `long_birth_spacing` | Interval >59 months | 1 | minor |
| `previous_preterm` | History of preterm | 2 | moderate |
| `previous_stillbirth` | History of stillbirth | 2 | moderate |
| `previous_abortion` | History of abortion | 2 | moderate |
| `rh_negative` | Rh negative | 1 | minor |
| `hiv_positive` | HIV positive | 3 | major |
| `syphilis_positive` | Syphilis positive | 3 | major |
| `malpresentation` | Abnormal presentation | 2 | moderate |
| `systemic_illness` | Systemic illness | 2 | moderate |

---

## 📊 V2 SAMPLE RESPONSES

### V2 High Risk Case
```json
{
  "rule_output": {
    "overall_risk": "HIGH",
    "total_score": 8,
    "is_hpr": true,
    "triggered_rules": [
      "short_stature",
      "high_bmi",
      "smoking",
      "high_birth_order",
      "short_birth_spacing",
      "mild_anaemia"
    ],
    "borderline_flags": [
      {
        "condition": "Borderline Anaemia",
        "value": "Hb 10.5 g/dL",
        "action": "IFA twice daily, monitor monthly",
        "severity": "watch"
      }
    ]
  }
}
```

### V2 Critical Risk Case
```json
{
  "rule_output": {
    "overall_risk": "CRITICAL",
    "total_score": 15,
    "is_hpr": true,
    "triggered_rules": [
      "severe_anaemia",
      "hypertension",
      "advanced_maternal_age",
      "twin_pregnancy",
      "hiv_positive",
      "previous_stillbirth",
      "short_stature"
    ],
    "immediate_referral": true,
    "referral_facility": "CEmOC/District Hospital"
  }
}
```

---

## 💡 V2 MIGRATION GUIDE

### For Existing Integrations

**No Breaking Changes:**
- All V1 fields remain unchanged
- New V2 fields are optional
- Existing queries work without modification
- V2 fields are ignored if not provided

**To Use V2 Features:**
1. Add new fields to your input JSON
2. Check `is_hpr` flag in output
3. Monitor `borderline_flags` array
4. Use new `triggered_rules` for V2 conditions

**Backward Compatibility:**
```json
// V1 query (still works)
{
  "query": "38-year-old with BP 150/95, Hb 10.5"
}

// V2 query (enhanced)
{
  "query": "38-year-old with BP 150/95, Hb 10.5, height 135 cm, smoker"
}
```

---

**API Version:** 2.0.0  
**Last Updated:** 2025-02-21  
**Backward Compatible:** Yes (with V1)
