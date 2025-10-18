"""
Pulse System Data Models

Defines the data structures for tracking system activity and metrics.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
import json


class EventType(str, Enum):
    """Types of events tracked by Pulse"""
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    AGENT_EXECUTION = "agent_execution"
    TOOL_EXECUTION = "tool_execution"
    ERROR = "error"
    SYSTEM_METRIC = "system_metric"
    USER_ACTION = "user_action"
    PERFORMANCE = "performance"


class EventSeverity(str, Enum):
    """Event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PulseEvent(BaseModel):
    """Individual pulse event"""
    id: str = Field(..., description="Unique event ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    event_type: EventType = Field(..., description="Type of event")
    severity: EventSeverity = Field(default=EventSeverity.LOW, description="Event severity")
    source: str = Field(..., description="Source component (e.g., 'api', 'agent', 'tool')")
    message: str = Field(..., description="Event message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")
    duration_ms: Optional[float] = Field(None, description="Event duration in milliseconds")
    user_id: Optional[str] = Field(None, description="Associated user ID")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    request_id: Optional[str] = Field(None, description="Associated request ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SystemMetrics(BaseModel):
    """System performance metrics"""
    cpu_percent: float = Field(0.0, description="CPU usage percentage")
    memory_percent: float = Field(0.0, description="Memory usage percentage")
    disk_usage_percent: float = Field(0.0, description="Disk usage percentage")
    active_connections: int = Field(0, description="Active connections")
    requests_per_second: float = Field(0.0, description="Requests per second")
    response_time_avg: float = Field(0.0, description="Average response time in ms")
    error_rate: float = Field(0.0, description="Error rate percentage")
    uptime_seconds: int = Field(0, description="System uptime in seconds")


class APIMetrics(BaseModel):
    """API-specific metrics"""
    total_requests: int = Field(0, description="Total API requests")
    successful_requests: int = Field(0, description="Successful requests")
    failed_requests: int = Field(0, description="Failed requests")
    avg_response_time: float = Field(0.0, description="Average response time")
    requests_by_endpoint: Dict[str, int] = Field(default_factory=dict, description="Requests by endpoint")
    requests_by_method: Dict[str, int] = Field(default_factory=dict, description="Requests by HTTP method")
    rate_limit_hits: int = Field(0, description="Rate limit hits")


class AgentMetrics(BaseModel):
    """Agent-specific metrics"""
    total_executions: int = Field(0, description="Total agent executions")
    successful_executions: int = Field(0, description="Successful executions")
    failed_executions: int = Field(0, description="Failed executions")
    avg_execution_time: float = Field(0.0, description="Average execution time")
    modifications_proposed: int = Field(0, description="Code modifications proposed")
    modifications_applied: int = Field(0, description="Code modifications applied")
    learning_cycles: int = Field(0, description="Learning cycles completed")
    optimization_opportunities: int = Field(0, description="Optimization opportunities identified")


class PulseMetrics(BaseModel):
    """Comprehensive pulse metrics"""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    system: SystemMetrics = Field(default_factory=SystemMetrics, description="System metrics")
    api: APIMetrics = Field(default_factory=APIMetrics, description="API metrics")
    agent: AgentMetrics = Field(default_factory=AgentMetrics, description="Agent metrics")
    events_count: int = Field(0, description="Total events in time window")
    active_sessions: int = Field(0, description="Active user sessions")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PulseDashboard(BaseModel):
    """Pulse dashboard data"""
    current_metrics: PulseMetrics = Field(..., description="Current metrics")
    historical_metrics: List[PulseMetrics] = Field(default_factory=list, description="Historical metrics")
    recent_events: List[PulseEvent] = Field(default_factory=list, description="Recent events")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active alerts")
    trends: Dict[str, Any] = Field(default_factory=dict, description="Trend analysis")
    uptime_percentage: float = Field(0.0, description="System uptime percentage")
    health_score: float = Field(0.0, description="Overall health score (0-100)")


class PulseConfig(BaseModel):
    """Pulse system configuration"""
    enabled: bool = Field(True, description="Enable pulse system")
    collection_interval: int = Field(30, description="Collection interval in seconds")
    retention_days: int = Field(7, description="Data retention in days")
    max_events_per_minute: int = Field(1000, description="Max events per minute")
    alert_thresholds: Dict[str, float] = Field(default_factory=dict, description="Alert thresholds")
    dashboard_refresh_interval: int = Field(5, description="Dashboard refresh interval in seconds")
    websocket_enabled: bool = Field(True, description="Enable WebSocket updates")
    log_level: str = Field("INFO", description="Logging level")


class PulseAlert(BaseModel):
    """Pulse alert"""
    id: str = Field(..., description="Alert ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Alert timestamp")
    severity: EventSeverity = Field(..., description="Alert severity")
    metric: str = Field(..., description="Metric that triggered alert")
    threshold: float = Field(..., description="Threshold value")
    current_value: float = Field(..., description="Current value")
    message: str = Field(..., description="Alert message")
    resolved: bool = Field(False, description="Whether alert is resolved")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }