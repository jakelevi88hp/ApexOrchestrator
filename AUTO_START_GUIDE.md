# 🚀 ApexOrchestrator - Auto-Startup Setup Guide

## Overview

This guide will configure ApexOrchestrator to automatically start when your PC boots or restarts. The system includes:

1. **Docker Desktop** - Container runtime
2. **Ollama** - LLM service
3. **ApexOrchestrator** - Main application with Content Lead & Investor agents

---

## 🎯 Quick Setup (5 Minutes)

### Step 1: Run the Auto-Configuration Script

**Open PowerShell as Administrator** (Right-click PowerShell → "Run as Administrator"):

```powershell
cd C:\ApexOrchestrator
.\setup_autostart.ps1
```

This script will:
- ✅ Configure Docker Desktop for auto-start
- ✅ Create Ollama service task
- ✅ Create ApexOrchestrator scheduled task
- ✅ Generate control scripts (start/stop/status)

### Step 2: Test the Setup

```powershell
# Start the server manually
.\start_service.ps1

# Wait 30-60 seconds for startup, then check status
.\check_status.ps1
```

### Step 3: Verify Auto-Startup

**Restart your PC** and wait 3-5 minutes. The system will:
1. Start Docker Desktop (immediately)
2. Start Ollama service (immediately)
3. Start ApexOrchestrator (2 minutes after boot)

After restart, check status:
```powershell
cd C:\ApexOrchestrator
.\check_status.ps1
```

---

## 📋 What Gets Configured

### 1. Docker Desktop Auto-Start
- **Method:** Windows Registry startup entry
- **Starts:** Immediately on login
- **Location:** `HKCU:\Software\Microsoft\Windows\CurrentVersion\Run`

### 2. Ollama Service
- **Method:** Windows Task Scheduler
- **Task Name:** `Ollama-Service-AutoStart`
- **Starts:** At system startup (as SYSTEM user)
- **Command:** `ollama serve`

### 3. ApexOrchestrator
- **Method:** Windows Task Scheduler
- **Task Name:** `ApexOrchestrator-AutoStart`
- **Starts:** 2 minutes after system startup
- **Restarts:** Automatically retries 3 times if crash
- **User:** Your current Windows user

---

## 🎮 Control Scripts

After setup, you have these convenient scripts:

### Start Server Manually
```powershell
.\start_service.ps1
```

### Stop Server
```powershell
.\stop_service.ps1
```

### Check Status
```powershell
.\check_status.ps1
```

**Example Status Output:**
```
📊 ApexOrchestrator Status Check
==================================================

✅ Server Status: RUNNING (PID: 12345)
✅ Port 8000: LISTENING
✅ API Health: HEALTHY

📋 Recent Logs (last 10 lines):
--------------------------------------------------
[2025-10-19 14:55:00] ApexOrchestrator server started
[2025-10-19 14:55:00] Content Lead Agent: LOADED
[2025-10-19 14:55:00] Investor Agent: LOADED
...
```

---

## 🐳 Docker Compose Option (Alternative)

If you prefer Docker containers, use Docker Compose:

### Build and Start
```powershell
docker-compose up -d --build
```

### Stop
```powershell
docker-compose down
```

### View Logs
```powershell
docker-compose logs -f
```

### Configure Docker Compose Auto-Start

Add this to your `setup_autostart.ps1` or run manually:

```powershell
$dockerComposeTask = @"
cd C:\ApexOrchestrator
docker-compose up -d
"@

$dockerComposeTask | Out-File -FilePath "C:\ApexOrchestrator\docker_startup.ps1" -Encoding UTF8

# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\ApexOrchestrator\docker_startup.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT3M"  # 3 minutes delay

Register-ScheduledTask -TaskName "ApexOrchestrator-Docker" -Action $action -Trigger $trigger -RunLevel Highest
```

---

## 📊 Access Points After Startup

Once the system is running:

| Service | URL | Description |
|---------|-----|-------------|
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Health Check** | http://localhost:8000/health | Server health status |
| **Content Lead Agent** | http://localhost:8000/content-lead/quick-start | Content generation |
| **Investor Agent** | http://localhost:8000/investor-agent/status | Investor outreach |
| **Validation Dashboard** | http://localhost:8000/validation/dashboard | System validation |
| **Ollama API** | http://localhost:11434 | LLM service |

---

## 🔧 Troubleshooting

### Issue: Server doesn't start after reboot

