# RAG Pipeline Test Suite — test1.md
# Medical High-Risk Pregnancy RAG Validation
# Version: 1.0.0 | Target: Close 30% Alignment Gap

---

## How to Use This File

1. Send each INPUT JSON to `POST http://localhost:8000/query`
2. Compare actual response against EXPECTED OUTPUT fields
3. Run PASS/FAIL checklist for each test
4. If FAIL → apply the CORRECTIVE PROMPT for that test
5. Re-run the test after applying the prompt
6. Run Test Case 5 last as regression test

---

## TEST CASE 1 — Topic Isolation Rule
### Goal: RAG must NOT pull GDM protocols for a non-diabetic patient

---

### INPUT JSON

```json
{
  "query": "A 28-year-old G3P2 at 30 weeks presents to a PHC with BP 150/95 mmHg, mild pedal edema, and headache for 2 days. No history of diabetes, thyroid disorder, or previous complications. Previous deliveries were uneventful vaginal births at term. Urine dipstick and labs unavailable. Fetal movements normal. Nearest FRU is 30 km away.",
  "care_level": "PHC",
  "verbose": true
}
```

---

### EXPECTED OUTPUT

```json
{
  "success": true,
  "blocked": false,
  "care_level": "PHC",
  "rule_output": {
    "overall_risk": "MODERATE",
    "total_score": 3,
    "triggered_rules": ["hypertension"],
    "risk_flags": [
      {
        "condition": "Hypertension",
        "present": true,
        "severity": "major",
        "value": "BP 150/95 mmHg",
        "threshold": ">=140/90 mmHg",
        "score": 3
      }
    ]
  },
  "features": {
    "age": 28,
    "systolic_bp": 150,
    "diastolic_bp": 95,
    "comorbidities": [],
    "missing_fields": ["gestational_age", "hemoglobin", "glucose"]
  }
}
```

**Answer field MUST contain:**
- "Suspected pre-eclampsia" OR "possible pre-eclampsia" (NOT confirmed)
- "Tab Alpha Methyl Dopa" OR "Nifedipine" OR "Labetalol" with doses
- "Refer to FRU"
- "proteinuria unconfirmed" OR "dipstick unavailable"

**Answer field MUST NOT contain:**
- "GDM" or "gestational diabetes"
- "blood glucose monitoring"
- "insulin"
- "OGTT"
- Any content sourced from Page 20 of document

**Covered Topics MUST NOT include:**
- "diabetes"
- "hypothyroid"

---

### PASS/FAIL CHECKLIST

```
[ ] overall_risk = "MODERATE"
[ ] total_score = 3
[ ] triggered_rules contains only "hypertension"
[ ] comorbidities = []
[ ] answer contains antihypertensive drug names with doses
[ ] answer uses "suspected" language for pre-eclampsia
[ ] answer does NOT mention GDM, glucose, insulin
[ ] covered_topics does NOT include diabetes or hypothyroid
[ ] risk score consistent between rule_output and answer text
```

---

### KNOWN FAILURES FROM CURRENT PIPELINE (Test Run 1)
- Pages Used included [20, 20] — GDM chunks retrieved ❌
- covered_topics incorrectly listed "diabetes" and "hypothyroid" ❌
- Betamethasone recommended without confirmed delivery decision ❌
- No antihypertensive drug names in answer ❌
- No "suspected" language used ❌

---

### CORRECTIVE PROMPT FOR TEST 1 FAILURES

Add this to your generator system prompt:

