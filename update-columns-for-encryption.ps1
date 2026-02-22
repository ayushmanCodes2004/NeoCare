# PowerShell script to update database columns for encryption
# Run this BEFORE enabling encryption

$env:PGPASSWORD = "ayushman@2004"
$dbName = "NeoSure"
$dbUser = "postgres"
$dbHost = "localhost"
$dbPort = "5432"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DATABASE MIGRATION FOR ENCRYPTION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find PostgreSQL bin directory
$pgPath = "C:\Program Files\PostgreSQL"
$psqlExe = $null

if (Test-Path $pgPath) {
    $psqlExe = Get-ChildItem -Path $pgPath -Recurse -Filter "psql.exe" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
}

if (-not $psqlExe) {
    Write-Host "❌ PostgreSQL psql.exe not found!" -ForegroundColor Red
    Write-Host "Please run these SQL commands manually in pgAdmin or your PostgreSQL client:" -ForegroundColor Yellow
    Write-Host ""
    Get-Content "Backend/update-columns-for-encryption.sql"
    exit 1
}

Write-Host "✅ Found psql at: $psqlExe" -ForegroundColor Green
Write-Host ""

Write-Host "Running migration..." -ForegroundColor Yellow

# Run the SQL file
& $psqlExe -U $dbUser -d $dbName -h $dbHost -p $dbPort -f "Backend/update-columns-for-encryption.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migration completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Restart the backend server" -ForegroundColor White
    Write-Host "  2. Run: ./test_encryption_flow.ps1" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Migration failed!" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
}
