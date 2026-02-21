# Clinical Thresholds — GoI High-Risk Pregnancy Guidelines
# Source: High-Risk-Conditions-in-preg-modified-Final.pdf
# Purpose: Rule-based pre-RAG threshold engine for Medical RAG Pipeline
# Implement ALL values below as hard-coded constants BEFORE retrieval

---

## HOW TO USE THIS FILE

These thresholds must be implemented as a **rule engine** that runs BEFORE
the RAG retrieval step. The pipeline flow must be:

```
Input → Rule Engine (this file) → Confirmed Conditions → Chunk Gate → RAG → Output
```

Never let the LLM guess these thresholds. They are exact values from the document.

---

## 1. ANAEMIA (Page 4)

### Definition
```
ANAEMIA_DEFINITION_THRESHOLD = 11.0  # Hb < 11 g/dL in pregnancy or postpartum
```

### Classification Thresholds
```python
ANAEMIA_THRESHOLDS = {
    "normal":   {"hb_min": 11.0, "hb_max": None,  "label": "No Anaemia",      "score": 0},
    "mild":     {"hb_min": 10.0, "hb_max": 10.9,  "label": "Mild Anaemia",    "score": 1},
    "moderate": {"hb_min": 7.0,  "hb_max": 9.9,   "label": "Moderate Anaemia","score": 2},
    "severe":   {"hb_min": None, "hb_max": 7.0,   "label": "Severe Anaemia",  "score": 4},
}
```

### Clinical Action Thresholds
| Hb Level | Action Required |
|----------|----------------|
| ≥11 g/dL | Normal — routine care |
| 10–10.9 g/dL | Mild — IFA twice daily, investigate type |
| 7–9.9 g/dL | Moderate — IFA twice daily + consider parenteral iron |
| 7–8 g/dL | IM iron therapy if no obstetric/systemic complication |
| < 7 g/dL | SEVERE — refer to FRU, likely blood transfusion |
| < 7 g/dL at term | MUST deliver at FRU with blood transfusion services |

### Drug Thresholds
```python
ANAEMIA_DRUGS = {
    "mild_moderate": {
        "drug": "IFA tablet",
        "dose": "100mg elemental iron + 0.5mg folic acid",
        "frequency": "twice daily",
        "monitor": "Hb monthly"
    },
    "prophylaxis": {
        "drug": "IFA tablet",
        "dose": "100mg elemental iron + 0.5mg folic acid",
        "frequency": "once daily for 180 days (6 months)",
        "start": "after first trimester"
    },
    "antihelminthic": {
        "indication": "moderate or severe anaemia in 2nd/3rd trimester",
        "options": [
            "Tab Mebendazole 100mg BD for 3 days",
            "Tab Albendazole 400mg single dose"
        ]
    },
    "parenteral_iron": {
        "indication": "intolerance/non-compliance to oral iron, moderate-severe in late pregnancy",
        "hb_range": "7–8 g/dL without complications"
    }
}
```

### High-Risk Flag
```python
ANAEMIA_HIGH_RISK_FLAG = 7.0   # Hb < 7 is HIGH RISK — triggers severe_anaemia rule
ANAEMIA_REFERRAL_THRESHOLD = 7.0  # Refer to FRU
```

---

## 2. HYPERTENSIVE DISORDERS (Page 3)

### Base Definition
```python
HYPERTENSION_SYSTOLIC_THRESHOLD = 140   # systolic >= 140 mmHg
HYPERTENSION_DIASTOLIC_THRESHOLD = 90   # diastolic >= 90 mmHg
# Required: TWO consecutive readings
```

