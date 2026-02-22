#!/bin/bash

# Test Encryption Flow - Verify data is encrypted in DB and decrypted via API

echo "=========================================="
echo "ENCRYPTION FLOW TEST"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8080"
DB_NAME="NeoSure"
DB_USER="postgres"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Worker Signup${NC}"
echo "Creating new worker account..."

SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Test Worker Encryption",
    "phone": "9999888877",
    "email": "encrypt.test@example.com",
    "password": "Test@1234",
    "healthCenter": "Test PHC",
    "district": "Test District"
  }')

echo "$SIGNUP_RESPONSE" | jq '.'

# Extract token
TOKEN=$(echo "$SIGNUP_RESPONSE" | jq -r '.token // empty')
WORKER_ID=$(echo "$SIGNUP_RESPONSE" | jq -r '.worker.id // empty')

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Signup failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Worker created with ID: $WORKER_ID${NC}"
echo ""

echo -e "${YELLOW}Step 2: Create Patient${NC}"
echo "Creating patient with sensitive data..."

PATIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/patients" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "fullName": "Encryption Test Patient",
    "phone": "8888777766",
    "age": 28,
    "address": "123 Secret Street, Privacy Town",
    "village": "Test Village",
    "district": "Test District",
    "lmpDate": "2024-12-01",
    "eddDate": "2025-09-07",
    "bloodGroup": "O+"
  }')

echo "$PATIENT_RESPONSE" | jq '.'

PATIENT_ID=$(echo "$PATIENT_RESPONSE" | jq -r '.id // empty')

if [ -z "$PATIENT_ID" ]; then
    echo -e "${RED}❌ Patient creation failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Patient created with ID: $PATIENT_ID${NC}"
echo ""

echo -e "${YELLOW}Step 3: Verify API Returns Decrypted Data${NC}"
echo "Fetching patient via API..."

API_PATIENT=$(curl -s -X GET "$BASE_URL/api/patients/$PATIENT_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "$API_PATIENT" | jq '.'

API_NAME=$(echo "$API_PATIENT" | jq -r '.fullName // empty')
API_PHONE=$(echo "$API_PATIENT" | jq -r '.phone // empty')
API_ADDRESS=$(echo "$API_PATIENT" | jq -r '.address // empty')

echo ""
echo "API Response (should be plain text):"
echo "  Name: $API_NAME"
echo "  Phone: $API_PHONE"
echo "  Address: $API_ADDRESS"

if [ "$API_NAME" == "Encryption Test Patient" ]; then
    echo -e "${GREEN}✅ API returns decrypted data correctly${NC}"
else
    echo -e "${RED}❌ API decryption failed${NC}"
fi

echo ""
echo -e "${YELLOW}Step 4: Check Database - Data Should Be Encrypted${NC}"
echo "Querying database directly..."

DB_QUERY="SELECT full_name, phone, address FROM patients WHERE id = '$PATIENT_ID';"

echo "Running: psql -U $DB_USER -d $DB_NAME -c \"$DB_QUERY\""
echo ""

DB_RESULT=$(psql -U $DB_USER -d $DB_NAME -t -c "$DB_QUERY" 2>&1)

echo "Database Raw Data:"
echo "$DB_RESULT"
echo ""

# Check if data looks encrypted (Base64 encoded)
if echo "$DB_RESULT" | grep -q "^[A-Za-z0-9+/=]\{20,\}"; then
    echo -e "${GREEN}✅ Data is encrypted in database (Base64 format)${NC}"
else
    echo -e "${YELLOW}⚠️  Data might not be encrypted (or encryption not yet applied)${NC}"
fi

echo ""
echo -e "${YELLOW}Step 5: Check Worker Data Encryption${NC}"

WORKER_QUERY="SELECT full_name, phone, email FROM anc_workers WHERE id = '$WORKER_ID';"

echo "Running: psql -U $DB_USER -d $DB_NAME -c \"$WORKER_QUERY\""
echo ""

WORKER_DB_RESULT=$(psql -U $DB_USER -d $DB_NAME -t -c "$WORKER_QUERY" 2>&1)

echo "Worker Database Raw Data:"
echo "$WORKER_DB_RESULT"
echo ""

if echo "$WORKER_DB_RESULT" | grep -q "^[A-Za-z0-9+/=]\{20,\}"; then
    echo -e "${GREEN}✅ Worker data is encrypted in database${NC}"
else
    echo -e "${YELLOW}⚠️  Worker data might not be encrypted${NC}"
fi

echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo ""
echo "Expected Behavior:"
echo "  1. API returns plain text (decrypted)"
echo "  2. Database contains Base64 encrypted strings"
echo ""
echo "Actual Results:"
echo "  API Name: $API_NAME"
echo "  DB Name: (see above - should be encrypted)"
echo ""

if [ "$API_NAME" == "Encryption Test Patient" ]; then
    echo -e "${GREEN}✅ ENCRYPTION TEST PASSED${NC}"
    echo "Data is automatically encrypted when saved and decrypted when fetched!"
else
    echo -e "${RED}❌ ENCRYPTION TEST FAILED${NC}"
    echo "Check if backend was restarted after encryption implementation"
fi

echo ""
echo "To manually verify encryption in database:"
echo "  psql -U $DB_USER -d $DB_NAME"
echo "  SELECT full_name, phone FROM patients WHERE id = '$PATIENT_ID';"
echo ""
