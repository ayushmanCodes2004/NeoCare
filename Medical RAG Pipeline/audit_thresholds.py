#!/usr/bin/env python3
"""Audit clinical_rules.py against clinical_thresholds.md"""

from clinical_rules import (
    ANAEMIA_THRESHOLDS, 
    HYPERTENSION_SYSTOLIC_THRESHOLD,
    HYPERTENSION_DIASTOLIC_THRESHOLD,
    GDM_TEST,
    AGE_RISK_THRESHOLDS,
    RISK_SCORE_MATRIX,
    RISK_LEVELS
)

print('='*70)
print('THRESHOLD AUDIT: clinical_rules.py vs clinical_thresholds.md')
print('='*70)

issues = []

# 1. ANAEMIA
print('\n1. ANAEMIA THRESHOLDS (Section 1):')
print(f'   Mild:     10.0-10.9 g/dL → Score {ANAEMIA_THRESHOLDS["mild"]["score"]}')
print(f'   Moderate: 7.0-9.9 g/dL → Score {ANAEMIA_THRESHOLDS["moderate"]["score"]}')
print(f'   Severe:   <7.0 g/dL → Score {ANAEMIA_THRESHOLDS["severe"]["score"]}')
if (ANAEMIA_THRESHOLDS["mild"]["score"] == 1 and 
    ANAEMIA_THRESHOLDS["moderate"]["score"] == 2 and 
    ANAEMIA_THRESHOLDS["severe"]["score"] == 4):
    print('   Status: ✓ MATCH')
else:
    issues.append('Anaemia scores do not match rulebook')
    print('   Status: ✗ MISMATCH')

# 2. HYPERTENSION
print('\n2. HYPERTENSION THRESHOLDS (Section 2):')
print(f'   Systolic: ≥{HYPERTENSION_SYSTOLIC_THRESHOLD} mmHg')
print(f'   Diastolic: ≥{HYPERTENSION_DIASTOLIC_THRESHOLD} mmHg')
if HYPERTENSION_SYSTOLIC_THRESHOLD == 140 and HYPERTENSION_DIASTOLIC_THRESHOLD == 90:
    print('   Status: ✓ MATCH')
else:
    issues.append('Hypertension thresholds do not match rulebook')
    print('   Status: ✗ MISMATCH')

# 3. GDM
print('\n3. GDM THRESHOLDS (Section 3):')
print(f'   2hr PG: ≥{GDM_TEST["positive_threshold_2hr_pg"]} mg/dL')
if GDM_TEST["positive_threshold_2hr_pg"] == 140:
    print('   Status: ✓ MATCH')
else:
    issues.append('GDM threshold does not match rulebook')
    print('   Status: ✗ MISMATCH')

# 4. AGE
print('\n4. AGE THRESHOLDS (Section 5):')
print(f'   Young Primi: <{AGE_RISK_THRESHOLDS["young_primi"]["age_max"]} years → Score {AGE_RISK_THRESHOLDS["young_primi"]["score"]}')
print(f'   Advanced: ≥{AGE_RISK_THRESHOLDS["advanced_maternal_age"]["age_min"]} years → Score {AGE_RISK_THRESHOLDS["advanced_maternal_age"]["score"]}')
if (AGE_RISK_THRESHOLDS["young_primi"]["age_max"] == 20 and
    AGE_RISK_THRESHOLDS["young_primi"]["score"] == 3 and
    AGE_RISK_THRESHOLDS["advanced_maternal_age"]["age_min"] == 35 and
    AGE_RISK_THRESHOLDS["advanced_maternal_age"]["score"] == 3):
    print('   Status: ✓ MATCH')
else:
    issues.append('Age thresholds do not match rulebook')
    print('   Status: ✗ MISMATCH')

# 5. RISK SCORING MATRIX (Section 14)
print('\n5. RISK SCORING MATRIX (Section 14):')
rulebook_scores = {
    'severe_anaemia': 4,
    'moderate_anaemia': 2,
    'mild_anaemia': 1,
    'severe_pre_eclampsia': 4,
    'pre_eclampsia': 3,
    'hypertension': 3,
    'eclampsia': 5,
    'gdm': 2,
    'hypothyroid_overt': 2,
    'hypothyroid_subclinical': 1,
    'twin_pregnancy': 3,
    'advanced_maternal_age': 3,
    'young_primi': 3,
    'previous_cs': 2,
    'placenta_previa': 4,
    'iugr_suspected': 3,
}

score_mismatches = []
for condition, expected_score in rulebook_scores.items():
    if condition in RISK_SCORE_MATRIX:
        actual_score = RISK_SCORE_MATRIX[condition][0]
        if actual_score != expected_score:
            score_mismatches.append(f'   ✗ {condition}: expected {expected_score}, got {actual_score}')
            print(f'   ✗ {condition}: expected {expected_score}, got {actual_score}')
        else:
            print(f'   ✓ {condition}: {actual_score}')
    else:
        score_mismatches.append(f'   ✗ {condition}: MISSING')
        print(f'   ✗ {condition}: MISSING from RISK_SCORE_MATRIX')

if score_mismatches:
    issues.extend(score_mismatches)

# 6. RISK LEVELS (Section 14)
print('\n6. RISK LEVEL RANGES (Section 14):')
print(f'   LOW:      {RISK_LEVELS["LOW"]["score_min"]}-{RISK_LEVELS["LOW"]["score_max"]}')
print(f'   MODERATE: {RISK_LEVELS["MODERATE"]["score_min"]}-{RISK_LEVELS["MODERATE"]["score_max"]}')
print(f'   HIGH:     {RISK_LEVELS["HIGH"]["score_min"]}-{RISK_LEVELS["HIGH"]["score_max"]}')
print(f'   CRITICAL: {RISK_LEVELS["CRITICAL"]["score_min"]}+')

if (RISK_LEVELS["LOW"]["score_min"] == 0 and RISK_LEVELS["LOW"]["score_max"] == 2 and
    RISK_LEVELS["MODERATE"]["score_min"] == 3 and RISK_LEVELS["MODERATE"]["score_max"] == 5 and
    RISK_LEVELS["HIGH"]["score_min"] == 6 and RISK_LEVELS["HIGH"]["score_max"] == 8 and
    RISK_LEVELS["CRITICAL"]["score_min"] == 9):
    print('   Status: ✓ MATCH')
else:
    issues.append('Risk level ranges do not match rulebook')
    print('   Status: ✗ MISMATCH')

# SUMMARY
print('\n' + '='*70)
if issues:
    print(f'AUDIT RESULT: {len(issues)} ISSUE(S) FOUND')
    print('='*70)
    for issue in issues:
        print(issue)
else:
    print('AUDIT RESULT: ✓ ALL THRESHOLDS MATCH RULEBOOK')
print('='*70)
