# ApexOrchestrator - Windows Auto-Startup Configuration
# This script creates a Windows Task Scheduler job to auto-start ApexOrchestrator on boot

Write-Host "🚀 ApexOrchestrator Auto-Startup Configuration" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

$projectPath = "C:\ApexOrchestrator"
$venvPath = "$projectPath\venv\Scripts\python.exe"
$logPath = "$projectPath\logs\startup.log"
$taskName = "ApexOrchestrator-AutoStart"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Step 1: Configure Docker Desktop to start on boot
Write-Host "📦 Step 1: Configuring Docker Desktop..." -ForegroundColor Cyan
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

if (Test-Path $dockerPath) {
    Write-Host "   Found Docker Desktop at: $dockerPath" -ForegroundColor Gray
    
    # Docker Desktop usually has its own startup setting, but let's ensure it
    $dockerStartupKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    Set-ItemProperty -Path $dockerStartupKey -Name "Docker Desktop" -Value "`"$dockerPath`"" -ErrorAction SilentlyContinue
    
    Write-Host "   ✅ Docker Desktop configured for auto-start" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Docker Desktop not found at default location" -ForegroundColor Yellow
    Write-Host "   Please ensure Docker Desktop is installed and set to start on boot" -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Configure Ollama to start on boot
Write-Host "🤖 Step 2: Configuring Ollama..." -ForegroundColor Cyan

# Check if Ollama is installed
$ollamaPath = (Get-Command ollama -ErrorAction SilentlyContinue).Source

if ($ollamaPath) {
    Write-Host "   Found Ollama at: $ollamaPath" -ForegroundColor Gray
    
    # Create Ollama startup task
    $ollamaTaskName = "Ollama-Service-AutoStart"
    
    # Remove existing task if present
    Unregister-ScheduledTask -TaskName $ollamaTaskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Create new task
    $ollamaAction = New-ScheduledTaskAction -Execute "ollama" -Argument "serve"
    $ollmaTrigger = New-ScheduledTaskTrigger -AtStartup
    $ollamaPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $ollamaSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName $ollamaTaskName `
        -Action $ollamaAction `
        -Trigger $ollmaTrigger `
        -Principal $ollamaPrincipal `
        -Settings $ollamaSettings `
        -Description "Auto-start Ollama service on system boot" | Out-Null
    
    Write-Host "   ✅ Ollama service configured for auto-start" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Ollama not found in PATH" -ForegroundColor Yellow
    Write-Host "   Please ensure Ollama is installed: https://ollama.ai" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Create ApexOrchestrator startup script
Write-Host "🔧 Step 3: Creating startup script..." -ForegroundColor Cyan

$startupScript = @"
# ApexOrchestrator Auto-Startup Script
# This script waits for dependencies and starts the server

`$ErrorActionPreference = "Continue"
`$logFile = "$logPath"
`$projectPath = "$projectPath"

function Write-Log {
    param([string]`$message)
    `$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    `$logMessage = "[`$timestamp] `$message"
    Add-Content -Path `$logFile -Value `$logMessage
    Write-Host `$logMessage
}

# Ensure log directory exists
`$logDir = Split-Path `$logFile -Parent
if (-not (Test-Path `$logDir)) {
    New-Item -ItemType Directory -Path `$logDir -Force | Out-Null
}

Write-Log "=========================================="
Write-Log "ApexOrchestrator Auto-Startup Initiated"
Write-Log "=========================================="

# Wait for Docker to be ready (max 2 minutes)
Write-Log "Waiting for Docker to start..."
`$dockerReady = `$false
for (`$i = 0; `$i -lt 24; `$i++) {
    try {
        docker ps 2>`$null | Out-Null
        if (`$LASTEXITCODE -eq 0) {
            `$dockerReady = `$true
            Write-Log "✅ Docker is ready"
            break
        }
    } catch {}
    Start-Sleep -Seconds 5
}

if (-not `$dockerReady) {
    Write-Log "⚠️ Docker did not start within timeout, continuing anyway..."
}

# Wait for Ollama to be ready (max 1 minute)
Write-Log "Waiting for Ollama to start..."
`$ollamaReady = `$false
for (`$i = 0; `$i -lt 12; `$i++) {
    try {
        `$response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if (`$response.StatusCode -eq 200) {
            `$ollamaReady = `$true
            Write-Log "✅ Ollama is ready"
            break
        }
    } catch {}
    Start-Sleep -Seconds 5
}