```
RULE TC1-A — NEGATION AWARENESS:
If the clinical query contains phrases like "No history of X", "no known X",
"denies X", or "without X", treat X as ABSENT and CONFIRMED ABSENT.
NEVER include that condition in:
- covered_topics
- triggered_rules
- drug recommendations
- monitoring protocols

RULE TC1-B — TOPIC ISOLATION AT RETRIEVAL:
Before using any retrieved chunk, check: does this chunk's primary topic
match a condition CONFIRMED PRESENT in the patient?
If a chunk is from the GDM/diabetes section AND diabetes is absent → DISCARD chunk.
If a chunk is from the hypothyroid section AND thyroid disorder is absent → DISCARD chunk.
Do this check BEFORE generating any recommendation.

RULE TC1-C — SUSPECTED VS CONFIRMED DIAGNOSIS:
If proteinuria/urine dipstick result is unavailable, you CANNOT confirm
pre-eclampsia. You MUST write:
"Suspected pre-eclampsia — proteinuria status unconfirmed (dipstick unavailable).
Manage as suspected pre-eclampsia and confirm at referral center."
Never drop the word "suspected" when lab confirmation is missing.

RULE TC1-D — ANTIHYPERTENSIVE COMPLETENESS:
Whenever BP ≥140/90 is present, your answer MUST include specific drug names:
- First line: Tab Alpha Methyl Dopa 250mg twice or thrice daily
- Second line: Tab Nifedipine 10-20mg orally BD/TDS
- Third line: Tab Labetalol 100mg twice daily
- In pre-eclampsia context: prophylactic MgSO4 IM
Do not omit these even if referral is being recommended.
```

Add this to your retriever/preprocessor code:

```python
# Negation filter for topic extraction
import re

NEGATION_PATTERNS = [
    r'no history of ([\w\s,]+)',
    r'no known ([\w\s,]+)',
    r'denies ([\w\s,]+)',
    r'without ([\w\s,]+)',
    r'no ([\w\s,]+) history',
]

CONDITION_KEYWORDS = {
    'diabetes': ['diabetes', 'gdm', 'gestational diabetes', 'blood glucose', 'insulin'],
    'hypothyroid': ['hypothyroid', 'thyroid', 'tsh', 'levothyroxine'],
    'anaemia': ['anaemia', 'anemia', 'hemoglobin', 'hb'],
}

def extract_confirmed_topics(query: str) -> list:
    query_lower = query.lower()
    negated_terms = []
    for pattern in NEGATION_PATTERNS:
        matches = re.findall(pattern, query_lower)
        negated_terms.extend(matches)
    negated_text = ' '.join(negated_terms)
    confirmed = []
    for topic, keywords in CONDITION_KEYWORDS.items():
        topic_in_negation = any(kw in negated_text for kw in keywords)
        topic_in_query = any(kw in query_lower for kw in keywords)
        if topic_in_query and not topic_in_negation:
            confirmed.append(topic)
    return confirmed

def filter_chunks_by_confirmed_topics(chunks, confirmed_topics):
    SECTION_TOPIC_MAP = {
        'gdm': ['gestational diabetes', 'gdm', 'blood glucose level',
                'insulin dose', 'ogtt', 'pppg'],
        'hypothyroid': ['hypothyroidism', 'tsh level', 'levothyroxine'],
        'anaemia': ['anaemia is defined', 'hb level', 'ifa tablet'],
    }
    filtered = []
    for chunk in chunks:
        chunk_text = chunk.page_content.lower()
        exclude = False
        for topic, markers in SECTION_TOPIC_MAP.items():
            if topic not in confirmed_topics:
                if any(m in chunk_text for m in markers):
                    exclude = True
                    break
        if not exclude:
            filtered.append(chunk)
    return filtered
```

---
---

## TEST CASE 2 — Drug Completeness Rule
### Goal: RAG must output all 3 antihypertensive drugs + MgSO4 when pre-eclampsia is confirmed

---

### INPUT JSON

```json
{
  "query": "A 32-year-old G1P0 at 36 weeks presents with BP 144/94 mmHg recorded twice 4 hours apart. She has mild headache and 1+ proteinuria on dipstick. No prior hypertension. She is at a CHC with a medical officer available. She is not in labor. Nearest district hospital is 20 km.",
  "care_level": "CHC",
  "verbose": true
}
```

---

### EXPECTED OUTPUT

```json
{
  "success": true,
  "blocked": false,
  "care_level": "CHC",
  "rule_output": {
    "overall_risk": "HIGH",
    "total_score": 6,
    "triggered_rules": ["hypertension", "pre_eclampsia_suspected"],
    "risk_flags": [
      {
        "condition": "Hypertension",
        "present": true,
        "severity": "major",
        "value": "BP 144/94 mmHg",
        "threshold": ">=140/90 mmHg",
        "score": 3
      }
    ]
  },
  "features": {
    "age": 32,
    "gestational_age_weeks": 36,
    "systolic_bp": 144,
    "diastolic_bp": 94,
    "comorbidities": []
  }
}
```

