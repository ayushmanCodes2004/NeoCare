# COMPLETE THRESHOLD EXTRACTION FOR HPR DETERMINISTIC ENGINE

Sources: PMSMA High-Risk Conditions PDF + JOGH Research Paper + Extended PMSMA Guidance Note

This is the authoritative rulebook for the deterministic HPR engine.

## 1. ANAEMIA THRESHOLDS

```python
ANAEMIA_DEFINITION_PREGNANCY     = Hb < 11.0 g/dL   # Pregnancy or immediate postpartum
ANAEMIA_MILD                     = Hb >= 10.0 AND Hb <= 10.9 g/dL
ANAEMIA_MODERATE                 = Hb >= 7.0 AND Hb <= 9.9 g/dL
ANAEMIA_SEVERE                   = Hb < 7.0 g/dL     # HPR trigger
ANAEMIA_SEVERE_REFER_FRU         = Hb < 7.0 g/dL     # Mandatory referral to FRU
ANAEMIA_SEVERE_DELIVER_FRU       = Hb < 7.0 g/dL at term → deliver at FRU only
ANAEMIA_IM_IRON_THRESHOLD        = Hb >= 7.0 AND Hb <= 8.0 g/dL → IM iron in divided doses
```

## 2. BLOOD PRESSURE / HYPERTENSION THRESHOLDS

```python
HYPERTENSION_DEFINITION          = BP >= 140/90 mmHg (two consecutive readings, any time in pregnancy)
CHRONIC_HYPERTENSION             = Hypertension before pregnancy OR before 20 weeks gestation
PIH                              = Hypertension after 20 weeks gestation
PREECLAMPSIA_MILD                = BP >= 140/90 AND BP < 160/110 + proteinuria trace/1+/2+ OR > 3g/dL in 24hr
PREECLAMPSIA_SEVERE              = BP >= 160/110 + proteinuria 3+ or 4+
ECLAMPSIA                        = Convulsions + BP >= 140/90 + proteinuria > trace
ANTIHYPERTENSIVE_START_OPD       = Diastolic >= 90-100 mmHg
PREECLAMPSIA_CALCIUM_PREVENTION  = 1g/day calcium after 1st trimester → reduces risk by 50%
```

## 3. BLOOD SUGAR / GDM THRESHOLDS

```python
GDM_DIAGNOSIS_75G_OGTT_2HR_PG   = 2hr PG >= 140 mg/dL → Positive for GDM
GDM_DIAGNOSIS_NEGATIVE           = 2hr PG < 140 mg/dL → Negative
GDM_FIRST_TEST_TIMING            = At first ANC contact (as early as possible)
GDM_SECOND_TEST_TIMING           = 24-28 weeks (if first test negative, min 4 weeks gap)
GDM_BEYOND_28_WEEKS              = Only one test at first contact
GDM_MNT_RESPONSE_2HR_PPPG       = < 120 mg/dL → Continue MNT
GDM_INSULIN_START                = 2hr PPPG >= 120 mg/dL after 2 weeks of MNT → Start insulin
GDM_MONITORING_UPTO_28WKS       = Monitor 2hr PPPG once in 2 weeks
GDM_MONITORING_AFTER_28WKS      = Monitor 2hr PPPG once a week
```

## 4. TSH / THYROID THRESHOLDS

```python
TSH_1ST_TRIMESTER_NORMAL_RANGE  = 0.1 - 2.5 mIU/L
TSH_2ND_TRIMESTER_NORMAL_RANGE  = 0.2 - 3.0 mIU/L
TSH_3RD_TRIMESTER_NORMAL_RANGE  = 0.3 - 3.0 mIU/L
TSH_NO_TREATMENT_1ST_TRIM       = TSH < 2.5 mIU/L → No treatment needed
TSH_NO_TREATMENT_2ND_3RD_TRIM   = TSH < 3.0 mIU/L → No treatment needed
SCH_SUBCLINICAL_HYPOTHYROIDISM  = TSH >= 2.5 AND TSH <= 10 mIU/L + normal FT4
OH_OVERT_HYPOTHYROIDISM_1       = TSH > 2.5-3 mIU/L + low FT4
OH_OVERT_HYPOTHYROIDISM_2       = TSH > 10 mIU/L (irrespective of FT4)
LEVOTHYROXINE_25MCG_START       = TSH >= 2.5/3 AND TSH <= 10 mIU/L
LEVOTHYROXINE_50MCG_START       = TSH > 10 mIU/L
TSH_REPEAT_AFTER_TREATMENT      = Repeat TSH 6 weeks after starting treatment
```

## 5. MATERNAL AGE THRESHOLDS

```python
ADOLESCENT_PREGNANCY_PMSMA      = Age < 20 years              # HPR trigger per PMSMA
ADOLESCENT_RESEARCH_LOWER       = Age 15-17 years             # HPR trigger per NFHS-5 study
ELDERLY_GRAVIDA                 = Age > 35 years              # HPR trigger
```

## 6. URINE PROTEIN THRESHOLDS