### Classification Thresholds
```python
HYPERTENSION_TYPES = {
    "chronic_hypertension": {
        "definition": "BP ≥140/90 before 20 weeks gestation",
        "gestational_age_weeks_max": 20,
        "bp_systolic_min": 140,
        "bp_diastolic_min": 90,
    },
    "pregnancy_induced_hypertension": {
        "definition": "BP ≥140/90 after 20 weeks, no proteinuria",
        "gestational_age_weeks_min": 20,
        "bp_systolic_min": 140,
        "bp_diastolic_min": 90,
        "proteinuria_required": False,
    },
    "pre_eclampsia": {
        "bp_systolic_min": 140,
        "bp_systolic_max": 159,
        "bp_diastolic_min": 90,
        "bp_diastolic_max": 109,
        "readings_gap_hours": "4–6 hrs apart",
        "proteinuria_options": [">3 gm/dL in 24hr specimen", "trace", "1+", "2+"],
        "symptoms": ["headache", "blurring of vision", "epigastric pain", "oliguria", "oedema"],
    },
    "severe_pre_eclampsia": {
        "bp_systolic_min": 160,
        "bp_diastolic_min": 110,
        "proteinuria_min": "3+",  # 3+ or 4+
    },
    "eclampsia": {
        "definition": "generalized convulsions with pre-eclampsia background",
        "bp_systolic_min": 140,
        "bp_diastolic_min": 90,
        "proteinuria": "more than trace",
        "seizures": True,
        "onset": "during pregnancy, labour, or within 7 days of delivery",
        "note": "can occur in normotensive women"
    }
}
```

### Treatment Initiation Threshold
```python
ANTIHYPERTENSIVE_INITIATION_DBP = 90   # Start antihypertensives at DBP 90-100 mmHg (OPD)
ANTIHYPERTENSIVE_INITIATION_DBP_MAX = 100
```

### Drug Thresholds
```python
HYPERTENSION_DRUGS = [
    {
        "line": 1,
        "drug": "Tab Alpha Methyl Dopa",
        "dose": "250mg",
        "frequency": "twice or thrice daily",
        "max_dose": "2g/day"
    },
    {
        "line": 2,
        "drug": "Nifedipine",
        "dose": "10–20mg",
        "route": "orally",
        "frequency": "BD/TDS"
    },
    {
        "line": 3,
        "drug": "Lobetalol",  # Note: spelled Lobetalol in document (Labetalol)
        "dose": "100mg",
        "frequency": "twice daily"
    },
    {
        "indication": "pre-eclampsia setting",
        "drug": "MgSO4",
        "route": "IM",
        "type": "prophylactic"
    }
]

CALCIUM_PREVENTION = {
    "drug": "Calcium",
    "dose": "1g/day",
    "start": "after 1st trimester",
    "benefit": "reduces Pre-eclampsia risk by 50%"
}
```

### Danger Signs (Trigger Immediate Referral)
```python
HYPERTENSION_DANGER_SIGNS = [
    "headache",
    "blurring of vision",
    "epigastric pain",
    "oliguria",
    "increasing edema",
    "rising BP",
    "bleeding PV",
    "absent or decreased fetal movements"
]
```

### Delivery Planning
```python
HYPERTENSION_DELIVERY = {
    "facility": "CEmOC center",
    "note": "Prolonged induction to be avoided",
    "iugr_rule_out_by_weeks": 34
}
```

---

## 3. GESTATIONAL DIABETES MELLITUS — GDM (Pages 8–10)

### Diagnostic Test
```python
GDM_TEST = {
    "test_type": "75g oral glucose — 2hr Plasma Glucose value",
    "positive_threshold_2hr_pg": 140,  # 2hr PG >= 140 mg/dL = POSITIVE
    "negative_threshold_2hr_pg": 140,  # 2hr PG < 140 mg/dL = NEGATIVE
}
```

### Testing Protocol Thresholds
```python
GDM_TESTING_PROTOCOL = {
    "first_test": "at first antenatal contact, as early as possible",
    "second_test": "at 24–28 weeks if first test negative",
    "min_gap_between_tests_weeks": 4,
    "late_presenter": "beyond 28 weeks → only one test at first contact",
    "test_for_all": True  # All PW regardless of timing
}
```

