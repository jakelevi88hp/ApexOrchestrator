# Autonomous Agent Documentation

## 🤖 Overview

The Apex Orchestrator Autonomous Agent is a self-improving, self-modifying system that learns from execution history, identifies optimization opportunities, and can propose and apply code modifications with extensive safety controls.

## ⚠️ CRITICAL SAFETY NOTICE

**The Autonomous Agent has the capability to modify its own code.** This is an advanced feature that should only be enabled after careful consideration and with proper safeguards in place.

### Default State

- **Agent**: DISABLED by default
- **Code Modifications**: DISABLED by default  
- **Approval Required**: YES (all modifications require approval)
- **Sandbox Mode**: ENABLED by default

## 🏗️ Architecture

### Core Components

1. **Memory System** (`agent/memory.py`)
   - Persistent SQLite database
   - Execution history tracking
   - Learned patterns storage
   - Code templates library
   - Self-modification logs

2. **Pattern Learner** (`agent/learner.py`)
   - Analyzes execution patterns
   - Identifies optimization opportunities
   - Learns from successes and failures
   - Generates improvement suggestions

3. **Code Generator** (`agent/code_generator.py`)
   - Generates new functions and tools
   - Creates code optimizations
   - Produces test cases
   - Analyzes code quality

4. **Self-Modifier** (`agent/self_modifier.py`)
   - Proposes code modifications
   - Creates backups before changes
   - Runs tests before applying
   - Supports rollback operations

5. **Safety Controller** (`agent/safety.py`)
   - Kill switch mechanism
   - Modification limits
   - Operation validation
   - Incident logging

6. **Agent Loop** (`agent/agent_loop.py`)
   - Main orchestration loop
   - Learning cycles
   - Analysis phases
   - Improvement execution

## 🚀 Getting Started

### Step 1: Enable the Agent

```bash
# Via API
curl -X POST http://localhost:8000/agent/enable \
  -H "Content-Type: application/json" \
  -d '{"password": "your-password-here"}'
```

**Environment Variables:**
```bash
# Set password for enabling agent
AGENT_ENABLE_PASSWORD=your_secure_password

# Set password for enabling modifications
MODIFICATIONS_ENABLE_PASSWORD=different_secure_password

# Set password for kill switch
KILL_SWITCH_PASSWORD=yet_another_password
```

### Step 2: Check Status

```bash
curl http://localhost:8000/agent/status
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

### Step 3: Start the Agent Loop (Optional)

```bash
curl -X POST "http://localhost:8000/agent/start-loop?interval_seconds=3600"
```

This starts the autonomous learning loop that runs every hour.

## 📊 API Endpoints

### Agent Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/status` | GET | Get agent status |
| `/agent/enable` | POST | Enable agent (requires password) |
| `/agent/disable` | POST | Disable agent |
| `/agent/start-loop` | POST | Start autonomous loop |
| `/agent/stop-loop` | POST | Stop autonomous loop |

### Learning & Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/learning-report` | GET | Get comprehensive learning report |
| `/agent/opportunities` | GET | List optimization opportunities |
| `/agent/suggestions` | GET | Get improvement suggestions |
| `/agent/memory/stats` | GET | Memory system statistics |
| `/agent/memory/executions` | GET | Execution history |

### Code Modifications

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/modifications/enable` | POST | Enable modifications (requires password) |
| `/agent/modifications/disable` | POST | Disable modifications |
| `/agent/modifications/propose` | POST | Propose a modification |
| `/agent/modifications/apply` | POST | Apply a proposed modification |

### Safety Controls

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/safety/status` | GET | Get safety status |
| `/agent/kill-switch/activate` | POST | Activate emergency kill switch |
| `/agent/kill-switch/deactivate` | POST | Deactivate kill switch (requires password) |

## 🔒 Safety Features

### 1. Kill Switch

Emergency stop mechanism that immediately halts all autonomous operations.

```bash
# Activate
curl -X POST "http://localhost:8000/agent/kill-switch/activate?reason=Emergency+stop"

# Creates file: AGENT_KILL_SWITCH

# Deactivate (requires password)
curl -X POST "http://localhost:8000/agent/kill-switch/deactivate?password=your_password"
```

### 2. Modification Limits

- **Daily Limit**: Maximum 5 modifications per day (configurable)
- **Requires Approval**: All modifications need explicit approval by default
- **Automatic Testing**: Tests are run before applying changes
- **Automatic Backup**: Backup created before every modification
- **Rollback Support**: Can rollback failed modifications

### 3. Operation Validation

Dangerous operations are blocked:
- System directory modifications
- Dangerous shell commands (`rm -rf`, `format`, etc.)
- Protected file paths
- Network restrictions

### 4. Sandbox Mode