**Answer field MUST contain ALL of:**
- "Tab Alpha Methyl Dopa 250mg" with frequency
- "Nifedipine 10-20mg" with frequency
- "Labetalol 100mg" with frequency
- "MgSO4" OR "Magnesium Sulfate" as prophylaxis
- "mild pre-eclampsia" classification (BP <160/110, proteinuria 1+)
- "Deliver at 38-39 weeks" OR referral for delivery planning
- Source citation from Page 13 or Page 43

**Answer field MUST NOT contain:**
- "severe pre-eclampsia" classification (BP does not meet ≥160/110)
- Any GDM content

---

### PASS/FAIL CHECKLIST

```
[ ] overall_risk = "HIGH"
[ ] answer contains "Alpha Methyl Dopa" with dose
[ ] answer contains "Nifedipine" with dose
[ ] answer contains "Labetalol" with dose
[ ] answer contains MgSO4 prophylaxis mention
[ ] pre-eclampsia classified as MILD not severe
[ ] delivery timing guidance present (38-39 weeks)
[ ] source citations reference Page 13 or Page 43
[ ] no GDM content in answer
```

---

### CORRECTIVE PROMPT FOR TEST 2 FAILURES

Add to generator system prompt:

```
RULE TC2-A — MANDATORY DRUG ENUMERATION:
When hypertension (BP ≥140/90) is confirmed, the answer MUST enumerate
ALL THREE antihypertensive options in this exact order:
1. First line: Tab Alpha Methyl Dopa 250mg twice or thrice daily (max 2g/day)
2. Second line: Tab Nifedipine 10-20mg orally BD/TDS
3. Third line: Tab Labetalol 100mg twice daily (max 2.4g/day)
Omitting even one of these is a FAILURE. List all three even if referring patient.

RULE TC2-B — MGSO4 MANDATORY IN PRE-ECLAMPSIA:
Whenever pre-eclampsia is present (BP ≥140/90 + proteinuria), you MUST mention:
"Prophylactic MgSO4 may be given IM in pre-eclampsia setting."
This is non-negotiable regardless of care level.

RULE TC2-C — SEVERITY CLASSIFICATION ACCURACY:
Mild pre-eclampsia = BP ≥140/90 but <160/110 + proteinuria trace to 2+
Severe pre-eclampsia = BP ≥160/110 + proteinuria 3+ or 4+
NEVER classify mild as severe or vice versa.
Always state the classification explicitly: "This is MILD pre-eclampsia."

RULE TC2-D — DELIVERY TIMING:
For mild pre-eclampsia at ≥37 weeks → state "Plan delivery at 38-39 weeks"
For mild pre-eclampsia at 34-37 weeks → state "Continue monitoring, deliver at 37 weeks"
For mild pre-eclampsia <34 weeks → state "Betamethasone if delivery anticipated,
continue surveillance"
Always include delivery timing guidance.
```

---
---

## TEST CASE 3 — Steroid Gating Rule
### Goal: Steroids recommended for IUGR (correct section), NOT GDM section

---

### INPUT JSON

```json
{
  "query": "A 26-year-old G2P1 at 29 weeks presents with fundal height measuring 24 cm (3 cm below gestational age). BP is 118/76 mmHg, no edema, no proteinuria. Fetal movements slightly reduced. No diabetes or hypertension history. USG not available at center. Nearest referral hospital 50 km away.",
  "care_level": "PHC",
  "verbose": true
}
```

---

### EXPECTED OUTPUT

```json
{
  "success": true,
  "blocked": false,
  "care_level": "PHC",
  "rule_output": {
    "overall_risk": "MODERATE",
    "triggered_rules": ["iugr_suspected", "reduced_fetal_movements"],
    "risk_flags": [
      {
        "condition": "Suspected IUGR",
        "present": true,
        "severity": "major",
        "rationale": "Fundal height 3cm below gestational age"
      }
    ]
  },
  "features": {
    "age": 26,
    "gestational_age_weeks": 29,
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "comorbidities": []
  }
}
```

