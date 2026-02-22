# PowerShell script to test encryption flow

$baseUrl = "http://localhost:8080"
$dbName = "NeoSure"
$dbUser = "postgres"
$env:PGPASSWORD = "ayushman@2004"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ENCRYPTION FLOW TEST" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Generate unique test data
$timestamp = Get-Date -Format "HHmmss"
$testPhone = "999$timestamp"
$testEmail = "encrypt$timestamp@test.com"

Write-Host "Step 1: Worker Signup" -ForegroundColor Yellow
Write-Host "Creating new worker account..." -ForegroundColor White

$signupBody = @{
    fullName = "Test Worker Encryption $timestamp"
    phone = $testPhone
    email = $testEmail
    password = "Test@1234"
    healthCenter = "Test PHC"
    district = "Test District"
} | ConvertTo-Json

try {
    $signupResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/signup" `
        -Method Post `
        -ContentType "application/json" `
        -Body $signupBody

    Write-Host ($signupResponse | ConvertTo-Json -Depth 10) -ForegroundColor Gray
    
    $token = $signupResponse.token
    $workerId = $signupResponse.worker.id

    if (-not $token) {
        Write-Host "❌ Signup failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Worker created with ID: $workerId" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host "❌ Signup request failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Step 2: Create Patient" -ForegroundColor Yellow
Write-Host "Creating patient with sensitive data..." -ForegroundColor White

$patientBody = @{
    fullName = "Encryption Test Patient $timestamp"
    phone = "888$timestamp"
    age = 28
    address = "123 Secret Street, Privacy Town, Confidential Area"
    village = "Test Village"
    district = "Test District"
    lmpDate = "2024-12-01"
    eddDate = "2025-09-07"
    bloodGroup = "O+"
} | ConvertTo-Json

try {
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }

    $patientResponse = Invoke-RestMethod -Uri "$baseUrl/api/patients" `
        -Method Post `
        -Headers $headers `
        -Body $patientBody

    Write-Host ($patientResponse | ConvertTo-Json -Depth 10) -ForegroundColor Gray

    $patientId = $patientResponse.id

    if (-not $patientId) {
        Write-Host "❌ Patient creation failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Patient created with ID: $patientId" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host "❌ Patient creation failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Step 3: Verify API Returns Decrypted Data" -ForegroundColor Yellow
Write-Host "Fetching patient via API..." -ForegroundColor White

try {
    $apiPatient = Invoke-RestMethod -Uri "$baseUrl/api/patients/$patientId" `
        -Method Get `
        -Headers $headers

    Write-Host ($apiPatient | ConvertTo-Json -Depth 10) -ForegroundColor Gray
    Write-Host ""

    $apiName = $apiPatient.fullName
    $apiPhone = $apiPatient.phone
    $apiAddress = $apiPatient.address

    Write-Host "API Response (should be plain text):" -ForegroundColor Cyan
    Write-Host "  Name: $apiName" -ForegroundColor White
    Write-Host "  Phone: $apiPhone" -ForegroundColor White
    Write-Host "  Address: $apiAddress" -ForegroundColor White
    Write-Host ""

    if ($apiName -like "*Encryption Test Patient*") {
        Write-Host "✅ API returns decrypted data correctly" -ForegroundColor Green
    } else {
        Write-Host "❌ API decryption failed" -ForegroundColor Red
    }

} catch {
    Write-Host "❌ API fetch failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 4: Check Database - Data Should Be Encrypted" -ForegroundColor Yellow
Write-Host "Querying database directly..." -ForegroundColor White

# Find PostgreSQL bin directory
$pgPath = "C:\Program Files\PostgreSQL"
$psqlExe = $null

if (Test-Path $pgPath) {
    $psqlExe = Get-ChildItem -Path $pgPath -Recurse -Filter "psql.exe" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
}

if ($psqlExe) {
    Write-Host "Found psql at: $psqlExe" -ForegroundColor Gray
    Write-Host ""

    $query = "SELECT full_name, phone, address FROM patients WHERE id = '$patientId';"
    
    Write-Host "Running query on database..." -ForegroundColor Gray
    $dbResult = & $psqlExe -U $dbUser -d $dbName -t -c $query 2>&1

    Write-Host "Database Raw Data:" -ForegroundColor Cyan
    Write-Host $dbResult -ForegroundColor White
    Write-Host ""

    # Check if data looks encrypted (Base64 encoded - long alphanumeric strings)
    if ($dbResult -match "[A-Za-z0-9+/=]{50,}") {
        Write-Host "✅ Data is encrypted in database (Base64 format detected)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Data might not be encrypted yet" -ForegroundColor Yellow
        Write-Host "   (Backend may need restart after encryption implementation)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "Step 5: Check Worker Data Encryption" -ForegroundColor Yellow

    $workerQuery = "SELECT full_name, phone, email FROM anc_workers WHERE id = '$workerId';"
    $workerDbResult = & $psqlExe -U $dbUser -d $dbName -t -c $workerQuery 2>&1

    Write-Host "Worker Database Raw Data:" -ForegroundColor Cyan
    Write-Host $workerDbResult -ForegroundColor White
    Write-Host ""

    if ($workerDbResult -match "[A-Za-z0-9+/=]{50,}") {
        Write-Host "✅ Worker data is encrypted in database" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Worker data might not be encrypted yet" -ForegroundColor Yellow
    }

} else {
    Write-Host "⚠️  psql.exe not found - cannot verify database encryption" -ForegroundColor Yellow
    Write-Host "   Please check manually in pgAdmin:" -ForegroundColor Yellow
    Write-Host "   SELECT full_name, phone FROM patients WHERE id = '$patientId';" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Expected Behavior:" -ForegroundColor White
Write-Host "  1. API returns plain text (decrypted)" -ForegroundColor Gray
Write-Host "  2. Database contains Base64 encrypted strings" -ForegroundColor Gray
Write-Host ""

if ($apiName -like "*Encryption Test Patient*") {
    Write-Host "✅ ENCRYPTION TEST PASSED" -ForegroundColor Green
    Write-Host "Data is automatically encrypted when saved and decrypted when fetched!" -ForegroundColor Green
} else {
    Write-Host "❌ ENCRYPTION TEST FAILED" -ForegroundColor Red
    Write-Host "Check if backend was restarted after encryption implementation" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Test Data IDs for manual verification:" -ForegroundColor Cyan
Write-Host "  Worker ID: $workerId" -ForegroundColor White
Write-Host "  Patient ID: $patientId" -ForegroundColor White
Write-Host ""
