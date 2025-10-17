"""
title: Apex Orchestrator
author: open-webui
version: 1.0.0
"""

import requests
import hmac
import hashlib
import time
import json


class Tools:
    def __init__(self):
        self.citation = True
        # CONFIGURE THESE VALUES:
        self.APEX_BASE_URL = "http://host.docker.internal:8000"
        self.APEX_SHARED_KEY = "XGR8IDzftIqPBLL5t62CU1OUYXfi-fbAnS7BNqa-AyA" 

    def execute_task(
        self,
        task_description: str,
        __event_emitter__=None,
        __user__=None
    ) -> str:
        """
        Execute a task using Apex Orchestrator
        :param task_description: What you want to do
        """
        
        if not self.APEX_SHARED_KEY:
            return "❌ ERROR: APEX_SHARED_KEY not set! Edit the function and add your key on line 18."
        
        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "🚀 Executing...", "done": False},
                }
            )
        
        try:
            # Create signature
            body = json.dumps({"text": task_description})
            timestamp = str(int(time.time()))
            message = body + timestamp
            signature = hmac.new(
                self.APEX_SHARED_KEY.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Call API
            response = requests.post(
                f"{self.APEX_BASE_URL}/nlm/run",
                headers={
                    "Content-Type": "application/json",
                    "X-TS": timestamp,
                    "X-SIG": signature
                },
                data=body,
                timeout=60
            )
            
            data = response.json()
            
            if data.get("ok"):
                result = f"### ✅ Success\n\n**Intent:** {data['plan']['intent']}\n\n"
                
                if data.get('results'):
                    result += f"**Results:**\n\n"
                    for i, r in enumerate(data['results'], 1):
                        result += f"**Step {i}:**\n"
                        if r.get('stdout'):
                            result += f"```\n{r['stdout']}\n```\n"
                        if r.get('path'):
                            result += f"File: `{r['path']}`\n"
                        if r.get('body'):
                            result += f"```json\n{json.dumps(r['body'], indent=2)}\n```\n"
                        result += "\n"
                
                if __event_emitter__:
                    __event_emitter__(
                        {"type": "status", "data": {"description": "✅ Done", "done": True}}
                    )
                
                return result
            else:
                return f"### ❌ Error\n\n{data.get('error', 'Unknown error')}"
                
        except Exception as e:
            if __event_emitter__:
                __event_emitter__(
                    {"type": "status", "data": {"description": "❌ Error", "done": True}}
                )
            return f"### ❌ Error\n\n{str(e)}\n\nCheck:\n- Is Apex running? http://localhost:8000/health\n- Is your key correct?"

    def check_status(self, __event_emitter__=None, __user__=None) -> str:
        """Check Apex Orchestrator status"""
        try:
            response = requests.get(f"{self.APEX_BASE_URL}/health", timeout=10)
            data = response.json()
            
            status = "✅" if data.get("ok") else "❌"
            return f"""## Apex Status

**Service:** {status}
- Version: {data.get('version', '?')}
- Environment: {data.get('environment', '?')}

**Health:**
- Ollama: {data.get('checks', {}).get('ollama', {}).get('status', '?')}
"""
        except Exception as e:
            return f"❌ Cannot connect: {str(e)}"

