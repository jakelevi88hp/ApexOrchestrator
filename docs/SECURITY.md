# Security Guide - Apex Orchestrator

## Overview

Apex Orchestrator implements multiple layers of security to ensure safe execution of automated tasks in enterprise environments.

## Authentication & Authorization

### HMAC Signature Authentication
- All API requests require valid HMAC-SHA256 signatures
- Signatures include timestamp to prevent replay attacks
- 5-minute timestamp tolerance window
- Shared key must be kept secure and rotated regularly

### Request Verification Process
1. Extract `X-TS` and `X-SIG` headers
2. Validate timestamp is within acceptable range
3. Recreate signature using shared key
4. Compare signatures using constant-time comparison

## Policy-Based Security

### Shell Command Restrictions
The system maintains an allowlist of permitted shell commands:

```yaml
shell_allow:
  - "git clone "
  - "git pull"
  - "python "
  - "pip install "
  - "docker compose "
  - "docker run "
  - "dir"
  - "type "
  - "copy "
  - "move "
  - "mkdir "
  - "rmdir "
  - "powershell -File "
```

**Security Benefits:**
- Prevents arbitrary command execution
- Limits to safe, high-level operations
- Blocks dangerous commands like `rm -rf`, `format`, etc.

### File System Access Control
Restricted to specific directory paths:

```yaml
paths_allow:
  - "C:\\ApexWork"
  - "C:\\ApexOrchestrator"
```

**Security Benefits:**
- Prevents access to system directories
- Isolates operations to designated workspaces
- Protects sensitive system files

### Network Security

#### Domain Allowlisting
HTTP requests are restricted to approved domains:

```yaml
network:
  http_allow_domains:
    - "api.github.com"
    - "raw.githubusercontent.com"
    - "pypi.org"
    - "files.pythonhosted.org"
```

**Security Benefits:**
- Prevents data exfiltration
- Blocks malicious website access
- Allows only trusted API endpoints

#### Request Timeouts
All operations have configurable timeouts:

```yaml
timeouts:
  shell_seconds: 120
  python_seconds: 120
  http_seconds: 30
```

## Secure Configuration

### Environment Variables
Store sensitive configuration in environment variables:

```env
APEX_SHARED_KEY=<secure_random_key>
OPENAI_API_KEY=<your_openai_key>
TELEGRAM_BOT_TOKEN=<your_bot_token>
```

**Best Practices:**
- Use strong, randomly generated keys
- Rotate keys regularly
- Never commit keys to version control
- Use separate keys for different environments

### File Permissions
Ensure proper file permissions on configuration files:

```bash
# Restrict access to configuration files
chmod 600 config/policy.yaml
chmod 600 .env
```

## Operational Security

### Logging & Monitoring
- All operations are logged with timestamps
- Failed authentication attempts are recorded
- Monitor logs for suspicious activity
- Set up alerts for policy violations

### Regular Security Maintenance
1. **Update Dependencies**: Regularly update all packages
2. **Review Policies**: Audit allowed commands and paths
3. **Rotate Keys**: Change authentication keys periodically
4. **Monitor Access**: Review API usage patterns

### Network Security
- Run behind a reverse proxy (nginx, Apache)
- Use HTTPS in production
- Implement IP allowlisting if needed
- Consider VPN access for administrative functions

## Incident Response

### Security Breach Checklist
1. **Immediate Response**:
   - Disable affected API keys
   - Review recent logs
   - Identify scope of compromise

2. **Investigation**:
   - Analyze execution logs
   - Check for unauthorized file access
   - Review network requests

3. **Recovery**:
   - Update all authentication keys
   - Review and tighten policies
   - Implement additional monitoring

### Log Analysis
Key log entries to monitor:
- Authentication failures
- Policy violations
- Unusual execution patterns
- Network requests to unauthorized domains

## Compliance Considerations

### Data Protection
- Logs may contain sensitive information
- Implement log retention policies
- Consider data encryption at rest
- Ensure GDPR/privacy compliance

### Audit Requirements
- Maintain execution logs for compliance
- Document policy changes
- Regular security assessments
- Access control reviews

## Security Recommendations

### Production Deployment
1. Use dedicated service accounts
2. Implement network segmentation
3. Enable comprehensive logging
4. Set up monitoring and alerting
5. Regular security updates
6. Backup and recovery procedures

### Development Security
1. Use separate environments
2. Implement code reviews
3. Automated security testing
4. Dependency vulnerability scanning

## Contact

For security concerns or to report vulnerabilities, contact the development team immediately.

