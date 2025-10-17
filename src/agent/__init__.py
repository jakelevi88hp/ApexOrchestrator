"""
Autonomous Agent Module

This module provides self-improving, self-modifying autonomous agent capabilities
with built-in safety controls and learning mechanisms.
"""

from .memory import MemorySystem
from .learner import PatternLearner
from .code_generator import CodeGenerator
from .self_modifier import SelfModifier
from .agent_loop import AutonomousAgent
from .safety import SafetyController

__all__ = [
    'MemorySystem',
    'PatternLearner',
    'CodeGenerator',
    'SelfModifier',
    'AutonomousAgent',
    'SafetyController'
]

__version__ = '1.0.0'

