# Restart backend to apply encryption changes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESTART BACKEND FOR ENCRYPTION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Stopping existing Java processes..." -ForegroundColor Yellow
Get-Process -Name "java" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "✅ Backend stopped" -ForegroundColor Green
Write-Host ""

Write-Host "Starting backend with encryption enabled..." -ForegroundColor Yellow
Write-Host "Please run manually in a new terminal:" -ForegroundColor White
Write-Host ""
Write-Host "  cd Backend" -ForegroundColor Cyan
Write-Host "  ./run.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "After backend starts, run:" -ForegroundColor White
Write-Host "  ./test_encryption_flow.ps1" -ForegroundColor Cyan
Write-Host ""
