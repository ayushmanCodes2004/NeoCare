# Full HPR Rule Engine V2 Implementation Plan

## Overview
Complete rewrite of clinical_rules.py to implement all 19 sections from COMPLETE_HPR_THRESHOLDS.md

## Files to Create/Update

### 1. clinical_rules_v2.py (NEW - Complete Rule Engine)
- All 19 threshold sections
- Comprehensive evaluation functions
- Extended HPR flag logic
- Borderline monitoring flags

### 2. layer1_extractor.py (UPDATE - Add New Fields)
New fields to extract:
- height (cm)
- weight (kg) 
- BMI (calculated or extracted)
- smoking (boolean)
- tobacco_use (boolean)
- alcohol_use (boolean)
- birth_order (int)
- inter_pregnancy_interval (months)
- stillbirth_count (int)
- abortion_count (int)
- preterm_delivery_history (boolean)
- rh_negative (boolean)
- hiv_positive (boolean)
- syphilis_positive (boolean)
- systemic_illness (boolean)
- malpresentation (boolean)

### 3. api_server.py (UPDATE - Extend Pydantic Models)
Update StructuredQueryRequest models to include:
- PatientInfo: height, weight, BMI
- MedicalHistory: smoking, tobacco, alcohol, systemic_illness, rh_negative, hiv_positive, syphilis_positive
- ObstetricHistory: birth_order, inter_pregnancy_interval, stillbirth_count, abortion_count, preterm_history, malpresentation
- PregnancyDetails: fetal_movements_status

### 4. Update HIGH_RISK_CONDITIONS List
Expand to include all new HPR flags from Section 10

## Implementation Steps

### STEP 1: Create clinical_rules_v2.py with all thresholds
### STEP 2: Test rule engine standalone
### STEP 3: Update layer1_extractor.py
### STEP 4: Update api_server.py models
### STEP 5: Integration testing
### STEP 6: Replace clinical_rules.py with v2
### STEP 7: Update HIGH_RISK_CONDITIONS in api_server.py

## New HPR Conditions Added (Total: ~30 conditions)

Existing (16):
- severe_anaemia, moderate_anaemia, mild_anaemia
- hypertension, pre_eclampsia, severe_pre_eclampsia, eclampsia
- gdm_confirmed, gdm_screening_pending
- hypothyroid_overt, hypothyroid_subclinical
- young_primi, advanced_maternal_age
- twin_pregnancy, previous_cs, placenta_previa

New (14):
- short_stature (height < 140cm)
- high_bmi (BMI >= 30)
- smoking, tobacco_use, alcohol_use
- high_birth_order (>= 5)
- short_birth_spacing (< 18 months)
- long_birth_spacing (> 59 months)
- rh_negative
- bad_obstetric_history (stillbirth/abortion/preterm)
- hiv_positive
- syphilis_positive
- systemic_illness
- malpresentation

## Risk Scoring Updates

Current: 0-2=LOW, 3-5=MODERATE, 6-8=HIGH, 9+=CRITICAL

New scores to add:
- short_stature: 2
- high_bmi: 2
- smoking: 2
- tobacco_use: 2
- alcohol_use: 2
- high_birth_order: 2
- short_birth_spacing: 2
- long_birth_spacing: 1
- rh_negative: 1
- bad_obstetric_history: 2
- hiv_positive: 3
- syphilis_positive: 3
- systemic_illness: 2
- malpresentation: 2

## Testing Strategy

1. Unit test each evaluation function
2. Test composite HPR logic
3. Test borderline monitoring flags
4. Integration test with API
5. Validate against COMPLETE_HPR_THRESHOLDS.md
