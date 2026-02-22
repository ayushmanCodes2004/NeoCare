#!/bin/bash

# Complete End-to-End Test using curl
# Tests: Frontend → Backend → RAG Pipeline

echo "================================================================================"
echo "COMPLETE FLOW TEST - Frontend → Backend → RAG"
echo "================================================================================"
echo ""

BASE_URL="http://localhost:8080"
RAG_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================
# STEP 1: Test RAG Pipeline Health
# ============================================================
echo "[STEP 1] Testing RAG Pipeline Health..."
RAG_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $RAG_URL/health)
if [ "$RAG_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ RAG Pipeline is running${NC}"
else
    echo -e "${RED}❌ RAG Pipeline not responding (HTTP $RAG_HEALTH)${NC}"
    exit 1
fi
echo ""

# ============================================================
# STEP 2: Worker Signup
# ============================================================
echo "[STEP 2] Creating Worker Account..."
SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Test Worker Curl",
    "phone": "9988776655",
    "email": "curltest@example.com",
    "password": "password123",
    "healthCenter": "PHC-TEST",
    "district": "Test District"
  }')

TOKEN=$(echo $SIGNUP_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
WORKER_ID=$(echo $SIGNUP_RESPONSE | grep -o '"workerId":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}⚠️  Signup failed, trying login...${NC}"
    
    # Try login instead
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
      -H "Content-Type: application/json" \
      -d '{
        "phone": "9988776655",
        "password": "password123"
      }')
    
    TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
    WORKER_ID=$(echo $LOGIN_RESPONSE | grep -o '"workerId":"[^"]*' | cut -d'"' -f4)
fi

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Authenticated${NC}"
echo "   Worker ID: $WORKER_ID"
echo "   Token: ${TOKEN:0:20}..."
echo ""

# ============================================================
# STEP 3: Create Patient
# ============================================================
echo "[STEP 3] Creating Test Patient..."
PATIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/patients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Test Patient Curl",
    "age": 26,
    "phone": "9876543210",
    "village": "Test Village",
    "district": "Test District",
    "address": "Test Address",
    "bloodGroup": "O+",
    "lmpDate": "2024-08-01",
    "eddDate": "2025-05-08"
  }')

