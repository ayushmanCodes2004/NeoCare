# Complete End-to-End Test using PowerShell
# Tests: Frontend → Backend → RAG Pipeline

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "COMPLETE FLOW TEST - Frontend → Backend → RAG" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$BASE_URL = "http://localhost:8080"
$RAG_URL = "http://localhost:8000"

# ============================================================
# STEP 1: Test RAG Pipeline Health
# ============================================================
Write-Host "[STEP 1] Testing RAG Pipeline Health..."
try {
    $response = Invoke-WebRequest -Uri "$RAG_URL/health" -Method GET -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ RAG Pipeline is running" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ RAG Pipeline not responding" -ForegroundColor Red
    exit 1
}
Write-Host ""

# ============================================================
# STEP 2: Worker Authentication
# ============================================================
Write-Host "[STEP 2] Authenticating Worker..."

$signupBody = @{
    fullName = "Test Worker PS"
    phone = "9988776655"
    email = "pstest@example.com"
    password = "password123"
    healthCenter = "PHC-TEST"
    district = "Test District"
} | ConvertTo-Json

try {
    $authResponse = Invoke-RestMethod -Uri "$BASE_URL/api/auth/signup" -Method POST -Body $signupBody -ContentType "application/json"
    $token = $authResponse.token
    $workerId = $authResponse.workerId
} catch {
    # Try login if signup fails
    Write-Host "⚠️  Signup failed, trying login..." -ForegroundColor Yellow
    
    $loginBody = @{
        phone = "9988776655"
        password = "password123"
    } | ConvertTo-Json
    
    try {
        $authResponse = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
        $token = $authResponse.token
        $workerId = $authResponse.workerId
    } catch {
        Write-Host "❌ Authentication failed: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Authenticated" -ForegroundColor Green
Write-Host "   Worker ID: $workerId"
Write-Host "   Token: $($token.Substring(0, 20))..."
Write-Host ""

# ============================================================
# STEP 3: Create/Get Patient
# ============================================================
Write-Host "[STEP 3] Getting Test Patient..."

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$patientBody = @{
    fullName = "Test Patient PS"
    age = 26
    phone = "9876543210"
    village = "Test Village"
    district = "Test District"
    address = "Test Address"
    bloodGroup = "O+"
    lmpDate = "2024-08-01"
    eddDate = "2025-05-08"
} | ConvertTo-Json

try {
    $patientResponse = Invoke-RestMethod -Uri "$BASE_URL/api/patients" -Method POST -Headers $headers -Body $patientBody
    $patientId = $patientResponse.id
} catch {
    Write-Host "⚠️  Patient creation failed, fetching existing..." -ForegroundColor Yellow
    
    try {
        $patientsResponse = Invoke-RestMethod -Uri "$BASE_URL/api/patients" -Method GET -Headers $headers
        $patientId = $patientsResponse[0].id
    } catch {
        Write-Host "❌ No patients available: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Patient ready" -ForegroundColor Green
Write-Host "   Patient ID: $patientId"
Write-Host ""

# ============================================================
# STEP 4: Register ANC Visit
# ============================================================
Write-Host "[STEP 4] Registering ANC Visit..." -ForegroundColor Cyan
Write-Host "   This will call Backend → RAG Pipeline"
Write-Host "   Please wait 30-60 seconds for AI processing..."
Write-Host ""

$visitBody = @{
    patientId = $patientId
    patientName = "Test Patient PS"
    workerId = $workerId
    phcId = "PHC-001"
    structured_data = @{
        patient_info = @{
            patientId = $patientId
            name = "Test Patient PS"
            age = 26
            gravida = 2
            para = 1
            livingChildren = 1
            gestationalWeeks = 24
            lmpDate = "2024-08-01"
            estimatedDueDate = "2025-05-08"
        }
        vitals = @{
            weightKg = 65.0
            heightCm = 160.0
            bmi = 25.4
            bpSystolic = 120
            bpDiastolic = 80
            pulseRate = 78
            respiratoryRate = 18
            temperatureCelsius = 37.0
            pallor = $false
            pedalEdema = $false
        }
        medical_history = @{
            previousLSCS = $false
            badObstetricHistory = $false
            previousStillbirth = $false
            previousPretermDelivery = $false
            previousAbortion = $false
            systemicIllness = "None"
            chronicHypertension = $false
            diabetes = $false
            thyroidDisorder = $false
            smoking = $false
            tobaccoUse = $false
            alcoholUse = $false
        }
        lab_reports = @{
            hemoglobin = 11.5
            plateletCount = $null
            bloodGroup = "O+"
            rhNegative = $false
            urineProtein = $false
            urineSugar = $false
            fastingBloodSugar = 90.0
            ogtt2hrPG = $null
            hivPositive = $false
            syphilisPositive = $false
            serumCreatinine = $null
            ast = $null
            alt = $null
        }
        obstetric_history = @{
            birthOrder = $null
            interPregnancyInterval = $null
            stillbirthCount = 0
            abortionCount = 0
            pretermHistory = $false
        }
        pregnancy_details = @{
            twinPregnancy = $false
            malpresentation = $false
            placentaPrevia = $false
            reducedFetalMovement = $false
            amnioticFluidNormal = $true
            umbilicalDopplerAbnormal = $false
        }
        current_symptoms = @{
            headache = $false
            visualDisturbance = $false
            epigastricPain = $false
            decreasedUrineOutput = $false
            bleedingPerVagina = $false
            convulsions = $false
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $visitResponse = Invoke-RestMethod -Uri "$BASE_URL/api/anc/register-visit" -Method POST -Headers $headers -Body $visitBody
    
    Write-Host "✅ Visit registered successfully" -ForegroundColor Green
    Write-Host "   Visit ID: $($visitResponse.visitId)"
    Write-Host "   Status: $($visitResponse.status)"
    Write-Host ""
    
    # ============================================================
    # STEP 5: Retrieve Visit with Risk Assessment
    # ============================================================
    Write-Host "[STEP 5] Retrieving Visit with Risk Assessment..." -ForegroundColor Cyan
    
    $visitDetail = Invoke-RestMethod -Uri "$BASE_URL/api/anc/visits/$($visitResponse.visitId)" -Method GET -Headers $headers
    
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "RISK ASSESSMENT RESULT" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    if ($visitDetail.riskAssessment) {
        $risk = $visitDetail.riskAssessment
        
        Write-Host "✅ AI Risk Assessment Available" -ForegroundColor Green
        Write-Host ""
        Write-Host "Risk Level: $($risk.risk_level)" -ForegroundColor Yellow
        Write-Host "Risk Score: $($risk.risk_score)/100" -ForegroundColor Yellow
        Write-Host "Requires Doctor: $($risk.requires_doctor_consultation)"
        Write-Host "Urgency: $($risk.urgency)"
        Write-Host ""
        
        if ($risk.risk_factors) {
            Write-Host "Risk Factors:" -ForegroundColor Yellow
            foreach ($factor in $risk.risk_factors) {
                Write-Host "  • $factor"
            }
            Write-Host ""
        }
        
        if ($risk.recommendations) {
            Write-Host "Recommendations:" -ForegroundColor Yellow
            foreach ($rec in $risk.recommendations) {
                Write-Host "  • $rec"
            }
            Write-Host ""
        }
        
        if ($risk.summary) {
            Write-Host "Summary:" -ForegroundColor Yellow
            Write-Host "  $($risk.summary)"
            Write-Host ""
        }
        
        Write-Host "================================================================================" -ForegroundColor Green
        Write-Host "🎉 SUCCESS! Complete flow is working!" -ForegroundColor Green
        Write-Host "   Frontend → Backend → RAG Pipeline → Response" -ForegroundColor Green
        Write-Host "================================================================================" -ForegroundColor Green
        
    } else {
        Write-Host "❌ Risk assessment not found in response" -ForegroundColor Red
        Write-Host "   Response:" -ForegroundColor Yellow
        $visitDetail | ConvertTo-Json -Depth 10
        Write-Host ""
        Write-Host "   Check if Backend was restarted after code changes" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Visit registration failed: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host ""
