# V2 Input/Output JSON Summary

## Quick Reference: What Changed in V2

### 📥 INPUT: 16 New Optional Fields

#### Anthropometric (2 fields)
```json
{
  "height": 135,        // cm (threshold: <140)
  "bmi": 32.0          // kg/m² (threshold: ≥30)
}
```

#### Lifestyle (3 fields)
```json
{
  "smoking": true,      // Current smoker
  "tobacco_use": false, // Tobacco use
  "alcohol_use": false  // Alcohol consumption
}
```

#### Obstetric History (5 fields)
```json
{
  "birth_order": 6,                    // Parity (threshold: ≥5)
  "inter_pregnancy_interval": 10,      // Months (threshold: <18 or >59)
  "stillbirth_count": 1,               // Number of stillbirths
  "abortion_count": 2,                 // Number of abortions
  "preterm_history": true              // History of preterm delivery
}
```

#### Serology (3 fields)
```json
{
  "rh_negative": false,      // Rh negative blood group
  "hiv_positive": false,     // HIV positive status
  "syphilis_positive": false // Syphilis positive status
}
```

#### Pregnancy Complications (2 fields)
```json
{
  "malpresentation": false,   // Abnormal fetal presentation
  "systemic_illness": false   // Current or past systemic illness
}
```

---

### 📤 OUTPUT: 3 New Fields + Enhanced Data

#### 1. Composite HPR Flag (NEW)
```json
{
  "rule_output": {
    "is_hpr": true  // 🆕 Boolean flag based on Section 19 logic
  }
}
```

#### 2. Borderline Monitoring (NEW)
```json
{
  "rule_output": {
    "borderline_flags": [  // 🆕 Values approaching thresholds
      {
        "condition": "Borderline Anaemia",
        "value": "Hb 10.5 g/dL",
        "action": "IFA twice daily, monitor monthly",
        "severity": "watch"
      },
      {
        "condition": "Pre-Hypertension",
        "value": "BP 135/87 mmHg",
        "action": "Monitor BP at each visit",
        "severity": "watch"
      }
    ]
  }
}
```

#### 3. Enhanced Rule Output (NEW)
```json
{
  "rule_output": {
    "confirmed_conditions": [      // 🆕 Lab-confirmed conditions
      "severe_anaemia",
      "gdm_confirmed"
    ],
    "suspected_conditions": [      // 🆕 Needs confirmatory tests
      "pre_eclampsia",
      "gdm_screening_pending"
    ],
    "referral_facility": "CEmOC/District Hospital",  // 🆕 Recommended facility
    "immediate_referral": true,    // 🆕 Urgent referral flag
    "diagnosis_notes": [           // 🆕 Clinical notes
      "GDM First Screening Pending - 75g OGTT required (14-28 weeks)"
    ]
  }
}
```

#### 4. 16 New Triggered Rules
```json
{
  "rule_output": {
    "triggered_rules": [
      // V1 rules (unchanged)
      "mild_anaemia",
      "hypertension",
      "gdm_confirmed",
      "young_primi",
      "advanced_maternal_age",
      "twin_pregnancy",
      "previous_cs",
      "placenta_previa",
      
      // 🆕 V2 NEW RULES
      "short_stature",           // Height <140 cm
      "high_bmi",                // BMI ≥30
      "smoking",                 // Current smoker
      "tobacco_use",             // Tobacco use
      "alcohol_use",             // Alcohol consumption
      "high_birth_order",        // Birth order ≥5
      "short_birth_spacing",     // <18 months
      "long_birth_spacing",      // >59 months
      "previous_preterm",        // Preterm history
      "previous_stillbirth",     // Stillbirth history
      "previous_abortion",       // Abortion history
      "rh_negative",             // Rh negative
      "hiv_positive",            // HIV positive
      "syphilis_positive",       // Syphilis positive
      "malpresentation",         // Abnormal presentation
      "systemic_illness"         // Systemic illness
    ]
  }
}
```

---

## 📊 Complete V2 Example

