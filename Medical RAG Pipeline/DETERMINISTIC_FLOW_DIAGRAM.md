# Deterministic Rule Engine Flow - Complete Mapping

## Your Input → Deterministic Rules → RAG → Output

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: STRUCTURED INPUT                                            │
├─────────────────────────────────────────────────────────────────────┤
│ Patient: Pooja Singh (ANC-MED-002)                                  │
│ Age: 28 years                                                        │
│ Gestational Age: 20 weeks                                           │
│ Hemoglobin: 10.6 g/dL                                               │
│ BP: 110/72 mmHg                                                      │
│ FBS: 0 (not done)                                                    │
│ OGTT 2hr PG: 0 (not done)                                           │
│ Twin Pregnancy: No                                                   │
│ Previous CS: No                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: DETERMINISTIC RULE ENGINE (clinical_rules.py)              │
├─────────────────────────────────────────────────────────────────────┤
│ Rule 1: ANAEMIA CHECK                                               │
│   Hb 10.6 g/dL < 11.0 g/dL threshold                                │
│   → 10.0 ≤ 10.6 ≤ 10.9 → MILD ANAEMIA                              │
│   → Score: 1 (per Section 1 & 14)                                   │
│   → Severity: minor                                                  │
│   → Confirmed Condition: "mild_anaemia"                             │
│                                                                      │
│ Rule 2: HYPERTENSION CHECK                                          │
│   BP 110/72 < 140/90 threshold                                      │
│   → NORMAL BP                                                        │
│   → Score: 0                                                         │
│   → No condition triggered                                           │
│                                                                      │
│ Rule 3: GDM CHECK                                                    │
│   OGTT 2hr PG: 0 (not done)                                         │
│   → GDM cannot be confirmed                                          │
│   → Score: 0                                                         │
│                                                                      │
│ Rule 4: GDM SCREENING CHECK (FIX 4)                                 │
│   GA: 20 weeks (14 ≤ 20 < 24)                                       │
│   OGTT not done: True                                                │
│   GDM not confirmed: True                                            │
│   → GDM SCREENING PENDING (first window)                             │
│   → Score: 1 (per Section 3)                                         │
│   → Severity: minor                                                  │
│   → Suspected Condition: "gdm_screening_pending"                    │
│                                                                      │
│ Rule 5: AGE CHECK                                                    │
│   Age 28: 20 ≤ 28 < 35                                              │
│   → NORMAL AGE                                                       │
│   → Score: 0                                                         │
│                                                                      │
│ Rule 6: TWIN PREGNANCY CHECK                                        │
│   Twin Pregnancy: No                                                 │
│   → Score: 0                                                         │
│                                                                      │
│ Rule 7: PREVIOUS CS CHECK                                           │
│   Previous CS: No                                                    │
│   → Score: 0                                                         │
│                                                                      │
│ TOTAL RISK SCORE: 1 + 1 = 2                                         │
│                                                                      │
│ RISK LEVEL CALCULATION (Section 14):                                │
│   Score 2 → LOW (0-2 range)                                         │
│                                                                      │
│ OUTPUT:                                                              │
│   ✓ confirmed_conditions: ["mild_anaemia"]                          │
│   ✓ suspected_conditions: ["gdm_screening_pending"]                 │
│   ✓ triggered_rules: ["mild_anaemia", "gdm_screening_pending"]      │
│   ✓ risk_score: 2                                                    │
│   ✓ risk_level: "LOW"                                                │
│   ✓ referral_facility: "PHC"                                         │
│   ✓ immediate_referral: False                                        │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: CHECK SECTION 13 HIGH-RISK CONDITIONS                      │
├─────────────────────────────────────────────────────────────────────┤
│ Section 13 Master List (19 conditions):                             │
│   1. severe_anaemia (Hb < 7) ← ONLY severe, NOT mild/moderate      │
│   2. pregnancy_induced_hypertension                                  │
│   3. pre_eclampsia                                                   │
│   4. pre_eclamptic_toxemia                                           │
│   5. syphilis_positive                                               │
│   6. hiv_positive                                                    │
│   7. gestational_diabetes_mellitus                                   │
│   8. hypothyroidism                                                  │
│   9. young_primi (< 20 years)                                        │
│  10. elderly_gravida (> 35 years)                                    │
│  11. twin_pregnancy                                                  │
│  12. multiple_pregnancy                                              │
│  13. malpresentation                                                 │
│  14. previous_lscs                                                   │
│  15. placenta_previa                                                 │
│  16. low_lying_placenta                                              │
│  17. bad_obstetric_history                                           │
│  18. rh_negative                                                     │
│  19. systemic_illness_current_or_past                                │
│                                                                      │
│ Patient's Triggered Rules:                                          │
│   - mild_anaemia ← NOT in Section 13 list                           │
│   - gdm_screening_pending ← NOT in Section 13 list                  │
│                                                                      │
│ RESULT:                                                              │
│   ✓ isHighRisk: FALSE                                                │
│   Reason: No conditions from Section 13 master list                 │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: BUILD DETECTED RISKS FOR OUTPUT                            │
├─────────────────────────────────────────────────────────────────────┤
│ From risk_flags:                                                     │
│   1. "Mild Anaemia" (Hb 10.6 g/dL)                                  │
│   2. "GDM First Screening Pending" (GA 20 weeks, no OGTT)           │
│                                                                      │
│ detectedRisks: ["Mild Anaemia", "GDM First Screening Pending"]      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: RAG PIPELINE (production_pipeline.py)                      │
├─────────────────────────────────────────────────────────────────────┤
│ Layer 1: Feature Extraction (already done in structured input)      │
│ Layer 2: Hybrid Retrieval                                           │
│   - Query: "28-year-old at 20 weeks, Hb 10.6, BP 110/72..."        │
│   - Retrieve relevant chunks from medical guidelines                │
│   - FAISS + BM25 + Cross-encoder reranking                          │
│                                                                      │
│ Layer 3: Rule Engine (already done - use pre_rag_rules)             │
│   - Skip duplicate rule engine                                       │
│   - Use deterministic results from Step 2                            │
│                                                                      │
│ Layer 4: Evidence-Grounded Reasoning                                │
│   - LLM generates explanation based on:                              │
│     * Confirmed conditions: mild_anaemia                             │
│     * Suspected conditions: gdm_screening_pending                    │
│     * Retrieved evidence chunks                                      │
│     * Risk level: LOW                                                │
│   - Generate recommendation based on keywords in explanation         │
│                                                                      │
│ Confidence Calculation (FIX 2):                                      │
│   - Base confidence from retrieval quality, rule coverage, etc.      │
│   - For structured JSON input: confidence = max(0.70, calculated)    │
│   - Minimum confidence: 0.70                                         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: FINAL OUTPUT (JSON Response)                               │
├─────────────────────────────────────────────────────────────────────┤
│ {                                                                    │
│   "isHighRisk": false,          ← From Section 13 check             │
│   "riskLevel": "LOW",            ← From risk score (2 → LOW)        │
│   "detectedRisks": [             ← From risk_flags                  │
│     "Mild Anaemia",                                                  │
│     "GDM First Screening Pending"                                    │
│   ],                                                                 │
│   "explanation": "Risk Assessment: LOW. Patient presents with 2     │
│                   risk factors: Mild Anaemia and GDM screening      │
│                   pending. Hb 10.6 g/dL indicates mild anaemia      │
│                   requiring iron supplementation. GDM screening     │
│                   should be performed at 24-28 weeks.",             │
│   "confidence": 0.70,            ← Minimum for structured JSON      │
│   "recommendation": "Continue routine antenatal care with regular   │
│                      monitoring. Start IFA tablets twice daily.     │
│                      Schedule 75g OGTT for GDM screening at         │
│                      24-28 weeks.",                                  │
│   "patientId": "ANC-MED-002",                                        │
│   "patientName": "Pooja Singh",                                      │
│   "age": 28,                                                         │
│   "gestationalWeeks": 20,                                            │
│   "visitMetadata": { ... }                                           │
│ }                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Points

