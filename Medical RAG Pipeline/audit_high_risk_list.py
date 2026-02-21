#!/usr/bin/env python3
"""Audit HIGH_RISK_CONDITIONS against Section 13 of clinical_thresholds.md"""

print('='*70)
print('HIGH-RISK CONDITIONS AUDIT (Section 13)')
print('='*70)

# Section 13 from clinical_thresholds.md
RULEBOOK_HIGH_RISK_CONDITIONS = [
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
    "bad_obstetric_history",
    "rh_negative",
    "systemic_illness_current_or_past"
]

# Read from api_server.py
import re
with open('api_server.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Extract HIGH_RISK_CONDITIONS from api_server.py
pattern = r'HIGH_RISK_CONDITIONS = \[(.*?)\]'
matches = re.findall(pattern, content, re.DOTALL)

if matches:
    # Parse the first occurrence
    conditions_str = matches[0]
    # Extract condition names
    code_conditions = re.findall(r'"([^"]+)"', conditions_str)
    
    print('\nRULEBOOK (Section 13):')
    for i, cond in enumerate(RULEBOOK_HIGH_RISK_CONDITIONS, 1):
        print(f'  {i:2d}. {cond}')
    
    print(f'\nCODE (api_server.py):')
    for i, cond in enumerate(code_conditions, 1):
        print(f'  {i:2d}. {cond}')
    
    print('\n' + '='*70)
    print('COMPARISON:')
    print('='*70)
    
    # Check for missing conditions
    missing_in_code = []
    for cond in RULEBOOK_HIGH_RISK_CONDITIONS:
        # Check for exact match or aliases
        found = False
        if cond in code_conditions:
            found = True
        elif cond == "elderly_gravida" and "advanced_maternal_age" in code_conditions:
            found = True  # Alias
        elif cond == "previous_lscs" and "previous_cs" in code_conditions:
            found = True  # Alias
        elif cond == "gestational_diabetes_mellitus" and "gdm_confirmed" in code_conditions:
            found = True  # Alias
        
        if not found:
            missing_in_code.append(cond)
    
    # Check for extra conditions in code
    extra_in_code = []
    for cond in code_conditions:
        # Check if it's in rulebook or is a valid alias
        found = False
        if cond in RULEBOOK_HIGH_RISK_CONDITIONS:
            found = True
        elif cond == "advanced_maternal_age" and "elderly_gravida" in RULEBOOK_HIGH_RISK_CONDITIONS:
            found = True  # Alias
        elif cond == "previous_cs" and "previous_lscs" in RULEBOOK_HIGH_RISK_CONDITIONS:
            found = True  # Alias
        elif cond == "gdm_confirmed" and "gestational_diabetes_mellitus" in RULEBOOK_HIGH_RISK_CONDITIONS:
            found = True  # Alias
        elif cond in ["hypothyroid_overt", "hypothyroid_subclinical"] and "hypothyroidism" in RULEBOOK_HIGH_RISK_CONDITIONS:
            found = True  # Subcategories of hypothyroidism
        elif cond == "iugr_suspected":
            # Check if this should be in the list
            print(f'\n⚠ WARNING: "{cond}" is in code but NOT in Section 13 rulebook')
            print('   However, it IS in Section 14 RISK_SCORE_MATRIX')
            found = True  # Accept it
        
        if not found:
            extra_in_code.append(cond)
    
    # CRITICAL CHECK: mild_anaemia and moderate_anaemia should NOT be in the list
    critical_errors = []
    if "mild_anaemia" in code_conditions:
        critical_errors.append('✗ CRITICAL: "mild_anaemia" should NOT be in HIGH_RISK_CONDITIONS (only severe_anaemia per Section 13)')
    if "moderate_anaemia" in code_conditions:
        critical_errors.append('✗ CRITICAL: "moderate_anaemia" should NOT be in HIGH_RISK_CONDITIONS (only severe_anaemia per Section 13)')
    if "hypertension" in code_conditions and "pregnancy_induced_hypertension" not in code_conditions:
        print('\n⚠ NOTE: "hypertension" is in code. Rulebook uses "pregnancy_induced_hypertension"')
        print('   This is acceptable as they refer to the same condition')
    
    # Report results
    if critical_errors:
        print('\n' + '='*70)
        print('CRITICAL ERRORS:')
        print('='*70)
        for error in critical_errors:
            print(error)
    
    if missing_in_code:
        print('\n' + '='*70)
        print('MISSING IN CODE (should be added):')
        print('='*70)
        for cond in missing_in_code:
            print(f'  ✗ {cond}')
    
    if extra_in_code:
        print('\n' + '='*70)
        print('EXTRA IN CODE (not in rulebook):')
        print('='*70)
        for cond in extra_in_code:
            print(f'  ⚠ {cond}')
    
    if not critical_errors and not missing_in_code and not extra_in_code:
        print('\n✓ HIGH_RISK_CONDITIONS list matches Section 13 (with acceptable aliases)')
    
    print('\n' + '='*70)
    print('KEY VERIFICATION:')
    print('='*70)
    print(f'✓ severe_anaemia in list: {"severe_anaemia" in code_conditions}')
    print(f'✓ mild_anaemia NOT in list: {"mild_anaemia" not in code_conditions}')
    print(f'✓ moderate_anaemia NOT in list: {"moderate_anaemia" not in code_conditions}')
    print('='*70)

else:
    print('ERROR: Could not find HIGH_RISK_CONDITIONS in api_server.py')