**Answer field MUST contain:**
- Antenatal steroids recommended — cited from IUGR section (Page 22)
- "One course between 24 and 34 weeks" phrasing
- Daily fetal movement count guidance
- SFH (symphysio-fundal height) monitoring
- Referral to center with NICU facility
- "Suspected IUGR" language

**Answer field MUST NOT contain:**
- Steroid recommendation citing Page 20 (GDM section)
- "blood glucose monitoring after steroid"
- "insulin adjustment"
- Any GDM content

**Source citation MUST reference:**
- Page 22 for steroids and IUGR management
- NOT Page 20

---

### PASS/FAIL CHECKLIST

```
[ ] IUGR flagged in triggered_rules
[ ] antenatal steroids recommended
[ ] steroids cited from Page 22 (IUGR), NOT Page 20 (GDM)
[ ] NO glucose monitoring after steroids mentioned
[ ] fetal movement count guidance present
[ ] referral to NICU-capable center mentioned
[ ] "Suspected IUGR" language used
[ ] BP correctly identified as NORMAL (not hypertensive)
[ ] comorbidities = [] (no diabetes/thyroid false positives)
```

---

### CORRECTIVE PROMPT FOR TEST 3 FAILURES

Add to generator system prompt:

```
RULE TC3-A — STEROID INDICATION SOURCING:
Antenatal steroids (Dexamethasone/Betamethasone) can be indicated for
MULTIPLE reasons. You MUST cite the CORRECT reason:

IF steroids are for IUGR → cite Page 22, state:
"Antenatal steroids: One course to be given between 24 and 34 weeks
of gestation (IUGR guideline, Page 22)"

IF steroids are for GDM with early delivery → cite Page 20, state:
"Antenatal steroids per GoI guidelines with enhanced glucose monitoring"
AND only if GDM is confirmed present.

NEVER mix these two. NEVER cite Page 20 steroid guidance for
a non-GDM patient.

RULE TC3-B — IUGR DETECTION:
If fundal height is ≥3 cm below gestational age in weeks → flag as
"Suspected IUGR". Trigger IUGR management protocol from Page 22.
This includes:
- Daily fetal movement count
- Serial SFH measurement
- NST/BPP where possible
- Antenatal steroids between 24-34 weeks
- Referral to center with NICU

RULE TC3-C — NORMAL BP MUST NOT TRIGGER HYPERTENSION PROTOCOL:
If systolic BP <140 AND diastolic BP <90 → BP is NORMAL.
Do NOT recommend antihypertensives.
Do NOT flag pre-eclampsia.
```

---
---

## TEST CASE 4 — Differential Clarity Rule
### Goal: RAG must use "suspected" language when labs are unavailable

---

### INPUT JSON

```json
{
  "query": "A 30-year-old G2P1 at 34 weeks presents with BP 148/96 mmHg, puffiness of face, and severe headache. No urine dipstick available. No visual disturbances or seizures yet. No prior hypertension. Fetal movements present. She is at a rural sub-center with no lab facilities. Referral hospital 60 km away.",
  "care_level": "PHC",
  "verbose": true
}
```

---

### EXPECTED OUTPUT

```json
{
  "success": true,
  "blocked": false,
  "care_level": "PHC",
  "rule_output": {
    "overall_risk": "HIGH",
    "total_score": 6,
    "triggered_rules": ["hypertension", "pre_eclampsia_suspected"],
    "risk_flags": [
      {
        "condition": "Hypertension",
        "present": true,
        "severity": "major",
        "value": "BP 148/96 mmHg",
        "score": 3
      }
    ]
  },
  "features": {
    "age": 30,
    "gestational_age_weeks": 34,
    "systolic_bp": 148,
    "diastolic_bp": 96
  }
}
```

**Answer field MUST contain:**
- "Suspected pre-eclampsia" — NOT "pre-eclampsia confirmed"
- "proteinuria unconfirmed" OR "dipstick unavailable"
- "Confirm at referral center"
- Danger signs counseling (headache, visual disturbances, oliguria)
- Referral urgency stated
- Antihypertensive drugs named

**Answer field MUST NOT contain:**
- "pre-eclampsia confirmed"
- "diagnosed with pre-eclampsia"
- Any statement implying proteinuria is known

---

### PASS/FAIL CHECKLIST