### Management Thresholds
```python
GDM_MANAGEMENT_THRESHOLDS = {
    "mnt_only": {
        "pppg_threshold": 120,    # 2hr PPPG < 120 mg/dL after 2 weeks MNT
        "action": "Continue MNT",
        "monitor_frequency_before_28wks": "once every 2 weeks",
        "monitor_frequency_after_28wks": "once weekly"
    },
    "insulin_therapy": {
        "pppg_threshold": 120,    # 2hr PPPG >= 120 mg/dL after 2 weeks MNT
        "action": "Start Insulin Therapy",
        "monitor": "FBG and 2hr PPPG every 3rd day (or more frequently)",
        "monitor_until": "insulin dose adjusted to maintain normal plasma glucose",
        "ongoing_monitor": "2hr PPPG once weekly"
    },
    "mnt_start": "Medical Nutrition Therapy for ALL GDM patients first",
    "review_period_weeks": 2   # Review after 2 weeks of MNT
}
```

### Special Obstetric Care Thresholds (Page 10)
```python
GDM_SPECIAL_CARE = {
    "fetal_anatomy_scan": {
        "indication": "diagnosed before 20 weeks",
        "timing_weeks": "18–20"
    },
    "fetal_growth_scan_1": {
        "timing_weeks": "28–30"
    },
    "fetal_growth_scan_2": {
        "timing_weeks": "34–36",
        "min_gap_between_scans_weeks": 3
    },
    "anc_visit_frequency_uncontrolled": {
        "second_trimester": "every 2 weeks",
        "third_trimester": "every week"
    },
    "antenatal_steroids_gdm": {
        "indication": "GDM confirmed + gestational age 24–34 weeks + early delivery required",
        "drug": "Inj. Dexamethasone",
        "dose": "6mg IM",
        "frequency": "12 hourly for 2 days",
        "post_steroid_glucose_monitor_hours": 72,
        "post_steroid_action": "Adjust insulin dose if blood glucose raised"
    },
    "fetal_kick_count": {
        "threshold_kicks": 10,
        "time_window_hours": 2,
        "action_if_fail": "Consult healthcare worker immediately, refer if needed"
    }
}
```

---

## 4. HYPOTHYROIDISM (Page 7)

### TSH Reference Ranges (Pregnancy-Specific)
```python
TSH_NORMAL_RANGES = {
    "trimester_1": {"min": 0.1, "max": 2.5, "unit": "mIU/L"},
    "trimester_2": {"min": 0.2, "max": 3.0, "unit": "mIU/L"},
    "trimester_3": {"min": 0.3, "max": 3.0, "unit": "mIU/L"},
}
```

### Diagnostic Thresholds
```python
HYPOTHYROID_DIAGNOSIS = {
    "subclinical_hypothyroidism_SCH": {
        "tsh_min": 2.5,
        "tsh_max": 10.0,
        "ft4": "normal",
        "label": "SCH — Sub-Clinical Hypothyroidism"
    },
    "overt_hypothyroidism_OH": {
        "definition_1": {"tsh_min": 2.5, "ft4": "low"},
        "definition_2": {"tsh_min": 10.0, "ft4": "any"},  # TSH>10 regardless of FT4
        "label": "OH — Overt Hypothyroidism"
    }
}
```

### Treatment Thresholds
```python
HYPOTHYROID_TREATMENT = {
    "no_treatment": {
        "tsh_t1": {"max": 2.5},
        "tsh_t2_t3": {"max": 3.0},
        "action": "Routine pregnancy care, no medication"
    },
    "low_dose": {
        "tsh_range": {"min": 2.5, "max": 10.0},
        "drug": "Levothyroxine Sodium",
        "dose_mcg": 25,
        "frequency": "once daily, empty stomach in morning"
    },
    "high_dose": {
        "tsh_min": 10.0,
        "drug": "Levothyroxine Sodium",
        "dose_mcg": 50,
        "frequency": "once daily, empty stomach in morning"
    },
    "follow_up": {
        "repeat_tsh_after_weeks": 6
    }
}
```