### Input (Text Query)
```json
{
  "query": "28-year-old woman at 20 weeks, height 135 cm, BMI 32, smoker, Hb 10.5, BP 110/70, birth order 6, previous pregnancy 10 months ago, history of stillbirth",
  "care_level": "PHC"
}
```

### Output (Simplified)
```json
{
  "success": true,
  "blocked": false,
  "rule_output": {
    "overall_risk": "HIGH",
    "total_score": 10,
    "is_hpr": true,
    "triggered_rules": [
      "mild_anaemia",
      "short_stature",
      "high_bmi",
      "smoking",
      "high_birth_order",
      "short_birth_spacing",
      "previous_stillbirth"
    ],
    "borderline_flags": [
      {
        "condition": "Borderline Anaemia",
        "value": "Hb 10.5 g/dL",
        "action": "IFA twice daily, monitor monthly"
      }
    ],
    "confirmed_conditions": [
      "mild_anaemia",
      "short_stature",
      "high_bmi",
      "smoking",
      "high_birth_order",
      "short_birth_spacing",
      "previous_stillbirth"
    ],
    "suspected_conditions": [
      "gdm_screening_pending"
    ],
    "referral_facility": "CHC/PHC",
    "immediate_referral": false
  },
  "features": {
    "age": 28,
    "gestational_age_weeks": 20,
    "hemoglobin": 10.5,
    "systolic_bp": 110,
    "diastolic_bp": 70,
    "height": 135,
    "bmi": 32,
    "smoking": true,
    "birth_order": 6,
    "inter_pregnancy_interval": 10,
    "stillbirth_count": 1
  },
  "confidence": {
    "score": 0.85,
    "level": "HIGH"
  }
}
```

---

## 🔄 Backward Compatibility

### V1 Queries Still Work
```json
// V1 query (no changes needed)
{
  "query": "38-year-old with BP 150/95, Hb 10.5"
}

// Returns V2 output with new fields (but V2 rules not triggered)
{
  "rule_output": {
    "is_hpr": true,              // New field
    "borderline_flags": [],      // New field (empty if none)
    "triggered_rules": [
      "advanced_maternal_age",
      "hypertension",
      "mild_anaemia"
    ]
  }
}
```

### V2 Fields Are Optional
```json
// Partial V2 query (only some new fields)
{
  "query": "28-year-old with Hb 10.5, height 135 cm"
}

// Only height-related V2 rule triggered
{
  "rule_output": {
    "triggered_rules": [
      "mild_anaemia",
      "short_stature"  // V2 rule
    ]
  }
}
```

---

## 📈 Risk Score Changes

### V1 vs V2 Scoring

**V1 Maximum Score:** ~15 points (8 conditions)
**V2 Maximum Score:** ~40+ points (33 conditions)

**Risk Levels (unchanged):**
- LOW: 0-2 points
- MODERATE: 3-5 points
- HIGH: 6-8 points
- CRITICAL: 9+ points

**Example: Same Patient, V1 vs V2**

```
Patient: 28-year-old, Hb 10.5, height 135 cm, smoker, birth order 6

V1 Score: 1 (mild_anaemia only)
V1 Risk: LOW

V2 Score: 9 (mild_anaemia + short_stature + high_bmi + smoking + high_birth_order + short_birth_spacing)
V2 Risk: CRITICAL
V2 is_hpr: true
```

---

## 🎯 Key Takeaways

1. **No Breaking Changes** - All V1 queries work unchanged
2. **16 New Conditions** - More comprehensive risk detection
3. **3 New Output Fields** - is_hpr, borderline_flags, enhanced rule_output
4. **Backward Compatible** - V2 fields optional, ignored if not provided
5. **More Accurate** - Detects risks missed by V1

---

## 📚 Full Documentation

- **V1 Format:** See `API_JSON_FORMATS.md`
- **V2 Format:** See `API_JSON_FORMATS_V2.md`
- **V2 Implementation:** See `V2_IMPLEMENTATION_COMPLETE.md`
- **Thresholds:** See `COMPLETE_HPR_THRESHOLDS.md`

---

**Version:** 2.0.0  
**Date:** 2025-02-21  
**Status:** ✅ System Prompt Updated, Extractor & API Pending
