# V1 vs V2 Comparison Table

## Input Fields Comparison

| Category | Field | V1 | V2 | Threshold | Score |
|----------|-------|----|----|-----------|-------|
| **Demographics** | age | ✅ | ✅ | <20 or ≥35 | 3 |
| | gestational_age_weeks | ✅ | ✅ | - | - |
| **Vitals** | systolic_bp | ✅ | ✅ | ≥140 | 3 |
| | diastolic_bp | ✅ | ✅ | ≥90 | 3 |
| | hemoglobin | ✅ | ✅ | <11 | 1-4 |
| | **height** | ❌ | 🆕 | <140 cm | 2 |
| | **bmi** | ❌ | 🆕 | ≥30 kg/m² | 2 |
| **Glucose** | fbs | ✅ | ✅ | - | - |
| | ogtt_2hr_pg | ✅ | ✅ | ≥140 | 2 |
| **Lifestyle** | **smoking** | ❌ | 🆕 | Yes | 2 |
| | **tobacco_use** | ❌ | 🆕 | Yes | 2 |
| | **alcohol_use** | ❌ | 🆕 | Yes | 2 |
| **Obstetric** | prior_cesarean | ✅ | ✅ | Yes | 2 |
| | twin_pregnancy | ✅ | ✅ | Yes | 3 |
| | placenta_previa | ✅ | ✅ | Yes | 4 |
| | **birth_order** | ❌ | 🆕 | ≥5 | 2 |
| | **inter_pregnancy_interval** | ❌ | 🆕 | <18 or >59 months | 2/1 |
| | **stillbirth_count** | ❌ | 🆕 | >0 | 2 |
| | **abortion_count** | ❌ | 🆕 | >0 | 2 |
| | **preterm_history** | ❌ | 🆕 | Yes | 2 |
| **Serology** | **rh_negative** | ❌ | 🆕 | Yes | 1 |
| | **hiv_positive** | ❌ | 🆕 | Yes | 3 |
| | **syphilis_positive** | ❌ | 🆕 | Yes | 3 |
| **Complications** | **malpresentation** | ❌ | 🆕 | Yes | 2 |
| | **systemic_illness** | ❌ | 🆕 | Yes | 2 |

**Legend:**
- ✅ Available in version
- ❌ Not available
- 🆕 New in V2

---

## Output Fields Comparison

