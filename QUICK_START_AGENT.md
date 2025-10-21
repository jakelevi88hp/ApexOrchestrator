# 🚀 Autonomous Agent - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Configure Passwords (Required)

Edit your `.env` file:

```bash
# Add these lines
AGENT_ENABLE_PASSWORD=MySecurePassword123!
MODIFICATIONS_ENABLE_PASSWORD=DifferentPassword456!
KILL_SWITCH_PASSWORD=EmergencyStop789!
```

### Step 2: Restart the Container

```bash
docker-compose restart
```

### Step 3: Enable the Agent (Learning Mode Only)

```powershell
# PowerShell
$body = @{password="MySecurePassword123!"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/agent/enable `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

```bash
# or Bash/curl
curl -X POST http://localhost:8000/agent/enable \
  -H "Content-Type: application/json" \
  -d '{"password":"MySecurePassword123!"}'
```

### Step 4: Check Status

```powershell
Invoke-WebRequest -Uri http://localhost:8000/agent/status | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

Expected response:
```json
{
  "running": false,
  "loop_count": 0,
  "safety": {
    "agent_enabled": true,
    "modifications_enabled": false,
    "kill_switch_active": false
  }
}
```

### Step 5: Start Learning Loop (Optional)

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/agent/start-loop?interval_seconds=3600" -Method POST
```

This makes the agent learn from operations every hour.

## 📊 Monitoring Commands

### Check What It's Learning

```powershell
# Learning report
Invoke-WebRequest -Uri http://localhost:8000/agent/learning-report | ConvertFrom-Json

# Memory statistics
Invoke-WebRequest -Uri http://localhost:8000/agent/memory/stats | ConvertFrom-Json

# Optimization opportunities
Invoke-WebRequest -Uri http://localhost:8000/agent/opportunities | ConvertFrom-Json
```

### View Execution History

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/agent/memory/executions?limit=10" | ConvertFrom-Json
```

## 🎯 Common Operations

### Stop the Agent

```powershell
Invoke-WebRequest -Uri http://localhost:8000/agent/disable -Method POST
```

### Emergency Stop (Kill Switch)

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/agent/kill-switch/activate?reason=Test" -Method POST
```

To resume:
```powershell
$body = @{password="EmergencyStop789!"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/agent/kill-switch/deactivate `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

## 🔐 Safety Settings

### Current Safety Status

```powershell
Invoke-WebRequest -Uri http://localhost:8000/agent/safety/status | ConvertFrom-Json
```

Shows:
- Agent enabled/disabled
- Modifications enabled/disabled
- Kill switch status
- Safety checks

## 📈 Dashboard View

Visit these URLs in your browser:

- **API Documentation**: http://localhost:8000/docs
- **Health Status**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **Agent Status**: http://localhost:8000/agent/status (needs JSON viewer extension)

## 🧪 Test It Out

### 1. Make the agent learn from an operation

Run some operations first:
```powershell
# Use the existing /nlm/run or /apex/run endpoints
# The agent will automatically learn from these
```

### 2. Check what it learned after a few hours

```powershell
Invoke-WebRequest -Uri http://localhost:8000/agent/learning-report | ConvertFrom-Json
```

### 3. View optimization suggestions

```powershell
Invoke-WebRequest -Uri http://localhost:8000/agent/suggestions | ConvertFrom-Json
```

## ⚙️ Advanced: Enable Self-Modification

⚠️ **WARNING**: This allows the agent to modify code! Only enable after extensive testing.

### Enable Modifications

```powershell
$body = @{password="DifferentPassword456!"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/agent/modifications/enable `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### Propose a Modification

```powershell
$body = @{
    target_file = "src/main.py"
    modification_type = "optimize"
    description = "Add caching to improve performance"
    reason = "Function called frequently"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/agent/modifications/propose `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### Apply a Modification

```powershell
$body = @{
    proposal_id = 20251017120000  # Use ID from proposal response
    auto_test = $true
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/agent/modifications/apply `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

