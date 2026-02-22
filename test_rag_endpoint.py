"""
Test script to verify RAG Pipeline is working correctly
"""
import requests
import json

# Test data
test_data = {
    "clinical_summary": "26-year-old G2P1 at 24 weeks gestation with mild anemia (Hb 11.5) and normal blood pressure",
    "structured_data": {
        "patient_info": {
            "patientId": "TEST-001",
            "name": "Test Patient",
            "age": 26,
            "gravida": 2,
            "para": 1,
            "livingChildren": 1,
            "gestationalWeeks": 24,
            "lmpDate": "2024-08-01",
            "estimatedDueDate": "2025-05-08"
        },
        "vitals": {
            "weightKg": 65.0,
            "heightCm": 160.0,
            "bmi": 25.4,
            "bpSystolic": 120,
            "bpDiastolic": 80,
            "pulseRate": 78,
            "respiratoryRate": 18,
            "temperatureCelsius": 37.0,
            "pallor": False,
            "pedalEdema": False
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
            "thyroidDisorder": False,
            "smoking": False,
            "tobaccoUse": False,
            "alcoholUse": False
        },
        "lab_reports": {
            "hemoglobin": 11.5,
            "plateletCount": None,
            "bloodGroup": "O+",
            "rhNegative": False,
            "urineProtein": False,
            "urineSugar": False,
            "fastingBloodSugar": 90.0,
            "ogtt2hrPG": None,
            "hivPositive": False,
            "syphilisPositive": False,
            "serumCreatinine": None,
            "ast": None,
            "alt": None
        },
        "obstetric_history": {
            "birthOrder": None,
            "interPregnancyInterval": None,
            "stillbirthCount": 0,
            "abortionCount": 0,
            "pretermHistory": False
        },
        "pregnancy_details": {
            "twinPregnancy": False,
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
        }
    },
    "care_level": "PHC",
    "verbose": False
}

print("=" * 60)
print("Testing RAG Pipeline Endpoint")
print("=" * 60)

try:
    # Test the endpoint
    response = requests.post(
        "http://localhost:8000/assess-structured",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! RAG Pipeline is working correctly!")
        result = response.json()
        print("\n" + "=" * 60)
        print("RISK ASSESSMENT RESULT:")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        # Extract key information
        print("\n" + "=" * 60)
        print("KEY FINDINGS:")
        print("=" * 60)
        print(f"Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"Risk Score: {result.get('risk_score', 'N/A')}/100")
        print(f"Requires Doctor: {result.get('requires_doctor_consultation', 'N/A')}")
        print(f"Urgency: {result.get('urgency', 'N/A')}")
        
        if result.get('risk_factors'):
            print(f"\nRisk Factors ({len(result['risk_factors'])}):")
            for i, factor in enumerate(result['risk_factors'], 1):
                print(f"  {i}. {factor}")
        
        if result.get('recommendations'):
            print(f"\nRecommendations ({len(result['recommendations'])}):")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
        
    elif response.status_code == 422:
        print("\n❌ VALIDATION ERROR (422)")
        print("\nThe RAG Pipeline rejected the data due to validation errors.")
        print("\nError Details:")
        try:
            error_detail = response.json()
            print(json.dumps(error_detail, indent=2))
        except:
            print(response.text)
    else:
        print(f"\n❌ ERROR: Unexpected status code {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR")
    print("Cannot connect to RAG Pipeline at http://localhost:8000")
    print("Make sure the RAG Pipeline is running (Terminal 4)")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