```python
PROTEINURIA_PREECLAMPSIA_MILD   = Urine protein trace / 1+ / 2+ on dipstick
PROTEINURIA_PREECLAMPSIA_SEVERE = Urine protein 3+ or 4+ on dipstick
PROTEINURIA_24HR_THRESHOLD      = > 3 g/dL in 24-hour specimen → Pre-eclampsia
```

## 7. GESTATIONAL AGE / PRETERM THRESHOLDS

```python
PRETERM_DEFINITION              = Delivery <= 8 months / < 37 weeks gestation
ANTENATAL_STEROIDS_WINDOW       = 24 to 34 weeks gestation
DEXAMETHASONE_DOSE              = 6 mg IM 12-hourly for 2 days
TWIN_REFER_FRU                  = Refer at 36 weeks for delivery
MULTIPLE_PREGNANCY_USG_TRIGGER  = Fundal height > period of gestation
```

## 8. IUGR THRESHOLDS

```python
IUGR_DEFINITION                 = Birth weight < 10th percentile for gestational age
IUGR_SFH_TRIGGER                = Fundal height < 3 cm below gestational age in weeks (after 20 weeks)
IUGR_WEIGHT_GAIN_TRIGGER        = Maternal weight gain < 500 g/week
IUGR_SFH_FORMULA_AFTER_20WKS   = Expected SFH = gestational weeks ± 2 cm
IUGR_PRE_PREGNANCY_WEIGHT_RISK  = < 50 kg
```

## 9. ANC VISIT FREQUENCY RULES

```python
STANDARD_ANC_SCHEDULE:
VISIT_1 = Registration + first check-up within 12 weeks
VISIT_2 = 14-26 weeks
VISIT_3 = 28-32 weeks
VISIT_4 = 36-40 weeks
HRP_ADDITIONAL_VISITS           = 3 additional ANC visits by doctor/obstetrician after HPR detection
GDM_INCREASED_FREQUENCY_2ND    = Every 2 weeks in second trimester (if uncontrolled)
GDM_INCREASED_FREQUENCY_3RD    = Every week in third trimester (if uncontrolled)
```

## 10. OFFICIAL PMSMA HIGH-RISK CONDITIONS LIST (GoI)

```python
HPR_FLAG_SEVERE_ANAEMIA             = Hb < 7.0 g/dL
HPR_FLAG_PIH_PREECLAMPSIA_ECLAMPSIA = BP >= 140/90 mmHg (after 20 weeks)
HPR_FLAG_SYPHILIS_HIV_POSITIVE      = Serology positive
HPR_FLAG_GDM                        = 2hr PG >= 140 mg/dL
HPR_FLAG_HYPOTHYROIDISM             = TSH out of trimester-specific range
HPR_FLAG_YOUNG_PRIMI                = Age < 20 years
HPR_FLAG_ELDERLY_GRAVIDA            = Age > 35 years
HPR_FLAG_TWIN_MULTIPLE_PREGNANCY    = Twin/multiple gestation confirmed
HPR_FLAG_MALPRESENTATION            = Abnormal fetal presentation
HPR_FLAG_PREVIOUS_LSCS              = History of caesarean section = true
HPR_FLAG_LOW_LYING_PLACENTA         = Placenta previa confirmed on USG
HPR_FLAG_BAD_OBSTETRIC_HISTORY      = Stillbirth > 0 OR abortion > 0 OR congenital malformation
                                      OR obstructed labor OR premature birth history
HPR_FLAG_RH_NEGATIVE                = Rh blood group = negative
HPR_FLAG_SYSTEMIC_ILLNESS           = Any current or past systemic illness
```

## 11. WARNING SIGNS (Immediate Facility Visit Triggers)

```python
WARNING_FEVER                   = Temperature > 38.5°C for > 24 hours
WARNING_HEADACHE_VISION         = Headache + blurring of vision (preeclampsia symptom)
WARNING_GENERALIZED_EDEMA       = Generalized body swelling + facial puffiness
WARNING_CARDIAC_SYMPTOMS        = Palpitations + easy fatigability + breathlessness at rest
WARNING_ABDOMINAL_PAIN          = Pain in abdomen
WARNING_VAGINAL_BLEEDING        = Vaginal bleeding or watery discharge
WARNING_REDUCED_FM              = Reduced fetal movements
WARNING_EPIGASTRIC_PAIN         = Epigastric pain (preeclampsia warning)
WARNING_OLIGURIA                = Reduced urine output (eclampsia warning)
WARNING_SCAR_TENDERNESS         = Scar tenderness in previous CS (uterine rupture risk)
```

## 12. MATERNAL RISK FACTORS (NFHS-5 / Research Thresholds)

```python
MATERNAL_AGE_ADOLESCENT         = Age 15-17 years → HPR
MATERNAL_AGE_ADVANCED           = Age > 35 years → HPR
SHORT_STATURE                   = Height < 140 cm → HPR
HIGH_BMI                        = BMI >= 30.0 kg/m² → HPR (Asian Indian cutoff ≥ 25.0 kg/m²)
GESTATIONAL_WEIGHT_GAIN_OVERWEIGHT = 7-11 kg (for BMI >= 25)
GESTATIONAL_WEIGHT_GAIN_OBESE   = 5-9 kg (for BMI >= 30)
```

