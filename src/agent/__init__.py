"""
Autonomous Agent Module

This module provides self-improving, self-modifying autonomous agent capabilities
with built-in safety controls and learning mechanisms.
"""

from .agent_loop import AutonomousAgent
from .code_generator import CodeGenerator
from .learner import PatternLearner
from .memory import MemorySystem
from .safety import SafetyController
from .self_modifier import SelfModifier

__all__ = ["MemorySystem", "PatternLearner", "CodeGenerator", "SelfModifier", "AutonomousAgent", "SafetyController"]

__version__ = "1.0.0"
