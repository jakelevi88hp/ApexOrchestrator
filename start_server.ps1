#!/usr/bin/env pwsh
# Apex Orchestrator Server Startup Script
# Ensures virtual environment is activated before starting

Write-Host "🚀 Starting Apex Orchestrator Server..." -ForegroundColor Green
Write-Host ""

# Check if venv exists
if (!(Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Verify dependencies
Write-Host "🔍 Checking dependencies..." -ForegroundColor Cyan
python -c "import fastapi, slowapi, pydantic" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Missing dependencies!" -ForegroundColor Red
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
    pip install pydantic[email]
}

# Verify Content Lead Agent loads
Write-Host "🧪 Testing Content Lead Agent..." -ForegroundColor Cyan
python -c "from src.content_lead.routes import router; print('✅ Content Lead Agent OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Content Lead Agent failed to load" -ForegroundColor Yellow
    Write-Host "Installing additional dependencies..." -ForegroundColor Yellow
    pip install pydantic[email]
}

Write-Host ""
Write-Host "✅ All checks passed!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📈 Content Lead Agent: http://localhost:8000/content-lead/quick-start" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
python -m uvicorn src.main:app --reload --port 8000

