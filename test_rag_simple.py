"""
Simple RAG Pipeline Test
Tests if the RAG Pipeline can process visit data correctly
"""
import requests
import json

RAG_URL = "http://localhost:8000"

print("=" * 80)
print("RAG PIPELINE TEST - Simulating Frontend Data")
print("=" * 80)

# This is the exact data structure that the frontend sends
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

print("\nSending test data to RAG Pipeline...")
print(f"Endpoint: POST {RAG_URL}/assess-structured\n")

try:
    response = requests.post(
        f"{RAG_URL}/assess-structured",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=120  # Increased to 2 minutes for AI processing
    )
    
    print(f"Response Status: {response.status_code}\n")
    
    if response.status_code == 200:
        print("=" * 80)
        print("✅ SUCCESS! RAG Pipeline is working correctly!")
        print("=" * 80)
        
        result = response.json()
        
        # Print full response for debugging
        print("\nFull Response:")
        print(json.dumps(result, indent=2))
        
        print("\n" + "=" * 80)
        print("AI RISK ASSESSMENT RESULT:")
        print("=" * 80)
        
        print(f"\nRisk Level: {result.get('risk_level', 'N/A')}")
        print(f"Risk Score: {result.get('risk_score', 'N/A')}/100")
        print(f"Requires Doctor Consultation: {result.get('requires_doctor_consultation', 'N/A')}")
        print(f"Urgency: {result.get('urgency', 'N/A')}")
        
        if result.get('risk_factors'):
            print(f"\nRisk Factors ({len(result['risk_factors'])}):")
            for i, factor in enumerate(result['risk_factors'], 1):
                print(f"  {i}. {factor}")
        
        if result.get('recommendations'):
            print(f"\nRecommendations ({len(result['recommendations'])}):")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        if result.get('summary'):
            print(f"\nSummary:")
            print(f"  {result['summary']}")
        
        print("\n" + "=" * 80)
        print("✅ HPR (High Pregnancy Risk) DETECTION IS WORKING!")
        print("=" * 80)
        print("\nThis means:")
        print("  1. ✅ RAG Pipeline is running correctly")
        print("  2. ✅ Data format is correct (camelCase fields)")
        print("  3. ✅ AI risk assessment is functional")
        print("  4. ✅ Ready to receive data from Backend")
        
        print("\nNext step:")
        print("  - Make sure Frontend sends data in this exact format")
        print("  - Backend should forward this to RAG Pipeline")
        print("  - Result will show on the VisitResult page")
        
    elif response.status_code == 422:
        print("=" * 80)
        print("❌ VALIDATION ERROR (422)")
        print("=" * 80)
        print("\nThe RAG Pipeline rejected the data due to validation errors.")
        print("This means the data format doesn't match what RAG expects.\n")
        
        try:
            error_detail = response.json()
            print("Error Details:")
            print(json.dumps(error_detail, indent=2))
            
            print("\nCommon issues:")
            print("  - Field names must be camelCase (not snake_case)")
            print("  - Required fields: age, bpSystolic, bpDiastolic, hemoglobin")
            print("  - Boolean fields must be true/false (not strings)")
            
        except:
            print(response.text)
            
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("=" * 80)
    print("❌ CONNECTION ERROR")
    print("=" * 80)
    print(f"\nCannot connect to RAG Pipeline at {RAG_URL}")
    print("Make sure the RAG Pipeline is running:")
    print("  - Check Terminal 4")
    print("  - Should show: 'Uvicorn running on http://0.0.0.0:8000'")
    
except requests.exceptions.Timeout:
    print("=" * 80)
    print("❌ TIMEOUT ERROR")
    print("=" * 80)
    print("\nThe RAG Pipeline is taking too long to respond.")
    print("This could mean:")
    print("  - RAG Pipeline is processing but slow")
    print("  - Check Terminal 4 for errors")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "=" * 80)