| Field | V1 | V2 | Description |
|-------|----|----|-------------|
| **success** | ✅ | ✅ | Request success status |
| **query** | ✅ | ✅ | Original query |
| **answer** | ✅ | ✅ | Full clinical response |
| **blocked** | ✅ | ✅ | Hallucination guard status |
| **care_level** | ✅ | ✅ | Care level (ASHA/PHC/CHC/DISTRICT) |
| **timestamp** | ✅ | ✅ | ISO 8601 timestamp |
| **processing_time_ms** | ✅ | ✅ | Processing time |
| | | | |
| **confidence.score** | ✅ | ✅ | Overall confidence (0-1) |
| **confidence.level** | ✅ | ✅ | HIGH/MEDIUM/LOW/VERY_LOW |
| **confidence.breakdown** | ✅ | ✅ | Component scores |
| | | | |
| **features.age** | ✅ | ✅ | Patient age |
| **features.gestational_age_weeks** | ✅ | ✅ | Gestational age |
| **features.systolic_bp** | ✅ | ✅ | Systolic BP |
| **features.diastolic_bp** | ✅ | ✅ | Diastolic BP |
| **features.hemoglobin** | ✅ | ✅ | Hemoglobin level |
| **features.fbs** | ✅ | ✅ | Fasting blood sugar |
| **features.twin_pregnancy** | ✅ | ✅ | Twin pregnancy flag |
| **features.prior_cesarean** | ✅ | ✅ | Previous cesarean flag |
| **features.placenta_previa** | ✅ | ✅ | Placenta previa flag |
| **features.comorbidities** | ✅ | ✅ | Comorbidities list |
| **features.extraction_confidence** | ✅ | ✅ | Extraction quality |
| **features.missing_fields** | ✅ | ✅ | Missing fields list |
| **features.height** | ❌ | 🆕 | Height in cm |
| **features.bmi** | ❌ | 🆕 | BMI in kg/m² |
| **features.smoking** | ❌ | 🆕 | Smoking status |
| **features.tobacco_use** | ❌ | 🆕 | Tobacco use |
| **features.alcohol_use** | ❌ | 🆕 | Alcohol use |
| **features.birth_order** | ❌ | 🆕 | Birth order |
| **features.inter_pregnancy_interval** | ❌ | 🆕 | Pregnancy interval |
| **features.stillbirth_count** | ❌ | 🆕 | Stillbirth count |
| **features.abortion_count** | ❌ | 🆕 | Abortion count |
| **features.preterm_history** | ❌ | 🆕 | Preterm history |
| **features.rh_negative** | ❌ | 🆕 | Rh negative status |
| **features.hiv_positive** | ❌ | 🆕 | HIV status |
| **features.syphilis_positive** | ❌ | 🆕 | Syphilis status |
| **features.malpresentation** | ❌ | 🆕 | Malpresentation |
| **features.systemic_illness** | ❌ | 🆕 | Systemic illness |
| | | | |
| **rule_output.overall_risk** | ✅ | ✅ | LOW/MODERATE/HIGH/CRITICAL |
| **rule_output.total_score** | ✅ | ✅ | Numeric risk score |
| **rule_output.rule_coverage** | ✅ | ✅ | Rule coverage (0-1) |
| **rule_output.triggered_rules** | ✅ | ✅ | List of triggered rules |
| **rule_output.risk_flags** | ✅ | ✅ | Detailed risk flags |
| **rule_output.is_hpr** | ❌ | 🆕 | Composite HPR flag (boolean) |
| **rule_output.borderline_flags** | ❌ | 🆕 | Borderline monitoring values |
| **rule_output.confirmed_conditions** | ❌ | 🆕 | Lab-confirmed conditions |
| **rule_output.suspected_conditions** | ❌ | 🆕 | Needs confirmatory tests |
| **rule_output.referral_facility** | ❌ | 🆕 | Recommended facility |
| **rule_output.immediate_referral** | ❌ | 🆕 | Urgent referral flag |
| **rule_output.diagnosis_notes** | ❌ | 🆕 | Clinical notes |
| | | | |
| **retrieval_stats.rewritten_query** | ✅ | ✅ | Query after rewriting |
| **retrieval_stats.faiss_count** | ✅ | ✅ | FAISS chunks |
| **retrieval_stats.bm25_count** | ✅ | ✅ | BM25 chunks |
| **retrieval_stats.final_count** | ✅ | ✅ | Final chunks |
| **retrieval_stats.retrieval_quality** | ✅ | ✅ | Quality score |
| **retrieval_stats.chunk_agreement** | ✅ | ✅ | Agreement score |

---

## Triggered Rules Comparison

