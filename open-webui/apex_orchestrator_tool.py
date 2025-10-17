"""
title: Apex Orchestrator Tool
author: Apex Orchestrator
version: 1.0.0
description: Execute tasks using Apex Orchestrator's AI-powered automation system
required_open_webui_version: 0.3.0
"""

import requests
import hmac
import hashlib
import time
import json
from typing import Callable, Any
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        APEX_BASE_URL: str = Field(
            default="http://host.docker.internal:8000",
            description="Base URL of the Apex Orchestrator API"
        )
        APEX_SHARED_KEY: str = Field(
            default="",
            description="Shared key for HMAC authentication (from APEX_SHARED_KEY env var)"
        )
        ENABLE_CITATION: bool = Field(
            default=True,
            description="Enable citations in responses"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = True

    def _generate_signature(self, body: str, timestamp: str) -> str:
        """Generate HMAC-SHA256 signature for authentication"""
        if not self.valves.APEX_SHARED_KEY:
            raise ValueError("APEX_SHARED_KEY not configured in tool settings")
        
        message = body + timestamp
        signature = hmac.new(
            self.valves.APEX_SHARED_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def execute_task(
        self, 
        task_description: str,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = None
    ) -> str:
        """
        Execute a task using Apex Orchestrator's natural language interface.
        
        This function can:
        - Run shell commands
        - Create/modify files
        - Make HTTP requests
        - Execute Python code
        - Create webhooks
        - And more!
        
        :param task_description: Natural language description of the task to execute
        :return: Execution results formatted as markdown
        """
        
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🚀 Executing via Apex Orchestrator: {task_description[:50]}...",
                        "done": False
                    },
                }
            )

        try:
            # Prepare request
            body = json.dumps({"text": task_description})
            timestamp = str(int(time.time()))
            signature = self._generate_signature(body, timestamp)
            
            # Make request to Apex Orchestrator
            response = requests.post(
                f"{self.valves.APEX_BASE_URL}/nlm/run",
                headers={
                    "Content-Type": "application/json",
                    "X-TS": timestamp,
                    "X-SIG": signature
                },
                data=body,
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
                        
                        # Handle different result types
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
                            if rc == 0:
                                result_text += f"✅ Exit code: {rc}\n"
                            else:
                                result_text += f"❌ Exit code: {rc}\n"
                        
                        result_text += "\n"
                
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": "✅ Task completed successfully",
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
                                "description": f"❌ Task failed: {error_msg}",
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
                            "description": f"❌ Connection error",
                            "done": True
                        },
                    }
                )
            
            return f"### ❌ Connection Error\n\n{error_msg}\n\nMake sure Apex Orchestrator is running at `{self.valves.APEX_BASE_URL}`"
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"❌ Error",
                            "done": True
                        },
                    }
                )
            
            return f"### ❌ Error\n\n{error_msg}"

    async def check_status(
        self,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = None
    ) -> str:
        """
        Check Apex Orchestrator system status and health.
        
        :return: System status and health information
        """
        try:
            # Check main health
            response = requests.get(
                f"{self.valves.APEX_BASE_URL}/health",
                timeout=10
            )
            health_data = response.json()
            
            # Check agent status
            agent_response = requests.get(
                f"{self.valves.APEX_BASE_URL}/agent/safety/status",
                timeout=10
            )
            agent_data = agent_response.json()
            
            # Format status
            status_text = "## 🤖 Apex Orchestrator Status\n\n"
            
            # Main service status
            status_icon = "✅" if health_data.get("ok") else "❌"
            status_text += f"### Service: {status_icon}\n"
            status_text += f"- **Version:** {health_data.get('version', 'unknown')}\n"
            status_text += f"- **Environment:** {health_data.get('environment', 'unknown')}\n"
            status_text += f"- **Timestamp:** {health_data.get('timestamp', 'unknown')}\n\n"
            
            # Check details
            if 'checks' in health_data:
                status_text += "### Health Checks:\n"
                for check_name, check_data in health_data['checks'].items():
                    check_status = check_data.get('status', 'unknown')
                    icon = "✅" if check_status == 'healthy' else "❌"
                    status_text += f"- {icon} **{check_name.title()}:** {check_status}\n"
                status_text += "\n"
            
            # Agent status
            status_text += "### 🤖 Autonomous Agent:\n"
            status_text += f"- **Enabled:** {'✅ Yes' if agent_data.get('agent_enabled') else '❌ No'}\n"
            status_text += f"- **Modifications:** {'⚠️ Enabled' if agent_data.get('modifications_enabled') else '✅ Disabled'}\n"
            status_text += f"- **Kill Switch:** {'🚨 Active' if agent_data.get('kill_switch_active') else '✅ Inactive'}\n"
            status_text += f"- **Sandbox Mode:** {'✅ Enabled' if agent_data.get('sandbox_mode') else '⚠️ Disabled'}\n"
            status_text += f"- **Approval Required:** {'✅ Yes' if agent_data.get('require_approval') else '⚠️ No'}\n"
            
            return status_text
            
        except Exception as e:
            return f"### ❌ Status Check Failed\n\n{str(e)}\n\nMake sure Apex Orchestrator is running at `{self.valves.APEX_BASE_URL}`"

    async def get_metrics(
        self,
        __event_emitter__: Callable[[dict], Any] = None,
        __user__: dict = None
    ) -> str:
        """
        Get Apex Orchestrator metrics and statistics.
        
        :return: System metrics and statistics
        """
        try:
            response = requests.get(
                f"{self.valves.APEX_BASE_URL}/metrics",
                timeout=10
            )
            data = response.json()
            
            metrics_text = "## 📊 Apex Orchestrator Metrics\n\n"
            metrics_text += f"- **Service:** {data.get('service', 'unknown')}\n"
            metrics_text += f"- **Uptime:** {data.get('uptime_seconds', 0):.2f} seconds\n"
            
            if 'logs' in data:
                metrics_text += f"\n### 📝 Logs:\n"
                metrics_text += f"- **Files:** {data['logs'].get('file_count', 0)}\n"
                metrics_text += f"- **Size:** {data['logs'].get('total_size_mb', 0):.2f} MB\n"
            
            if 'work_dir' in data:
                metrics_text += f"\n### 📁 Work Directory:\n"
                metrics_text += f"- **Path:** `{data['work_dir'].get('path', 'unknown')}`\n"
                metrics_text += f"- **Exists:** {data['work_dir'].get('exists', False)}\n"
            
            return metrics_text
            
        except Exception as e:
            return f"### ❌ Metrics Check Failed\n\n{str(e)}"

