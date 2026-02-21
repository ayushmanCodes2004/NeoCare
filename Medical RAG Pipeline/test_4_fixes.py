"""
Test script to verify 4 critical fixes
"""

import requests
import json

# Test case ANC-MED-002: Twin pregnancy at 28 weeks
test_data = {
    "clinical_summary": "31-year-old G2P1 at 28 weeks with twin pregnancy, normal vitals",
    "structured_data": {
        "patient_info": {
            "patientId": "ANC-MED-002",
            "name": "Test Patient",
            "age": 31,
            "gravida": 2,
            "para": 1,
            "gestationalWeeks": 28
        },
        "medical_history": {
            "previousLSCS": False,
            "chronicHypertension": False,
            "diabetes": False
        },
        "vitals": {
            "bpSystolic": 120,
            "bpDiastolic": 80
        },
        "lab_reports": {
            "hemoglobin": 11.5,
            "fastingBloodSugar": None  # No OGTT done - should trigger FIX 4
        },
        "pregnancy_details": {
            "twinPregnancy": True
        },
        "current_symptoms": {
            "headache": False
        }
    }
}

print("="*70)
print("TESTING 4 CRITICAL FIXES")
print("="*70)
print("\nTest Case: ANC-MED-002 (Twin pregnancy, 28 weeks, no OGTT)")
print("\nExpected Results:")
print("  FIX 1: isHighRisk = true (twin_pregnancy in triggered_rules)")
print("  FIX 2: confidence >= 0.70 (structured JSON input)")
print("  FIX 3: recommendation from RECOMMENDATION_MAP only (max 200 chars)")
print("  FIX 4: gdm_screening_overdue flagged (GA 28 weeks, no OGTT)")
print("\nSending request...")

try:
    response = requests.post(
        "http://localhost:8000/assess-structured",
        json=test_data,
        timeout=120
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
        
        # FIX 1: Check isHighRisk
        is_high_risk = result.get('isHighRisk')
        print(f"\nFIX 1 - isHighRisk Logic:")
        print(f"  isHighRisk: {is_high_risk}")
        if is_high_risk:
            print("  ✅ PASS: isHighRisk=true (twin_pregnancy detected)")
        else:
            print("  ❌ FAIL: isHighRisk should be true for twin pregnancy")
        
        # FIX 2: Check confidence >= 0.70
        confidence = result.get('confidence', 0)
        print(f"\nFIX 2 - Confidence Formula:")
        print(f"  Confidence: {confidence}")
        if confidence >= 0.70:
            print("  ✅ PASS: Confidence >= 0.70 for structured JSON")
        else:
            print(f"  ❌ FAIL: Confidence should be >= 0.70, got {confidence}")
        
        # FIX 3: Check recommendation
        recommendation = result.get('recommendation', '')
        print(f"\nFIX 3 - Recommendation Isolation:")
        print(f"  Recommendation: {recommendation}")
        print(f"  Length: {len(recommendation)} chars")
        
        # Check for bad patterns
        bad_patterns = ['===', 'Page', 'pdf', '...', 'truncated']
        has_bad_pattern = any(pattern in recommendation for pattern in bad_patterns)
        
        if len(recommendation) <= 200 and not has_bad_pattern:
            print("  ✅ PASS: Clean recommendation from RECOMMENDATION_MAP")
        else:
            if len(recommendation) > 200:
                print(f"  ❌ FAIL: Recommendation too long ({len(recommendation)} > 200)")
            if has_bad_pattern:
                print(f"  ❌ FAIL: Recommendation contains bad patterns")
        
        # FIX 4: Check for GDM screening overdue
        detected_risks = result.get('detectedRisks', [])
        explanation = result.get('explanation', '')
        print(f"\nFIX 4 - GDM Screening Due Check:")
        print(f"  Detected Risks: {detected_risks}")
        
        # Check if screening overdue is mentioned
        screening_mentioned = 'screening' in explanation.lower() or 'ogtt' in explanation.lower()
        if screening_mentioned:
            print("  ✅ PASS: GDM screening overdue flagged")
        else:
            print("  ⚠️  INFO: GDM screening not mentioned (may be in full output)")
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        fixes_passed = 0
        if is_high_risk:
            fixes_passed += 1
        if confidence >= 0.70:
            fixes_passed += 1
        if len(recommendation) <= 200 and not has_bad_pattern:
            fixes_passed += 1
        if screening_mentioned:
            fixes_passed += 1
        
        print(f"\nFixes Passed: {fixes_passed}/4")
        
        if fixes_passed == 4:
            print("✅ ALL FIXES VERIFIED")
        else:
            print(f"❌ {4 - fixes_passed} FIX(ES) FAILED")
        
    else:
        print(f"\n❌ ERROR: API returned status code {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*70)