PATIENT_ID=$(echo $PATIENT_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$PATIENT_ID" ]; then
    echo -e "${YELLOW}⚠️  Patient creation failed, fetching existing patients...${NC}"
    
    # Get existing patients
    PATIENTS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/patients" \
      -H "Authorization: Bearer $TOKEN")
    
    PATIENT_ID=$(echo $PATIENTS_RESPONSE | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
fi

if [ -z "$PATIENT_ID" ]; then
    echo -e "${RED}❌ No patients available${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Patient ready${NC}"
echo "   Patient ID: $PATIENT_ID"
echo ""

# ============================================================
# STEP 4: Register ANC Visit (Complete Flow)
# ============================================================
echo "[STEP 4] Registering ANC Visit..."
echo "   This will call Backend → RAG Pipeline"
echo "   Please wait 30-60 seconds for AI processing..."
echo ""

VISIT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/anc/register-visit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"patientId\": \"$PATIENT_ID\",
    \"patientName\": \"Test Patient Curl\",
    \"workerId\": \"$WORKER_ID\",
    \"phcId\": \"PHC-001\",
    \"structured_data\": {
      \"patient_info\": {
        \"patientId\": \"$PATIENT_ID\",
        \"name\": \"Test Patient Curl\",
        \"age\": 26,
        \"gravida\": 2,
        \"para\": 1,
        \"livingChildren\": 1,
        \"gestationalWeeks\": 24,
        \"lmpDate\": \"2024-08-01\",
        \"estimatedDueDate\": \"2025-05-08\"
      },
      \"vitals\": {
        \"weightKg\": 65.0,
        \"heightCm\": 160.0,
        \"bmi\": 25.4,
        \"bpSystolic\": 120,
        \"bpDiastolic\": 80,
        \"pulseRate\": 78,
        \"respiratoryRate\": 18,
        \"temperatureCelsius\": 37.0,
        \"pallor\": false,
        \"pedalEdema\": false
      },
      \"medical_history\": {
        \"previousLSCS\": false,
        \"badObstetricHistory\": false,
        \"previousStillbirth\": false,
        \"previousPretermDelivery\": false,
        \"previousAbortion\": false,
        \"systemicIllness\": \"None\",
        \"chronicHypertension\": false,
        \"diabetes\": false,
        \"thyroidDisorder\": false,
        \"smoking\": false,
        \"tobaccoUse\": false,
        \"alcoholUse\": false
      },
      \"lab_reports\": {
        \"hemoglobin\": 11.5,
        \"plateletCount\": null,
        \"bloodGroup\": \"O+\",
        \"rhNegative\": false,
        \"urineProtein\": false,
        \"urineSugar\": false,
        \"fastingBloodSugar\": 90.0,
        \"ogtt2hrPG\": null,
        \"hivPositive\": false,
        \"syphilisPositive\": false,
        \"serumCreatinine\": null,
        \"ast\": null,
        \"alt\": null
      },
      \"obstetric_history\": {
        \"birthOrder\": null,
        \"interPregnancyInterval\": null,
        \"stillbirthCount\": 0,
        \"abortionCount\": 0,
        \"pretermHistory\": false
      },
      \"pregnancy_details\": {
        \"twinPregnancy\": false,
        \"malpresentation\": false,
        \"placentaPrevia\": false,
        \"reducedFetalMovement\": false,
        \"amnioticFluidNormal\": true,
        \"umbilicalDopplerAbnormal\": false
      },
      \"current_symptoms\": {
        \"headache\": false,
        \"visualDisturbance\": false,
        \"epigastricPain\": false,
        \"decreasedUrineOutput\": false,
        \"bleedingPerVagina\": false,
        \"convulsions\": false
      }
    }
  }")

echo "$VISIT_RESPONSE" | python -m json.tool 2>/dev/null || echo "$VISIT_RESPONSE"

VISIT_ID=$(echo $VISIT_RESPONSE | grep -o '"visitId":"[^"]*' | cut -d'"' -f4)
STATUS=$(echo $VISIT_RESPONSE | grep -o '"status":"[^"]*' | cut -d'"' -f4)

echo ""
if [ -z "$VISIT_ID" ]; then
    echo -e "${RED}❌ Visit registration failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Visit registered successfully${NC}"
echo "   Visit ID: $VISIT_ID"
echo "   Status: $STATUS"
echo ""

# ============================================================
# STEP 5: Retrieve Visit with Risk Assessment
# ============================================================
echo "[STEP 5] Retrieving Visit with Risk Assessment..."
VISIT_DETAIL=$(curl -s -X GET "$BASE_URL/api/anc/visits/$VISIT_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "$VISIT_DETAIL" | python -m json.tool 2>/dev/null || echo "$VISIT_DETAIL"

# Extract risk assessment fields
RISK_LEVEL=$(echo $VISIT_DETAIL | grep -o '"risk_level":"[^"]*' | cut -d'"' -f4)
RISK_SCORE=$(echo $VISIT_DETAIL | grep -o '"risk_score":[0-9]*' | cut -d':' -f2)

echo ""
echo "================================================================================"
echo "RISK ASSESSMENT RESULT"
echo "================================================================================"

if [ -n "$RISK_LEVEL" ]; then
    echo -e "${GREEN}✅ AI Risk Assessment Available${NC}"
    echo "   Risk Level: $RISK_LEVEL"
    echo "   Risk Score: $RISK_SCORE/100"
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Complete flow is working!${NC}"
    echo "   Frontend → Backend → RAG Pipeline → Response"
else
    echo -e "${RED}❌ Risk assessment not found in response${NC}"
    echo "   Check if Backend was restarted after code changes"
fi

echo "================================================================================"
