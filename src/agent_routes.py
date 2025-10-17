"""
API Routes for Autonomous Agent

Endpoints for managing and interacting with the autonomous agent.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Header, Depends, status
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from agent.agent_loop import get_agent, AutonomousAgent
from agent.safety import SafetyController

logger = logging.getLogger("apex_orchestrator.agent_routes")

# Create router
router = APIRouter(prefix="/agent", tags=["Autonomous Agent"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


# Pydantic models
class AgentEnableRequest(BaseModel):
    password: Optional[str] = Field(None, description="Password for enabling agent")

class ModificationProposal(BaseModel):
    target_file: str = Field(..., description="File to modify")
    modification_type: str = Field(..., description="Type of modification")
    description: str = Field(..., description="Description of changes")
    reason: str = Field(..., description="Reason for modification")

class ModificationApproval(BaseModel):
    proposal_id: int = Field(..., description="Proposal ID to apply")
    auto_test: bool = Field(True, description="Run tests before applying")


# Routes
@router.get("/status")
@limiter.limit("30/minute")
async def get_agent_status(request: Request):
    """Get autonomous agent status"""
    try:
        agent = get_agent()
        return agent.get_agent_status()
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(500, "Failed to retrieve agent status")


@router.get("/learning-report")
@limiter.limit("10/minute")
async def get_learning_report(request: Request):
    """Get learning and analysis report"""
    try:
        agent = get_agent()
        return agent.get_learning_report()
    except Exception as e:
        logger.error(f"Failed to get learning report: {e}")
        raise HTTPException(500, "Failed to generate learning report")


@router.post("/enable")
@limiter.limit("5/minute")
async def enable_agent(request: Request, body: AgentEnableRequest):
    """Enable autonomous agent (requires password in production)"""
    try:
        agent = get_agent()
        agent.safety.enable_agent(body.password)
        
        return {
            "status": "enabled",
            "message": "⚠️  Autonomous agent enabled",
            "safety_status": agent.safety.get_safety_status()
        }
    except PermissionError:
        raise HTTPException(403, "Invalid password")
    except Exception as e:
        logger.error(f"Failed to enable agent: {e}")
        raise HTTPException(500, str(e))


@router.post("/disable")
@limiter.limit("5/minute")
async def disable_agent(request: Request):
    """Disable autonomous agent"""
    try:
        agent = get_agent()
        agent.safety.disable_agent()
        agent.stop()
        
        return {
            "status": "disabled",
            "message": "Autonomous agent disabled"
        }
    except Exception as e:
        logger.error(f"Failed to disable agent: {e}")
        raise HTTPException(500, str(e))


@router.post("/modifications/enable")
@limiter.limit("3/minute")
async def enable_modifications(request: Request, body: AgentEnableRequest):
    """Enable code modifications (requires password)"""
    try:
        agent = get_agent()
        agent.safety.enable_modifications(body.password)
        
        return {
            "status": "enabled",
            "message": "⚠️  Code modifications enabled - USE WITH EXTREME CAUTION",
            "max_per_day": agent.safety.get_max_modifications_per_day()
        }
    except PermissionError:
        raise HTTPException(403, "Invalid password")
    except Exception as e:
        logger.error(f"Failed to enable modifications: {e}")
        raise HTTPException(500, str(e))


@router.post("/modifications/disable")
@limiter.limit("3/minute")
async def disable_modifications(request: Request):
    """Disable code modifications"""
    try:
        agent = get_agent()
        agent.safety.disable_modifications()
        
        return {
            "status": "disabled",
            "message": "Code modifications disabled"
        }
    except Exception as e:
        logger.error(f"Failed to disable modifications: {e}")
        raise HTTPException(500, str(e))


@router.post("/modifications/propose")
@limiter.limit("5/hour")
async def propose_modification(request: Request, proposal: ModificationProposal):
    """Propose a code modification"""
    try:
        agent = get_agent()
        
        result = await agent.propose_modification(
            target_file=proposal.target_file,
            modification_type=proposal.modification_type,
            description=proposal.description,
            reason=proposal.reason
        )
        
        return result
    except Exception as e:
        logger.error(f"Failed to propose modification: {e}")
        raise HTTPException(500, str(e))


@router.post("/modifications/apply")
@limiter.limit("3/hour")
async def apply_modification(request: Request, approval: ModificationApproval):
    """Apply a proposed modification"""
    try:
        agent = get_agent()
        
        result = await agent.apply_modification(approval.proposal_id)
        
        if result['status'] == 'applied':
            logger.warning(f"✅ Modification applied: {result['file']}")
        
        return result
    except Exception as e:
        logger.error(f"Failed to apply modification: {e}")
        raise HTTPException(500, str(e))


@router.post("/start-loop")
@limiter.limit("3/minute")
async def start_agent_loop(request: Request, interval_seconds: int = 3600):
    """Start the autonomous agent loop"""
    try:
        agent = get_agent()
        
        if agent.running:
            return {
                "status": "already_running",
                "message": "Agent loop is already running"
            }
        
        # Start in background task
        import asyncio
        asyncio.create_task(agent.start(interval_seconds))
        
        return {
            "status": "started",
            "message": f"Agent loop started (interval: {interval_seconds}s)",
            "loop_count": agent.loop_count
        }
    except Exception as e:
        logger.error(f"Failed to start agent loop: {e}")
        raise HTTPException(500, str(e))


@router.post("/stop-loop")
@limiter.limit("3/minute")
async def stop_agent_loop(request: Request):
    """Stop the autonomous agent loop"""
    try:
        agent = get_agent()
        agent.stop()
        
        return {
            "status": "stopped",
            "message": "Agent loop stopped",
            "total_cycles": agent.loop_count
        }
    except Exception as e:
        logger.error(f"Failed to stop agent loop: {e}")
        raise HTTPException(500, str(e))


@router.post("/kill-switch/activate")
@limiter.limit("5/minute")
async def activate_kill_switch(request: Request, reason: str):
    """Activate emergency kill switch"""
    try:
        agent = get_agent()
        agent.safety.activate_kill_switch(reason)
        
        return {
            "status": "activated",
            "message": "🚨 KILL SWITCH ACTIVATED - All operations halted",
            "reason": reason
        }
    except Exception as e:
        logger.error(f"Failed to activate kill switch: {e}")
        raise HTTPException(500, str(e))


@router.post("/kill-switch/deactivate")
@limiter.limit("3/minute")
async def deactivate_kill_switch(request: Request, password: str):
    """Deactivate kill switch (requires password)"""
    try:
        agent = get_agent()
        agent.safety.deactivate_kill_switch(password)
        
        return {
            "status": "deactivated",
            "message": "Kill switch deactivated"
        }
    except PermissionError:
        raise HTTPException(403, "Invalid password")
    except Exception as e:
        logger.error(f"Failed to deactivate kill switch: {e}")
        raise HTTPException(500, str(e))


@router.get("/memory/stats")
@limiter.limit("20/minute")
async def get_memory_stats(request: Request):
    """Get memory system statistics"""
    try:
        agent = get_agent()
        return agent.memory.get_statistics()
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(500, str(e))


@router.get("/memory/executions")
@limiter.limit("20/minute")
async def get_execution_history(request: Request, limit: int = 100):
    """Get execution history"""
    try:
        agent = get_agent()
        history = agent.memory.get_execution_history(limit=limit)
        return {
            "count": len(history),
            "executions": history
        }
    except Exception as e:
        logger.error(f"Failed to get execution history: {e}")
        raise HTTPException(500, str(e))


@router.get("/safety/status")
@limiter.limit("30/minute")
async def get_safety_status(request: Request):
    """Get comprehensive safety status"""
    try:
        agent = get_agent()
        return agent.safety.get_safety_status()
    except Exception as e:
        logger.error(f"Failed to get safety status: {e}")
        raise HTTPException(500, str(e))


@router.get("/opportunities")
@limiter.limit("10/minute")
async def get_optimization_opportunities(request: Request):
    """Get current optimization opportunities"""
    try:
        agent = get_agent()
        opportunities = agent.learner.identify_optimization_opportunities()
        
        return {
            "count": len(opportunities),
            "opportunities": opportunities
        }
    except Exception as e:
        logger.error(f"Failed to get opportunities: {e}")
        raise HTTPException(500, str(e))


@router.get("/suggestions")
@limiter.limit("10/minute")
async def get_improvement_suggestions(request: Request):
    """Get improvement suggestions"""
    try:
        agent = get_agent()
        suggestions = agent.learner.suggest_improvements()
        
        return {
            "count": len(suggestions),
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(500, str(e))

