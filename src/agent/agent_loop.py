"""
Autonomous Agent Loop

Main orchestration loop for autonomous learning, optimization, and self-improvement.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import traceback

from .memory import MemorySystem
from .learner import PatternLearner
from .code_generator import CodeGenerator
from .self_modifier import SelfModifier
from .safety import SafetyController

logger = logging.getLogger("apex_orchestrator.agent.loop")


class AutonomousAgent:
    """Autonomous agent that learns, optimizes, and self-improves"""
    
    def __init__(self, memory_db_path: str = "logs/agent_memory.db"):
        # Initialize components
        self.memory = MemorySystem(memory_db_path)
        self.safety = SafetyController(self.memory)
        self.learner = PatternLearner(self.memory)
        self.code_generator = CodeGenerator(self.memory, llm_client=None)
        self.self_modifier = SelfModifier(self.memory, self.code_generator, self.safety)
        
        # Agent state
        self.running = False
        self.loop_count = 0
        self.last_learning_time = None
        self.last_optimization_time = None
        
        logger.info("🤖 Autonomous Agent initialized")
        logger.info(f"Safety status: {self.safety.get_safety_status()}")
    
    async def start(self, interval_seconds: int = 3600):
        """Start the autonomous agent loop"""
        if not self.safety.is_enabled():
            logger.warning("Cannot start: Agent is disabled")
            return {
                "status": "disabled",
                "message": "Agent is not enabled. Enable it first."
            }
        
        self.running = True
        logger.info(f"🚀 Starting autonomous agent loop (interval: {interval_seconds}s)")
        
        try:
            while self.running:
                await self._run_cycle()
                
                # Wait for next cycle
                await asyncio.sleep(interval_seconds)
                
        except Exception as e:
            logger.error(f"Agent loop crashed: {e}")
            logger.error(traceback.format_exc())
            self.safety.record_safety_incident("agent_crash", str(e), "critical")
            self.running = False
    
    def stop(self):
        """Stop the autonomous agent loop"""
        self.running = False
        logger.info("Stopping autonomous agent loop...")
    
    async def _run_cycle(self):
        """Run one cycle of the autonomous agent"""
        self.loop_count += 1
        cycle_start = datetime.utcnow()
        
        logger.info(f"=== Agent Cycle {self.loop_count} ===")
        
        try:
            # Safety check
            if not self.safety.is_enabled():
                logger.warning("Agent disabled during cycle, stopping...")
                self.stop()
                return
            
            safety_checks = self.safety.check_safety_limits()
            if not safety_checks["agent_enabled"]:
                logger.warning("Safety checks failed, skipping cycle")
                return
            
            # 1. Learn from recent executions
            await self._learning_phase()
            
            # 2. Analyze patterns and identify opportunities
            await self._analysis_phase()
            
            # 3. Generate improvements (if enabled)
            if self.safety.modifications_enabled_check():
                await self._improvement_phase()
            
            # 4. Self-optimization (if enabled)
            if self.safety.modifications_enabled_check() and self._should_self_optimize():
                await self._self_optimization_phase()
            
            # 5. Record metrics
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            self.memory.record_metric("agent_cycle_duration_seconds", cycle_duration)
            
            logger.info(f"Cycle {self.loop_count} completed in {cycle_duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Error in agent cycle: {e}")
            logger.error(traceback.format_exc())
            self.safety.record_safety_incident("cycle_error", str(e), "medium")
    
    async def _learning_phase(self):
        """Learn from recent execution history"""
        logger.info("📚 Learning Phase")
        
        # Get recent executions
        recent_history = self.memory.get_execution_history(limit=100)
        
        # Learn from successes and failures
        for execution in recent_history:
            if execution['success']:
                self.learner.learn_from_success(execution)
            else:
                self.learner.learn_from_failure(execution)
        
        # Update last learning time
        self.last_learning_time = datetime.utcnow()
        
        # Get success rate
        success_rate = self.memory.get_success_rate(hours=24)
        logger.info(f"Current 24h success rate: {success_rate*100:.1f}%")
        
        # Safety check: if success rate too low, alert
        if success_rate < 0.5 and len(recent_history) > 10:
            logger.warning(f"⚠️  Low success rate detected: {success_rate*100:.1f}%")
            self.safety.record_safety_incident(
                "low_success_rate",
                f"Success rate dropped to {success_rate*100:.1f}%",
                "medium"
            )
    
    async def _analysis_phase(self):
        """Analyze patterns and identify opportunities"""
        logger.info("🔍 Analysis Phase")
        
        # Analyze execution patterns
        analysis = self.learner.analyze_execution_patterns(hours=24)
        logger.info(f"Analyzed {analysis.get('total_executions', 0)} executions")
        
        # Log recommendations
        for recommendation in analysis.get('recommendations', []):
            logger.info(f"💡 Recommendation: {recommendation}")
        
        # Identify optimization opportunities
        opportunities = self.learner.identify_optimization_opportunities()
        logger.info(f"Found {len(opportunities)} optimization opportunities")
        
        # Store top opportunities for improvement phase
        self.memory.set_agent_state(
            "current_opportunities",
            str(len(opportunities))
        )
        
        return opportunities
    
    async def _improvement_phase(self):
        """Generate and propose improvements"""
        logger.info("🔧 Improvement Phase")
        
        # Get improvement suggestions
        suggestions = self.learner.suggest_improvements()
        
        if not suggestions:
            logger.info("No high-priority improvements identified")
            return
        
        logger.info(f"Processing {len(suggestions)} improvement suggestions")
        
        for suggestion in suggestions[:3]:  # Top 3 suggestions
            try:
                await self._process_suggestion(suggestion)
            except Exception as e:
                logger.error(f"Failed to process suggestion: {e}")
    
    async def _process_suggestion(self, suggestion: Dict[str, Any]):
        """Process an improvement suggestion"""
        category = suggestion['category']
        description = suggestion['description']
        action = suggestion['action']
        
        logger.info(f"Processing suggestion: {category} - {description}")
        
        if category == "code_reuse":
            # Generate template for reuse
            await self._generate_template(description, action)
        
        elif category == "performance":
            # Propose performance optimization
            if self.safety.modifications_enabled_check() and not self.safety.approval_required():
                await self._propose_optimization(description, action)
        
        elif category == "reliability":
            # Improve error handling
            logger.info(f"Reliability improvement needed: {action}")
            # Could generate improved error handling code
    
    async def _generate_template(self, pattern: str, action: str):
        """Generate a code template from pattern"""
        logger.info(f"Generating template for pattern: {pattern}")
        
        result = await self.code_generator.generate_function(
            purpose=pattern,
            requirements={"reusable": True, "documented": True}
        )
        
        if result['status'] == 'success':
            logger.info(f"✅ Template created: {result.get('template_name')}")
        else:
            logger.warning(f"Template generation failed: {result.get('error')}")
    
    async def _propose_optimization(self, description: str, action: str):
        """Propose a code optimization"""
        logger.info(f"Proposing optimization: {description}")
        
        # This would identify target files and propose modifications
        # For safety, always require approval for actual modifications
        logger.info(f"Action: {action}")
        logger.info("Note: Actual code modifications require approval")
    
    async def _self_optimization_phase(self):
        """Self-optimization phase (most advanced)"""
        logger.info("⚡ Self-Optimization Phase")
        
        if not self.safety.modifications_enabled_check():
            logger.info("Self-modifications disabled, skipping")
            return
        
        # Analyze own performance
        stats = self.memory.get_statistics()
        logger.info(f"Agent stats: {stats}")
        
        # Check if improvements are needed
        if stats['overall_success_rate'] < 85.0:
            logger.info("Success rate below target, analyzing for improvements")
            # Could propose self-modifications here
        
        # Check modification stats
        mod_stats = self.self_modifier.get_modification_stats()
        logger.info(f"Modification stats: {mod_stats}")
    
    def _should_self_optimize(self) -> bool:
        """Determine if self-optimization should run"""
        # Only optimize once per day
        if self.last_optimization_time:
            time_since_last = datetime.utcnow() - self.last_optimization_time
            if time_since_last < timedelta(hours=24):
                return False
        
        # Check if enough data
        stats = self.memory.get_statistics()
        if stats['total_executions'] < 100:
            return False  # Need more data
        
        return True
    
    async def manual_learn_from_execution(self, execution: Dict[str, Any]):
        """Manually trigger learning from an execution"""
        logger.info("Manual learning triggered")
        
        if execution['success']:
            self.learner.learn_from_success(execution)
        else:
            self.learner.learn_from_failure(execution)
        
        return {"status": "learned", "success": execution['success']}
    
    async def propose_modification(self, target_file: str, modification_type: str,
                                  description: str, reason: str) -> Dict[str, Any]:
        """Manually propose a modification"""
        logger.info(f"Manual modification proposal: {target_file}")
        
        return await self.self_modifier.propose_modification(
            target_file, modification_type, description, reason
        )
    
    async def apply_modification(self, proposal_id: int) -> Dict[str, Any]:
        """Apply a proposed modification"""
        logger.info(f"Applying modification proposal {proposal_id}")
        
        return await self.self_modifier.apply_modification(proposal_id)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {
            "running": self.running,
            "loop_count": self.loop_count,
            "last_learning_time": self.last_learning_time.isoformat() if self.last_learning_time else None,
            "last_optimization_time": self.last_optimization_time.isoformat() if self.last_optimization_time else None,
            "safety": self.safety.get_safety_status(),
            "memory_stats": self.memory.get_statistics(),
            "modification_stats": self.self_modifier.get_modification_stats()
        }
    
    def get_learning_report(self) -> Dict[str, Any]:
        """Get learning and analysis report"""
        analysis = self.learner.analyze_execution_patterns(hours=24)
        opportunities = self.learner.identify_optimization_opportunities()
        suggestions = self.learner.suggest_improvements()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "execution_analysis": analysis,
            "optimization_opportunities": opportunities,
            "improvement_suggestions": suggestions,
            "patterns_learned": self.memory.get_statistics()['learned_patterns']
        }


# Global agent instance (initialized when needed)
_agent_instance: Optional[AutonomousAgent] = None


def get_agent() -> AutonomousAgent:
    """Get or create the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AutonomousAgent()
    return _agent_instance

