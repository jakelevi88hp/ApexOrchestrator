import os, time, hmac, hashlib, json, subprocess, shlex, re, pathlib, asyncio, logging, sys, signal
from typing import List, Dict, Any, Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Request, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx, yaml

load_dotenv()

# --- Rate Limiter Configuration ---
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

# --- Logging Configuration ---
def setup_logging():
    """Configure structured logging with rotation"""
    log_dir = pathlib.Path(os.getenv("LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Main application log
    log_file = log_dir / "apex_orchestrator.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation (10MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return logging.getLogger("apex_orchestrator")

logger = setup_logging()

# Import agent routes (after logger is set up)
try:
    from agent_routes import router as agent_router
    AGENT_AVAILABLE = True
    logger.info("Agent module loaded successfully")
except ImportError as e:
    AGENT_AVAILABLE = False
    logger.warning(f"Agent module not available: {e}")

# Import AGI system (after logger is set up)
try:
    from agi.core import AGICore
    AGI_AVAILABLE = True
    logger.info("AGI system loaded successfully")
except ImportError as e:
    AGI_AVAILABLE = False
    logger.warning(f"AGI system not available: {e}")

APP = FastAPI(
    title="Apex Orchestrator", 
    version="1.0.0",
    description="AI-powered task automation system with secure execution",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files for Admin UI
static_path = pathlib.Path(__file__).parent.parent / "static"
if static_path.exists():
    APP.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"Static files mounted from {static_path}")

# Add rate limiter to app
APP.state.limiter = limiter
APP.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Global Error Handlers ---
@APP.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "ok": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )

@APP.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    # Don't log auth errors at error level (too noisy)
    if exc.status_code in [401, 403]:
        logger.warning(f"Auth error: {exc.detail}")
    else:
        logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": exc.detail
        }
    )

@APP.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "error": "Internal server error"
        }
    )

# --- Middleware Configuration ---
# CORS Configuration (restrictive by default)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
if ALLOWED_ORIGINS and ALLOWED_ORIGINS[0]:
    APP.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {ALLOWED_ORIGINS}")

# Trusted host middleware (if configured)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
if ALLOWED_HOSTS and ALLOWED_HOSTS[0]:
    APP.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
    logger.info(f"Trusted hosts: {ALLOWED_HOSTS}")

# Security headers middleware
@APP.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Relaxed CSP for API docs endpoints, strict for everything else
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        # Allow Swagger UI and ReDoc to load properly
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data: cdn.jsdelivr.net"
    else:
        # Strict CSP for all other endpoints
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response

# Request logging middleware
@APP.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Generate request ID
    request_id = f"{int(time.time()*1000)}-{id(request)}"
    
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f"[{request_id}] Status: {response.status_code} Duration: {duration:.3f}s")
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[{request_id}] Error after {duration:.3f}s: {e}")
        raise

# --- Configuration Management ---
class Config:
    """Application configuration with validation"""
    def __init__(self):
        # Authentication
        self.SHARED_KEY = os.getenv("APEX_SHARED_KEY", "")
        
        # Model Configuration
        self.MODEL_PROVIDER = os.getenv("ORCH_MODEL_PROVIDER", "ollama").lower()
        self.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
        self.OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Integration Configuration
        self.MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL", "")
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
        
        # Directory Configuration
        self.LOG_DIR = pathlib.Path(os.getenv("LOG_DIR", "logs"))
        self.WORK_DIR = pathlib.Path(os.getenv("WORK_DIR", "C:\\ApexWork"))
        
        # Environment
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # Policy
        policy_path = pathlib.Path(__file__).parent.parent / "config" / "policy.yaml"
        with open(policy_path, "r", encoding="utf-8") as f:
            self.POLICY = yaml.safe_load(f)
        
        # Validate and create directories
        self._validate_and_setup()
    
    def _validate_and_setup(self):
        """Validate configuration and setup required resources"""
        errors = []
        
        # Critical configuration checks
        if not self.SHARED_KEY:
            errors.append("APEX_SHARED_KEY is required")
        elif len(self.SHARED_KEY) < 32:
            errors.append("APEX_SHARED_KEY must be at least 32 characters")
        
        if self.MODEL_PROVIDER not in ["ollama", "openai"]:
            errors.append(f"Invalid ORCH_MODEL_PROVIDER: {self.MODEL_PROVIDER}")
        
        if self.MODEL_PROVIDER == "openai" and not self.OPENAI_KEY:
            errors.append("OPENAI_API_KEY is required when using OpenAI provider")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        # Create directories
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.WORK_DIR.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Environment: {self.ENVIRONMENT}")
        logger.info(f"Model Provider: {self.MODEL_PROVIDER}")
        logger.info(f"Work Directory: {self.WORK_DIR}")