When enabled (default):
- Read-only access to production code
- Modifications proposed but not applied
- Full audit trail maintained

### 5. Incident Logging

All safety incidents are logged to `logs/safety_incidents.log`:
```
2025-10-17T12:00:00Z [CRITICAL] emergency_shutdown: Manual intervention required
2025-10-17T11:30:00Z [MEDIUM] low_success_rate: Success rate dropped to 45%
```

## 📈 How It Works

### Learning Cycle (Default: Every Hour)

1. **Learning Phase**
   - Analyze recent executions
   - Learn from successes and failures
   - Update pattern database
   - Calculate success rates

2. **Analysis Phase**
   - Identify execution patterns
   - Find optimization opportunities
   - Generate recommendations
   - Prioritize improvements

3. **Improvement Phase** (if enabled)
   - Process top suggestions
   - Generate code templates
   - Propose optimizations
   - Create improvement proposals

4. **Self-Optimization Phase** (if enabled)
   - Analyze own performance
   - Identify self-improvements
   - Propose code modifications
   - Apply approved changes

### Example Learning Process

```
1. Execute operation: "list files"
2. Record: success=true, time=150ms
3. Learn: Pattern saved with confidence=1.0
4. Analyze: This pattern works well
5. Template: Create reusable "list_files" template
6. Optimize: Suggest caching for repeated calls
```

## 🛠️ Working with Modifications

### Proposing a Modification

```bash
curl -X POST http://localhost:8000/agent/modifications/propose \
  -H "Content-Type: application/json" \
  -d '{
    "target_file": "src/main.py",
    "modification_type": "optimize",
    "description": "Add caching to frequently called function",
    "reason": "Function called 100+ times with same inputs"
  }'
```

Response:
```json
{
  "status": "proposed",
  "proposal": {
    "id": 20251017120000,
    "target_file": "src/main.py",
    "backup_path": "backups/main.py.backup_20251017_120000",
    "validation": {
      "quality_score": 95,
      "issues": [],
      "suggestions": []
    }
  }
}
```

### Applying a Modification

```bash
curl -X POST http://localhost:8000/agent/modifications/apply \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": 20251017120000,
    "auto_test": true
  }'
```

Response:
```json
{
  "status": "applied",
  "file": "src/main.py",
  "backup": "backups/main.py.backup_20251017_120000",
  "test_results": {
    "status": "passed"
  },
  "modifications_remaining_today": 4
}
```

## 📊 Monitoring

### View Learning Report

```bash
curl http://localhost:8000/agent/learning-report
```

Returns:
- Execution analysis (24h)
- Optimization opportunities
- Improvement suggestions
- Patterns learned

### Check Memory Stats

```bash
curl http://localhost:8000/agent/memory/stats
```

Returns:
- Total executions
- Success rate
- Learned patterns count
- Code templates count
- Modifications applied

### View Opportunities

```bash
curl http://localhost:8000/agent/opportunities
```

Returns prioritized list of:
- Performance optimizations
- Reliability improvements
- Code reuse opportunities

## 🎯 Use Cases

### 1. Automated Learning

Let the agent learn from your usage patterns:

```bash
# Enable agent (learning only, no modifications)
curl -X POST http://localhost:8000/agent/enable \
  -H "Content-Type: application/json" \
  -d '{"password": "your_password"}'

# Start learning loop
curl -X POST "http://localhost:8000/agent/start-loop?interval_seconds=3600"

# Check what it learned after a day
curl http://localhost:8000/agent/learning-report
```

### 2. Performance Optimization

Get optimization suggestions:

```bash
# View opportunities
curl http://localhost:8000/agent/opportunities

# Get specific suggestions
curl http://localhost:8000/agent/suggestions
```

### 3. Self-Improvement (Advanced)

Enable full autonomous mode:

```bash
# Enable agent
curl -X POST http://localhost:8000/agent/enable \
  -d '{"password": "agent_password"}'

# Enable modifications
curl -X POST http://localhost:8000/agent/modifications/enable \
  -d '{"password": "mod_password"}'

# Start autonomous loop
curl -X POST "http://localhost:8000/agent/start-loop?interval_seconds=7200"
```

**Note**: This mode allows the agent to modify its own code. Use with extreme caution!

## ⚙️ Configuration

### Environment Variables

```bash
# Agent Control
AGENT_ENABLED=false  # Enable agent on startup
AGENT_MODIFICATIONS_ENABLED=false  # Enable modifications on startup
AGENT_MAX_MODIFICATIONS_PER_DAY=5  # Daily modification limit
AGENT_REQUIRE_APPROVAL=true  # Require human approval
AGENT_SANDBOX_MODE=true  # Run in sandbox mode
AGENT_GIT_INTEGRATION=true  # Commit changes to git

# Security
AGENT_ENABLE_PASSWORD=secure_password_here
MODIFICATIONS_ENABLE_PASSWORD=different_secure_password
KILL_SWITCH_PASSWORD=emergency_password
```

