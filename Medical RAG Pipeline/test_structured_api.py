"""
Test script for structured /assess-structured endpoint
Demonstrates structured JSON input format
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Your example structured data
STRUCTURED_TEST_CASE = {
    "clinical_summary": "Pregnant woman aged 36, 30 weeks gestation, Hb 6.5 g/dL, BP 150/100 mmHg, previous LSCS, twin pregnancy. Complains of pedal edema and reduced fetal movements.",
    "structured_data": {
        "patient_info": {
            "patientId": "ANC-2025-00123",
            "name": "Sita Devi",
            "age": 36,
            "gravida": 3,
            "para": 1,
            "livingChildren": 1,
            "gestationalWeeks": 30,
            "lmpDate": "2025-07-15",
            "estimatedDueDate": "2026-04-22"
        },
        "medical_history": {
            "previousLSCS": True,
            "badObstetricHistory": False,
            "previousStillbirth": False,
            "previousPretermDelivery": False,
            "previousAbortion": True,
            "systemicIllness": "None",
            "chronicHypertension": False,
            "diabetes": False,
            "thyroidDisorder": False
        },
        "vitals": {
            "weightKg": 78,
            "heightCm": 158,
            "bmi": 31.2,
            "bpSystolic": 150,
            "bpDiastolic": 100,
            "pulseRate": 96,
            "respiratoryRate": 20,
            "temperatureCelsius": 36.9,
            "pallor": True,
            "pedalEdema": True
        },
        "lab_reports": {
            "hemoglobin": 6.5,
            "plateletCount": 150000,
            "bloodGroup": "B+",
            "rhNegative": False,
            "urineProtein": True,
            "urineSugar": False,
            "fastingBloodSugar": 92,
            "hivPositive": False,
            "syphilisPositive": False,
            "serumCreatinine": 0.8,
            "ast": 32,
            "alt": 28
        },
        "pregnancy_details": {
            "twinPregnancy": True,
            "malpresentation": False,
            "placentaPrevia": False,
            "reducedFetalMovement": True,
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
            "visitNumber": 5,
            "healthWorkerId": "ASHA-234",
            "subCenterId": "SC-12",
            "district": "Kalahandi",
            "state": "Odisha",
            "timestamp": "2026-02-20T10:30:00Z"
        }
    },
    "care_level": "PHC",
    "verbose": False
}


def test_structured_endpoint():
    """Test the structured /assess-structured endpoint."""
    print("="*80)
    print("TESTING STRUCTURED /assess-structured ENDPOINT")
    print("="*80)
    
    # Check server health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding. Please start: python api_server.py")
            return
        print("✅ Server is running\n")
    except:
        print("❌ Cannot connect to server. Please start: python api_server.py")
        return
    
    # Show input
    print(f"\n{'='*80}")
    print("INPUT: Structured Patient Data")
    print(f"{'='*80}")
    print(f"Patient: {STRUCTURED_TEST_CASE['structured_data']['patient_info']['name']}")
    print(f"Patient ID: {STRUCTURED_TEST_CASE['structured_data']['patient_info']['patientId']}")
    print(f"Age: {STRUCTURED_TEST_CASE['structured_data']['patient_info']['age']} years")
    print(f"Gestational Age: {STRUCTURED_TEST_CASE['structured_data']['patient_info']['gestationalWeeks']} weeks")
    print(f"BP: {STRUCTURED_TEST_CASE['structured_data']['vitals']['bpSystolic']}/{STRUCTURED_TEST_CASE['structured_data']['vitals']['bpDiastolic']} mmHg")
    print(f"Hb: {STRUCTURED_TEST_CASE['structured_data']['lab_reports']['hemoglobin']} g/dL")
    print(f"Twin Pregnancy: {STRUCTURED_TEST_CASE['structured_data']['pregnancy_details']['twinPregnancy']}")
    print(f"Previous LSCS: {STRUCTURED_TEST_CASE['structured_data']['medical_history']['previousLSCS']}")
    print(f"Care Level: {STRUCTURED_TEST_CASE['care_level']}")
    
    try:
        # Send request
        print(f"\n📤 Sending structured request...")
        response = requests.post(
            f"{BASE_URL}/assess-structured",
            json=STRUCTURED_TEST_CASE,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Pretty print result
            print(f"\n{'='*80}")
            print("📊 RESULT:")
            print(f"{'='*80}")
            print(json.dumps(result, indent=2))
            
            # Validate structure
            required_fields = ['isHighRisk', 'riskLevel', 'detectedRisks', 'explanation', 'confidence', 'recommendation']
            missing = [f for f in required_fields if f not in result]
            
            if missing:
                print(f"\n⚠️  Missing fields: {missing}")
            else:
                print(f"\n✅ All required fields present")
                
                # Show key metrics
                print(f"\n{'='*80}")
                print("📈 KEY METRICS:")
                print(f"{'='*80}")
                print(f"   Patient ID: {result.get('patientId', 'N/A')}")
                print(f"   Patient Name: {result.get('patientName', 'N/A')}")
                print(f"   Age: {result.get('age', 'N/A')} years")
                print(f"   Gestational Age: {result.get('gestationalWeeks', 'N/A')} weeks")
                print(f"   High Risk: {'YES ⚠️' if result['isHighRisk'] else 'NO ✓'}")
                print(f"   Risk Level: {result['riskLevel']}")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   Detected Risks: {len(result['detectedRisks'])}")
                if result['detectedRisks']:
                    for risk in result['detectedRisks']:
                        print(f"      • {risk}")
                
                print(f"\n📝 EXPLANATION:")
                print(f"   {result['explanation']}")
                
                print(f"\n💊 RECOMMENDATION:")
                print(f"   {result['recommendation']}")
                
                if result.get('visitMetadata'):
                    print(f"\n📍 VISIT INFO:")
                    print(f"   District: {result['visitMetadata'].get('district', 'N/A')}")
                    print(f"   State: {result['visitMetadata'].get('state', 'N/A')}")
                    print(f"   Health Worker: {result['visitMetadata'].get('healthWorkerId', 'N/A')}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️  Request timed out (>120s)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")


def show_input_format():
    """Show the expected input format."""
    print("\n" + "="*80)
    print("EXPECTED INPUT FORMAT")
    print("="*80)
    print(json.dumps(STRUCTURED_TEST_CASE, indent=2))
    print("="*80)


if __name__ == "__main__":
    show_input_format()
    test_structured_endpoint()