```
[ ] Answer uses "suspected" pre-eclampsia language
[ ] Answer explicitly states proteinuria is unconfirmed
[ ] Answer recommends confirm diagnosis at referral
[ ] Danger signs listed for patient counseling
[ ] Antihypertensive drugs named with doses
[ ] Referral urgency communicated
[ ] Answer does NOT confirm pre-eclampsia diagnosis
[ ] overall_risk = "HIGH"
```

---

### CORRECTIVE PROMPT FOR TEST 4 FAILURES

Add to generator system prompt:

```
RULE TC4-A — EPISTEMIC HONESTY ABOUT DIAGNOSIS:
You must NEVER state a diagnosis as confirmed if the confirmatory test
result is absent. Apply this mapping:

Pre-eclampsia requires BOTH: BP ≥140/90 AND proteinuria.
If proteinuria result is absent/unavailable:
→ Write: "Suspected pre-eclampsia (proteinuria status unknown — dipstick
  unavailable). Manage empirically as suspected pre-eclampsia.
  Confirm proteinuria at referral facility."

GDM requires: abnormal OGTT result.
If OGTT not done:
→ Write: "GDM cannot be confirmed without OGTT."

Eclampsia requires: seizures.
If no seizures:
→ Write: "No seizures — not eclampsia. Monitor for progression."

RULE TC4-B — DANGER SIGNS MANDATORY FOR HYPERTENSIVE PATIENTS:
For any patient with BP ≥140/90, you MUST include a danger signs section:
"Counsel patient to seek IMMEDIATE care if:
- Severe headache or blurring of vision
- Epigastric pain
- Oliguria (reduced urine)
- Increasing swelling
- Any seizure"

RULE TC4-C — REFERRAL URGENCY GRADING:
Based on clinical picture, state urgency explicitly:
- BP 140-159/90-109 + no lab confirmation → "Refer within 24 hours"
- BP ≥160/110 → "URGENT referral within 2-4 hours"
- Seizures → "EMERGENCY — refer immediately"
```

---
---

## TEST CASE 5 — All Rules Combined (Regression Test)
### Goal: Clean separation of 3 concurrent conditions; all rules fire correctly

---

### INPUT JSON

```json
{
  "query": "A 19-year-old primigravida at 26 weeks presents with BP 160/108 mmHg, severe headache, blurring of vision, and 2+ pedal edema. She was diagnosed with GDM at 24 weeks and is on dietary management only. Urine dipstick shows 3+ proteinuria. Hb is 8.5 g/dl. Fetal movements are reduced. No seizures yet. Nearest CEmOC facility is 40 km away.",
  "care_level": "CHC",
  "verbose": true
}
```

---

### EXPECTED OUTPUT

```json
{
  "success": true,
  "blocked": false,
  "care_level": "CHC",
  "rule_output": {
    "overall_risk": "CRITICAL",
    "total_score": 10,
    "triggered_rules": [
      "adolescent_pregnancy",
      "severe_pre_eclampsia",
      "gdm_confirmed",
      "moderate_anaemia",
      "reduced_fetal_movements"
    ],
    "risk_flags": [
      {
        "condition": "Adolescent Pregnancy",
        "present": true,
        "severity": "major",
        "value": "19 years",
        "threshold": "<20 years",
        "score": 3
      },
      {
        "condition": "Severe Pre-Eclampsia",
        "present": true,
        "severity": "critical",
        "value": "BP 160/108 + proteinuria 3+",
        "score": 4
      },
      {
        "condition": "GDM",
        "present": true,
        "severity": "moderate",
        "value": "Diagnosed at 24 weeks",
        "score": 2
      },
      {
        "condition": "Moderate Anaemia",
        "present": true,
        "severity": "moderate",
        "value": "Hb 8.5 g/dL",
        "threshold": "<10 g/dL",
        "score": 2
      }
    ]
  },
  "features": {
    "age": 19,
    "gestational_age_weeks": 26,
    "systolic_bp": 160,
    "diastolic_bp": 108,
    "hemoglobin": 8.5,
    "comorbidities": ["gdm"]
  }
}
```

**Answer field MUST contain ALL of:**

