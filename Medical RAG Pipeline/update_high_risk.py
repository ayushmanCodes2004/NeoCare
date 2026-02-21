#!/usr/bin/env python3
"""Update HIGH_RISK_CONDITIONS in api_server.py to match Section 13"""

with open('api_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace HIGH_RISK_CONDITIONS lists
in_high_risk_block = False
block_start = -1
indent = ""

i = 0
while i < len(lines):
    line = lines[i]
    
    # Detect start of HIGH_RISK_CONDITIONS block
    if 'HIGH_RISK_CONDITIONS = [' in line:
        in_high_risk_block = True
        block_start = i
        indent = line[:line.index('HIGH_RISK_CONDITIONS')]
        
        # Find the end of the list (closing bracket)
        j = i + 1
        while j < len(lines) and ']' not in lines[j]:
            j += 1
        
        # Replace the entire block
        new_block = [
            f'{indent}# FIX 1: isHighRisk based on GoI master high-risk list (Section 13)\n',
            f'{indent}# Source: clinical_thresholds.md Section 13 - Only SEVERE anaemia is high-risk\n',
            f'{indent}HIGH_RISK_CONDITIONS = [\n',
            f'{indent}    "severe_anaemia",  # Hb < 7 g/dL (NOT mild or moderate)\n',
            f'{indent}    "pregnancy_induced_hypertension",\n',
            f'{indent}    "pre_eclampsia",\n',
            f'{indent}    "pre_eclamptic_toxemia",\n',
            f'{indent}    "syphilis_positive",\n',
            f'{indent}    "hiv_positive",\n',
            f'{indent}    "gestational_diabetes_mellitus",\n',
            f'{indent}    "gdm_confirmed",\n',
            f'{indent}    "hypothyroidism",\n',
            f'{indent}    "hypothyroid_overt",\n',
            f'{indent}    "hypothyroid_subclinical",\n',
            f'{indent}    "young_primi",  # < 20 years\n',
            f'{indent}    "elderly_gravida",  # > 35 years\n',
            f'{indent}    "advanced_maternal_age",\n',
            f'{indent}    "twin_pregnancy",\n',
            f'{indent}    "multiple_pregnancy",\n',
            f'{indent}    "malpresentation",\n',
            f'{indent}    "previous_lscs",\n',
            f'{indent}    "previous_cs",\n',
            f'{indent}    "placenta_previa",\n',
            f'{indent}    "low_lying_placenta",\n',
            f'{indent}    "bad_obstetric_history",\n',
            f'{indent}    "rh_negative",\n',
            f'{indent}    "iugr_suspected",\n',
            f'{indent}    "systemic_illness_current_or_past"\n',
            f'{indent}]\n',
        ]
        
        # Find where the comment starts (2 lines before HIGH_RISK_CONDITIONS)
        comment_start = block_start - 1
        while comment_start >= 0 and '# FIX 1:' in lines[comment_start]:
            comment_start -= 1
        comment_start += 1
        
        # Replace from comment to end of list
        lines[comment_start:j+1] = new_block
        
        # Skip past the replaced section
        i = comment_start + len(new_block)
        continue
    
    i += 1

# Write back
with open('api_server.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Updated HIGH_RISK_CONDITIONS in api_server.py")
print("Changed: Only severe_anaemia (Hb < 7) is high-risk, NOT mild or moderate")
