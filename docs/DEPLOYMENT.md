# Production Deployment Guide - Apex Orchestrator

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Reverse Proxy Configuration](#reverse-proxy-configuration)
6. [Monitoring Setup](#monitoring-setup)
7. [Security Hardening](#security-hardening)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### Critical Requirements
- [ ] Python 3.11+ installed (for manual deployment)
- [ ] Docker and Docker Compose installed (for container deployment)
- [ ] Minimum 2GB RAM available
- [ ] 10GB disk space for logs and work directory
- [ ] Network connectivity for LLM provider (Ollama or OpenAI)
- [ ] Valid SSL certificate (for production HTTPS)
- [ ] Backup system in place

### Security Requirements
- [ ] Generated secure `APEX_SHARED_KEY` (minimum 32 characters)
- [ ] Reviewed and customized `config/policy.yaml`
- [ ] Configured firewall rules
- [ ] Set up monitoring and alerting
- [ ] Created separate non-root user for running service
- [ ] Configured CORS and trusted hosts (if needed)

### Configuration Files
- [ ] Created `.env` file from `config/env.example`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configured LLM provider settings
- [ ] Set up optional integrations (Telegram, webhooks)
- [ ] Reviewed timeout and rate limit settings

## Environment Setup

### 1. Generate Secure Keys

```bash
# Generate a secure shared key (Linux/Mac)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# On Windows PowerShell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Configure Environment Variables

Create `.env` file:

```bash
cp config/env.example .env
```

Edit `.env` with your production values:

```env
# CRITICAL: Use a strong random key
APEX_SHARED_KEY=<your-secure-key-from-above>

# Environment
ENVIRONMENT=production

# Model Provider
ORCH_MODEL_PROVIDER=ollama  # or openai
OLLAMA_URL=http://ollama:11434  # Use service name in Docker
OPENAI_API_KEY=<your-openai-key>

# Optional: Telegram notifications
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_ID=<your-chat-id>

# Directories (default paths work for Docker)
LOG_DIR=/app/logs
WORK_DIR=/app/work

# Security (production)
ALLOWED_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 3. Review Security Policy

Edit `config/policy.yaml` to match your requirements:

```yaml
shell_allow:
  # Only add commands you absolutely need
  - "git clone "
  - "docker compose "
  # Remove or add commands as needed

paths_allow:
  # Restrict to minimal necessary paths
  - "/app/work"

timeouts:
  shell_seconds: 120  # Adjust based on your use case
  python_seconds: 120
  http_seconds: 30

network:
  http_allow_domains:
    # Only add domains you trust
    - "api.github.com"
    - "your-trusted-api.com"
```

## Docker Deployment (Recommended)

### 1. Build and Start Services

```bash
# Build and start in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f apex-orchestrator

# Check status
docker-compose ps
```

### 2. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Expected response: {"ok": true, "service": "Apex Orchestrator", ...}
```

### 3. Docker Management Commands

```bash
# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Update after code changes
docker-compose down
docker-compose up -d --build

# View resource usage
docker stats apex-orchestrator

# Access container shell
docker exec -it apex-orchestrator /bin/bash
```

### 4. Docker Production Configuration

For production, update `docker-compose.yml`:

```yaml
services:
  apex-orchestrator:
    restart: always  # Change from unless-stopped
    deploy:
      resources:
        limits:
          cpus: '4'      # Increase based on load
          memory: 4G
        reservations:
          cpus: '1'
          memory: 1G
```

## Manual Deployment

### 1. System Preparation

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash apexuser
sudo usermod -aG docker apexuser  # If using Docker commands

# Create directories
sudo mkdir -p /opt/apex-orchestrator
sudo mkdir -p /var/log/apex
sudo mkdir -p /var/lib/apex/work

# Set ownership
sudo chown -R apexuser:apexuser /opt/apex-orchestrator
sudo chown -R apexuser:apexuser /var/log/apex
sudo chown -R apexuser:apexuser /var/lib/apex
```

### 2. Install Application

```bash
# Switch to service user
sudo su - apexuser

# Clone/copy application
cd /opt/apex-orchestrator
git clone <your-repo-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Systemd Service

Create `/etc/systemd/system/apex-orchestrator.service`:

```ini
[Unit]
Description=Apex Orchestrator Service
After=network.target

[Service]
Type=simple
User=apexuser
Group=apexuser
WorkingDirectory=/opt/apex-orchestrator
Environment="PATH=/opt/apex-orchestrator/venv/bin"
EnvironmentFile=/opt/apex-orchestrator/.env
ExecStart=/opt/apex-orchestrator/venv/bin/python scripts/start.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/apex/stdout.log
StandardError=append:/var/log/apex/stderr.log

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/apex /var/lib/apex

[Install]
WantedBy=multi-user.target
```

### 4. Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable autostart
sudo systemctl enable apex-orchestrator

# Start service
sudo systemctl start apex-orchestrator

# Check status
sudo systemctl status apex-orchestrator

# View logs
sudo journalctl -u apex-orchestrator -f
```

## Reverse Proxy Configuration

### Nginx Configuration

Create `/etc/nginx/sites-available/apex-orchestrator`:

```nginx
upstream apex_orchestrator {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting (additional layer)
    limit_req_zone $binary_remote_addr zone=apex_limit:10m rate=30r/m;
    limit_req zone=apex_limit burst=10 nodelay;

    # Logging
    access_log /var/log/nginx/apex-access.log;
    error_log /var/log/nginx/apex-error.log;

    # Proxy settings
    location / {
        proxy_pass http://apex_orchestrator;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Disable buffering for SSE if needed
        proxy_buffering off;
    }

    # Health check endpoint (no auth required)
    location /health {
        proxy_pass http://apex_orchestrator;
        access_log off;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/apex-orchestrator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Monitoring Setup

### 1. Application Monitoring

Monitor these endpoints:

- **Health**: `GET /health` - Overall system health
- **Metrics**: `GET /metrics` - Application metrics

### 2. Log Monitoring

```bash
# Monitor application logs
tail -f logs/apex_orchestrator.log

# Monitor execution logs
tail -f logs/*.log

# Search for errors
grep -r "ERROR" logs/

# Monitor specific operations
grep "Shell command" logs/apex_orchestrator.log
```

### 3. System Monitoring

```bash
# Resource usage
htop
docker stats

# Disk space
df -h
du -sh logs/

# Network connections
netstat -tulpn | grep 8000
```

### 4. Prometheus Metrics (Optional)

Consider adding `prometheus-fastapi-instrumentator` for detailed metrics:

```python
# Add to src/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(APP).expose(APP)
```

### 5. Alerting Rules

Set up alerts for:
- Service down (health check fails)
- High error rate (>5% of requests)
- Disk space low (<10% free)
- Memory usage high (>80%)
- Unusual authentication failures

## Security Hardening

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (for redirect)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Fail2ban Configuration

Create `/etc/fail2ban/filter.d/apex-orchestrator.conf`:

```ini
[Definition]
failregex = .*Auth error.*
ignoreregex =
```

Create `/etc/fail2ban/jail.d/apex-orchestrator.conf`:

```ini
[apex-orchestrator]
enabled = true
port = https,http
filter = apex-orchestrator
logpath = /var/log/apex/apex_orchestrator.log
maxretry = 5
bantime = 3600
findtime = 600
```

### 3. Regular Security Updates

```bash
# Create update script
cat > /opt/apex-orchestrator/update.sh << 'EOF'
#!/bin/bash
cd /opt/apex-orchestrator
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart apex-orchestrator
EOF

chmod +x /opt/apex-orchestrator/update.sh
```

### 4. Audit Logging

Enable audit logging for compliance:

```bash
# Log all sudo commands
sudo visudo
# Add: Defaults log_output
# Add: Defaults!/usr/bin/sudoreplay !log_output

# Monitor file changes
sudo apt-get install auditd
sudo auditctl -w /opt/apex-orchestrator/config -p wa -k apex-config
```

## Backup and Recovery

### 1. Backup Strategy

```bash
#!/bin/bash
# /opt/apex-orchestrator/backup.sh

BACKUP_DIR="/backup/apex"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/ .env

# Backup logs (last 7 days)
find logs/ -name "*.log" -mtime -7 -exec tar -czf $BACKUP_DIR/logs_$DATE.tar.gz {} +

# Backup work directory
tar -czf $BACKUP_DIR/work_$DATE.tar.gz /var/lib/apex/work

# Remove old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 2. Automated Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/apex-orchestrator/backup.sh >> /var/log/apex/backup.log 2>&1
```

### 3. Disaster Recovery Plan

1. **Restore Configuration**:
   ```bash
   tar -xzf config_YYYYMMDD_HHMMSS.tar.gz
   ```

2. **Restore Application**:
   ```bash
   git clone <repo-url> /opt/apex-orchestrator-new
   cd /opt/apex-orchestrator-new
   # ... follow installation steps
   ```

3. **Restore Data**:
   ```bash
   tar -xzf work_YYYYMMDD_HHMMSS.tar.gz -C /var/lib/apex/
   ```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u apex-orchestrator -n 50 --no-pager

# Check configuration
python -m src.main  # Will show config errors

# Check port availability
sudo netstat -tulpn | grep 8000

# Check file permissions
ls -la /opt/apex-orchestrator
```

### High Memory Usage

```bash
# Check process memory
ps aux | grep python | grep apex

# Reduce workers in start.py
export WORKERS=1

# Monitor over time
watch -n 5 'ps aux | grep python | grep apex'
```

### Authentication Failures

```bash
# Verify shared key is set
grep APEX_SHARED_KEY .env

# Check key length
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(len(os.getenv('APEX_SHARED_KEY', '')))"

# Test authentication
curl -X POST http://localhost:8000/auth/echo-sign \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Log Files Growing Too Large

```bash
# Check log sizes
du -sh logs/*

# Manual log rotation
cd logs
for log in *.log; do
  mv $log $log.$(date +%Y%m%d)
  gzip $log.$(date +%Y%m%d)
done

# Find and delete old logs
find logs/ -name "*.gz" -mtime +30 -delete
```

### Performance Issues

```bash
# Check system resources
top
iostat -x 1
vmstat 1

# Check slow queries in logs
grep "Duration: [5-9]" logs/apex_orchestrator.log

# Increase worker count
export WORKERS=4

# Optimize rate limits in src/main.py
```

## Post-Deployment Verification

### Smoke Tests

```bash
# 1. Health check
curl https://api.yourdomain.com/health

# 2. Metrics check
curl https://api.yourdomain.com/metrics

# 3. Authentication test
curl -X POST https://api.yourdomain.com/auth/echo-sign \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# 4. Check logs
tail -n 50 logs/apex_orchestrator.log
```

### Load Testing (Optional)

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 https://api.yourdomain.com/health

# Monitor during test
watch -n 1 'curl -s http://localhost:8000/metrics | jq .'
```

## Maintenance Schedule

### Daily
- [ ] Monitor logs for errors
- [ ] Check disk space
- [ ] Verify health check status

### Weekly
- [ ] Review security logs
- [ ] Check backup success
- [ ] Update dependencies (test environment first)
- [ ] Review rate limit logs

### Monthly
- [ ] Security audit
- [ ] Performance review
- [ ] Backup recovery test
- [ ] Update SSL certificates (if not automated)

### Quarterly
- [ ] Full disaster recovery drill
- [ ] Security policy review
- [ ] Capacity planning review
- [ ] Documentation update

## Support and Resources

- **Documentation**: `/docs` directory
- **Logs**: `/var/log/apex/` or `logs/`
- **Configuration**: `config/policy.yaml` and `.env`
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`

## Emergency Contacts

Document your emergency procedures:

1. **Service Down**: [procedure]
2. **Security Incident**: [procedure]
3. **Data Loss**: [procedure]
4. **Escalation Path**: [contacts]

