"""
End-to-End Integration Test
Tests the complete flow: Frontend → Backend → RAG Pipeline
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8080"
RAG_URL = "http://localhost:8000"

print("=" * 80)
print("END-TO-END INTEGRATION TEST")
print("Testing: Frontend → Backend → RAG Pipeline")
print("=" * 80)

# ============================================================
# STEP 1: Test RAG Pipeline Health
# ============================================================
print("\n[STEP 1] Testing RAG Pipeline Health...")
try:
    response = requests.get(f"{RAG_URL}/health", timeout=5)
    if response.status_code == 200:
        print("✅ RAG Pipeline is running")
        health = response.json()
        print(f"   Status: {health.get('status')}")
    else:
        print(f"❌ RAG Pipeline health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Cannot connect to RAG Pipeline: {e}")
    print("   Make sure RAG Pipeline is running on port 8000")
    exit(1)

# ============================================================
# STEP 2: Test Backend Health
# ============================================================
print("\n[STEP 2] Testing Backend Health...")
try:
    response = requests.get(f"{BASE_URL}/actuator/health", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is running")
    else:
        print(f"⚠️  Backend health endpoint returned: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot connect to Backend: {e}")
    print("   Make sure Backend is running on port 8080")
    exit(1)

# ============================================================
# STEP 3: Worker Signup (if needed) and Login
# ============================================================
print("\n[STEP 3] Testing Worker Authentication...")

# Try to login first
login_data = {
    "phone": "9999999999",
    "password": "password123"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        auth_data = response.json()
        token = auth_data.get('token')
        worker_id = auth_data.get('workerId')
        print(f"✅ Worker login successful")
        print(f"   Worker ID: {worker_id}")
    elif response.status_code == 401:
        # Worker doesn't exist, create one
        print("   Worker account not found, creating new account...")
        signup_data = {
            "fullName": "Test Worker",
            "phone": "9999999999",
            "email": "testworker@example.com",
            "password": "password123",
            "healthCenter": "PHC-001",
            "district": "Test District"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            auth_data = response.json()
            token = auth_data.get('token')
            worker_id = auth_data.get('workerId')
            print(f"✅ Worker account created and logged in")
            print(f"   Worker ID: {worker_id}")
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"   Response: {response.text}")
            exit(1)
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Authentication error: {e}")
    exit(1)

# ============================================================
# STEP 4: Get Patient List
# ============================================================
print("\n[STEP 4] Getting Patient List...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(
        f"{BASE_URL}/api/patients",
        headers=headers
    )
    
    if response.status_code == 200:
        patients = response.json()
        print(f"✅ Retrieved {len(patients)} patients")
        if len(patients) > 0:
            patient_id = patients[0]['id']
            patient_name = patients[0]['fullName']
            print(f"   Using patient: {patient_name} (ID: {patient_id})")
        else:
            print("   No patients found. Creating test patient...")
            # Create a test patient
            patient_data = {
                "fullName": "Test Patient",
                "age": 26,
                "phone": "9876543210",
                "village": "Test Village",
                "district": "Test District",
                "address": "Test Address",
                "bloodGroup": "O+",
                "lmpDate": "2024-08-01",
                "eddDate": "2025-05-08"
            }
            response = requests.post(
                f"{BASE_URL}/api/patients",
                json=patient_data,
                headers=headers
            )
            if response.status_code == 201:
                patient = response.json()
                patient_id = patient['id']
                patient_name = patient['fullName']
                print(f"✅ Created test patient: {patient_name}")
            else:
                print(f"❌ Failed to create patient: {response.status_code}")
                exit(1)
    else:
        print(f"❌ Failed to get patients: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Error getting patients: {e}")
    exit(1)

# ============================================================
# STEP 5: Register ANC Visit (Complete Flow Test)
# ============================================================
print("\n[STEP 5] Registering ANC Visit (Testing Complete Flow)...")
print("   This simulates the frontend form submission...")

visit_data = {
    "patientId": patient_id,
    "patientName": patient_name,
    "workerId": worker_id,
    "phcId": "PHC-001",
    "structured_data": {
        "patient_info": {
            "patientId": patient_id,
            "name": patient_name,
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
    }
}

print("\n   Sending visit data to backend...")
print(f"   Endpoint: POST {BASE_URL}/api/anc/register-visit")

try:
    response = requests.post(
        f"{BASE_URL}/api/anc/register-visit",
        json=visit_data,
        headers=headers,
        timeout=30  # RAG analysis may take time
    )
    
    print(f"\n   Response Status: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        print("\n" + "=" * 80)
        print("✅ SUCCESS! COMPLETE FLOW WORKING!")
        print("=" * 80)
        
        print(f"\nVisit ID: {result.get('visitId')}")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        
        # Check if risk assessment is present
        risk = result.get('riskAssessment')
        if risk:
            print("\n" + "=" * 80)
            print("AI RISK ASSESSMENT RESULT:")
            print("=" * 80)
            print(f"Risk Level: {risk.get('risk_level')}")
            print(f"Risk Score: {risk.get('risk_score')}/100")
            print(f"Requires Doctor: {risk.get('requires_doctor_consultation')}")
            print(f"Urgency: {risk.get('urgency')}")
            
            if risk.get('risk_factors'):
                print(f"\nRisk Factors ({len(risk['risk_factors'])}):")
                for i, factor in enumerate(risk['risk_factors'], 1):
                    print(f"  {i}. {factor}")
            
            if risk.get('recommendations'):
                print(f"\nRecommendations ({len(risk['recommendations'])}):")
                for i, rec in enumerate(risk['recommendations'], 1):
                    print(f"  {i}. {rec}")
            
            if risk.get('summary'):
                print(f"\nSummary: {risk['summary']}")
            
            print("\n" + "=" * 80)
            print("✅ HPR (High Pregnancy Risk) DETECTION WORKING!")
            print("=" * 80)
        else:
            print("\n⚠️  Visit registered but no risk assessment returned")
            print("   This may indicate an issue with RAG Pipeline integration")
            
    elif response.status_code == 422:
        print("\n" + "=" * 80)
        print("❌ VALIDATION ERROR (422)")
        print("=" * 80)
        print("The RAG Pipeline rejected the data.")
        print("\nError Details:")
        try:
            error = response.json()
            print(json.dumps(error, indent=2))
        except:
            print(response.text)
        print("\nThis means the data format doesn't match what RAG expects.")
        print("Check the field names and data types.")
        
    else:
        print(f"\n❌ Unexpected response: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("\n❌ Request timed out")
    print("   The RAG analysis is taking too long")
    print("   Check if RAG Pipeline is responding")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("✅ RAG Pipeline: Running")
print("✅ Backend: Running")
print("✅ Authentication: Working")
print("✅ Patient Management: Working")
print(f"{'✅' if response.status_code in [200, 201] else '❌'} Visit Registration: {'Working' if response.status_code in [200, 201] else 'Failed'}")
print(f"{'✅' if risk else '❌'} AI Risk Assessment: {'Working' if risk else 'Not Available'}")
print("=" * 80)

if response.status_code in [200, 201] and risk:
    print("\n🎉 ALL SYSTEMS OPERATIONAL!")
    print("The complete flow from Frontend → Backend → RAG is working correctly.")
    print(f"\nYou can now view the result at:")
    print(f"http://localhost:5173/worker/visits/{result.get('visitId')}/result")
else:
    print("\n⚠️  Some issues detected. Check the errors above.")