### Safety Limits

```python
# In code or via API
agent.safety.set_max_modifications_per_day(10)  # Increase limit
```

## 🔧 Troubleshooting

### Agent Won't Start

```bash
# Check safety status
curl http://localhost:8000/agent/safety/status

# Common issues:
# 1. Kill switch is active - check for AGENT_KILL_SWITCH file
# 2. Agent not enabled - call /agent/enable
# 3. Configuration error - check logs
```

### Modifications Blocked

```bash
# Check modification stats
curl http://localhost:8000/agent/status

# Possible reasons:
# - Daily limit reached (max_modifications_per_day)
# - Modifications disabled globally
# - Kill switch active
# - Approval required but not granted
```

### High Error Rate

```bash
# Check learning report
curl http://localhost:8000/agent/learning-report

# Agent will:
# - Slow down operations
# - Increase validation
# - Log safety incidents
# - May self-disable if critical
```

## 🚨 Emergency Procedures

### Immediate Stop

```bash
# Activate kill switch
curl -X POST "http://localhost:8000/agent/kill-switch/activate?reason=Emergency"

# Or create file manually
echo "EMERGENCY STOP" > AGENT_KILL_SWITCH
```

### Rollback Last Modification

```bash
# List recent modifications
curl http://localhost:8000/agent/memory/executions?limit=10

# Restore from backup
cp backups/main.py.backup_TIMESTAMP src/main.py

# Restart service
docker-compose restart
```

### Full Reset

```bash
# 1. Stop everything
docker-compose down

# 2. Remove agent database
rm logs/agent_memory.db

# 3. Remove proposals and backups
rm -rf proposals/ backups/

# 4. Remove kill switch if present
rm AGENT_KILL_SWITCH

# 5. Restart
docker-compose up -d
```

## 📚 Best Practices

### 1. Start Conservative

- Enable agent first (learning only)
- Run for days/weeks to build patterns
- Review learning reports regularly
- Only then consider enabling modifications

### 2. Use Sandbox Mode

- Keep `AGENT_SANDBOX_MODE=true` initially
- Review proposed modifications manually
- Test in staging environment first
- Gradually increase autonomy

### 3. Monitor Actively

- Check learning reports daily
- Review safety incidents
- Monitor success rates
- Watch for anomalies

### 4. Set Appropriate Limits

- Start with `max_modifications_per_day=1`
- Require approval for all changes
- Keep git integration enabled
- Maintain comprehensive backups

### 5. Have Rollback Plan

- Test backup restoration
- Keep multiple backup versions
- Document rollback procedures
- Maintain manual control access

## 🔬 Advanced Features

### Custom Pattern Learning

The agent automatically learns from:
- Successful operations
- Failed operations
- Performance characteristics
- Common workflows

### Code Quality Analysis

Automatic analysis includes:
- Syntax validation
- Docstring presence
- Error handling patterns
- Performance metrics

### Self-Optimization Triggers

The agent may propose modifications when:
- Success rate drops below threshold
- Performance degrades significantly
- Repeated failures occur
- Better patterns identified

## 📝 Logging

### Agent Logs

```bash
# Main agent log
tail -f logs/apex_orchestrator.log | grep agent

# Safety incidents
tail -f logs/safety_incidents.log

# Modification history (in database)
sqlite3 logs/agent_memory.db "SELECT * FROM modifications ORDER BY timestamp DESC LIMIT 10"
```

### Database Queries

```sql
-- View execution history
SELECT * FROM executions ORDER BY timestamp DESC LIMIT 20;

-- View learned patterns
SELECT * FROM patterns ORDER BY confidence_score DESC;

-- View code templates
SELECT name, description, use_count FROM code_templates;

-- View modifications
SELECT * FROM modifications WHERE applied = 1;
```

## 🎓 Learning More

- Review `src/agent/` source code for implementation details
- Check `logs/agent_memory.db` for stored knowledge
- Monitor `/agent/learning-report` endpoint for insights
- Read safety controller implementation for security model

## ⚖️ Ethical Considerations

This system can modify its own code. Consider:

1. **Responsibility**: Who is responsible for autonomous modifications?
2. **Transparency**: All actions are logged and auditable
3. **Control**: Human oversight remains paramount
4. **Safety**: Multiple layers of protection are in place
5. **Testing**: Extensive testing before any production use

---

**Remember**: The autonomous agent is a powerful tool. Use responsibly, start conservatively, and maintain human oversight.

For issues or questions, review the logs and safety status first, then consult the development team.

