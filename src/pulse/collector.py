"""
Pulse Data Collector

Collects system metrics, events, and performance data for the Pulse system.
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from threading import Lock
import uuid

from .models import (
    PulseEvent, PulseMetrics, SystemMetrics, APIMetrics, AgentMetrics,
    EventType, EventSeverity, PulseConfig
)

logger = logging.getLogger("apex_orchestrator.pulse.collector")


class PulseCollector:
    """Collects and manages pulse data"""
    
    def __init__(self, config: PulseConfig):
        self.config = config
        self.events: deque = deque(maxlen=config.max_events_per_minute * 60)  # 1 hour buffer
        self.metrics_history: deque = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.api_stats: Dict[str, Any] = defaultdict(int)
        self.agent_stats: Dict[str, Any] = defaultdict(int)
        self.session_tracker: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.lock = Lock()
        self.running = False
        self.collection_task: Optional[asyncio.Task] = None
        
        # Initialize default alert thresholds
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0,
            "error_rate": 10.0,
            "response_time_avg": 5000.0,
            "requests_per_second": 100.0
        }
        self.alert_thresholds.update(config.alert_thresholds)
    
    async def start(self):
        """Start the pulse collector"""
        if self.running:
            return
        
        self.running = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Pulse collector started")
    
    async def stop(self):
        """Stop the pulse collector"""
        self.running = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Pulse collector stopped")
    
    async def _collection_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.config.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _collect_metrics(self):
        """Collect current system metrics"""
        try:
            # System metrics
            system_metrics = SystemMetrics(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=psutil.virtual_memory().percent,
                disk_usage_percent=psutil.disk_usage('/').percent,
                active_connections=len(psutil.net_connections()),
                requests_per_second=self._calculate_rps(),
                response_time_avg=self._calculate_avg_response_time(),
                error_rate=self._calculate_error_rate(),
                uptime_seconds=int(time.time() - psutil.boot_time())
            )
            
            # API metrics
            api_metrics = APIMetrics(
                total_requests=self.api_stats.get('total_requests', 0),
                successful_requests=self.api_stats.get('successful_requests', 0),
                failed_requests=self.api_stats.get('failed_requests', 0),
                avg_response_time=self.api_stats.get('avg_response_time', 0.0),
                requests_by_endpoint=dict(self.api_stats.get('requests_by_endpoint', {})),
                requests_by_method=dict(self.api_stats.get('requests_by_method', {})),
                rate_limit_hits=self.api_stats.get('rate_limit_hits', 0)
            )
            
            # Agent metrics
            agent_metrics = AgentMetrics(
                total_executions=self.agent_stats.get('total_executions', 0),
                successful_executions=self.agent_stats.get('successful_executions', 0),
                failed_executions=self.agent_stats.get('failed_executions', 0),
                avg_execution_time=self.agent_stats.get('avg_execution_time', 0.0),
                modifications_proposed=self.agent_stats.get('modifications_proposed', 0),
                modifications_applied=self.agent_stats.get('modifications_applied', 0),
                learning_cycles=self.agent_stats.get('learning_cycles', 0),
                optimization_opportunities=self.agent_stats.get('optimization_opportunities', 0)
            )
            
            # Create comprehensive metrics
            pulse_metrics = PulseMetrics(
                system=system_metrics,
                api=api_metrics,
                agent=agent_metrics,
                events_count=len(self.events),
                active_sessions=len(self.session_tracker)
            )
            
            # Store metrics
            with self.lock:
                self.metrics_history.append(pulse_metrics)
            
            # Check for alerts
            await self._check_alerts(pulse_metrics)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def _calculate_rps(self) -> float:
        """Calculate requests per second"""
        with self.lock:
            recent_events = [e for e in self.events if 
                           e.event_type in [EventType.API_REQUEST, EventType.API_RESPONSE] and
                           (datetime.utcnow() - e.timestamp).total_seconds() < 60]
            return len(recent_events) / 60.0
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        with self.lock:
            response_events = [e for e in self.events if 
                             e.event_type == EventType.API_RESPONSE and e.duration_ms is not None]
            if not response_events:
                return 0.0
            return sum(e.duration_ms for e in response_events) / len(response_events)
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        with self.lock:
            recent_events = [e for e in self.events if 
                           (datetime.utcnow() - e.timestamp).total_seconds() < 300]  # 5 minutes
            if not recent_events:
                return 0.0
            
            error_events = [e for e in recent_events if e.event_type == EventType.ERROR]
            return (len(error_events) / len(recent_events)) * 100.0
    
    async def _check_alerts(self, metrics: PulseMetrics):
        """Check for alert conditions"""
        alerts_to_check = [
            ("cpu_percent", metrics.system.cpu_percent),
            ("memory_percent", metrics.system.memory_percent),
            ("disk_usage_percent", metrics.system.disk_usage_percent),
            ("error_rate", metrics.system.error_rate),
            ("response_time_avg", metrics.system.response_time_avg),
            ("requests_per_second", metrics.system.requests_per_second)
        ]
        
        for metric_name, current_value in alerts_to_check:
            threshold = self.alert_thresholds.get(metric_name, float('inf'))
            if current_value > threshold:
                await self._create_alert(metric_name, threshold, current_value)
    
    async def _create_alert(self, metric: str, threshold: float, current_value: float):
        """Create a new alert"""
        alert_id = str(uuid.uuid4())
        severity = EventSeverity.HIGH if current_value > threshold * 1.5 else EventSeverity.MEDIUM
        
        alert = {
            "id": alert_id,
            "timestamp": datetime.utcnow(),
            "severity": severity,
            "metric": metric,
            "threshold": threshold,
            "current_value": current_value,
            "message": f"{metric} exceeded threshold: {current_value:.2f} > {threshold:.2f}",
            "resolved": False
        }
        
        with self.lock:
            self.alerts.append(alert)
        
        logger.warning(f"Alert created: {alert['message']}")
    
    def record_event(self, event: PulseEvent):
        """Record a new event"""
        with self.lock:
            self.events.append(event)
        
        # Update statistics based on event type
        if event.event_type == EventType.API_REQUEST:
            self.api_stats['total_requests'] += 1
            endpoint = event.data.get('endpoint', 'unknown')
            method = event.data.get('method', 'unknown')
            self.api_stats['requests_by_endpoint'][endpoint] += 1
            self.api_stats['requests_by_method'][method] += 1
            
        elif event.event_type == EventType.API_RESPONSE:
            if event.data.get('status_code', 200) < 400:
                self.api_stats['successful_requests'] += 1
            else:
                self.api_stats['failed_requests'] += 1
            
            if event.duration_ms:
                # Update average response time
                current_avg = self.api_stats.get('avg_response_time', 0.0)
                total_requests = self.api_stats.get('total_requests', 1)
                self.api_stats['avg_response_time'] = (
                    (current_avg * (total_requests - 1) + event.duration_ms) / total_requests
                )
        
        elif event.event_type == EventType.AGENT_EXECUTION:
            self.agent_stats['total_executions'] += 1
            if event.data.get('success', False):
                self.agent_stats['successful_executions'] += 1
            else:
                self.agent_stats['failed_executions'] += 1
            
            if event.duration_ms:
                current_avg = self.agent_stats.get('avg_execution_time', 0.0)
                total_executions = self.agent_stats.get('total_executions', 1)
                self.agent_stats['avg_execution_time'] = (
                    (current_avg * (total_executions - 1) + event.duration_ms) / total_executions
                )
        
        elif event.event_type == EventType.ERROR:
            logger.error(f"Pulse recorded error: {event.message}")
    
    def get_recent_events(self, limit: int = 100) -> List[PulseEvent]:
        """Get recent events"""
        with self.lock:
            return list(self.events)[-limit:]
    
    def get_current_metrics(self) -> Optional[PulseMetrics]:
        """Get current metrics"""
        with self.lock:
            return self.metrics_history[-1] if self.metrics_history else None
    
    def get_historical_metrics(self, hours: int = 24) -> List[PulseMetrics]:
        """Get historical metrics for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        with self.lock:
            return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_alerts(self, unresolved_only: bool = True) -> List[Dict[str, Any]]:
        """Get alerts"""
        with self.lock:
            if unresolved_only:
                return [a for a in self.alerts if not a.get('resolved', False)]
            return list(self.alerts)
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        with self.lock:
            for alert in self.alerts:
                if alert['id'] == alert_id:
                    alert['resolved'] = True
                    alert['resolved_at'] = datetime.utcnow()
                    break
    
    def cleanup_old_data(self):
        """Clean up old data based on retention policy"""
        cutoff_time = datetime.utcnow() - timedelta(days=self.config.retention_days)
        
        with self.lock:
            # Clean up old events
            self.events = deque([e for e in self.events if e.timestamp >= cutoff_time], 
                              maxlen=self.events.maxlen)
            
            # Clean up old metrics
            self.metrics_history = deque([m for m in self.metrics_history if m.timestamp >= cutoff_time],
                                       maxlen=self.metrics_history.maxlen)
            
            # Clean up old alerts
            self.alerts = [a for a in self.alerts if a['timestamp'] >= cutoff_time]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        with self.lock:
            current_metrics = self.get_current_metrics()
            historical_metrics = list(self.metrics_history)[-60:]  # Last hour
            recent_events = self.get_recent_events(50)
            alerts = self.get_alerts(unresolved_only=True)
            
            # Calculate trends
            trends = self._calculate_trends(historical_metrics)
            
            # Calculate health score
            health_score = self._calculate_health_score(current_metrics)
            
            # Calculate uptime percentage
            uptime_percentage = self._calculate_uptime_percentage()
            
            return {
                "current_metrics": current_metrics,
                "historical_metrics": historical_metrics,
                "recent_events": recent_events,
                "alerts": alerts,
                "trends": trends,
                "health_score": health_score,
                "uptime_percentage": uptime_percentage
            }
    
    def _calculate_trends(self, historical_metrics: List[PulseMetrics]) -> Dict[str, Any]:
        """Calculate trend analysis"""
        if len(historical_metrics) < 2:
            return {}
        
        trends = {}
        latest = historical_metrics[-1]
        previous = historical_metrics[-2]
        
        # Calculate percentage changes
        trends['cpu_trend'] = self._calculate_percentage_change(
            previous.system.cpu_percent, latest.system.cpu_percent
        )
        trends['memory_trend'] = self._calculate_percentage_change(
            previous.system.memory_percent, latest.system.memory_percent
        )
        trends['response_time_trend'] = self._calculate_percentage_change(
            previous.system.response_time_avg, latest.system.response_time_avg
        )
        trends['error_rate_trend'] = self._calculate_percentage_change(
            previous.system.error_rate, latest.system.error_rate
        )
        
        return trends
    
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        return ((new_value - old_value) / old_value) * 100.0
    
    def _calculate_health_score(self, metrics: Optional[PulseMetrics]) -> float:
        """Calculate overall health score (0-100)"""
        if not metrics:
            return 0.0
        
        score = 100.0
        
        # Deduct points for high resource usage
        if metrics.system.cpu_percent > 80:
            score -= (metrics.system.cpu_percent - 80) * 0.5
        if metrics.system.memory_percent > 80:
            score -= (metrics.system.memory_percent - 80) * 0.5
        if metrics.system.disk_usage_percent > 90:
            score -= (metrics.system.disk_usage_percent - 90) * 0.5
        
        # Deduct points for high error rate
        if metrics.system.error_rate > 5:
            score -= metrics.system.error_rate * 2
        
        # Deduct points for slow response times
        if metrics.system.response_time_avg > 1000:
            score -= (metrics.system.response_time_avg - 1000) / 100
        
        return max(0.0, min(100.0, score))
    
    def _calculate_uptime_percentage(self) -> float:
        """Calculate system uptime percentage"""
        try:
            boot_time = psutil.boot_time()
            current_time = time.time()
            total_time = current_time - boot_time
            
            # This is a simplified calculation - in production you'd want to track
            # actual service uptime vs downtime
            return 99.9  # Placeholder - would need actual uptime tracking
        except:
            return 0.0