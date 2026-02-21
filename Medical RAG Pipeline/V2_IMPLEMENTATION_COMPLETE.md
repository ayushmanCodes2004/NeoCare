# HPR Rule Engine V2 - Implementation Complete

## Summary

Created comprehensive `clinical_rules_v2.py` implementing all 19 sections from COMPLETE_HPR_THRESHOLDS.md

## What's New

### Expanded from 16 to 30+ HPR Conditions

**Original Conditions (16):**
- Anaemia (mild, moderate, severe)
- Hypertension, Pre-eclampsia, Severe Pre-eclampsia, Eclampsia
- GDM confirmed, GDM screening pending
- Hypothyroid (overt, subclinical)
- Young primi, Advanced maternal age
- Twin pregnancy, Previous CS, Placenta previa

**New Conditions Added (14):**
1. **short_stature** - Height < 140 cm (score: 2)
2. **high_bmi** - BMI ≥ 30 kg/m² (score: 2)
3. **smoking** - Current smoker (score: 2)
4. **tobacco_use** - Tobacco consumption (score: 2)
5. **alcohol_use** - Alcohol consumption (score: 2)
6. **high_birth_order** - Birth order ≥ 5 (score: 2)
7. **short_birth_spacing** - < 18 months (score: 2)
8. **long_birth_spacing** - > 59 months (score: 1)
9. **previous_preterm** - History of preterm delivery (score: 2)
10. **previous_stillbirth** - Stillbirth history (score: 2)
11. **previous_abortion** - Abortion history (score: 2)
12. **rh_negative** - Rh negative blood group (score: 1)
13. **hiv_positive** - HIV confirmed (score: 3)
14. **syphilis_positive** - Syphilis confirmed (score: 3)
15. **malpresentation** - Abnormal fetal presentation (score: 2)
16. **systemic_illness** - Current/past systemic illness (score: 2)

### New Features

1. **Borderline Monitoring Flags**
   - Borderline anaemia (Hb 10-10.9)
   - Pre-hypertension (BP 130-139/85-89)
   - TSH approaching limits
   - Returns monitoring recommendations

2. **Composite HPR Flag**
   - `is_hpr` boolean field in RuleEngineResult
   - Implements Section 19 logic
   - TRUE if ANY HPR condition triggered

3. **Extended RuleEngineResult**
   ```python
   @dataclass
   class RuleEngineResult:
       confirmed_conditions: List[str]
       suspected_conditions: List[str]
       risk_score: int
       risk_level: str
       triggered_rules: List[str]
       risk_flags: List[Dict]
       referral_facility: str
       immediate_referral: bool
       diagnosis_notes: List[str]
       rule_coverage: float = 1.0
       borderline_flags: List[Dict] = None  # NEW
       is_hpr: bool = False  # NEW
   ```

## Next Steps to Deploy

### STEP 1: Test V2 Engine Standalone
```bash
python -c "
from clinical_rules_v2 import run_rule_engine

# Test with comprehensive features
features = {
    'age': 28,
    'gestational_age_weeks': 20,
    'hemoglobin': 10.6,
    'systolic_bp': 110,
    'diastolic_bp': 72,
    'height': 145,  # NEW
    'bmi': 28.5,  # NEW
    'smoking': False,  # NEW
    'birth_order': 3,  # NEW
    'rh_negative': False,  # NEW
}

result = run_rule_engine(features, verbose=True)
print(f'IS_HPR: {result.is_hpr}')
print(f'Risk Level: {result.risk_level}')
print(f'Score: {result.risk_score}')
print(f'Triggered: {result.triggered_rules}')
print(f'Borderline: {result.borderline_flags}')
"
```

### STEP 2: Update layer1_extractor.py

Add extraction patterns for new fields:
- height, weight, BMI
- smoking, tobacco, alcohol
- birth_order, inter_pregnancy_interval
- stillbirth_count, abortion_count
- rh_negative, hiv_positive, syphilis_positive
- systemic_illness, malpresentation

### STEP 3: Update api_server.py Models

Extend Pydantic models in StructuredQueryRequest:

```python
class PatientInfo(BaseModel):
    # Existing fields...
    height: Optional[float] = None  # NEW
    weight: Optional[float] = None  # NEW
    bmi: Optional[float] = None  # NEW

class MedicalHistory(BaseModel):
    # Existing fields...
    smoking: Optional[bool] = False  # NEW
    tobaccoUse: Optional[bool] = False  # NEW
    alcoholUse: Optional[bool] = False  # NEW
    rhNegative: Optional[bool] = False  # NEW
    hivPositive: Optional[bool] = False  # NEW
    syphilisPositive: Optional[bool] = False  # NEW
    systemicIllness: Optional[bool] = False  # NEW

class ObstetricHistory(BaseModel):
    # Existing fields...
    birthOrder: Optional[int] = None  # NEW
    interPregnancyInterval: Optional[int] = None  # NEW (months)
    stillbirthCount: Optional[int] = 0  # NEW
    abortionCount: Optional[int] = 0  # NEW
    pretermHistory: Optional[bool] = False  # NEW
    malpresentation: Optional[bool] = False  # NEW
```

### STEP 4: Replace clinical_rules.py

```bash
# Backup old version
cp clinical_rules.py clinical_rules_v1_backup.py

# Replace with V2
cp clinical_rules_v2.py clinical_rules.py
```

### STEP 5: Update HIGH_RISK_CONDITIONS in api_server.py

Add new conditions to the HPR master list.

### STEP 6: Integration Testing

Test full pipeline with new fields.

## Benefits

1. **Comprehensive Coverage**: All PMSMA + JOGH + Extended thresholds
2. **Research-Grade**: Implements latest NFHS-5 findings
3. **Borderline Monitoring**: Catches at-risk cases early
4. **Composite HPR Flag**: Clear boolean for HPR status
5. **Extensible**: Easy to add more conditions

## Validation

Run audit script to verify all thresholds match COMPLETE_HPR_THRESHOLDS.md:
```bash
python audit_thresholds_v2.py
```

## Documentation

- Source: `COMPLETE_HPR_THRESHOLDS.md`
- Implementation: `clinical_rules_v2.py`
- Plan: `IMPLEMENTATION_PLAN_V2.md`
- This file: `V2_IMPLEMENTATION_COMPLETE.md`