### Screening Criteria (High-Risk Factors)
```python
HYPOTHYROID_SCREEN_IF = [
    "residing in moderate-severe iodine deficient area",
    "obesity",
    "history of prior thyroid dysfunction or goiter",
    "history of mental retardation in family or previous birth",
    "history of recurrent miscarriage / stillbirth / preterm delivery / IUD / abruptio placentae",
    "history of infertility"
]
```

### Delivery
```python
HYPOTHYROID_DELIVERY = {
    "uncomplicated": "PHC/CHC by Medical Officer",
    "with_complication": "under Obstetrician supervision"
}
```

---

## 5. AGE-RELATED RISK (Page 2)

```python
AGE_RISK_THRESHOLDS = {
    "adolescent_young_primi": {
        "age_max": 20,           # < 20 years
        "label": "Young Primi",
        "risk": "HIGH",
        "score": 3
    },
    "normal_age": {
        "age_min": 20,
        "age_max": 35,
        "label": "Normal Maternal Age",
        "risk": "LOW",
        "score": 0
    },
    "advanced_maternal_age": {
        "age_min": 35,           # > 35 years
        "label": "Elderly Gravida",
        "risk": "HIGH",
        "score": 3
    }
}
```

---

## 6. IUGR — INTRAUTERINE GROWTH RETARDATION (Page 12)

### Diagnostic Thresholds
```python
IUGR_THRESHOLDS = {
    "sfh_threshold": {
        "definition": "Fundal height less than 3cm below gestational age in weeks",
        "formula": "SFH_cm < (gestational_age_weeks - 3)",
        "valid_after_weeks": 20,
        "normal_range": "gestational_age_weeks ± 2 cm"
    },
    "weight_gain": {
        "threshold_grams_per_week": 500,
        "flag_if_below": True   # < 500g/week flags IUGR concern
    },
    "birth_weight_percentile": {
        "threshold": 10,         # Below 10th percentile for gestational age
    }
}
```

### Antenatal Steroid Threshold
```python
IUGR_STEROIDS = {
    "indication": "IUGR with anticipated early delivery",
    "gestational_age_weeks_min": 24,
    "gestational_age_weeks_max": 34,
    "regimen": "One course between 24 and 34 weeks",
    "source_page": 12,           # IMPORTANT: Page 12 (IUGR), NOT Page 10 (GDM)
}
```

### Monitoring
```python
IUGR_MONITORING = [
    "Daily fetal movement count",
    "Serial SFH and abdominal girth measurement",
    "NST (Non-Stress Test) where possible",
    "BPP (Biophysical Profile) where possible"
]
```

### Delivery
```python
IUGR_DELIVERY = {
    "facility": "centres with antenatal and intrapartum fetal monitoring + NICU",
    "timing": "determined by gestational age, IUGR severity, fetal condition"
}
```

---

## 7. TWINS / MULTIPLE PREGNANCY (Page 5)

```python
TWIN_PREGNANCY = {
    "diagnosis_trigger": "Fundal height > Period of Gestation (POG)",
    "diagnosis_confirm": "USG",
    "referral_weeks": 36,        # Refer to FRU at 36 weeks
    "facility": "FRU",
    "risk_score": 3,
    "anc_frequency": "more frequent than standard",
    "supplementation": "increased calories, protein, iron"
}
```

---

## 8. PLACENTA PREVIA (Page 5)

```python
PLACENTA_PREVIA = {
    "diagnosis": "painless PV bleeding + USG confirmation",
    "management_anc_continue_till_weeks": 37,
    "terminate_if": ["labour begins", "heavy bleeding"],
    "pv_exam": False,            # NO PV examination
    "facility": "FRU/CEmOC",
    "warning": "Warning bleeding to be taken seriously",
    "risk_score": 4
}
```

