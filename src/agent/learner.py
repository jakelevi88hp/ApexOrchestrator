"""
Pattern Learning System

Analyzes execution history, identifies patterns, and suggests optimizations.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import re

logger = logging.getLogger("apex_orchestrator.agent.learner")


class PatternLearner:
    """Learn patterns from execution history and suggest improvements"""

    def __init__(self, memory_system):
        self.memory = memory_system
        logger.info("Pattern learner initialized")

    def analyze_execution_patterns(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze recent execution patterns"""
        history = self.memory.get_execution_history(limit=1000)

        # Filter by time
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [ex for ex in history if datetime.fromisoformat(ex["timestamp"]) > cutoff]

        if not recent:
            return {"message": "No recent executions to analyze"}

        analysis = {
            "total_executions": len(recent),
            "success_rate": sum(1 for ex in recent if ex["success"]) / len(recent),
            "avg_execution_time_ms": sum(ex["execution_time_ms"] for ex in recent) / len(recent),
            "operation_types": self._analyze_operation_types(recent),
            "common_failures": self._analyze_failures(recent),
            "performance_trends": self._analyze_performance(recent),
            "recommendations": [],
        }

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        logger.info(f"Analyzed {len(recent)} executions")
        return analysis

    def _analyze_operation_types(self, executions: List[Dict]) -> Dict:
        """Analyze distribution of operation types"""
        types = [ex["operation_type"] for ex in executions]
        counter = Counter(types)

        return {"distribution": dict(counter), "most_common": counter.most_common(5)}

    def _analyze_failures(self, executions: List[Dict]) -> List[Dict]:
        """Analyze common failure patterns"""
        failures = [ex for ex in executions if not ex["success"]]

        if not failures:
            return []

        error_patterns = Counter()
        for failure in failures:
            if failure["error_message"]:
                # Extract error type
                error_type = self._extract_error_type(failure["error_message"])
                error_patterns[error_type] += 1

        return [
            {"error_type": error, "count": count, "percentage": count / len(failures) * 100}
            for error, count in error_patterns.most_common(5)
        ]

    def _extract_error_type(self, error_message: str) -> str:
        """Extract error type from message"""
        # Common error patterns
        patterns = [
            (r"timeout", "Timeout"),
            (r"permission denied", "Permission Denied"),
            (r"not found", "Not Found"),
            (r"connection", "Connection Error"),
            (r"rate limit", "Rate Limit"),
        ]

        error_lower = error_message.lower()
        for pattern, error_type in patterns:
            if re.search(pattern, error_lower):
                return error_type

        return "Unknown Error"

    def _analyze_performance(self, executions: List[Dict]) -> Dict:
        """Analyze performance trends"""
        if len(executions) < 10:
            return {"message": "Insufficient data for trend analysis"}

        # Sort by timestamp
        sorted_execs = sorted(executions, key=lambda x: x["timestamp"])

        # Split into first half and second half
        mid = len(sorted_execs) // 2
        first_half = sorted_execs[:mid]
        second_half = sorted_execs[mid:]

        first_avg = sum(ex["execution_time_ms"] for ex in first_half) / len(first_half)
        second_avg = sum(ex["execution_time_ms"] for ex in second_half) / len(second_half)

        improvement = ((first_avg - second_avg) / first_avg * 100) if first_avg > 0 else 0

        return {
            "early_period_avg_ms": round(first_avg, 2),
            "recent_period_avg_ms": round(second_avg, 2),
            "performance_change_percent": round(improvement, 2),
            "trend": "improving" if improvement > 5 else "degrading" if improvement < -5 else "stable",
        }

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Success rate recommendations
        if analysis["success_rate"] < 0.8:
            recommendations.append(
                f"Success rate is {analysis['success_rate']*100:.1f}%. "
                "Consider reviewing failed operations and improving error handling."
            )

        # Performance recommendations
        if analysis["avg_execution_time_ms"] > 5000:
            recommendations.append(
                f"Average execution time is {analysis['avg_execution_time_ms']:.0f}ms. "
                "Consider optimizing slow operations or implementing caching."
            )

        # Failure pattern recommendations
        if analysis["common_failures"]:
            top_failure = analysis["common_failures"][0]
            recommendations.append(
                f"Most common failure: {top_failure['error_type']} "
                f"({top_failure['percentage']:.1f}% of failures). "
                "Implement specific handling for this error type."
            )

        return recommendations

    def identify_optimization_opportunities(self) -> List[Dict]:
        """Identify specific code optimization opportunities"""
        opportunities = []

        # Check for slow operations
        history = self.memory.get_execution_history(limit=500)
        slow_ops = [ex for ex in history if ex["execution_time_ms"] > 10000]

        if slow_ops:
            # Group by operation type
            slow_by_type = {}
            for op in slow_ops:
                op_type = op["operation_type"]
                if op_type not in slow_by_type:
                    slow_by_type[op_type] = []
                slow_by_type[op_type].append(op)

            for op_type, ops in slow_by_type.items():
                avg_time = sum(op["execution_time_ms"] for op in ops) / len(ops)
                opportunities.append(
                    {
                        "type": "performance",
                        "operation": op_type,
                        "issue": f"Slow execution (avg {avg_time:.0f}ms)",
                        "suggestion": "Consider adding caching, parallel execution, or optimization",
                        "priority": "high" if avg_time > 30000 else "medium",
                        "occurrences": len(ops),
                    }
                )

        # Check for frequent failures
        failures = [ex for ex in history if not ex["success"]]
        if len(failures) / len(history) > 0.2:  # More than 20% failure rate
            opportunities.append(
                {
                    "type": "reliability",
                    "issue": f"High failure rate: {len(failures)/len(history)*100:.1f}%",
                    "suggestion": "Implement retry logic, better error handling, or input validation",
                    "priority": "high",
                }
            )

        # Check for repeated patterns that could be templated
        intents = [ex["intent"] for ex in history if ex["intent"]]
        intent_patterns = Counter(intents)

        for intent, count in intent_patterns.most_common(10):
            if count > 10:  # Repeated more than 10 times
                opportunities.append(
                    {
                        "type": "code_reuse",
                        "pattern": intent,
                        "occurrences": count,
                        "suggestion": f"Create a reusable template for: '{intent}'",
                        "priority": "medium",
                    }
                )

        logger.info(f"Identified {len(opportunities)} optimization opportunities")
        return opportunities

    def learn_from_success(self, execution: Dict):
        """Learn from a successful execution"""
        if not execution.get("success"):
            return

        # Extract pattern from successful execution
        pattern_data = {
            "operation_type": execution["operation_type"],
            "intent": execution["intent"],
            "plan_summary": self._summarize_plan(execution.get("plan", {})),
        }

        self.memory.save_pattern(
            pattern_type="successful_execution",
            pattern_data=pattern_data,
            success=True,
            execution_time_ms=execution["execution_time_ms"],
        )

        logger.debug(f"Learned from successful {execution['operation_type']}")

    def learn_from_failure(self, execution: Dict):
        """Learn from a failed execution"""
        if execution.get("success"):
            return

        # Extract pattern from failed execution
        pattern_data = {
            "operation_type": execution["operation_type"],
            "intent": execution["intent"],
            "error_type": self._extract_error_type(execution.get("error_message", "")),
            "error_message": execution.get("error_message", "")[:200],  # Limit length
        }

        self.memory.save_pattern(
            pattern_type="failed_execution",
            pattern_data=pattern_data,
            success=False,
            execution_time_ms=execution["execution_time_ms"],
        )

        logger.debug(f"Learned from failed {execution['operation_type']}")

    def _summarize_plan(self, plan: Any) -> str:
        """Create a summary of an execution plan"""
        if isinstance(plan, str):
            try:
                plan = json.loads(plan)
            except:
                return str(plan)[:100]

        if isinstance(plan, dict):
            steps = plan.get("steps", [])
            if steps:
                return f"{len(steps)} steps: " + ", ".join(step.get("tool", "unknown") for step in steps[:3])

        return str(plan)[:100]

    def suggest_improvements(self) -> List[Dict]:
        """Suggest specific code improvements"""
        suggestions = []

        # Analyze patterns
        opportunities = self.identify_optimization_opportunities()

        for opp in opportunities:
            if opp.get("priority") == "high":
                suggestions.append(
                    {
                        "category": opp["type"],
                        "description": opp.get("issue", opp.get("pattern", "")),
                        "action": opp["suggestion"],
                        "impact": "high",
                        "effort": self._estimate_effort(opp),
                    }
                )

        # Check for missing features
        stats = self.memory.get_statistics()
        if stats["total_executions"] > 100 and stats["code_templates"] < 5:
            suggestions.append(
                {
                    "category": "code_reuse",
                    "description": "Few code templates despite many executions",
                    "action": "Generate reusable code templates from successful patterns",
                    "impact": "medium",
                    "effort": "low",
                }
            )

        logger.info(f"Generated {len(suggestions)} improvement suggestions")
        return suggestions

    def _estimate_effort(self, opportunity: Dict) -> str:
        """Estimate implementation effort"""
        if opportunity["type"] == "code_reuse":
            return "low"
        elif opportunity["type"] == "performance":
            return "medium"
        elif opportunity["type"] == "reliability":
            return "high"
        return "medium"
