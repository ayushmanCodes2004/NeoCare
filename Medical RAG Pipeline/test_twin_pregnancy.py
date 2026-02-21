"""
Test script to verify twin pregnancy risk classification
"""

import requests
import json

# Test case: Twin pregnancy only (should be MODERATE risk, score 3)
test_data = {
    "clinical_summary": "31-year-old pregnant woman at 28 weeks with twin pregnancy",
    "structured_data": {
        "patient_info": {
            "patientId": "ANC-TRICK-003",
            "name": "Rekha Das",
            "age": 31,
            "gravida": 2,
            "para": 1,
            "livingChildren": 1,
            "gestationalWeeks": 28,
            "lmpDate": "2025-08-01",
            "estimatedDueDate": "2026-05-08"
        },
        "medical_history": {
            "previousLSCS": False,
            "badObstetricHistory": False,
            "previousStillbirth": False,
            "previousPretermDelivery": False,
            "previousAbortion": False,
            "systemicIllness": "None",
            "chronicHypertension": False,
            "diabetes": False,
            "thyroidDisorder": False
        },
        "vitals": {
            "weightKg": 65,
            "heightCm": 160,
            "bmi": 25.4,
            "bpSystolic": 120,
            "bpDiastolic": 80,
            "pulseRate": 82,
            "respiratoryRate": 18,
            "temperatureCelsius": 36.8,
            "pallor": False,
            "pedalEdema": False
        },
        "lab_reports": {
            "hemoglobin": 11.5,
            "plateletCount": 200000,
            "bloodGroup": "O",
            "rhNegative": False,
            "urineProtein": False,
            "urineSugar": False,
            "fastingBloodSugar": 85,
            "hivPositive": False,
            "syphilisPositive": False,
            "serumCreatinine": 0.7,
            "ast": 28,
            "alt": 25
        },
        "pregnancy_details": {
            "twinPregnancy": True,
            "malpresentation": False,
            "placentaPrevia": False,
            "reducedFetalMovement": False,
            "amnioticFluidNormal": True,
            "umbilicalDopplerAbnormal": False
        },
        "current_symptoms": {
            "headache": False,
            "visualDisturbance": False,
            "epigastricPain": False,
            "decreasedUrineOutput": False,
            "bleedingPerVagina": False,
            "convulsions": False
        },
        "visit_metadata": {
            "visitType": "Routine ANC",
            "visitNumber": 4,
            "healthWorkerId": "ASHA-455",
            "subCenterId": None,
            "district": "Mayurbhanj",
            "state": "Odisha",
            "timestamp": None
        }
    },
    "care_level": "PHC",
    "verbose": False
}

print("="*70)
print("TESTING TWIN PREGNANCY RISK CLASSIFICATION")
print("="*70)
print("\nTest Case: 31-year-old at 28 weeks with twin pregnancy")
print("Expected: MODERATE risk (score 3)")
print("\nSending request to API...")

try:
    response = requests.post(
        "http://localhost:8000/assess-structured",
        json=test_data,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*70)
        print("RESULT")
        print("="*70)
        print(json.dumps(result, indent=2))
        
        print("\n" + "="*70)
        print("VERIFICATION")
        print("="*70)
        
        # Verify risk level
        risk_level = result.get('riskLevel')
        is_high_risk = result.get('isHighRisk')
        detected_risks = result.get('detectedRisks', [])
        
        print(f"Risk Level: {risk_level}")
        print(f"Is High Risk: {is_high_risk}")
        print(f"Detected Risks: {detected_risks}")
        
        # Check if correct
        if risk_level == "MODERATE":
            print("\n✅ PASS: Risk level correctly classified as MODERATE")
        else:
            print(f"\n❌ FAIL: Expected MODERATE, got {risk_level}")
        
        if is_high_risk:
            print("✅ PASS: isHighRisk=True (MODERATE is high-risk)")
        else:
            print("❌ FAIL: isHighRisk should be True for MODERATE risk")
        
        if "Multiple Gestation (Twins)" in detected_risks or "Twin Pregnancy" in detected_risks:
            print("✅ PASS: Twin pregnancy detected in risks")
        else:
            print(f"❌ FAIL: Twin pregnancy not detected. Got: {detected_risks}")
        
    else:
        print(f"\n❌ ERROR: API returned status code {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*70)