---

## 9. PREVIOUS CAESAREAN SECTION (Page 11)

```python
PREVIOUS_CS = {
    "danger_sign": "Scar tenderness",
    "delivery_facility": "CEmOC facility with blood transfusion",
    "risk_score": 2
}
```

---

## 10. SYPHILIS (Page 6)

### Screening
```python
SYPHILIS_SCREENING = {
    "universal": True,           # All pregnant women
    "first_test": "first ANC visit using POC test or RPR",
    "repeat_test": "3rd trimester if high-risk or adverse outcome history"
}

SYPHILIS_HIGH_RISK_FACTORS = [
    "current or past history of STI",
    "more than one sexual partner",
    "sex worker",
    "injecting drug user"
]
```

### Treatment Thresholds
```python
SYPHILIS_TREATMENT = {
    "early_stage": {
        "definition": "primary/secondary syphilis < 2 years, RPR titer < 1:8",
        "drug": "Benzathine Benzyl Penicillin",
        "dose": "2.4 million IU IM",
        "frequency": "single dose"
    },
    "late_stage": {
        "definition": "tertiary > 2 years or unknown, RPR titer > 1:8",
        "drug": "Benzathine Benzyl Penicillin",
        "dose": "2.4 million IU IM",
        "frequency": "once weekly for 3 weeks (3 doses total)"
    },
    "penicillin_allergic_early": {
        "drug": "Erythromycin",
        "dose": "500mg orally 4 times daily for 15 days"
    },
    "penicillin_allergic_late": {
        "drug": "Erythromycin",
        "dose": "500mg orally 4 times daily for 30 days"
    },
    "penicillin_allergic_primary_alternate": {
        "drug": "Azithromycin",
        "dose": "2g orally single dose"
    },
    "delivery_facility": "FRU/EmOC center"
}
```

---

## 11. ANC VISIT SCHEDULE (Page 2)

```python
ANC_MINIMUM_VISITS = 4

ANC_VISIT_SCHEDULE = [
    {"visit": 1, "timing": "Registration, within 12 weeks"},
    {"visit": 2, "timing": "14–26 weeks"},
    {"visit": 3, "timing": "28–32 weeks"},
    {"visit": 4, "timing": "36–40 weeks"},
]
```

---

## 12. UNIVERSAL WARNING SIGNS (Page 2)

```python
WARNING_SIGNS_IMMEDIATE_REFERRAL = [
    {"sign": "fever",           "threshold": ">38.5°C for more than 24 hours"},
    {"sign": "headache",        "threshold": "any"},
    {"sign": "blurring of vision", "threshold": "any"},
    {"sign": "generalized swelling", "threshold": "body + puffiness of face"},
    {"sign": "palpitations",    "threshold": "at rest"},
    {"sign": "breathlessness",  "threshold": "at rest"},
    {"sign": "abdominal pain",  "threshold": "any"},
    {"sign": "vaginal bleeding", "threshold": "any"},
    {"sign": "watery discharge", "threshold": "any"},
    {"sign": "reduced fetal movements", "threshold": "any"},
]

FEVER_THRESHOLD_CELSIUS = 38.5
FEVER_DURATION_HOURS = 24
```

---

## 13. HIGH-RISK CONDITIONS MASTER LIST (Page 2)

```python
HIGH_RISK_CONDITIONS = [
    "severe_anaemia",           # Hb < 7 g/dL
    "pregnancy_induced_hypertension",
    "pre_eclampsia",
    "pre_eclamptic_toxemia",
    "syphilis_positive",
    "hiv_positive",
    "gestational_diabetes_mellitus",
    "hypothyroidism",
    "young_primi",              # < 20 years
    "elderly_gravida",          # > 35 years
    "twin_pregnancy",
    "multiple_pregnancy",
    "malpresentation",
    "previous_lscs",
    "placenta_previa",
    "low_lying_placenta",
    "bad_obstetric_history",    # stillbirth, abortion, congenital malformation, etc.
    "rh_negative",
    "systemic_illness_current_or_past"
]
```

