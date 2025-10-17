"""
title: Apex Orchestrator
author: Apex Orchestrator Team
version: 1.0.0
description: Execute tasks using Apex Orchestrator's AI-powered automation system
required_open_webui_version: 0.3.0
"""

import requests
import hmac
import hashlib
import time
import json
from typing import Callable, Any, Optional
from pydantic import BaseModel, Field


class Function:
    """
    Apex Orchestrator Function for Open WebUI
    Execute tasks via natural language using your Apex Orchestrator backend
    """
    
    class Valves(BaseModel):
        APEX_BASE_URL: str = Field(
            default="http://host.docker.internal:8000",
            description="Base URL of the Apex Orchestrator API"
        )
        APEX_SHARED_KEY: str = Field(
            default="",
            description="Shared key for HMAC authentication (get from .env file)"
        )

    def __init__(self):
        self.valves = self.Valves()

    def _generate_signature(self, body: str, timestamp: str) -> str:
        """Generate HMAC-SHA256 signature for authentication"""
        if not self.valves.APEX_SHARED_KEY:
            raise ValueError("❌ APEX_SHARED_KEY not configured! Set it in Function Settings → Valves")
        
        message = body + timestamp
        signature = hmac.new(
            self.valves.APEX_SHARED_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def pipe(
        self, 
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[Callable[[dict], Any]] = None
    ) -> str:
        """
        Main execution function called by Open WebUI
        
        This gets called when the user mentions executing tasks
        """
        
        # Get the user's message
        messages = body.get("messages", [])
        if not messages:
            return "No message provided"
        
        # Get the last user message
        user_message = messages[-1].get("content", "")
        
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🚀 Executing via Apex Orchestrator...",
                        "done": False
                    },
                }
            )

        try:
            # Prepare request
            request_body = json.dumps({"text": user_message})
            timestamp = str(int(time.time()))
            signature = self._generate_signature(request_body, timestamp)
            
            # Make request to Apex Orchestrator
            response = requests.post(
                f"{self.valves.APEX_BASE_URL}/nlm/run",
                headers={
                    "Content-Type": "application/json",
                    "X-TS": timestamp,
                    "X-SIG": signature
                },
                data=request_body,
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("ok"):
                # Format results as markdown
                result_text = f"### 🎯 Task Executed Successfully\n\n"
                result_text += f"**Intent:** {data['plan']['intent']}\n\n"
                
                if data.get('results'):
                    result_text += f"**Results ({len(data['results'])} steps):**\n\n"
                    
                    for i, result in enumerate(data['results'], 1):
                        result_text += f"#### Step {i}\n"
                        
                        if result.get('stdout'):
                            stdout = result['stdout'].strip()
                            if stdout:
                                result_text += f"```\n{stdout}\n```\n"
                        
                        if result.get('stderr'):
                            stderr = result['stderr'].strip()
                            if stderr:
                                result_text += f"⚠️ **Errors:**\n```\n{stderr}\n```\n"
                        
                        if result.get('path'):
                            result_text += f"📄 **File:** `{result['path']}`\n"
                        
                        if result.get('body'):
                            result_text += f"**Response:**\n```json\n{json.dumps(result['body'], indent=2)}\n```\n"
                        
                        if result.get('returncode') is not None:
                            rc = result['returncode']
                            icon = "✅" if rc == 0 else "❌"
                            result_text += f"{icon} Exit code: {rc}\n"
                        
                        result_text += "\n"
                
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": "✅ Task completed",
                                "done": True
                            },
                        }
                    )
                
                return result_text
            else:
                error_msg = data.get('error', 'Unknown error')
                result_text = f"### ❌ Task Failed\n\n**Error:** {error_msg}\n"
                
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": f"❌ Failed: {error_msg}",
                                "done": True
                            },
                        }
                    )
                
                return result_text
                
        except requests.RequestException as e:
            error_msg = f"Failed to connect to Apex Orchestrator: {str(e)}"
            
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "❌ Connection error",
                            "done": True
                        },
                    }
                )
            
            return f"### ❌ Connection Error\n\n{error_msg}\n\n**Troubleshooting:**\n- Check if Apex Orchestrator is running: http://localhost:8000/health\n- Verify APEX_BASE_URL is correct: `{self.valves.APEX_BASE_URL}`"
        
        except ValueError as e:
            # Configuration error
            return f"### ⚙️ Configuration Error\n\n{str(e)}\n\n**Setup:**\n1. Go to Function Settings\n2. Click 'Valves' tab\n3. Set your APEX_SHARED_KEY"
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "❌ Error",
                            "done": True
                        },
                    }
                )
            
            return f"### ❌ Error\n\n{error_msg}"

