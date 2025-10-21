#!/usr/bin/env pwsh
# Content Lead Agent Deployment and Verification Script

Write-Host "`n🚀 Content Lead Agent Deployment Script`n" -ForegroundColor Green

# Step 1: Activate venv
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
if (!(Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    exit 1
}
& .\venv\Scripts\Activate.ps1

# Step 2: Install/verify dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Step 3: Test Content Lead Agent import
Write-Host "🧪 Testing Content Lead Agent..." -ForegroundColor Cyan
python -c "from src.content_lead.routes import router; print('✅ Content Lead Agent imports successfully')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Content Lead Agent failed to load!" -ForegroundColor Red
    exit 1
}

# Step 4: Test Investor Agent import
Write-Host "🧪 Testing Investor Agent..." -ForegroundColor Cyan
python -c "from src.investor_agent.core import InvestorAgent; print('✅ Investor Agent imports successfully')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Investor Agent has issues (non-critical)" -ForegroundColor Yellow
}

Write-Host "`n✅ All pre-flight checks passed!`n" -ForegroundColor Green

# Step 5: Start the server
Write-Host "🌐 Starting Apex Orchestrator server..." -ForegroundColor Cyan
Write-Host "📍 Server will run on: http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "📈 Content Lead Agent: http://localhost:8000/content-lead/*" -ForegroundColor Magenta
Write-Host "`nPress CTRL+C to stop`n" -ForegroundColor Yellow

python -m uvicorn src.main:app --reload --port 8000

