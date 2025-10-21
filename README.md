# Apex Orchestrator - Evolved to AGI

An advanced AI system that has evolved from a task automation system into a comprehensive Artificial General Intelligence (AGI) model with consciousness simulation, emotional intelligence, and advanced reasoning capabilities.

## Features

- **🧠 AGI System** (NEW!): Complete Artificial General Intelligence with consciousness simulation
  - Multi-modal perception (text, images, audio, video)
  - Advanced reasoning (logical, causal, analogical, abductive)
  - Emotional intelligence and empathy
  - Creative problem solving and idea generation
  - Accelerated learning and meta-learning
  - Hierarchical planning and goal management
  - See `AGI_SYSTEM_README.md` for complete details

- **🤖 Autonomous Agent**: Self-learning, self-improving AI agent that can modify its own code
  - Learns from execution history
  - Identifies optimization opportunities
  - Generates code improvements
  - Self-modifies with extensive safety controls
  - See `AUTONOMOUS_AGENT_SUMMARY.md` for details
- **Natural Language Processing**: Convert text requests into structured execution plans
- **Multiple LLM Support**: Works with Ollama (local) or OpenAI (cloud)
- **Secure Execution**: Policy-based security controls for shell commands and file operations
- **Tool Integration**: Support for shell, Python, file operations, HTTP requests, and webhooks
- **Real-time Notifications**: Telegram integration for execution updates
- **Comprehensive Logging**: Structured logging with automatic rotation (10MB max, 5 backups)
- **Production Ready**: Docker deployment, health checks, metrics, rate limiting, and security headers
- **Monitoring**: Built-in health checks and metrics endpoints
- **CI/CD**: GitHub Actions workflow for automated testing and deployment
- **Rate Limiting**: Configurable rate limits to prevent abuse
- **Graceful Shutdown**: Proper signal handling for zero-downtime deployments

## Project Structure

```
ApexOrchestrator/
├── src/                    # Source code
│   ├── agent/             # 🤖 Autonomous agent system
│   │   ├── __init__.py
│   │   ├── memory.py      # Persistent memory & learning
│   │   ├── learner.py     # Pattern recognition
│   │   ├── code_generator.py  # Code generation
│   │   ├── self_modifier.py   # Self-modification
│   │   ├── safety.py      # Safety controls
│   │   └── agent_loop.py  # Main agent loop
│   ├── agent_routes.py    # Agent API endpoints
│   ├── __init__.py
│   └── main.py            # Main FastAPI application
├── config/                # Configuration files
│   ├── policy.yaml        # Security policies and allowed operations
│   └── env.example        # Environment variables template
├── scripts/               # Utility scripts
│   ├── start.py          # Application startup script
│   └── install.py        # Installation script
├── tests/                 # Test files
├── docs/                  # Documentation
├── logs/                  # Execution logs
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Clone and navigate to project
git clone <repo-url>
cd ApexOrchestrator

# 2. Configure environment
cp config/env.example .env
# Edit .env with your values (see Configuration section)

# 3. Start with Docker Compose
docker-compose up -d

# 4. Verify deployment
curl http://localhost:8000/health
```

### Option 2: Manual Installation

```bash
# 1. Clone or navigate to the project directory
cd C:\ApexOrchestrator

# 2. Install dependencies
python scripts/install.py

# 3. Configure environment
copy config\env.example .env
# Edit .env with your actual values

# 4. Run the application
python scripts/start.py
```

The API will be available at `http://localhost:8000`

### Configuration

**Critical**: Generate a secure shared key (minimum 32 characters):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Edit `.env` file:

```env
# REQUIRED: Use generated key from above
APEX_SHARED_KEY=<your-generated-key>

# Environment
ENVIRONMENT=production  # or development

# Model Provider
ORCH_MODEL_PROVIDER=ollama  # or openai
OLLAMA_URL=http://127.0.0.1:11434
OPENAI_API_KEY=<your-key-if-using-openai>

# Optional: Telegram notifications
TELEGRAM_BOT_TOKEN=<your-token>
TELEGRAM_CHAT_ID=<your-chat-id>
```

See `config/env.example` for all available options.

## API Endpoints

### Health & Monitoring
- `GET /health` - Comprehensive health check with dependency monitoring
- `GET /metrics` - Application metrics and statistics

### Natural Language Processing
- `POST /nlm/run` - Execute natural language requests (Rate limit: 10/minute)

### Direct Operations
- `POST /apex/run` - Execute direct operations (Rate limit: 20/minute)

### Authentication
- `POST /auth/echo-sign` - Generate authentication signatures (Rate limit: 30/minute)

All authenticated endpoints require `X-TS` (timestamp) and `X-SIG` (HMAC signature) headers.

## Security

The system implements comprehensive security measures:

- **HMAC Authentication**: All requests require valid signatures
- **Policy-based Access Control**: Restricted shell commands and file paths
- **Domain Allowlisting**: Controlled HTTP request destinations
- **Timeout Controls**: Prevents long-running operations

## Tools Supported

