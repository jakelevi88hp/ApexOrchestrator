# 🎯 AUTO-START SETUP - QUICK REFERENCE

## ⚡ Setup in 3 Steps

```
┌─────────────────────────────────────────────────────┐
│  STEP 1: Run Setup Script (as Administrator)       │
└─────────────────────────────────────────────────────┘

   Right-click PowerShell → "Run as Administrator"
   
   cd C:\ApexOrchestrator
   .\setup_autostart.ps1


┌─────────────────────────────────────────────────────┐
│  STEP 2: Test Manual Start                         │
└─────────────────────────────────────────────────────┘

   .\start_service.ps1
   
   Wait 30 seconds...
   
   .\check_status.ps1


┌─────────────────────────────────────────────────────┐
│  STEP 3: Restart PC & Verify                       │
└─────────────────────────────────────────────────────┘

   Restart Windows
   
   Wait 3-5 minutes for full startup
   
   cd C:\ApexOrchestrator
   .\check_status.ps1
```

---

## 📊 What Gets Auto-Started

```
BOOT SEQUENCE:
═══════════════

t=0s    │ Windows Boots
        │
t=5s    │ ┌──────────────────┐
        │ │ Docker Desktop   │ ← Starts immediately
        │ │ (via Registry)   │
        │ └──────────────────┘
        │
t=10s   │ ┌──────────────────┐
        │ │ Ollama Service   │ ← Starts at boot
        │ │ (Task Scheduler) │
        │ └──────────────────┘
        │
t=120s  │ ┌──────────────────────────────┐
        │ │ ApexOrchestrator             │ ← Starts after 2min delay
        │ │ - Content Lead Agent         │
        │ │ - Investor Agent             │
        │ │ - Pulse System               │
        │ │ - Validation Dashboard       │
        │ └──────────────────────────────┘
        │
t=150s  │ ✅ FULLY OPERATIONAL
```

---

## 🎮 Control Commands

```powershell
# START SERVER
.\start_service.ps1

# STOP SERVER
.\stop_service.ps1

# CHECK STATUS
.\check_status.ps1

# VIEW LOGS
Get-Content logs\startup.log -Tail 20 -Wait
```

---

## 🌐 Access URLs (after startup)

```
┌──────────────────────────────────────────────────────┐
│  📚 API Docs                                         │
│  http://localhost:8000/docs                          │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  💰 Content Lead Agent                               │
│  http://localhost:8000/content-lead/quick-start      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  📈 Investor Agent                                   │
│  http://localhost:8000/investor-agent/status         │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  ❤️  Health Check                                    │
│  http://localhost:8000/health                        │
└──────────────────────────────────────────────────────┘
```

---

## 🔧 Files Created

| File | Purpose |
|------|---------|
| `setup_autostart.ps1` | **Main setup script (run once)** |
| `startup_service.ps1` | Auto-start script (used by Task Scheduler) |
| `start_service.ps1` | Manual start |
| `stop_service.ps1` | Manual stop |
| `check_status.ps1` | Status checker |
| `docker-compose.yml` | Docker container config (optional) |
| `Dockerfile` | Container image definition |
| `AUTO_START_GUIDE.md` | Full documentation |

---

## ✅ Success Indicators

After reboot, you should see:

```
.\check_status.ps1

📊 ApexOrchestrator Status Check
==================================================

✅ Server Status: RUNNING (PID: xxxxx)
✅ Port 8000: LISTENING
✅ API Health: HEALTHY

📋 Recent Logs:
[2025-10-19 XX:XX:XX] ========================================
[2025-10-19 XX:XX:XX] ApexOrchestrator Auto-Startup Initiated
[2025-10-19 XX:XX:XX] ========================================
[2025-10-19 XX:XX:XX] ✅ Docker is ready
[2025-10-19 XX:XX:XX] ✅ Ollama is ready
[2025-10-19 XX:XX:XX] Starting ApexOrchestrator server...
[2025-10-19 XX:XX:XX] SERVER: [CONTENT LEAD] Agent routes registered
[2025-10-19 XX:XX:XX] SERVER: [INVESTOR] Agent routes registered
[2025-10-19 XX:XX:XX] SERVER: INFO: Application startup complete.
```

---

## 🆘 Quick Troubleshooting

### Server didn't start after reboot?

```powershell
# Check startup log
Get-Content logs\startup.log -Tail 30

# Start manually
.\start_service.ps1
```

### Ollama not responding?

```powershell
# Start Ollama task
Start-ScheduledTask -TaskName "Ollama-Service-AutoStart"
```

### Docker not running?

```powershell
# Check Docker Desktop
Get-Process "Docker Desktop" -ErrorAction SilentlyContinue

# Start Docker Desktop manually
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

---

## 🎯 Next Steps

1. **Run Setup:** `.\setup_autostart.ps1` (as Administrator)
2. **Test:** `.\start_service.ps1` then `.\check_status.ps1`
3. **Reboot:** Restart PC to test auto-start
4. **Verify:** Check status after reboot

---

## 📚 Full Documentation

See `AUTO_START_GUIDE.md` for complete details including:
- Docker Compose setup
- Security configuration
- Monitoring & logging
- Performance tuning
- Troubleshooting guides

---

**🚀 Your revenue-generating agents will now run 24/7 automatically!** 💰

