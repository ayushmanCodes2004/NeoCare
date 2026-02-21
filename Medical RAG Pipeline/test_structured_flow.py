#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test structured input flow: Input → Deterministic Rules → RAG → Output
Shows exactly what happens at each step.
"""

import sys
import json

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Your structured input
structured_input = {
    "clinical_summary": "28-year-old G1P0 at 20 weeks, first pregnancy, Hb 10.6, BP 110/72, no edema, no symptoms, fetal movements present, no known conditions, regular ANC attendance.",
    "structured_data": {
        "patient_info": {
            "patientId": "ANC-MED-002",
            "name": "Pooja Singh",
            "age": 28,
            "gravida": 1,
            "para": 0,
            "livingChildren": 0,
            "gestationalWeeks": 20
        },
        "medical_history": {
            "previousLSCS": False,
            "knownDiabetes": False,
            "knownHypertension": False,
            "thyroidDisorder": False,
            "rhNegative": False,
            "gdmCurrentPregnancy": False,
            "obstetricHistory": {
                "stillbirth": 0,
                "abortion": 0,
                "pretermDelivery": 0
            }
        },
        "vitals": {
            "bpSystolic": 110,
            "bpDiastolic": 72,
            "pulseRate": 80,
            "pedalEdema": False,
            "breathlessnessAtRest": False
        },
        "lab_reports": {
            "hemoglobin": 10.6,
            "urineProtein": False,
            "urineProteinDipstick": "negative",
            "fastingBloodSugar": 0,
            "twoHourPG": 0,
            "tshLevel": 0
        },
        "pregnancy_details": {
            "twinPregnancy": False,
            "fetalMovements": "present"
        },
        "current_symptoms": {
            "headache": False,
            "visualDisturbances": False,
            "epigastricPain": False,
            "giddiness": False,
            "weakness": False,
            "breathlessnessAtRest": False
        },
        "visit_metadata": {
            "visitType": "Routine ANC",
            "visitNumber": 2,
            "healthWorkerId": "ANM-115",
            "subCenterId": "SC-033",
            "district": "Jaipur",
            "state": "Rajasthan",
            "timestamp": "2026-02-20T11:30:00Z"
        }
    },
    "care_level": "PHC"
}

print("="*70)
print("STRUCTURED INPUT FLOW TEST")
print("="*70)

# STEP 1: Extract features from structured data
print("\n[STEP 1] EXTRACT FEATURES FROM STRUCTURED DATA")
print("-"*70)

features = {
    'age': structured_input['structured_data']['patient_info']['age'],
    'gestational_age_weeks': structured_input['structured_data']['patient_info']['gestationalWeeks'],
    'hemoglobin': structured_input['structured_data']['lab_reports']['hemoglobin'],
    'systolic_bp': structured_input['structured_data']['vitals']['bpSystolic'],
    'diastolic_bp': structured_input['structured_data']['vitals']['bpDiastolic'],
    'fbs': structured_input['structured_data']['lab_reports']['fastingBloodSugar'] if structured_input['structured_data']['lab_reports']['fastingBloodSugar'] > 0 else None,
    'ogtt_2hr_pg': structured_input['structured_data']['lab_reports']['twoHourPG'] if structured_input['structured_data']['lab_reports']['twoHourPG'] > 0 else None,
    'proteinuria': structured_input['structured_data']['lab_reports']['urineProtein'],
    'seizures': False,
    'twin_pregnancy': structured_input['structured_data']['pregnancy_details']['twinPregnancy'],
    'prior_cesarean': structured_input['structured_data']['medical_history']['previousLSCS'],
    'placenta_previa': False,
}

print("Extracted Features:")
for key, value in features.items():
    if value is not None and value != False:
        print(f"  {key}: {value}")

# STEP 2: Run deterministic rule engine
print("\n[STEP 2] RUN DETERMINISTIC RULE ENGINE")
print("-"*70)

from clinical_rules import run_rule_engine

rule_result = run_rule_engine(features, verbose=True)

print(f"\nRule Engine Output:")
print(f"  Risk Level: {rule_result.risk_level}")
print(f"  Risk Score: {rule_result.risk_score}")
print(f"  Confirmed Conditions: {rule_result.confirmed_conditions}")
print(f"  Suspected Conditions: {rule_result.suspected_conditions}")
print(f"  Triggered Rules: {rule_result.triggered_rules}")
print(f"  Referral Facility: {rule_result.referral_facility}")
print(f"  Immediate Referral: {rule_result.immediate_referral}")

# STEP 3: Check against HIGH_RISK_CONDITIONS (Section 13)
print("\n[STEP 3] CHECK AGAINST HIGH_RISK_CONDITIONS (Section 13)")
print("-"*70)

HIGH_RISK_CONDITIONS = [
    "severe_anaemia",  # Only severe, NOT mild or moderate
    "pregnancy_induced_hypertension",
    "pre_eclampsia",
    "pre_eclamptic_toxemia",
    "syphilis_positive",
    "hiv_positive",
    "gestational_diabetes_mellitus",
    "gdm_confirmed",
    "hypothyroidism",
    "hypothyroid_overt",
    "hypothyroid_subclinical",
    "young_primi",
    "elderly_gravida",
    "advanced_maternal_age",
    "twin_pregnancy",
    "multiple_pregnancy",
    "malpresentation",
    "previous_lscs",
    "previous_cs",
    "placenta_previa",
    "low_lying_placenta",
    "bad_obstetric_history",
    "rh_negative",
    "iugr_suspected",
    "systemic_illness_current_or_past"
]

is_high_risk = any(rule in HIGH_RISK_CONDITIONS for rule in rule_result.triggered_rules)

print(f"Triggered Rules: {rule_result.triggered_rules}")
print(f"High-Risk Conditions from Section 13: {[r for r in rule_result.triggered_rules if r in HIGH_RISK_CONDITIONS]}")
print(f"isHighRisk: {is_high_risk}")
print(f"\nExplanation:")
if is_high_risk:
    print(f"  Patient HAS high-risk condition(s) from Section 13 master list")
else:
    print(f"  Patient has NO high-risk conditions from Section 13 master list")
    print(f"  Note: mild_anaemia (Hb 10-10.9) is NOT in Section 13 high-risk list")
    print(f"        Only severe_anaemia (Hb <7) is considered high-risk")

# STEP 4: Build detected risks for output
print("\n[STEP 4] BUILD DETECTED RISKS FOR OUTPUT")
print("-"*70)

detected_risks = []
for flag in rule_result.risk_flags:
    condition = flag['condition']
    if condition not in detected_risks:
        detected_risks.append(condition)

print(f"Detected Risks: {detected_risks}")

# STEP 5: Expected output structure
print("\n[STEP 5] EXPECTED OUTPUT STRUCTURE")
print("-"*70)

expected_output = {
    "isHighRisk": is_high_risk,
    "riskLevel": rule_result.risk_level,
    "detectedRisks": detected_risks,
    "explanation": f"Risk Assessment: {rule_result.risk_level}. Patient presents with {len(detected_risks)} risk factor(s): {', '.join(detected_risks)}.",
    "confidence": 0.70,  # Minimum for structured JSON
    "recommendation": "Continue routine antenatal care with regular monitoring. Schedule 75g OGTT for GDM screening at 24-28 weeks.",
    "patientId": structured_input['structured_data']['patient_info']['patientId'],
    "patientName": structured_input['structured_data']['patient_info']['name'],
    "age": structured_input['structured_data']['patient_info']['age'],
    "gestationalWeeks": structured_input['structured_data']['patient_info']['gestationalWeeks'],
    "visitMetadata": structured_input['structured_data']['visit_metadata']
}

print(json.dumps(expected_output, indent=2))

# STEP 6: Summary
print("\n" + "="*70)
print("FLOW SUMMARY")
print("="*70)
print(f"1. Structured Input → Features Extracted")
print(f"2. Features → Deterministic Rule Engine")
print(f"   - Detected: {', '.join(rule_result.triggered_rules)}")
print(f"   - Risk Score: {rule_result.risk_score} → Risk Level: {rule_result.risk_level}")
print(f"3. Rule Engine → Check Section 13 High-Risk List")
print(f"   - isHighRisk: {is_high_risk}")
print(f"   - Reason: {'Has high-risk condition' if is_high_risk else 'No high-risk conditions (mild_anaemia NOT in Section 13)'}")
print(f"4. Rule Engine + RAG → Generate Explanation & Recommendation")
print(f"5. Output → Clean JSON Response")
print("="*70)

print("\n[SUCCESS] Flow completed successfully!")