*Severe Pre-Eclampsia Section:*
- "Severe pre-eclampsia" classification (BP ≥160/110 + proteinuria 3+)
- MgSO4 loading dose: "4gm IV + 5gm IM each buttock"
- Antihypertensive: "Oral Nifedipine 10mg stat" OR "Inj Labetalol 20mg IV"
- "Deliver irrespective of gestational age" (severe PE at 26 weeks)
- Betamethasone for lung maturity (26 weeks < 34 weeks)

*GDM Section (SEPARATE, clearly labeled):*
- GDM management stated separately
- "Monitor blood glucose after steroid injection for 72 hours"
- "Adjust insulin if blood glucose elevated"
- Cited from Page 20

*Anaemia Section (SEPARATE, clearly labeled):*
- "Moderate anaemia (Hb 8.5 g/dL)"
- Iron and folic acid supplementation
- Consider parenteral iron

*Common:*
- Risk score 10 in BOTH rule_output AND answer text (consistency)
- EMERGENCY referral to CEmOC stated
- Adolescent age flagged as additional risk factor

**Answer field MUST NOT contain:**
- GDM glucose monitoring mixed into pre-eclampsia section
- Steroid indication sourced from Page 20 for the pre-eclampsia indication
- Pre-eclampsia classified as "mild"
- Risk score inconsistency between sections

---

### PASS/FAIL CHECKLIST

```
[ ] overall_risk = "CRITICAL"
[ ] total_score = 10 in rule_output
[ ] total_score = 10 in answer text (CONSISTENCY CHECK)
[ ] adolescent_pregnancy flagged
[ ] severe_pre_eclampsia correctly classified (NOT mild)
[ ] MgSO4 loading dose specified
[ ] antihypertensive drug named
[ ] betamethasone recommended (26 weeks < 34 weeks)
[ ] betamethasone indication: early delivery due to severe PE (NOT GDM)
[ ] GDM section present and SEPARATE from PE section
[ ] glucose monitoring after steroids cited from GDM section (Page 20)
[ ] anaemia section present and separate
[ ] NO cross-contamination between PE and GDM drug protocols
[ ] EMERGENCY referral stated
[ ] adolescent age risk mentioned
[ ] all 3 conditions managed in clean separate sections
```

---

### CORRECTIVE PROMPT FOR TEST 5 FAILURES

Add to generator system prompt:

```
RULE TC5-A — MULTI-CONDITION SEPARATION:
When a patient has multiple confirmed conditions (e.g., severe pre-eclampsia
+ GDM + anaemia), you MUST structure the answer in clearly labeled sections:

SECTION 1: [Primary Emergency Condition]
SECTION 2: [Secondary Condition]
SECTION 3: [Tertiary Condition]
SECTION 4: Combined Management & Referral

NEVER mix drug protocols across sections.
Each section must cite its own page source.

RULE TC5-B — SEVERITY ESCALATION:
BP ≥160/110 = SEVERE pre-eclampsia regardless of other factors.
Severe PE overrides mild PE management entirely.
Severe PE at ANY gestational age → deliver after stabilization.
State this explicitly: "Severe pre-eclampsia — deliver after stabilization
irrespective of gestational age."

RULE TC5-C — STEROID INDICATION CLARITY IN MULTI-CONDITION:
When steroids are needed AND GDM is confirmed:
- State steroid indication: "Betamethasone for fetal lung maturity
  (gestational age 26 weeks, preterm delivery anticipated)"
- Then separately: "BECAUSE GDM is confirmed, monitor blood glucose
  closely for 72 hours post-injection and adjust insulin accordingly
  (Page 20, GDM guideline)"
These must appear as TWO separate statements, not merged.

RULE TC5-D — RISK SCORE CONSISTENCY (HARD RULE):
The total_score in rule_output.total_score MUST exactly match
the risk score mentioned in the answer text.
Before finalizing output, verify: rule_output.total_score == answer_score.
If they differ → recompute and correct before output.

RULE TC5-E — ADOLESCENT AGE FLAG:
Age <20 years = adolescent pregnancy = HIGH RISK factor.
ALWAYS flag this in triggered_rules and mention in answer.
Never ignore age as a risk factor even when other conditions are present.
```

---
---

## OVERALL TEST SCORING MATRIX