### 1. Deterministic Rule Engine (clinical_rules.py)
- **100% rule-based** - No LLM guessing
- Follows clinical_thresholds.md exactly
- Runs BEFORE RAG retrieval
- Establishes confirmed/suspected conditions

### 2. Section 13 High-Risk Check
- Only **severe_anaemia** (Hb < 7) is high-risk
- **mild_anaemia** (Hb 10-10.9) is NOT high-risk
- **moderate_anaemia** (Hb 7-9.9) is NOT high-risk
- isHighRisk = true ONLY if condition is in Section 13 master list

### 3. Risk Scoring (Section 14)
- Mild anaemia: 1 point
- GDM screening pending: 1 point
- Total: 2 points → LOW risk (0-2 range)

### 4. RAG Role
- Generates human-readable explanation
- Provides evidence-based recommendations
- Does NOT override deterministic rules
- Uses confirmed conditions to filter relevant chunks

### 5. Confidence Boost (FIX 2)
- Structured JSON input: minimum confidence 0.70
- Reflects higher data quality from structured input

## Verification

Run this test to verify the flow:
```bash
python test_structured_flow.py
```

Expected output:
- isHighRisk: **false** (mild_anaemia NOT in Section 13)
- riskLevel: **LOW** (score 2)
- detectedRisks: ["Mild Anaemia", "GDM First Screening Pending"]
- confidence: ≥ 0.70