---

## 14. RISK SCORING MATRIX

```python
RISK_SCORE_MATRIX = {
    # Condition: (score, severity, label)
    "severe_anaemia":              (4, "critical", "Hb < 7 g/dL"),
    "moderate_anaemia":            (2, "moderate", "Hb 7–9.9 g/dL"),
    "mild_anaemia":                (1, "minor",    "Hb 10–10.9 g/dL"),
    "severe_pre_eclampsia":        (4, "critical", "BP ≥160/110 + proteinuria 3+/4+"),
    "pre_eclampsia":               (3, "major",    "BP ≥140/90 + proteinuria"),
    "hypertension":                (3, "major",    "BP ≥140/90"),
    "eclampsia":                   (5, "critical", "Seizures + BP ≥140/90"),
    "gdm":                         (2, "moderate", "2hr PG ≥140 mg/dL"),
    "hypothyroid_overt":           (2, "moderate", "TSH >10 or TSH >2.5 with low FT4"),
    "hypothyroid_subclinical":     (1, "minor",    "TSH 2.5–10, normal FT4"),
    "twin_pregnancy":              (3, "major",    "Multiple gestation"),
    "advanced_maternal_age":       (3, "major",    "Age > 35 years"),
    "young_primi":                 (3, "major",    "Age < 20 years"),
    "previous_cs":                 (2, "moderate", "History of LSCS"),
    "placenta_previa":             (4, "critical", "Confirmed or suspected"),
    "iugr_suspected":              (3, "major",    "SFH < GA-3 cm"),
    "bad_obstetric_history":       (2, "moderate", "Stillbirth/abortion/malformation"),
    "rh_negative":                 (1, "minor",    "Rh negative blood group"),
    "syphilis_positive":           (3, "major",    "RPR/POC positive"),
    "hiv_positive":                (3, "major",    "HIV confirmed")
}

RISK_LEVELS = {
    "LOW":      {"score_min": 0,  "score_max": 2},
    "MODERATE": {"score_min": 3,  "score_max": 5},
    "HIGH":     {"score_min": 6,  "score_max": 8},
    "CRITICAL": {"score_min": 9,  "score_max": None}
}
```

---

## 15. ANTENATAL STEROID RULES — CRITICAL GATING TABLE

```python
# THIS TABLE PREVENTS GDM/IUGR STEROID CROSS-CONTAMINATION
ANTENATAL_STEROID_RULES = {
    "iugr_indication": {
        "condition_required": "iugr_suspected",
        "gestational_age_min_weeks": 24,
        "gestational_age_max_weeks": 34,
        "drug": "Betamethasone OR Dexamethasone (one course)",
        "source_page": 12,
        "glucose_monitoring_required": False   # NOT required unless GDM co-exists
    },
    "gdm_early_delivery_indication": {
        "condition_required": "gdm_confirmed",
        "additional_condition": "early delivery required",
        "gestational_age_min_weeks": 24,
        "gestational_age_max_weeks": 34,
        "drug": "Inj. Dexamethasone 6mg IM 12 hourly for 2 days",
        "source_page": 10,
        "glucose_monitoring_required": True,   # MANDATORY for GDM indication
        "glucose_monitor_hours": 72,
        "post_steroid_action": "Adjust insulin if blood glucose raised"
    },
    "gestational_age_alone_NOT_sufficient": True  # GA < 34 wks alone does NOT trigger steroids
}
```

---

## 16. DIAGNOSIS CONFIRMATION REQUIREMENTS

