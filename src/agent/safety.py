"""
Safety Controller

Critical safety controls and kill switches for autonomous agent operations.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger("apex_orchestrator.agent.safety")


class SafetyController:
    """Safety controls and circuit breakers for autonomous operations"""

    def __init__(self, memory_system):
        self.memory = memory_system
        self.enabled = self._load_safety_setting("agent_enabled", "false") == "true"
        self.modifications_enabled = self._load_safety_setting("modifications_enabled", "false") == "true"
        self.max_modifications_per_day = int(self._load_safety_setting("max_modifications_per_day", "5"))
        self.git_integration = self._load_safety_setting("git_integration", "true") == "true"
        self.require_approval = self._load_safety_setting("require_approval", "true") == "true"
        self.sandbox_mode = self._load_safety_setting("sandbox_mode", "true") == "true"

        # Emergency stop file
        self.kill_switch_file = Path("AGENT_KILL_SWITCH")

        logger.info(f"Safety controller initialized - Agent enabled: {self.enabled}")
        logger.warning(f"Modifications enabled: {self.modifications_enabled}")
        logger.warning(f"Max modifications/day: {self.max_modifications_per_day}")

    def _load_safety_setting(self, key: str, default: str) -> str:
        """Load safety setting from environment or memory"""
        # Check environment first (takes precedence)
        env_key = f"AGENT_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Check memory
        mem_value = self.memory.get_agent_state(key)
        return mem_value if mem_value is not None else default

    def is_enabled(self) -> bool:
        """Check if agent is enabled"""
        # Check kill switch
        if self.kill_switch_file.exists():
            logger.critical("KILL SWITCH ACTIVATED - Agent disabled")
            return False

        return self.enabled

    def modifications_enabled_check(self) -> bool:
        """Check if modifications are allowed"""
        if not self.is_enabled():
            return False

        if self.kill_switch_file.exists():
            return False

        return self.modifications_enabled

    def enable_agent(self, password: Optional[str] = None):
        """Enable autonomous agent (requires password in production)"""
        required_password = os.getenv("AGENT_ENABLE_PASSWORD")

        if required_password and password != required_password:
            logger.error("Invalid password for agent enable")
            raise PermissionError("Invalid password")

        self.enabled = True
        self.memory.set_agent_state("agent_enabled", "true")
        logger.warning("⚠️  AUTONOMOUS AGENT ENABLED")

    def disable_agent(self):
        """Disable autonomous agent"""
        self.enabled = False
        self.memory.set_agent_state("agent_enabled", "false")
        logger.info("Autonomous agent disabled")

    def enable_modifications(self, password: Optional[str] = None):
        """Enable code modifications (requires password)"""
        required_password = os.getenv("MODIFICATIONS_ENABLE_PASSWORD")

        if required_password and password != required_password:
            logger.error("Invalid password for modifications enable")
            raise PermissionError("Invalid password")

        self.modifications_enabled = True
        self.memory.set_agent_state("modifications_enabled", "true")
        logger.warning("⚠️  CODE MODIFICATIONS ENABLED - Use with extreme caution!")

    def disable_modifications(self):
        """Disable code modifications"""
        self.modifications_enabled = False
        self.memory.set_agent_state("modifications_enabled", "false")
        logger.info("Code modifications disabled")

    def activate_kill_switch(self, reason: str):
        """Activate emergency kill switch"""
        with open(self.kill_switch_file, "w") as f:
            f.write(f"KILL SWITCH ACTIVATED\n")
            f.write(f"Timestamp: {datetime.utcnow().isoformat()}\n")
            f.write(f"Reason: {reason}\n")

        self.enabled = False
        self.modifications_enabled = False

        logger.critical(f"🚨 KILL SWITCH ACTIVATED: {reason}")
        logger.critical("All autonomous operations halted")

    def deactivate_kill_switch(self, password: str):
        """Deactivate kill switch (requires password)"""
        required_password = os.getenv("KILL_SWITCH_PASSWORD")

        if required_password and password != required_password:
            logger.error("Invalid password for kill switch deactivation")
            raise PermissionError("Invalid password")

        if self.kill_switch_file.exists():
            self.kill_switch_file.unlink()
            logger.warning("Kill switch deactivated")

    def check_safety_limits(self) -> Dict[str, Any]:
        """Check all safety limits and constraints"""
        checks = {
            "agent_enabled": self.is_enabled(),
            "modifications_enabled": self.modifications_enabled_check(),
            "kill_switch_active": self.kill_switch_file.exists(),
            "sandbox_mode": self.sandbox_mode,
            "require_approval": self.require_approval,
        }

        # Check error rates
        error_rate = self._check_error_rate()
        checks["error_rate_ok"] = error_rate < 0.3  # Less than 30% errors
        checks["error_rate"] = error_rate

        # Check modification rate
        stats = self.memory.get_statistics()
        if stats["total_modifications"] > 0:
            mod_success_rate = stats["applied_modifications"] / stats["total_modifications"]
            checks["modification_success_rate"] = mod_success_rate
            checks["modification_rate_ok"] = mod_success_rate > 0.7

        return checks

    def _check_error_rate(self) -> float:
        """Check recent error rate"""
        history = self.memory.get_execution_history(limit=100)
        if not history:
            return 0.0

        errors = sum(1 for ex in history if not ex["success"])
        return errors / len(history)

    def validate_operation(self, operation_type: str, params: Dict[str, Any]) -> tuple[bool, str]:
        """Validate if an operation is safe to execute"""
        # Check if agent is enabled
        if not self.is_enabled():
            return False, "Agent is disabled"

        # Check for dangerous operations
        dangerous_patterns = ["rm -rf", "del /f /s", "format", "dd if=", "shutdown", "reboot", "> /dev/sda"]

        # Check shell commands
        if operation_type == "shell":
            cmd = params.get("cmd", "").lower()
            for pattern in dangerous_patterns:
                if pattern in cmd:
                    logger.error(f"Blocked dangerous command: {pattern}")
                    return False, f"Dangerous pattern detected: {pattern}"

        # Check file operations
        if operation_type == "file_write":
            path = params.get("path", "")
            protected_paths = ["/etc", "/sys", "/proc", "C:\\Windows", "C:\\Program Files"]

            for protected in protected_paths:
                if protected.lower() in path.lower():
                    logger.error(f"Blocked write to protected path: {path}")
                    return False, f"Protected path: {protected}"

        return True, "Operation validated"

    def get_max_modifications_per_day(self) -> int:
        """Get maximum modifications allowed per day"""
        return self.max_modifications_per_day

    def set_max_modifications_per_day(self, max_count: int):
        """Set maximum modifications per day"""
        if max_count < 0 or max_count > 100:
            raise ValueError("Invalid modification limit")

        self.max_modifications_per_day = max_count
        self.memory.set_agent_state("max_modifications_per_day", str(max_count))
        logger.info(f"Max modifications/day set to {max_count}")

    def git_integration_enabled(self) -> bool:
        """Check if git integration is enabled"""
        return self.git_integration

    def approval_required(self) -> bool:
        """Check if human approval is required"""
        return self.require_approval

    def is_sandbox_mode(self) -> bool:
        """Check if running in sandbox mode"""
        return self.sandbox_mode

    def record_safety_incident(self, incident_type: str, description: str, severity: str):
        """Record a safety incident"""
        incident = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": incident_type,
            "description": description,
            "severity": severity,
        }

        # Log to file
        incident_log = Path("logs/safety_incidents.log")
        incident_log.parent.mkdir(exist_ok=True)

        with open(incident_log, "a", encoding="utf-8") as f:
            f.write(f"{incident['timestamp']} [{severity.upper()}] {incident_type}: {description}\n")

        logger.error(f"Safety incident: {incident_type} - {description}")

        # If critical, consider activating kill switch
        if severity == "critical":
            logger.critical("Critical safety incident - consider activating kill switch")

    def get_safety_status(self) -> Dict[str, Any]:
        """Get comprehensive safety status"""
        return {
            "agent_enabled": self.enabled,
            "modifications_enabled": self.modifications_enabled,
            "kill_switch_active": self.kill_switch_file.exists(),
            "sandbox_mode": self.sandbox_mode,
            "require_approval": self.require_approval,
            "max_modifications_per_day": self.max_modifications_per_day,
            "git_integration": self.git_integration,
            "safety_checks": self.check_safety_limits(),
        }

    def emergency_shutdown(self, reason: str):
        """Emergency shutdown of all autonomous operations"""
        logger.critical(f"🚨 EMERGENCY SHUTDOWN: {reason}")

        # Activate kill switch
        self.activate_kill_switch(reason)

        # Disable everything
        self.disable_agent()
        self.disable_modifications()

        # Record incident
        self.record_safety_incident("emergency_shutdown", reason, "critical")

        logger.critical("All operations halted - manual intervention required")