| Rule Name | V1 | V2 | Threshold | Score |
|-----------|----|----|-----------|-------|
| **Anaemia** | | | | |
| mild_anaemia | ✅ | ✅ | Hb 10-10.9 g/dL | 1 |
| moderate_anaemia | ✅ | ✅ | Hb 7-9.9 g/dL | 2 |
| severe_anaemia | ✅ | ✅ | Hb <7 g/dL | 4 |
| **Hypertension** | | | | |
| hypertension | ✅ | ✅ | BP ≥140/90 | 3 |
| pre_eclampsia | ✅ | ✅ | BP ≥140/90 + proteinuria | 3 |
| severe_pre_eclampsia | ✅ | ✅ | BP ≥160/110 + proteinuria | 4 |
| eclampsia | ✅ | ✅ | Seizures + BP ≥140/90 | 5 |
| **GDM** | | | | |
| gdm_confirmed | ✅ | ✅ | 2hr PG ≥140 mg/dL | 2 |
| gdm_screening_pending | ✅ | ✅ | No OGTT, GA 14-28 weeks | 1 |
| **Age** | | | | |
| young_primi | ✅ | ✅ | Age <20 years | 3 |
| advanced_maternal_age | ✅ | ✅ | Age ≥35 years | 3 |
| **Obstetric** | | | | |
| twin_pregnancy | ✅ | ✅ | Multiple gestation | 3 |
| previous_cs | ✅ | ✅ | Prior cesarean | 2 |
| placenta_previa | ✅ | ✅ | Confirmed/suspected | 4 |
| **Anthropometric** | | | | |
| short_stature | ❌ | 🆕 | Height <140 cm | 2 |
| high_bmi | ❌ | 🆕 | BMI ≥30 kg/m² | 2 |
| **Lifestyle** | | | | |
| smoking | ❌ | 🆕 | Current smoker | 2 |
| tobacco_use | ❌ | 🆕 | Tobacco use | 2 |
| alcohol_use | ❌ | 🆕 | Alcohol consumption | 2 |
| **Obstetric History** | | | | |
| high_birth_order | ❌ | 🆕 | Birth order ≥5 | 2 |
| short_birth_spacing | ❌ | 🆕 | Interval <18 months | 2 |
| long_birth_spacing | ❌ | 🆕 | Interval >59 months | 1 |
| previous_preterm | ❌ | 🆕 | Preterm history | 2 |
| previous_stillbirth | ❌ | 🆕 | Stillbirth history | 2 |
| previous_abortion | ❌ | 🆕 | Abortion history | 2 |
| **Serology** | | | | |
| rh_negative | ❌ | 🆕 | Rh negative | 1 |
| hiv_positive | ❌ | 🆕 | HIV positive | 3 |
| syphilis_positive | ❌ | 🆕 | Syphilis positive | 3 |
| **Complications** | | | | |
| malpresentation | ❌ | 🆕 | Abnormal presentation | 2 |
| systemic_illness | ❌ | 🆕 | Systemic illness | 2 |

**Total Conditions:**
- V1: 17 conditions
- V2: 33 conditions (+16 new)

---

## Statistics

### Coverage
| Metric | V1 | V2 | Change |
|--------|----|----|--------|
| Total Conditions | 17 | 33 | +94% |
| Input Fields | 12 | 28 | +133% |
| Output Fields | 25 | 32 | +28% |
| Max Risk Score | ~15 | ~40+ | +167% |

### Detection Capability
| Category | V1 | V2 | Improvement |
|----------|----|----|-------------|
| Anaemia | ✅ 3 levels | ✅ 3 levels | Same |
| Hypertension | ✅ 4 types | ✅ 4 types | Same |
| GDM | ✅ 2 states | ✅ 2 states | Same |
| Age Risk | ✅ 2 types | ✅ 2 types | Same |
| Anthropometric | ❌ None | ✅ 2 types | +100% |
| Lifestyle | ❌ None | ✅ 3 types | +100% |
| Obstetric History | ✅ 3 types | ✅ 8 types | +167% |
| Serology | ❌ None | ✅ 3 types | +100% |
| Complications | ✅ 2 types | ✅ 4 types | +100% |

---

## Migration Impact

### For Frontend Developers
- ✅ No breaking changes
- ✅ All V1 fields still present
- ✅ New fields optional
- ⚠️ Check for `is_hpr` flag
- ⚠️ Display `borderline_flags` if present

### For Backend Integrations
- ✅ V1 queries work unchanged
- ✅ V2 fields ignored if not provided
- ✅ Gradual migration possible
- ⚠️ Update data models for new fields
- ⚠️ Handle new output fields

### For Clinical Users
- ✅ More comprehensive risk detection
- ✅ Borderline value monitoring
- ✅ Better referral guidance
- ⚠️ Higher risk scores expected
- ⚠️ More conditions flagged

---

**Version:** V1 → V2  
**Date:** 2025-02-21  
**Backward Compatible:** ✅ Yes