## 🗄️ Database Queries

Access the agent's memory database:

```powershell
# Enter container
docker exec -it apex-orchestrator bash

# Open database
sqlite3 logs/agent_memory.db

# View recent executions
SELECT * FROM executions ORDER BY timestamp DESC LIMIT 10;

# View learned patterns
SELECT * FROM patterns ORDER BY confidence_score DESC;

# Exit
.exit
exit
```

## 📋 Environment Variables Cheat Sheet

Add to `.env` file:

```bash
# Passwords (REQUIRED)
AGENT_ENABLE_PASSWORD=your_password
MODIFICATIONS_ENABLE_PASSWORD=different_password
KILL_SWITCH_PASSWORD=emergency_password

# Agent Behavior (Optional)
AGENT_ENABLED=false  # Auto-enable on startup (keep false!)
AGENT_MODIFICATIONS_ENABLED=false  # Auto-enable mods (keep false!)
AGENT_MAX_MODIFICATIONS_PER_DAY=5  # Daily limit
AGENT_REQUIRE_APPROVAL=true  # Require approval for changes
AGENT_SANDBOX_MODE=true  # Sandbox mode
AGENT_GIT_INTEGRATION=true  # Git commits for changes
```

## 🎨 Visual Status Check

```powershell
# Create a simple status dashboard
while ($true) {
    Clear-Host
    Write-Host "=== AUTONOMOUS AGENT STATUS ===" -ForegroundColor Cyan
    Write-Host ""
    
    $status = Invoke-WebRequest -Uri http://localhost:8000/agent/status | ConvertFrom-Json
    $safety = Invoke-WebRequest -Uri http://localhost:8000/agent/safety/status | ConvertFrom-Json
    
    Write-Host "Agent Enabled: $($safety.agent_enabled)" -ForegroundColor $(if ($safety.agent_enabled) {"Green"} else {"Red"})
    Write-Host "Modifications: $($safety.modifications_enabled)" -ForegroundColor $(if ($safety.modifications_enabled) {"Yellow"} else {"Green"})
    Write-Host "Kill Switch: $($safety.kill_switch_active)" -ForegroundColor $(if ($safety.kill_switch_active) {"Red"} else {"Green"})
    Write-Host "Loop Running: $($status.running)" -ForegroundColor $(if ($status.running) {"Green"} else {"Gray"})
    Write-Host "Loop Count: $($status.loop_count)" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "Press Ctrl+C to exit..." -ForegroundColor DarkGray
    
    Start-Sleep -Seconds 5
}
```

## 🔍 Troubleshooting

### Issue: Agent won't enable
**Solution**: Check if kill switch is active
```powershell
# Check for kill switch file
docker exec apex-orchestrator ls -la | Select-String "KILL_SWITCH"

# Remove if present
docker exec apex-orchestrator rm AGENT_KILL_SWITCH
```

### Issue: Can't access endpoints
**Solution**: Check if container is running
```powershell
docker-compose ps
docker-compose logs apex-orchestrator --tail 20
```

### Issue: Modifications blocked
**Solution**: Check daily limit
```powershell
Invoke-WebRequest -Uri http://localhost:8000/agent/status | ConvertFrom-Json | Select -ExpandProperty modification_stats
```

## 📚 Next Steps

1. ✅ Set passwords in `.env`
2. ✅ Enable agent in learning mode
3. ✅ Let it learn for a few days
4. ✅ Review learning reports regularly
5. ⏳ Consider enabling modifications (after testing!)

## 🆘 Emergency Commands

```powershell
# Stop everything
docker-compose down

# Reset agent
docker exec apex-orchestrator rm logs/agent_memory.db
docker exec apex-orchestrator rm -rf proposals backups

# Restart fresh
docker-compose up -d
```

---

**Ready to go!** Your autonomous agent is installed and ready for learning mode.

For full documentation, see: `docs/AUTONOMOUS_AGENT.md`

For complete summary, see: `AUTONOMOUS_AGENT_SUMMARY.md`

