# PowerShell script to generate all React frontend files
# Run this from Frontend/anc-frontend directory

Write-Host "🚀 Generating NeoSure ANC Frontend Files..." -ForegroundColor Cyan

# Create directory structure
Write-Host "`n📁 Creating directory structure..." -ForegroundColor Yellow
$directories = @(
    "src/api",
    "src/context",
    "src/hooks",
    "src/routes",
    "src/pages",
    "src/components/layout",
    "src/components/ui",
    "src/components/patients",
    "src/components/visits"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Created $dir" -ForegroundColor Green
    } else {
        Write-Host "  ⏭️  $dir already exists" -ForegroundColor Gray
    }
}

Write-Host "`n✅ Directory structure created!" -ForegroundColor Green
Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Copy all source files from react-frontend.md" -ForegroundColor White
Write-Host "  2. Or ask me to create specific file groups:" -ForegroundColor White
Write-Host "     - Authentication files (API + Context + Pages)" -ForegroundColor White
Write-Host "     - UI Components (Button, Input, Badge, etc.)" -ForegroundColor White
Write-Host "     - Patient Management (Pages + Components)" -ForegroundColor White
Write-Host "     - ANC Visit Form (7-step form + Result page)" -ForegroundColor White
Write-Host "`n  3. Run: npm run dev" -ForegroundColor White
Write-Host "`n📚 See SETUP_COMPLETE.md for detailed instructions" -ForegroundColor Cyan

Write-Host "`n✨ Setup complete! Ready for implementation." -ForegroundColor Green