## 13. LIFESTYLE RISK FLAGS

```python
LIFESTYLE_RISK_SMOKING          = Current smoker = true → HPR
LIFESTYLE_RISK_TOBACCO          = Tobacco use (non-cigarette) = true → HPR
LIFESTYLE_RISK_ALCOHOL          = Alcohol consumption = true → HPR
```

## 14. BIRTH HISTORY / OBSTETRIC RISK THRESHOLDS

```python
HIGH_BIRTH_ORDER                = Birth order >= 5 → HPR
SHORT_BIRTH_SPACING             = Inter-pregnancy interval (last birth to current conception) < 18 months → HPR
LONG_BIRTH_SPACING              = Inter-pregnancy interval > 59 months → HPR
PREVIOUS_PRETERM                = History of preterm delivery (< 37 weeks) = true → HPR
ADVERSE_BIRTH_OUTCOME           = Miscarriage OR abortion OR stillbirth = true → HPR
PREVIOUS_CS                     = Previous caesarean section = true → HPR
```

## 15. REFERRAL LEVEL DECISION RULES

```python
REFER_TO_FRU_IF:
- Hb < 7.0 g/dL (severe anaemia)
- BP >= 140/90 (for further PIH/PE management)
- Syphilis positive
- Previous CS → deliver at CEmOC facility
- HIV positive → deliver at FRU/EmOC center
- Twin pregnancy → refer at 36 weeks
- IUGR → centre with antenatal/intrapartum monitoring + NICU
- GDM uncontrolled → escalate care frequency

DELIVER_AT_PHC_CHC_IF:
- Hypothyroidism uncomplicated → PHC/CHC with MO
- Low risk cases with no active flags
```

## 16. FETAL SURVEILLANCE THRESHOLDS

```python
FETAL_KICK_COUNT_ALERT          = Fetus does not kick 10 times within 2 hours → refer
FETAL_GROWTH_SCAN_GDM_1        = 28-30 weeks
FETAL_GROWTH_SCAN_GDM_2        = 34-36 weeks (min 3 weeks gap between scans)
FETAL_ANATOMY_SURVEY_GDM       = 18-20 weeks (if diagnosed before 20 weeks)
```

## 17. SYPHILIS STAGING THRESHOLDS

```python
SYPHILIS_EARLY_STAGE            = < 2 years duration OR RPR titer < 1:8
SYPHILIS_LATE_STAGE             = > 2 years duration OR RPR titer > 1:8
SYPHILIS_RESCREEN_TRIGGER       = High risk OR adverse outcome in previous pregnancy → rescreen in 3rd trimester
```

## 18. NATIONAL PREVALENCE BENCHMARKS (for risk scoring context)

```python
NATIONAL_HRP_PREVALENCE_INDIA   = 49.4% (NFHS-5)
SINGLE_HRP_PREVALENCE           = 33.0%
MULTIPLE_HRP_PREVALENCE         = 16.4%
PMSMA_REPORTED_HRP_RATE         = ~14% (underreporting noted)
EXPECTED_HRP_RATE_LITERATURE    = 20-30%
PERINATAL_MORTALITY_DUE_HRP     = 75% of perinatal deaths
SHORT_BIRTH_SPACING_PREVALENCE  = 31.1% of Indian pregnant women
COMORBIDITY_PREVALENCE          = 6.4%
GDM_INDIA_PREVALENCE            = 10-14.3%
HYPOTHYROIDISM_INDIA_PREVALENCE = 4.8-12%
ANAEMIA_INDIA_PREVALENCE        = 58.7%
```

## 19. COMPOSITE HPR FLAG LOGIC (engine ready)

```python
IS_HPR = TRUE if ANY of the following:

age < 20 OR age > 35
OR height < 140 cm
OR BMI >= 30.0
OR smoking = true OR tobacco = true OR alcohol = true
OR Hb < 7.0                             # severe anaemia (strict PMSMA threshold)
OR knownDiabetes = true OR gdmCurrentPregnancy = true OR 2hrPG >= 140
OR knownHypertension = true
OR bpSystolic >= 140 OR bpDiastolic >= 90
OR tshLevel out of trimester range (see TSH thresholds above)
OR thyroidDisorder = true
OR twinPregnancy = true
OR previousLSCS = true
OR rhNegative = true
OR stillbirth > 0 OR abortion > 0 OR pretermDelivery > 0
OR birthOrder >= 5
OR interPregnancyInterval < 18 months OR > 59 months
OR urineProtein = positive
OR HIV_positive = true OR syphilis_positive = true
OR systemic_illness = true

WATCH_BORDERLINE (not HPR but monitor):
Hb >= 10.0 AND Hb < 11.0      # mild anaemia → IFA twice daily
bpSystolic 130-139 OR bpDiastolic 85-89  # pre-hypertension watch
TSH approaching upper trimester limit
fetalMovements = reduced (not absent)
gestationalWeeks <= 20 AND no anomaly scan done yet
```