# Initialize configuration
try:
    config = Config()
    SHARED_KEY = config.SHARED_KEY
    MODEL_PROVIDER = config.MODEL_PROVIDER
    OLLAMA_URL = config.OLLAMA_URL
    OPENAI_KEY = config.OPENAI_KEY
    OPENAI_MODEL = config.OPENAI_MODEL
    MAKE_WEBHOOK_URL = config.MAKE_WEBHOOK_URL
    TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID = config.TELEGRAM_CHAT_ID
    LOG_DIR = config.LOG_DIR
    WORK_DIR = config.WORK_DIR
    POLICY = config.POLICY
except Exception as e:
    logger.critical(f"Failed to load configuration: {e}")
    sys.exit(1)

# Initialize AGI system
agi_core = None
if AGI_AVAILABLE:
    try:
        agi_core = AGICore()
        logger.info("AGI core system initialized")
    except Exception as e:
        logger.error(f"Failed to initialize AGI core: {e}")
        agi_core = None
        AGI_AVAILABLE = False

# --- Startup/Shutdown Events ---
@APP.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    global AGI_AVAILABLE
    logger.info("=" * 50)
    logger.info("Apex Orchestrator Starting")
    logger.info("=" * 50)
    logger.info(f"Version: {APP.version}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    
    # Include agent routes if available
    if AGENT_AVAILABLE:
        try:
            APP.include_router(agent_router)
            logger.info("🤖 Autonomous Agent routes registered")
            logger.info("Agent endpoints: /agent/*")
        except Exception as e:
            logger.error(f"Failed to register agent routes: {e}")
    else:
        logger.warning("Autonomous Agent not available")
    
    # Initialize AGI system if available
    if AGI_AVAILABLE and agi_core:
        try:
            await agi_core.initialize()
            logger.info("🧠 AGI system initialized and ready")
        except Exception as e:
            logger.error(f"Failed to initialize AGI system: {e}")
            AGI_AVAILABLE = False
    else:
        logger.warning("AGI system not available")
    
    # Notify startup
    await notify("🚀 Apex Orchestrator started")

@APP.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Apex Orchestrator shutting down...")
    
    # Stop agent if running
    if AGENT_AVAILABLE:
        try:
            from agent.agent_loop import get_agent
            agent = get_agent()
            if agent.running:
                agent.stop()
                logger.info("Autonomous agent stopped")
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
    
    # Shutdown AGI system if running
    if AGI_AVAILABLE and agi_core:
        try:
            await agi_core.shutdown()
            logger.info("AGI system shutdown complete")
        except Exception as e:
            logger.error(f"Error shutting down AGI system: {e}")
    
    await notify("🛑 Apex Orchestrator stopped")

# --- Models with Validation ---
class ToolCall(BaseModel):
    tool: str = Field(..., description="Tool name to execute")
    args: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    description: str = Field(default="", description="Step description")
    
    @validator('tool')
    def validate_tool(cls, v):
        allowed_tools = ["shell", "python", "file_write", "http_request", "docker", "make_hook"]
        if v not in allowed_tools:
            raise ValueError(f"Tool must be one of: {', '.join(allowed_tools)}")
        return v

class Plan(BaseModel):
    intent: str = Field(..., min_length=1, max_length=500, description="Plan intent")
    steps: List[ToolCall] = Field(..., min_items=1, max_items=50, description="Execution steps")

class NLRunRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Natural language request")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DirectOp(BaseModel):
    op: str = Field(..., description="Operation to execute")
    params: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('op')
    def validate_op(cls, v):
        allowed_ops = ["file_write", "shell", "python", "make_hook"]
        if v not in allowed_ops:
            raise ValueError(f"Operation must be one of: {', '.join(allowed_ops)}")
        return v

# --- Utils ---
def sign(body: bytes, ts: str) -> str:
    return hmac.new(SHARED_KEY.encode(), ts.encode() + b"." + body, hashlib.sha256).hexdigest()

def verify(x_sig: Optional[str], x_ts: Optional[str], body: bytes):
    if not SHARED_KEY:
        raise HTTPException(500, "Server misconfigured")
    if not x_sig or not x_ts:
        raise HTTPException(401, "Missing auth headers")
    try:
        t = int(x_ts)
    except:
        raise HTTPException(401, "Bad timestamp")
    if abs(int(time.time()) - t) > 300:
        raise HTTPException(401, "Stale timestamp")
    if not hmac.compare_digest(sign(body, x_ts), x_sig):
        raise HTTPException(401, "Bad signature")

async def notify(msg: str):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                await c.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
        except Exception:
            pass

def _policy_path_ok(path: str) -> bool:
    p = pathlib.Path(path).resolve()
    for allowed in POLICY.get("paths_allow", []):
        if str(p).lower().startswith(allowed.lower()):
            return True
    return False

def _policy_shell_ok(cmd: str) -> bool:
    allowed_prefixes = POLICY.get("shell_allow", [])
    c = cmd.strip().lower()
    return any(c.startswith(prefix.strip().lower()) for prefix in allowed_prefixes)

def _safe_join(base: pathlib.Path, rel: str) -> pathlib.Path:
    target = (base / rel).resolve()
    if not _policy_path_ok(str(target)):
        raise HTTPException(403, f"Path not allowed by policy: {target}")
    return target

# --- Executors with Enhanced Error Handling ---
def run_shell(cmd: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Execute shell command with policy enforcement"""
    logger.info(f"Executing shell command: {cmd[:100]}...")
    
    if not _policy_shell_ok(cmd):
        logger.warning(f"Shell command blocked by policy: {cmd}")
        raise HTTPException(403, f"Shell command not allowed by policy")
    
    timeout = POLICY.get("timeouts", {}).get("shell_seconds", 120)
    
    try:
        proc = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd, 
            timeout=timeout
        )
        
        result = {
            "returncode": proc.returncode, 
            "stdout": proc.stdout[:10000],  # Limit output size
            "stderr": proc.stderr[:10000]
        }
        
        if proc.returncode != 0:
            logger.warning(f"Shell command failed with code {proc.returncode}")
        else:
            logger.info("Shell command completed successfully")
        
        return result
        
    except subprocess.TimeoutExpired:
        logger.error(f"Shell command timed out after {timeout}s")
        raise HTTPException(408, f"Command timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Shell command error: {e}")
        raise HTTPException(500, f"Shell execution error: {str(e)}")

def run_python(code: str) -> Dict[str, Any]:
    """Execute Python code in isolated file"""
    logger.info(f"Executing Python code ({len(code)} bytes)")
    
    timeout = POLICY.get("timeouts", {}).get("python_seconds", 120)
    pyfile = None
    
    try:
        # Write to temp file in WORK_DIR
        pyfile = _safe_join(WORK_DIR, f"tmp_{int(time.time())}_{os.getpid()}.py")
        pyfile.write_text(code, encoding="utf-8")
        
        proc = subprocess.run(
            f'python "{pyfile}"', 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout, 
            cwd=str(WORK_DIR)
        )
        
        result = {
            "returncode": proc.returncode, 
            "stdout": proc.stdout[:10000],
            "stderr": proc.stderr[:10000], 
            "file": str(pyfile)
        }
        
        if proc.returncode != 0:
            logger.warning(f"Python execution failed with code {proc.returncode}")
        else:
            logger.info("Python execution completed successfully")
        
        return result
        
    except subprocess.TimeoutExpired:
        logger.error(f"Python execution timed out after {timeout}s")
        raise HTTPException(408, f"Python execution timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Python execution error: {e}")
        raise HTTPException(500, f"Python execution error: {str(e)}")

def file_write(rel_path: str, content: str, overwrite: bool=True) -> Dict[str, Any]:
    """Write file with path validation"""
    logger.info(f"Writing file: {rel_path} ({len(content)} bytes)")
    
    try:
        target = _safe_join(WORK_DIR, rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        
        if target.exists() and not overwrite:
            logger.warning(f"File exists and overwrite=False: {target}")
            raise HTTPException(409, f"File exists: {rel_path}")
        
        target.write_text(content, encoding="utf-8")
        logger.info(f"File written successfully: {target}")
        
        return {"path": str(target), "bytes": len(content)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File write error: {e}")
        raise HTTPException(500, f"File write error: {str(e)}")

async def http_request(method: str, url: str, headers: Dict[str, str]=None, body: Any=None) -> Dict[str, Any]:
    """Execute HTTP request with domain allowlist"""
    logger.info(f"HTTP request: {method} {url}")
    
    # Domain allowlist check
    ok_domains = set(POLICY.get("network", {}).get("http_allow_domains", []))
    domain = re.sub(r"^https?://", "", url).split("/")[0].lower()
    
    if ok_domains and domain not in ok_domains:
        logger.warning(f"HTTP request blocked - domain not allowed: {domain}")
        raise HTTPException(403, f"Domain not allowed")
    
    timeout = POLICY.get("timeouts", {}).get("http_seconds", 30)
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as c:
            r = await c.request(
                method.upper(), 
                url, 
                headers=headers or {}, 
                json=body if isinstance(body, (dict, list)) else None, 
                data=None if isinstance(body, (dict, list)) else body
            )
            
            result = {
                "status": r.status_code, 
                "headers": dict(r.headers), 
                "text": r.text[:20000]
            }
            
            logger.info(f"HTTP request completed: {r.status_code}")
            return result
            
    except httpx.TimeoutException:
        logger.error(f"HTTP request timed out after {timeout}s")
        raise HTTPException(408, f"HTTP request timed out")
    except Exception as e:
        logger.error(f"HTTP request error: {e}")
        raise HTTPException(500, f"HTTP request error: {str(e)}")

async def make_hook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger Make.com webhook"""
    logger.info("Triggering Make webhook")
    
    if not MAKE_WEBHOOK_URL:
        logger.error("MAKE_WEBHOOK_URL not configured")
        raise HTTPException(412, "MAKE_WEBHOOK_URL not set")
    
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(MAKE_WEBHOOK_URL, json=payload)
            
            result = {"status": r.status_code, "text": r.text[:20000]}
            logger.info(f"Make webhook completed: {r.status_code}")
            
            return result
            
    except httpx.TimeoutException:
        logger.error("Make webhook timed out")
        raise HTTPException(408, "Webhook request timed out")
    except Exception as e:
        logger.error(f"Make webhook error: {e}")
        raise HTTPException(500, f"Webhook error: {str(e)}")

# --- Planner (LLM) ---
PLANNER_SYS = """You are the Apex Planner. Convert a user's natural-language request into a minimal JSON plan.
Use only these tools: "shell", "python", "file_write", "http_request", "make_hook", "docker".
- "shell": for PowerShell/cmd commands (only safe, high-level devops/automation commands).
- "python": for quick scripts (write files, transform data, etc.).
- "file_write": create/update files under WORK_DIR.
- "http_request": call approved APIs.
- "make_hook": trigger cloud automations in Make/n8n with structured payloads.
- "docker": run docker or docker compose commands.

Return JSON: {"intent": "...", "steps": [{"tool":"...", "args":{...}, "description":"..."}]}
Keep steps few and reliable. Write files before running them. Use C:\\ApexWork as workspace paths.
"""

async def plan_with_ollama(prompt: str) -> Plan:
    payload = {
        "model": "llama3.1",
        "messages": [{"role":"system","content":PLANNER_SYS},{"role":"user","content":prompt}],
        "format": "json",  # Ollama expects simple "json" format
        "stream": False,
        "options":{"temperature":0.2}
    }
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{OLLAMA_URL}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
    try:
        content = data["message"]["content"]
        if isinstance(content, str):
            plan_data = json.loads(content)
        else:
            plan_data = content
        return Plan(**plan_data)
    except Exception as e:
        raise HTTPException(500, f"Ollama plan parse error: {e}")

async def plan_with_openai(prompt: str) -> Plan:
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    body = {
      "model": OPENAI_MODEL,
      "messages": [{"role":"system","content":PLANNER_SYS},{"role":"user","content":prompt}],
      "response_format": {"type": "json_object"},
      "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
        r.raise_for_status()
        j = r.json()
        content = j["choices"][0]["message"]["content"]
        return Plan(**json.loads(content))

async def make_plan(text: str) -> Plan:
    if MODEL_PROVIDER == "ollama":
        return await plan_with_ollama(text)
    elif MODEL_PROVIDER == "openai":
        if not OPENAI_KEY:
            raise HTTPException(412, "OPENAI_API_KEY not set")
        return await plan_with_openai(text)
    else:
        raise HTTPException(500, "Unknown ORCH_MODEL_PROVIDER")

# --- Runner ---
async def run_step(step: ToolCall, run_id: str) -> Dict[str, Any]:
    out = {"tool": step.tool, "description": step.description, "args": step.args}
    if step.tool == "file_write":
        res = file_write(step.args.get("path","artifact.txt"), step.args.get("content",""), bool(step.args.get("overwrite", True)))
    elif step.tool == "python":
        res = run_python(step.args.get("code",""))
    elif step.tool == "shell" or step.tool == "docker":
        res = run_shell(step.args.get("cmd",""), cwd=step.args.get("cwd"))
    elif step.tool == "http_request":
        res = await http_request(step.args.get("method","GET"), step.args.get("url",""), step.args.get("headers") or {}, step.args.get("body"))
    elif step.tool == "make_hook":
        res = await make_hook(step.args.get("payload", {}))
    else:
        raise HTTPException(400, f"Unknown tool: {step.tool}")
    # log
    logf = LOG_DIR / f"{run_id}.log"
    with open(logf, "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": int(time.time()), "step": out, "result": res}, ensure_ascii=False) + "\n")
    return res

# --- API Endpoints ---
@APP.get("/")
async def root():
    """Serve the Admin UI dashboard"""
    static_path = pathlib.Path(__file__).parent.parent / "static" / "index.html"
    if static_path.exists():
        return FileResponse(static_path)
    return {"message": "Apex Orchestrator API", "docs": "/docs"}

@APP.get("/health")
@limiter.limit("30/minute")
async def health(request: Request):
    """Comprehensive health check endpoint"""
    health_status = {
        "ok": True,
        "service": "Apex Orchestrator",
        "version": APP.version,
        "environment": config.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {}
    }
    
    # Check work directory
    try:
        health_status["checks"]["work_dir"] = {
            "status": "healthy",
            "path": str(WORK_DIR),
            "writable": os.access(WORK_DIR, os.W_OK)
        }
    except Exception as e:
        health_status["checks"]["work_dir"] = {"status": "unhealthy", "error": str(e)}
        health_status["ok"] = False
    
    # Check log directory
    try:
        health_status["checks"]["log_dir"] = {
            "status": "healthy",
            "path": str(LOG_DIR),
            "writable": os.access(LOG_DIR, os.W_OK)
        }
    except Exception as e:
        health_status["checks"]["log_dir"] = {"status": "unhealthy", "error": str(e)}
        health_status["ok"] = False
    
    # Check model provider
    if MODEL_PROVIDER == "ollama":
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                r = await c.get(f"{OLLAMA_URL}/api/tags")
                health_status["checks"]["ollama"] = {
                    "status": "healthy" if r.status_code == 200 else "degraded",
                    "url": OLLAMA_URL
                }
        except Exception as e:
            health_status["checks"]["ollama"] = {"status": "unhealthy", "error": str(e)}
            logger.warning(f"Ollama health check failed: {e}")
    elif MODEL_PROVIDER == "openai":
        health_status["checks"]["openai"] = {
            "status": "configured" if OPENAI_KEY else "missing_key",
            "model": OPENAI_MODEL
        }
    
    return health_status

@APP.get("/metrics")
@limiter.limit("10/minute")
async def metrics(request: Request):
    """Basic metrics endpoint for monitoring"""
    log_files = list(LOG_DIR.glob("*.log"))
    
    return {
        "service": "Apex Orchestrator",
        "version": APP.version,
        "uptime_seconds": int(time.time() - startup_time),
        "logs": {
            "count": len(log_files),
            "total_size_mb": sum(f.stat().st_size for f in log_files) / (1024 * 1024)
        },
        "work_dir": {
            "path": str(WORK_DIR),
            "exists": WORK_DIR.exists()
        }
    }

# Track startup time for uptime metric
startup_time = time.time()

@APP.post("/nlm/run")
@limiter.limit("10/minute")
async def nlm_run(request: Request, x_ts: Optional[str]=Header(None), x_sig: Optional[str]=Header(None)):
    body = await request.body()
    verify(x_sig, x_ts, body)
    payload = NLRunRequest(**json.loads(body))
    run_id = f"nl_{int(time.time())}"
    await notify(f"🧠 Planning: {payload.text[:80]}…")
    plan = await make_plan(payload.text)
    await notify(f"🛠️ Executing plan '{plan.intent}' ({len(plan.steps)} steps)")
    results = []
    for step in plan.steps:
        results.append(await run_step(step, run_id))
    await notify(f"✅ Done: {plan.intent}")
    return {"ok": True, "run_id": run_id, "plan": plan.model_dump(), "results": results}

@APP.post("/apex/run")
@limiter.limit("20/minute")
async def apex_run(request: Request, x_ts: Optional[str]=Header(None), x_sig: Optional[str]=Header(None)):
    body = await request.body()
    verify(x_sig, x_ts, body)
    d = DirectOp(**json.loads(body))
    run_id = f"op_{int(time.time())}"
    # simple router: map op to a toolcall
    table = {
      "file_write": lambda p: ToolCall(tool="file_write", args=p),
      "shell": lambda p: ToolCall(tool="shell", args=p),
      "python": lambda p: ToolCall(tool="python", args=p),
      "make_hook": lambda p: ToolCall(tool="make_hook", args=p),
    }
    if d.op not in table:
        raise HTTPException(400, f"Unknown op: {d.op}")
    step = table[d.op](d.params)
    res = await run_step(step, run_id)
    return {"ok": True, "run_id": run_id, "result": res}

@APP.post("/auth/echo-sign")
@limiter.limit("30/minute")
async def echo_sign(request: Request):
    body = await request.body()
    ts = str(int(time.time()))
    return {"ts": ts, "sig": sign(body, ts)}

# --- AGI Endpoints ---
@APP.post("/agi/process")
@limiter.limit("5/minute")
async def agi_process(request: Request, x_ts: Optional[str]=Header(None), x_sig: Optional[str]=Header(None)):
    """Process input through AGI system"""
    if not AGI_AVAILABLE or not agi_core:
        raise HTTPException(503, "AGI system not available")
    
    body = await request.body()
    verify(x_sig, x_ts, body)
    
    try:
        payload = json.loads(body)
        input_data = payload.get("input", "")
        input_type = payload.get("type", "text")
        
        # Process through AGI
        result = await agi_core.process_input(input_data, input_type)
        
        return {"ok": True, "result": result}
    except Exception as e:
        logger.error(f"AGI processing error: {e}")
        raise HTTPException(500, f"AGI processing failed: {str(e)}")

@APP.get("/agi/status")
@limiter.limit("10/minute")
async def agi_status(request: Request):
    """Get AGI system status"""
    if not AGI_AVAILABLE or not agi_core:
        raise HTTPException(503, "AGI system not available")
    
    try:
        status = await agi_core.get_status()
        return {"ok": True, "status": status}
    except Exception as e:
        logger.error(f"AGI status error: {e}")
        raise HTTPException(500, f"AGI status failed: {str(e)}")

@APP.post("/agi/goal")
@limiter.limit("10/minute")
async def agi_set_goal(request: Request, x_ts: Optional[str]=Header(None), x_sig: Optional[str]=Header(None)):
    """Set a new goal for AGI system"""
    if not AGI_AVAILABLE or not agi_core:
        raise HTTPException(503, "AGI system not available")
    
    body = await request.body()
    verify(x_sig, x_ts, body)
    
    try:
        payload = json.loads(body)
        goal = payload.get("goal", "")
        priority = payload.get("priority", 5)
        deadline = payload.get("deadline")
        
        if deadline:
            deadline = datetime.fromisoformat(deadline)
        
        await agi_core.set_goal(goal, priority, deadline)
        
        return {"ok": True, "message": f"Goal set: {goal}"}
    except Exception as e:
        logger.error(f"AGI goal setting error: {e}")
        raise HTTPException(500, f"AGI goal setting failed: {str(e)}")
