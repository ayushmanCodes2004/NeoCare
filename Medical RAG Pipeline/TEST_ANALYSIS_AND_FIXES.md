# Test Suite Analysis & Implementation Plan

## 📋 Test Suite Overview

**Source:** test1.md  
**Goal:** Close 30% alignment gap  
**Target Score:** 95/100 for production readiness

### Test Cases Summary

| Test | Focus | Current Issues | Priority |
|------|-------|----------------|----------|
| TC1 | Topic Isolation + Negation | GDM chunks for non-diabetic | 🔴 CRITICAL |
| TC2 | Drug Completeness | Missing antihypertensive drugs | 🔴 CRITICAL |
| TC3 | Steroid Gating | Wrong source citation | 🟡 HIGH |
| TC4 | Differential Clarity | Missing "suspected" language | 🟡 HIGH |
| TC5 | All Rules Combined | Multi-condition separation | 🔴 CRITICAL |

---

## 🔧 Implementation Plan

### Phase 1: Negation Awareness & Topic Isolation (TC1)
**Files to modify:**
1. `layer1_extractor.py` - Add negation detection
2. `layer2_retrieval.py` - Add topic-based chunk filtering
3. `layer4_reasoning.py` - Update system prompt with TC1 rules

**Key Changes:**
- Detect "no history of", "denies", "without" patterns
- Filter chunks by confirmed conditions only
- Never include negated conditions in comorbidities

### Phase 2: Drug Completeness (TC2)
**Files to modify:**
1. `layer4_reasoning.py` - Enhance drug validation
2. `config_production.py` - Add drug protocol definitions

**Key Changes:**
- Mandatory enumeration of all 3 antihypertensives
- MgSO4 for pre-eclampsia
- Severity classification (mild vs severe)
- Delivery timing guidance

### Phase 3: Steroid Gating (TC3)
**Files to modify:**
1. `layer4_reasoning.py` - Add steroid indication tracking
2. `layer3_rules.py` - Add IUGR detection

**Key Changes:**
- Separate IUGR steroids from GDM steroids
- Correct source citation (Page 22 vs Page 20)
- Fundal height-based IUGR detection

### Phase 4: Differential Clarity (TC4)
**Files to modify:**
1. `layer4_reasoning.py` - Add epistemic honesty rules
2. `layer1_extractor.py` - Track missing lab results

**Key Changes:**
- "Suspected" language when labs unavailable
- Danger signs counseling mandatory
- Referral urgency grading

### Phase 5: Multi-Condition Separation (TC5)
**Files to modify:**
1. `layer4_reasoning.py` - Add section structuring
2. `layer4_reasoning.py` - Enhance consistency validation

**Key Changes:**
- Clean section separation for multiple conditions
- Risk score consistency check
- Adolescent age flagging

---

## 🚀 Starting Implementation

I will now implement all fixes systematically...