if (-not `$ollamaReady) {
    Write-Log "⚠️ Ollama did not start within timeout, continuing anyway..."
}

# Additional delay to ensure system stability
Write-Log "Waiting 10 seconds for system stabilization..."
Start-Sleep -Seconds 10

# Change to project directory
Set-Location `$projectPath

# Activate virtual environment and start server
Write-Log "Starting ApexOrchestrator server..."
try {
    & "$venvPath" -m uvicorn src.main:app --host 0.0.0.0 --port 8000 2>&1 | ForEach-Object {
        Write-Log "SERVER: `$_"
    }
} catch {
    Write-Log "❌ Error starting server: `$_"
    exit 1
}
"@

$startupScriptPath = "$projectPath\startup_service.ps1"
$startupScript | Out-File -FilePath $startupScriptPath -Encoding UTF8 -Force

Write-Host "   Created startup script: $startupScriptPath" -ForegroundColor Gray
Write-Host "   ✅ Startup script created" -ForegroundColor Green
Write-Host ""

# Step 4: Create scheduled task for ApexOrchestrator
Write-Host "📅 Step 4: Creating Windows Scheduled Task..." -ForegroundColor Cyan

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Create new task
$action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$startupScriptPath`"" `
    -WorkingDirectory $projectPath

$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT2M"  # Delay 2 minutes after startup

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -RestartCount 3

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Auto-start ApexOrchestrator server on system boot with Content Lead and Investor agents" | Out-Null

Write-Host "   ✅ Scheduled task '$taskName' created" -ForegroundColor Green
Write-Host ""

# Step 5: Create manual start/stop scripts
Write-Host "🔧 Step 5: Creating control scripts..." -ForegroundColor Cyan

# Start script
$manualStartScript = @"
# Manual Start - ApexOrchestrator
Write-Host "🚀 Starting ApexOrchestrator..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName "$taskName"
Write-Host "✅ Server starting in background. Check logs at: $logPath" -ForegroundColor Green
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
"@

$manualStartScript | Out-File -FilePath "$projectPath\start_service.ps1" -Encoding UTF8 -Force

# Stop script
$manualStopScript = @"
# Manual Stop - ApexOrchestrator
Write-Host "🛑 Stopping ApexOrchestrator..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {`$_.Path -like "*ApexOrchestrator*"} | Stop-Process -Force
Write-Host "✅ Server stopped" -ForegroundColor Green
"@

$manualStopScript | Out-File -FilePath "$projectPath\stop_service.ps1" -Encoding UTF8 -Force

# Status script
$statusScript = @"
# Status Check - ApexOrchestrator
Write-Host "📊 ApexOrchestrator Status Check" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

# Check if process is running
`$process = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {`$_.Path -like "*ApexOrchestrator*"}
if (`$process) {
    Write-Host "✅ Server Status: RUNNING (PID: `$(`$process.Id))" -ForegroundColor Green
} else {
    Write-Host "❌ Server Status: STOPPED" -ForegroundColor Red
}

# Check if port 8000 is listening
`$port = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (`$port) {
    Write-Host "✅ Port 8000: LISTENING" -ForegroundColor Green
} else {
    Write-Host "❌ Port 8000: NOT LISTENING" -ForegroundColor Red
}

# Test API endpoint
try {
    `$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
    if (`$response.StatusCode -eq 200) {
        Write-Host "✅ API Health: HEALTHY" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ API Health: UNREACHABLE" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 Recent Logs (last 10 lines):" -ForegroundColor Cyan
Write-Host "-" * 50 -ForegroundColor Gray
Get-Content "$logPath" -Tail 10 -ErrorAction SilentlyContinue
Write-Host ""
Write-Host "📚 Full logs: $logPath" -ForegroundColor Gray
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
"@

$statusScript | Out-File -FilePath "$projectPath\check_status.ps1" -Encoding UTF8 -Force

Write-Host "   ✅ Control scripts created:" -ForegroundColor Green
Write-Host "      - start_service.ps1   (Start server manually)" -ForegroundColor Gray
Write-Host "      - stop_service.ps1    (Stop server)" -ForegroundColor Gray
Write-Host "      - check_status.ps1    (Check server status)" -ForegroundColor Gray
Write-Host ""

# Summary
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "✅ AUTO-STARTUP CONFIGURATION COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

Write-Host "📋 What's Configured:" -ForegroundColor Cyan
Write-Host "   1. Docker Desktop    - Auto-starts on boot" -ForegroundColor White
Write-Host "   2. Ollama Service    - Auto-starts on boot" -ForegroundColor White
Write-Host "   3. ApexOrchestrator  - Auto-starts 2 minutes after boot" -ForegroundColor White
Write-Host ""

Write-Host "🎮 Control Commands:" -ForegroundColor Cyan
Write-Host "   .\start_service.ps1   - Start server manually" -ForegroundColor White
Write-Host "   .\stop_service.ps1    - Stop server" -ForegroundColor White
Write-Host "   .\check_status.ps1    - Check server status" -ForegroundColor White
Write-Host ""

Write-Host "📊 Access Points:" -ForegroundColor Cyan
Write-Host "   API Docs:         http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Content Lead:     http://localhost:8000/content-lead/quick-start" -ForegroundColor White
Write-Host "   Investor Agent:   http://localhost:8000/investor-agent/status" -ForegroundColor White
Write-Host "   Logs:             $logPath" -ForegroundColor White
Write-Host ""

Write-Host "🧪 Test It Now:" -ForegroundColor Cyan
Write-Host "   .\start_service.ps1" -ForegroundColor Yellow
Write-Host "   Wait 30 seconds, then:" -ForegroundColor Gray
Write-Host "   .\check_status.ps1" -ForegroundColor Yellow
Write-Host ""

Write-Host "🔄 The server will auto-start on next reboot!" -ForegroundColor Green
Write-Host ""

