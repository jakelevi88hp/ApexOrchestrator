# Production Readiness Checklist

## Pre-Launch Verification

### Configuration ✓
- [ ] `.env` file created from `config/env.example`
- [ ] `APEX_SHARED_KEY` set (minimum 32 characters)
- [ ] `ENVIRONMENT` set to `production`
- [ ] Model provider configured (Ollama or OpenAI)
- [ ] All required API keys configured
- [ ] `config/policy.yaml` reviewed and customized
- [ ] Rate limits reviewed and adjusted if needed
- [ ] CORS and trusted hosts configured (if needed)

### Security ✓
- [ ] Strong random key generated for `APEX_SHARED_KEY`
- [ ] Shell command allowlist reviewed in policy.yaml
- [ ] File path restrictions reviewed in policy.yaml
- [ ] Network domain allowlist reviewed in policy.yaml
- [ ] Firewall rules configured
- [ ] SSL/TLS certificates installed
- [ ] Security headers enabled (automatic)
- [ ] Rate limiting enabled (automatic)
- [ ] Fail2ban configured (optional but recommended)

### Infrastructure ✓
- [ ] Minimum 2GB RAM available
- [ ] Minimum 10GB disk space for logs
- [ ] Docker and Docker Compose installed (for container deployment)
- [ ] Python 3.11+ installed (for manual deployment)
- [ ] Reverse proxy configured (Nginx/Apache)
- [ ] Monitoring system set up
- [ ] Backup system configured
- [ ] Log rotation configured (automatic with application)

### Testing ✓
- [ ] Health endpoint responds: `GET /health`
- [ ] Metrics endpoint responds: `GET /metrics`
- [ ] Authentication working: `POST /auth/echo-sign`
- [ ] Can execute safe commands through API
- [ ] Dangerous commands blocked by policy
- [ ] Rate limiting working correctly
- [ ] Logs being written properly
- [ ] All tests passing: `pytest tests/`

### Deployment ✓
- [ ] Application deployed (Docker or manual)
- [ ] Service running and healthy
- [ ] Accessible via reverse proxy
- [ ] HTTPS working correctly
- [ ] Health checks passing
- [ ] Logs accessible and readable
- [ ] Restart behavior verified
- [ ] Graceful shutdown tested

### Monitoring & Logging ✓
- [ ] Application logs monitored: `logs/apex_orchestrator.log`
- [ ] Execution logs monitored: `logs/*.log`
- [ ] Health check monitoring configured
- [ ] Error alerting configured
- [ ] Disk space monitoring configured
- [ ] Memory usage monitoring configured
- [ ] Log rotation working (10MB max per file)
- [ ] Old logs cleaned up automatically

### Documentation ✓
- [ ] `README.md` reviewed
- [ ] `docs/DEPLOYMENT.md` read and understood
- [ ] `docs/SECURITY.md` reviewed
- [ ] `docs/API.md` available for users
- [ ] Team trained on operations procedures
- [ ] Emergency contacts documented
- [ ] Disaster recovery plan created

### Backup & Recovery ✓
- [ ] Backup script created
- [ ] Automated backups scheduled
- [ ] Backup restoration tested
- [ ] Configuration backed up
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined

### Performance ✓
- [ ] Load testing completed (optional)
- [ ] Response times acceptable
- [ ] Resource usage within limits
- [ ] Worker count optimized
- [ ] Database connections optimized (if applicable)
- [ ] Timeout values appropriate for workload

### Compliance ✓
- [ ] Data protection requirements met
- [ ] Audit logging enabled
- [ ] Access controls documented
- [ ] Security policies documented
- [ ] Change management process in place
- [ ] Incident response plan created

## Post-Launch Monitoring

### First 24 Hours
- [ ] Monitor logs continuously
- [ ] Check health endpoint every 5 minutes
- [ ] Review error rates
- [ ] Monitor resource usage
- [ ] Verify backups running
- [ ] Check rate limiting effectiveness

### First Week
- [ ] Review all error logs
- [ ] Analyze performance metrics
- [ ] Check disk space trends
- [ ] Review authentication failures
- [ ] Verify backup integrity
- [ ] Optimize based on usage patterns

### First Month
- [ ] Full security audit
- [ ] Performance optimization review
- [ ] Capacity planning review
- [ ] Documentation updates
- [ ] Team feedback and training
- [ ] Disaster recovery drill

## Production Readiness Score

Calculate your score:

- **Configuration**: __/8 points (1 per item)
- **Security**: __/9 points (1 per item)
- **Infrastructure**: __/8 points (1 per item)
- **Testing**: __/8 points (1 per item)
- **Deployment**: __/8 points (1 per item)
- **Monitoring & Logging**: __/8 points (1 per item)
- **Documentation**: __/7 points (1 per item)
- **Backup & Recovery**: __/6 points (1 per item)
- **Performance**: __/6 points (1 per item)
- **Compliance**: __/6 points (1 per item)

**Total**: __/74 points

### Score Interpretation

- **70-74 points**: Excellent - Ready for production
- **60-69 points**: Good - Minor improvements needed
- **50-59 points**: Fair - Significant improvements needed
- **Below 50**: Not ready - Address critical gaps

## Sign-off

### Deployment Team
- [ ] Developer Sign-off: _____________ Date: _______
- [ ] DevOps Sign-off: _____________ Date: _______
- [ ] Security Sign-off: _____________ Date: _______
- [ ] Management Sign-off: _____________ Date: _______

### Notes
```
[Add any special considerations, exceptions, or additional notes here]
```

## Quick Commands Reference

```bash
# Check service status
systemctl status apex-orchestrator
docker-compose ps

# View logs
tail -f logs/apex_orchestrator.log
docker-compose logs -f

# Health check
curl https://api.yourdomain.com/health

# Restart service
systemctl restart apex-orchestrator
docker-compose restart

# Update application
git pull && docker-compose up -d --build

# Backup now
/opt/apex-orchestrator/backup.sh

# Monitor resources
docker stats
htop
```

## Emergency Procedures

### Service Down
1. Check logs: `journalctl -u apex-orchestrator -n 100`
2. Check resources: `htop` and `df -h`
3. Restart service: `systemctl restart apex-orchestrator`
4. Verify health: `curl localhost:8000/health`
5. Check reverse proxy: `nginx -t && systemctl status nginx`

### High Resource Usage
1. Check current usage: `docker stats` or `top`
2. Review logs for errors
3. Consider reducing workers: Update `WORKERS` env var
4. Restart service
5. Monitor after restart

### Security Incident
1. Immediately rotate `APEX_SHARED_KEY`
2. Review logs for suspicious activity
3. Check for unauthorized access
4. Review and tighten policies
5. Document incident
6. Notify stakeholders

### Data Loss
1. Stop service immediately
2. Assess extent of loss
3. Restore from most recent backup
4. Verify restoration
5. Resume service
6. Document incident and improve backup strategy

