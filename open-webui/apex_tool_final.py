"""
title: Apex Orchestrator
author: open-webui
version: 1.0.0
required_open_webui_version: 0.1.0
"""

import requests
import hmac
import hashlib
import time
import json
from typing import Callable, Any


class Tools:
    def __init__(self):
        pass

    def execute_task(
        self,
        task_description: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Execute a task using Apex Orchestrator.
        :param task_description: Description of the task to execute.
        :return: Task execution results.
        """
        
        # CONFIGURE THESE (copy from your .env file):
        APEX_BASE_URL = "http://host.docker.internal:8000"
        APEX_SHARED_KEY = "XGR8IDzftIqPBLL5t62CU1OUYXfi-fbAnS7BNqa-AyA"
        
        if not APEX_SHARED_KEY or APEX_SHARED_KEY == "":
            return "❌ Configure APEX_SHARED_KEY in the function code (line 31)"
        
        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "🚀 Executing task...", "done": False},
                }
            )
        
        try:
            # Generate HMAC signature
            body = json.dumps({"text": task_description})
            timestamp = str(int(time.time()))
            message = body + timestamp
            signature = hmac.new(
                APEX_SHARED_KEY.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Call Apex Orchestrator API
            response = requests.post(
                f"{APEX_BASE_URL}/nlm/run",
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
                # Format success response
                result = f"### ✅ Task Completed\n\n"
                result += f"**Intent:** {data['plan']['intent']}\n\n"
                
                if data.get('results'):
                    result += f"**Results:**\n\n"
                    for i, r in enumerate(data['results'], 1):
                        result += f"**Step {i}:**\n"
                        if r.get('stdout'):
                            result += f"```\n{r['stdout']}\n```\n"
                        if r.get('path'):
                            result += f"📄 File: `{r['path']}`\n"
                        if r.get('body'):
                            result += f"```json\n{json.dumps(r['body'], indent=2)}\n```\n"
                        result += "\n"
                
                if __event_emitter__:
                    __event_emitter__(
                        {"type": "status", "data": {"description": "✅ Completed", "done": True}}
                    )
                
                return result
            else:
                error = data.get('error', 'Unknown error')
                if __event_emitter__:
                    __event_emitter__(
                        {"type": "status", "data": {"description": f"❌ Error: {error}", "done": True}}
                    )
                return f"### ❌ Task Failed\n\n{error}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {"type": "status", "data": {"description": "❌ Connection failed", "done": True}}
                )
            return f"### ❌ Connection Error\n\n{error_msg}\n\n**Troubleshooting:**\n- Check Apex is running: http://localhost:8000/health\n- Verify URL: {APEX_BASE_URL}"
        
        except Exception as e:
            if __event_emitter__:
                __event_emitter__(
                    {"type": "status", "data": {"description": "❌ Error", "done": True}}
                )
            return f"### ❌ Error\n\n{str(e)}"

    def check_status(
        self,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Check Apex Orchestrator system status.
        :return: System status information.
        """
        
        APEX_BASE_URL = "http://host.docker.internal:8000"
        
        try:
            response = requests.get(f"{APEX_BASE_URL}/health", timeout=10)
            data = response.json()
            
            status_icon = "✅" if data.get("ok") else "❌"
            
            result = f"## {status_icon} Apex Orchestrator Status\n\n"
            result += f"**Service:** {data.get('service', 'Unknown')}\n"
            result += f"**Version:** {data.get('version', 'Unknown')}\n"
            result += f"**Environment:** {data.get('environment', 'Unknown')}\n\n"
            
            if 'checks' in data:
                result += "**Health Checks:**\n"
                for name, check in data['checks'].items():
                    check_status = check.get('status', 'unknown')
                    icon = "✅" if check_status == 'healthy' else "❌"
                    result += f"- {icon} {name.title()}: {check_status}\n"
            
            return result
            
        except Exception as e:
            return f"### ❌ Cannot Connect\n\n{str(e)}\n\nMake sure Apex Orchestrator is running at: {APEX_BASE_URL}"