```python
# Use this to enforce "suspected" vs "confirmed" language
DIAGNOSIS_CONFIRMATION_REQUIRED = {
    "pre_eclampsia": {
        "required_criteria": ["bp_elevated", "proteinuria_result"],
        "confirmatory_test": "urine dipstick or 24hr urine protein",
        "if_test_unavailable": "SUSPECTED pre-eclampsia — confirm at referral"
    },
    "severe_pre_eclampsia": {
        "required_criteria": ["bp_gte_160_110", "proteinuria_3plus"],
        "confirmatory_test": "urine dipstick",
        "if_test_unavailable": "SUSPECTED severe pre-eclampsia"
    },
    "gdm": {
        "required_criteria": ["ogtt_2hr_pg_gte_140"],
        "confirmatory_test": "75g OGTT — 2hr plasma glucose",
        "if_test_unavailable": "GDM CANNOT be confirmed without OGTT"
    },
    "hypothyroid": {
        "required_criteria": ["tsh_result"],
        "confirmatory_test": "TSH level",
        "if_test_unavailable": "Hypothyroid CANNOT be confirmed without TSH"
    },
    "eclampsia": {
        "required_criteria": ["seizures_observed", "bp_elevated", "proteinuria"],
        "if_no_seizures": "NOT eclampsia — monitor for progression"
    },
    "iugr": {
        "required_criteria": ["sfh_3cm_below_ga OR weight_gain_lt_500g_per_week"],
        "confirmatory": "USG fetal biometry",
        "if_usg_unavailable": "SUSPECTED IUGR — confirm with USG at referral"
    }
}
```

---

## 17. REFERRAL FACILITY DECISION TABLE

```python
REFERRAL_DECISION = {
    "PHC": {
        "can_manage": ["mild_anaemia", "hypothyroid_uncomplicated", "low_risk_pregnancy"],
        "must_refer_to": "FRU or CHC"
    },
    "FRU": {
        "can_manage": ["moderate_anaemia", "hypertension_mild", "gdm_dietary"],
        "must_refer_to": "District Hospital or CEmOC"
    },
    "CEmOC": {
        "can_manage": ["severe_anaemia", "severe_pre_eclampsia", "eclampsia",
                       "previous_cs", "placenta_previa", "syphilis_delivery"],
        "requires": "blood transfusion facility, OT, NICU"
    }
}

REFERRAL_TRIGGERS_IMMEDIATE = [
    "eclampsia",
    "severe_pre_eclampsia",
    "severe_anaemia",
    "placenta_previa_with_bleeding",
    "fetal_movements_absent"
]
```

---

## IMPLEMENTATION NOTES FOR CODE EDITOR

```
1. Create clinical_rules.py and import this file as constants.

2. Run rule_engine(patient_features) BEFORE any RAG retrieval.

3. rule_engine() must return:
   {
     "confirmed_conditions": [...],   # Only conditions with confirmed criteria
     "suspected_conditions": [...],   # Conditions needing confirmatory tests
     "risk_score": int,
     "risk_level": "LOW|MODERATE|HIGH|CRITICAL",
     "triggered_rules": [...],
     "referral_facility": "PHC|FRU|CHC|CEmOC",
     "immediate_referral": bool
   }

4. Pass confirmed_conditions to chunk_relevance_gate.py to filter chunks.

5. Pass suspected_conditions to diagnosis_confidence_gate.py to enforce
   "suspected" language in generated answer.

6. Risk score in rule_engine output MUST match risk score in answer text.
   Use validate_score_consistency() as final step before API response.

7. FBS/OGTT threshold for GDM is 2hr PG >= 140 mg/dL (NOT FBS 92 mg/dL).
   The FBS 92 boundary logic in your pipeline is WRONG — fix it using
   the OGTT threshold above.
```

---

*Source Document: High-Risk-Conditions-in-preg-modified-Final.pdf*
*MoHFW / NHM / PMSMA Guidelines*
*Extracted: All pages 1–12*
*Version: 1.0 | For use as pre-RAG rule engine*