| Test | Rule Tested | Pass Criteria Summary | Weight |
|------|-------------|----------------------|--------|
| TC1 | Topic Isolation + Negation | Zero GDM content, correct topics only | 20% |
| TC2 | Drug Completeness | All 3 antihypertensives + MgSO4 named | 20% |
| TC3 | Steroid Gating | Steroids cited from IUGR section, not GDM | 20% |
| TC4 | Differential Clarity | "Suspected" language, no false confirmation | 20% |
| TC5 | All Rules Regression | Clean 3-condition separation, score consistent | 20% |

**Score each test:**
- All checklist items pass = 20 points
- Each failed item = -2 points
- Target: 80/100 to close the 30% gap
- Target: 95/100 for production readiness

---

## MASTER CORRECTIVE PROMPT
### Apply this if running all tests at once

```
MEDICAL RAG CLINICAL REASONING RULES v2.0
Apply ALL rules below for every query:

=== NEGATION & TOPIC RULES ===
1. NEGATION AWARENESS: "No history of X" = X is ABSENT. Never include
   absent conditions in recommendations, topics, or drug protocols.

2. TOPIC ISOLATION: Only use retrieved chunks whose primary topic matches
   a CONFIRMED PRESENT condition. Discard GDM chunks if no GDM. Discard
   thyroid chunks if no thyroid disorder.

=== DIAGNOSIS RULES ===
3. SUSPECTED VS CONFIRMED:
   Pre-eclampsia = BP ≥140/90 AND proteinuria. If proteinuria unknown →
   ALWAYS write "Suspected pre-eclampsia — confirm at referral center."
   Never confirm a diagnosis without all required criteria.

4. SEVERITY ACCURACY:
   Mild PE = BP 140-159/90-109 + proteinuria trace to 2+
   Severe PE = BP ≥160/110 + proteinuria 3+ or 4+
   State classification explicitly. Never misclassify.

=== DRUG RULES ===
5. ANTIHYPERTENSIVE COMPLETENESS: For BP ≥140/90, ALWAYS list:
   - Alpha Methyl Dopa 250mg BD/TDS (first line)
   - Nifedipine 10-20mg BD/TDS (second line)
   - Labetalol 100mg BD (third line)
   - MgSO4 prophylaxis in pre-eclampsia setting

6. STEROID GATING: Recommend steroids ONLY if BOTH:
   - Gestational age 24-34 weeks AND
   - Early delivery is planned OR IUGR/fetal compromise confirmed
   If GDM is also present, add glucose monitoring separately.

=== STRUCTURE RULES ===
7. MULTI-CONDITION SEPARATION: Separate sections for each condition.
   Never mix drug protocols across conditions.

8. RISK SCORE CONSISTENCY: rule_output.total_score MUST match
   the score stated in the answer text. Verify before output.

9. DANGER SIGNS MANDATORY: For any BP ≥140/90, include danger signs
   counseling: headache, visual changes, epigastric pain, oliguria,
   seizures, reduced fetal movements.

10. REFERRAL URGENCY: State explicit timeframe:
    Mild disease → "Within 24 hours"
    Severe PE → "Within 2-4 hours"
    Eclampsia/emergency → "Immediately"
```

---

## PIPELINE IMPROVEMENT TRACKING

| Run | TC1 | TC2 | TC3 | TC4 | TC5 | Total | Gap Remaining |
|-----|-----|-----|-----|-----|-----|-------|---------------|
| Baseline (pre-fix) | ❌ | ❌ | ❌ | ❌ | ❌ | 0/100 | 30% |
| After TC1 prompt | ⚠️ | ❌ | ❌ | ❌ | ❌ | ~35/100 | ~25% |
| After TC2 prompt | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | ~50/100 | ~18% |
| After TC3 prompt | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | ~65/100 | ~12% |
| After TC4 prompt | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ~80/100 | ~7% |
| After TC5 prompt | ✅ | ✅ | ✅ | ✅ | ⚠️ | ~90/100 | ~3% |
| After code fixes | ✅ | ✅ | ✅ | ✅ | ✅ | ~97/100 | <1% |

Fill this table as you run each test to track improvement.

---

*Test Suite Version: 1.0.0*
*Document: test1.md*
*Pipeline: Medical High-Risk Pregnancy RAG*
*Model: mistral:7b-instruct via Ollama*
*Last Updated: 2026-02-20*
