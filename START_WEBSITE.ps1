# LinkScout Web Interface Starter
# Smart Analysis. Simple Answers.

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   LinkScout Web Interface" -ForegroundColor Yellow
Write-Host "   Smart Analysis. Simple Answers." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1/2] Checking if backend server is running..." -ForegroundColor White

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting Next.js Development Server..." -ForegroundColor White
Write-Host ""
Write-Host "Web interface will be available at:" -ForegroundColor Green
Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location web_interface\LinkScout
npm run dev
