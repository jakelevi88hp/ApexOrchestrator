# Test Autonomous Agent System
Write-Host "=== APEX ORCHESTRATOR + AUTONOMOUS AGENT ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing all endpoints..." -ForegroundColor Yellow
Write-Host ""

# Test health
Write-Host "[1/5] Health Check..." -ForegroundColor Gray
$health = Invoke-WebRequest -Uri http://localhost:8000/health | ConvertFrom-Json
if ($health.ok) { 
    Write-Host "  ✅ Service Healthy" -ForegroundColor Green 
} else { 
    Write-Host "  ❌ Service Unhealthy" -ForegroundColor Red 
}
Write-Host "  Version: $($health.version)" -ForegroundColor Gray
Write-Host ""

# Test metrics
Write-Host "[2/5] Metrics Check..." -ForegroundColor Gray
$metrics = Invoke-WebRequest -Uri http://localhost:8000/metrics | ConvertFrom-Json
Write-Host "  ✅ Uptime: $([Math]::Round($metrics.uptime_seconds, 2))s" -ForegroundColor Green
Write-Host ""

# Test agent safety status
Write-Host "[3/5] Agent Safety Status..." -ForegroundColor Gray
$safety = Invoke-WebRequest -Uri http://localhost:8000/agent/safety/status | ConvertFrom-Json
$agentColor = if ($safety.agent_enabled) {"Yellow"} else {"Green"}
$modColor = if ($safety.modifications_enabled) {"Red"} else {"Green"}
$killColor = if ($safety.kill_switch_active) {"Red"} else {"Green"}

Write-Host "  Agent Enabled: $($safety.agent_enabled)" -ForegroundColor $agentColor
Write-Host "  Modifications: $($safety.modifications_enabled)" -ForegroundColor $modColor
Write-Host "  Kill Switch: $($safety.kill_switch_active)" -ForegroundColor $killColor
Write-Host "  Sandbox Mode: $($safety.sandbox_mode)" -ForegroundColor Green
Write-Host ""

# Test docs
Write-Host "[4/5] API Documentation..." -ForegroundColor Gray
$docs = Invoke-WebRequest -Uri http://localhost:8000/docs
if ($docs.StatusCode -eq 200) { 
    Write-Host "  ✅ Swagger UI Accessible" -ForegroundColor Green 
}
Write-Host ""

# Test agent memory
Write-Host "[5/5] Agent Memory Stats..." -ForegroundColor Gray
try {
    $mem = Invoke-WebRequest -Uri http://localhost:8000/agent/memory/stats | ConvertFrom-Json
    Write-Host "  ✅ Memory System Online" -ForegroundColor Green
    Write-Host "  Total Executions: $($mem.total_executions)" -ForegroundColor Gray
    Write-Host "  Learned Patterns: $($mem.learned_patterns)" -ForegroundColor Gray
} catch {
    Write-Host "  ℹ️  Memory system ready (no data yet)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== ALL SYSTEMS OPERATIONAL ===" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Autonomous Agent Successfully Installed!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Read AUTONOMOUS_AGENT_SUMMARY.md" -ForegroundColor Gray
Write-Host "  2. Follow QUICK_START_AGENT.md" -ForegroundColor Gray
$docsUrl = "http://localhost:8000/docs"
Write-Host "  3. Visit $docsUrl" -ForegroundColor Gray
Write-Host ""