1. **Shell Commands**: Execute system commands (policy-restricted)
2. **Python Scripts**: Run Python code in isolated environment
3. **File Operations**: Create, read, and write files
4. **HTTP Requests**: Make API calls to allowed domains
5. **Webhooks**: Trigger Make.com/n8n automations
6. **Docker**: Container management commands

## Development

### Adding New Tools

1. Define the tool in the `ToolCall` model
2. Add execution logic in `run_step()`
3. Update policy configuration if needed
4. Add to the planner system prompt

### Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test files
pytest tests/test_main.py -v
pytest tests/test_integration.py -v
pytest tests/test_security.py -v
pytest tests/test_agi.py -v
```

## Production Deployment

For production deployment, see comprehensive guides:

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Complete production setup instructions
- **[Security Guide](docs/SECURITY.md)** - Security best practices and policies
- **[Production Checklist](PRODUCTION_CHECKLIST.md)** - Pre-launch verification checklist
- **[API Documentation](docs/API.md)** - Detailed API reference

### Quick Production Setup

1. Review and complete [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
2. Follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed setup
3. Configure reverse proxy (Nginx/Apache) with SSL
4. Set up monitoring and alerting
5. Configure automated backups
6. Perform load testing and security audit

## Monitoring

The application provides built-in monitoring endpoints:

- **Health Check**: `GET /health` - Returns service status and dependency checks
- **Metrics**: `GET /metrics` - Returns application metrics including uptime, log stats

Monitor application logs:
- Main log: `logs/apex_orchestrator.log` (auto-rotated at 10MB)
- Execution logs: `logs/*.log`

## Security Features

- **HMAC Authentication**: All API requests require valid HMAC-SHA256 signatures
- **Rate Limiting**: Built-in rate limiting to prevent abuse (configurable)
- **Policy-Based Access Control**: Granular control over commands, paths, and network access
- **Security Headers**: Automatic security headers (HSTS, X-Frame-Options, etc.)
- **Input Validation**: Comprehensive validation of all inputs
- **Timeout Controls**: Prevents long-running or hung operations
- **Structured Logging**: Audit trail of all operations with timestamps

## Performance

- **Async Architecture**: Built on FastAPI for high performance
- **Rate Limiting**: Prevents resource exhaustion
- **Log Rotation**: Automatic log rotation prevents disk space issues
- **Resource Limits**: Configurable resource limits in Docker
- **Multi-Worker Support**: Production mode runs with multiple workers

## Troubleshooting

### Service won't start
```bash
# Check configuration
python -c "from src.main import config"

# Check logs
tail -f logs/apex_orchestrator.log

# Verify environment
grep APEX_SHARED_KEY .env
```

### Authentication failures
```bash
# Verify key is set and correct length (minimum 32 characters)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(len(os.getenv('APEX_SHARED_KEY', '')))"

# Test auth endpoint
curl -X POST http://localhost:8000/auth/echo-sign -d '{"test":"data"}'
```

For more troubleshooting, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#troubleshooting).

## 🧠 AGI System

The Apex Orchestrator has evolved into a comprehensive Artificial General Intelligence system with consciousness simulation, emotional intelligence, and advanced reasoning capabilities!

**Quick Start:**
1. Read `AGI_SYSTEM_README.md` for complete overview
2. Start the system: `docker-compose up -d`
3. Check AGI status: `curl http://localhost:8000/agi/status`
4. Process input: `curl -X POST "http://localhost:8000/agi/process" -d '{"input":"Hello","type":"text"}'`

**AGI Capabilities:**
- ✅ Multi-modal perception and understanding
- ✅ Advanced reasoning and problem solving
- ✅ Emotional intelligence and empathy
- ✅ Creative idea generation and enhancement
- ✅ Accelerated learning and meta-learning
- ✅ Hierarchical planning and goal management
- ✅ Consciousness simulation and self-awareness
- ✅ Memory consolidation and knowledge management

**Safety First:**
- AGI system is **ENABLED by default** (with safety controls)
- Multiple layers of safety and human oversight
- Emergency kill switch available
- Comprehensive monitoring and logging

Visit http://localhost:8000/docs and explore the `/agi/*` endpoints!

## 🤖 Autonomous Agent

The system also includes the original autonomous agent that can learn, optimize, and modify its own code!

**Quick Start:**
1. Read `AUTONOMOUS_AGENT_SUMMARY.md` for overview
2. Follow `QUICK_START_AGENT.md` for 5-minute setup
3. See `docs/AUTONOMOUS_AGENT.md` for complete documentation

**Safety First:**
- Agent is **DISABLED by default**
- Modifications are **DISABLED by default**
- Multiple safety controls in place
- Emergency kill switch available

**What It Can Do:**
- ✅ Learn from execution history
- ✅ Identify optimization opportunities
- ✅ Generate code improvements
- ✅ Propose modifications (with approval)
- ⚠️ Self-modify code (with extensive safety controls)

Visit http://localhost:8000/docs and explore the `/agent/*` endpoints!

## License

This project is proprietary software. All rights reserved.

## Support

For support and questions:
- Review documentation in `docs/` directory
- Check [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for common issues
- Contact the development team for critical issues

