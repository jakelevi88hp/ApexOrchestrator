# Apex Orchestrator - Quick Reference Card

## 🚀 Quick Start

### Docker Deployment
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f apex-orchestrator

# Restart
docker-compose restart
```

### Manual Deployment
```bash
# Start
python scripts/start.py

# Stop
Ctrl+C or systemctl stop apex-orchestrator
```

## 🔍 Health & Status

### Check Health
```bash
curl http://localhost:8000/health
```

### Check Metrics
```bash
curl http://localhost:8000/metrics
```

### View Logs
```bash
# Real-time logs
tail -f logs/apex_orchestrator.log

# Recent logs
tail -n 100 logs/apex_orchestrator.log

# Search for errors
grep ERROR logs/apex_orchestrator.log
```

## 🔐 Configuration

### Environment Variables (.env)
```env
# Required
APEX_SHARED_KEY=<32+ character key>
ENVIRONMENT=production
ORCH_MODEL_PROVIDER=ollama

# Optional
TELEGRAM_BOT_TOKEN=<token>
ALLOWED_ORIGINS=https://yourdomain.com
```

### Generate Secure Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📊 API Endpoints

| Endpoint | Method | Rate Limit | Auth Required |
|----------|--------|------------|---------------|
| `/health` | GET | 30/min | No |
| `/metrics` | GET | 10/min | No |
| `/nlm/run` | POST | 10/min | Yes |
| `/apex/run` | POST | 20/min | Yes |
| `/auth/echo-sign` | POST | 30/min | No |

## 🔒 Authentication

### Headers Required
```
X-TS: <unix timestamp>
X-SIG: <HMAC-SHA256 signature>
```

### Generate Signature
```bash
curl -X POST http://localhost:8000/auth/echo-sign \
  -H "Content-Type: application/json" \
  -d '{"text": "test request"}'
```

## 🛠️ Common Operations

### Restart Service
```bash
# Docker
docker-compose restart

# Systemd
sudo systemctl restart apex-orchestrator

# Manual
pkill -f "python.*start.py" && python scripts/start.py
```

### View Resource Usage
```bash
# Docker
docker stats apex-orchestrator

# System
htop
ps aux | grep apex
```

### Check Disk Space
```bash
df -h
du -sh logs/
```

### Rotate Logs Manually
```bash
cd logs
for log in *.log; do
  mv $log $log.$(date +%Y%m%d)
  gzip $log.$(date +%Y%m%d)
done
```

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
tail -f logs/apex_orchestrator.log

# Verify config
python -c "from src.main import config"

# Check port
netstat -tulpn | grep 8000

# Check key length
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(len(os.getenv('APEX_SHARED_KEY', '')))"
```

### High Memory Usage
```bash
# Check usage
docker stats

# Reduce workers
export WORKERS=1

# Restart
docker-compose restart
```

### Authentication Failures
```bash
# Verify key is set
grep APEX_SHARED_KEY .env

# Test auth
curl -X POST http://localhost:8000/auth/echo-sign -d '{}'

# Check logs for auth errors
grep "Auth error" logs/apex_orchestrator.log
```

### Log Files Too Large
```bash
# Check sizes
du -h logs/*.log

# Clean old logs
find logs/ -name "*.log.*" -mtime +30 -delete

# Note: Auto-rotation at 10MB enabled
```

## 📈 Monitoring

### What to Monitor
- Health endpoint status (every 30s)
- Error rate in logs
- Disk space usage
- Memory usage
- CPU usage
- Response times

### Alert Thresholds
- Health check fails
- Error rate > 5%
- Disk space < 10%
- Memory usage > 80%
- CPU usage > 90% sustained

## 🔄 Updates

### Update Application
```bash
# Docker
git pull
docker-compose down
docker-compose up -d --build

# Manual
git pull
source venv/bin/activate
pip install -r requirements.txt -U
systemctl restart apex-orchestrator
```

### Update Configuration
```bash
# Edit policy
nano config/policy.yaml

# Edit environment
nano .env

# Restart to apply
docker-compose restart
```

## 💾 Backup & Recovery

### Backup Now
```bash
# Configuration
tar -czf backup_config_$(date +%Y%m%d).tar.gz config/ .env

# Logs
tar -czf backup_logs_$(date +%Y%m%d).tar.gz logs/

# Work directory
tar -czf backup_work_$(date +%Y%m%d).tar.gz /var/lib/apex/work/
```

### Restore
```bash
# Stop service
docker-compose down

# Restore files
tar -xzf backup_config_YYYYMMDD.tar.gz

# Start service
docker-compose up -d
```

## 🔐 Security

### Review Access
```bash
# Check auth failures
grep "401" logs/apex_orchestrator.log

# Check policy violations
grep "403" logs/apex_orchestrator.log

# Recent operations
tail -n 50 logs/*.log
```

### Rotate Secrets
```bash
# Generate new key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
nano .env

# Restart
docker-compose restart

# Update all clients with new key
```

## 📞 Emergency Procedures

### Service Down
1. Check logs: `tail -f logs/apex_orchestrator.log`
2. Check resources: `docker stats` or `htop`
3. Restart: `docker-compose restart`
4. Verify: `curl localhost:8000/health`

### Security Incident
1. Stop service: `docker-compose down`
2. Review logs for suspicious activity
3. Rotate `APEX_SHARED_KEY`
4. Review and tighten policies
5. Resume service
6. Document incident

### Data Loss
1. Stop service immediately
2. Restore from backup
3. Verify restoration
4. Resume service
5. Document and improve backup strategy

## 📚 Documentation Links

- **Full Deployment Guide**: `docs/DEPLOYMENT.md`
- **Security Guide**: `docs/SECURITY.md`
- **API Documentation**: `docs/API.md`
- **Production Checklist**: `PRODUCTION_CHECKLIST.md`
- **Production Summary**: `PRODUCTION_READY_SUMMARY.md`

## 🎯 Key Files

```
Configuration:
  .env                  # Environment variables
  config/policy.yaml    # Security policies
  
Logs:
  logs/apex_orchestrator.log  # Main application log
  logs/*.log                  # Execution logs
  
Scripts:
  scripts/start.py      # Startup script
  scripts/install.py    # Installation script
  
Docker:
  Dockerfile           # Container image
  docker-compose.yml   # Orchestration
```

## 🔢 Default Ports

- **Application**: 8000
- **Ollama** (optional): 11434
- **HTTPS** (reverse proxy): 443

## 📊 Performance Baselines

- **Response Time**: < 200ms for health check
- **Memory Usage**: < 500MB typical
- **Disk Usage**: ~10MB/day for logs
- **CPU Usage**: < 10% idle, < 50% under load

---

**For detailed information, see full documentation in `docs/` directory**