**Check 1: View startup logs**
```powershell
Get-Content C:\ApexOrchestrator\logs\startup.log -Tail 50
```

**Check 2: Verify scheduled task**
```powershell
Get-ScheduledTask -TaskName "ApexOrchestrator-AutoStart"
```

**Check 3: Run task manually**
```powershell
Start-ScheduledTask -TaskName "ApexOrchestrator-AutoStart"
```

### Issue: Docker not starting

**Solution:**
1. Open Docker Desktop
2. Go to Settings → General
3. Enable "Start Docker Desktop when you log in"
4. Click "Apply & Restart"

### Issue: Ollama not responding

**Solution:**
```powershell
# Check if Ollama is running
Get-Process ollama -ErrorAction SilentlyContinue

# If not, start manually
Start-ScheduledTask -TaskName "Ollama-Service-AutoStart"

# Or start directly
ollama serve
```

### Issue: Port 8000 already in use

**Solution:**
```powershell
# Find what's using port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

# Kill the process
Stop-Process -Id <PID> -Force
```

---

## 🔐 Security Considerations

### Firewall Rules

If you want to access ApexOrchestrator from other devices on your network:

```powershell
# Allow inbound traffic on port 8000 (run as Administrator)
New-NetFirewallRule -DisplayName "ApexOrchestrator API" `
    -Direction Inbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow
```

### Production Recommendations

For production deployments:

1. **Use HTTPS:** Configure reverse proxy (nginx/Caddy) with SSL
2. **Authentication:** Enable API key authentication in `.env`
3. **Rate Limiting:** Already configured via slowapi
4. **Monitoring:** Set up Prometheus + Grafana
5. **Backups:** Schedule regular backups of logs and data

---

## 📈 Monitoring & Logs

### Log Locations

| Log Type | Location |
|----------|----------|
| **Startup Logs** | `C:\ApexOrchestrator\logs\startup.log` |
| **Application Logs** | `C:\ApexOrchestrator\logs\apex_orchestrator.log` |
| **Docker Logs** | `docker-compose logs` |
| **Task Scheduler** | Event Viewer → Task Scheduler logs |

### View Real-Time Logs

```powershell
# Application logs
Get-Content C:\ApexOrchestrator\logs\apex_orchestrator.log -Wait -Tail 20

# Startup logs
Get-Content C:\ApexOrchestrator\logs\startup.log -Wait -Tail 20
```

---

## 🔄 Updating the System

### Update ApexOrchestrator Code

```powershell
# Stop the server
.\stop_service.ps1

# Pull latest code
git pull origin main

# Activate venv and update dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start server
.\start_service.ps1
```

### Update Ollama Models

```powershell
# Update models
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

---

## 🎯 Performance Optimization

### Startup Delay Tuning

If your system boots slowly, adjust the delay:

```powershell
# Open Task Scheduler
taskschd.msc

# Navigate to: Task Scheduler Library
# Right-click "ApexOrchestrator-AutoStart" → Properties
# Triggers tab → Edit
# Delay task for: Change from 2 minutes to 3-5 minutes
```

### Resource Limits

For Docker, adjust resources in Docker Desktop:
- Settings → Resources
- Increase CPU and Memory allocations
- Recommended: 4 CPUs, 8GB RAM

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Docker Desktop starts automatically
- [ ] Ollama service runs on boot
- [ ] ApexOrchestrator starts after 2-3 minutes
- [ ] Can access http://localhost:8000/docs
- [ ] Content Lead Agent responds
- [ ] Investor Agent responds
- [ ] Check status script works
- [ ] Logs are being written
- [ ] Server restarts after reboot

---

## 🆘 Support

If you encounter issues:

1. **Check logs:** `.\check_status.ps1`
2. **Review startup log:** `logs\startup.log`
3. **Test components individually:**
   - Docker: `docker ps`
   - Ollama: `ollama list`
   - Server: `.\start_service.ps1`

---

## 📚 Additional Resources

- **Main Documentation:** `COMPREHENSIVE_REPORT.md`
- **Deployment Guide:** `DEPLOYMENT_STATUS.md`
- **API Documentation:** http://localhost:8000/docs (when running)
- **Docker Compose Docs:** https://docs.docker.com/compose/

---

**🎉 Your ApexOrchestrator will now start automatically on every boot!**

The Content Lead Agent and Investor Agent are ready to generate revenue 24/7! 💰🚀

