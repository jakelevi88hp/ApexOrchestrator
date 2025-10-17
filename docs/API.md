# Apex Orchestrator API Documentation

## Authentication

All API endpoints (except `/health` and `/auth/echo-sign`) require HMAC authentication using the `APEX_SHARED_KEY`.

### Headers Required
- `X-TS`: Unix timestamp
- `X-SIG`: HMAC-SHA256 signature

### Signature Generation
```python
import hmac
import hashlib
import time

def generate_signature(body: bytes, timestamp: str, shared_key: str) -> str:
    message = timestamp.encode() + b"." + body
    return hmac.new(shared_key.encode(), message, hashlib.sha256).hexdigest()
```

## Endpoints

### GET /health
Check service health status.

**Response:**
```json
{
  "ok": true,
  "service": "Apex Orchestrator"
}
```

### POST /nlm/run
Execute natural language requests using AI planning.

**Headers:**
- `X-TS`: Unix timestamp
- `X-SIG`: HMAC signature

**Request Body:**
```json
{
  "text": "Create a Python script that calculates fibonacci numbers",
  "meta": {
    "user": "example_user",
    "priority": "normal"
  }
}
```

**Response:**
```json
{
  "ok": true,
  "run_id": "nl_1234567890",
  "plan": {
    "intent": "Create fibonacci calculator script",
    "steps": [
      {
        "tool": "file_write",
        "args": {
          "path": "fibonacci.py",
          "content": "def fibonacci(n): ..."
        },
        "description": "Create fibonacci calculation script"
      }
    ]
  },
  "results": [
    {
      "path": "C:\\ApexWork\\fibonacci.py",
      "bytes": 150
    }
  ]
}
```

### POST /apex/run
Execute direct operations without AI planning.

**Headers:**
- `X-TS`: Unix timestamp
- `X-SIG`: HMAC signature

**Request Body:**
```json
{
  "op": "file_write",
  "params": {
    "path": "test.txt",
    "content": "Hello World"
  },
  "meta": {
    "user": "example_user"
  }
}
```

**Response:**
```json
{
  "ok": true,
  "run_id": "op_1234567890",
  "result": {
    "path": "C:\\ApexWork\\test.txt",
    "bytes": 11
  }
}
```

### POST /auth/echo-sign
Generate authentication signature for testing.

**Request Body:**
```json
{
  "test": "data"
}
```

**Response:**
```json
{
  "ts": "1234567890",
  "sig": "generated_signature_here"
}
```

## Supported Operations

### file_write
Create or update files.

**Parameters:**
- `path`: Relative path from WORK_DIR
- `content`: File content
- `overwrite`: Boolean (default: true)

### python
Execute Python code.

**Parameters:**
- `code`: Python code to execute

### shell
Execute shell commands.

**Parameters:**
- `cmd`: Command to execute
- `cwd`: Working directory (optional)

### http_request
Make HTTP requests.

**Parameters:**
- `method`: HTTP method (GET, POST, etc.)
- `url`: Target URL
- `headers`: Request headers (optional)
- `body`: Request body (optional)

### make_hook
Trigger webhook automations.

**Parameters:**
- `payload`: Data to send to webhook

## Error Responses

All errors return HTTP status codes with JSON responses:

```json
{
  "detail": "Error message description"
}
```

Common error codes:
- `401`: Authentication failed
- `403`: Operation not allowed by policy
- `409`: File already exists (when overwrite=false)
- `412`: Required configuration missing
- `500`: Internal server error

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing based on your use case.

## Logging

All operations are logged to the `logs/` directory with detailed execution information including timestamps, parameters, and results.

