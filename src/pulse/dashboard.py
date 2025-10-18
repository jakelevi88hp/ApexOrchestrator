"""
Pulse Dashboard API

Provides REST API endpoints for the Pulse dashboard and real-time monitoring.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from .models import PulseEvent, PulseMetrics, PulseDashboard, PulseConfig
from .collector import PulseCollector
from .analytics import PulseAnalytics

logger = logging.getLogger("apex_orchestrator.pulse.dashboard")

# Create router
router = APIRouter(prefix="/pulse", tags=["Pulse Dashboard"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global instances
pulse_collector: Optional[PulseCollector] = None
pulse_analytics = PulseAnalytics()
websocket_connections: List[WebSocket] = []


def initialize_pulse(config: PulseConfig):
    """Initialize pulse system"""
    global pulse_collector
    pulse_collector = PulseCollector(config)
    asyncio.create_task(pulse_collector.start())


async def cleanup_pulse():
    """Cleanup pulse system"""
    global pulse_collector
    if pulse_collector:
        await pulse_collector.stop()


@router.get("/status")
@limiter.limit("30/minute")
async def get_pulse_status(request: Request):
    """Get pulse system status"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    return {
        "status": "running" if pulse_collector.running else "stopped",
        "events_count": len(pulse_collector.events),
        "metrics_count": len(pulse_collector.metrics_history),
        "alerts_count": len(pulse_collector.get_alerts(unresolved_only=True))
    }


@router.get("/dashboard")
@limiter.limit("20/minute")
async def get_dashboard_data(request: Request):
    """Get comprehensive dashboard data"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    try:
        dashboard_data = pulse_collector.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(500, "Failed to retrieve dashboard data")


@router.get("/metrics/current")
@limiter.limit("30/minute")
async def get_current_metrics(request: Request):
    """Get current system metrics"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    metrics = pulse_collector.get_current_metrics()
    if not metrics:
        raise HTTPException(404, "No metrics available")
    
    return metrics


@router.get("/metrics/historical")
@limiter.limit("20/minute")
async def get_historical_metrics(request: Request, hours: int = 24):
    """Get historical metrics"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    if hours < 1 or hours > 168:  # Max 1 week
        raise HTTPException(400, "Hours must be between 1 and 168")
    
    metrics = pulse_collector.get_historical_metrics(hours)
    return {
        "count": len(metrics),
        "time_range_hours": hours,
        "metrics": metrics
    }


@router.get("/events/recent")
@limiter.limit("30/minute")
async def get_recent_events(request: Request, limit: int = 100):
    """Get recent events"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    if limit < 1 or limit > 1000:
        raise HTTPException(400, "Limit must be between 1 and 1000")
    
    events = pulse_collector.get_recent_events(limit)
    return {
        "count": len(events),
        "events": events
    }


@router.get("/events/filtered")
@limiter.limit("20/minute")
async def get_filtered_events(
    request: Request,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    source: Optional[str] = None,
    hours: int = 24,
    limit: int = 100
):
    """Get filtered events"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    with pulse_collector.lock:
        filtered_events = []
        for event in pulse_collector.events:
            if event.timestamp < cutoff_time:
                continue
            
            if event_type and event.event_type != event_type:
                continue
            if severity and event.severity != severity:
                continue
            if source and event.source != source:
                continue
            
            filtered_events.append(event)
            
            if len(filtered_events) >= limit:
                break
    
    return {
        "count": len(filtered_events),
        "filters": {
            "event_type": event_type,
            "severity": severity,
            "source": source,
            "hours": hours
        },
        "events": filtered_events
    }


@router.get("/alerts")
@limiter.limit("30/minute")
async def get_alerts(request: Request, unresolved_only: bool = True):
    """Get alerts"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    alerts = pulse_collector.get_alerts(unresolved_only=unresolved_only)
    return {
        "count": len(alerts),
        "alerts": alerts
    }


@router.post("/alerts/{alert_id}/resolve")
@limiter.limit("10/minute")
async def resolve_alert(request: Request, alert_id: str):
    """Resolve an alert"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    pulse_collector.resolve_alert(alert_id)
    return {"message": f"Alert {alert_id} resolved"}


@router.get("/analytics/trends")
@limiter.limit("10/minute")
async def get_trend_analysis(request: Request, hours: int = 24):
    """Get trend analysis"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    metrics = pulse_collector.get_historical_metrics(hours)
    if len(metrics) < 2:
        raise HTTPException(400, "Insufficient data for trend analysis")
    
    analysis = pulse_analytics.analyze_performance_trends(metrics)
    return analysis


@router.get("/analytics/events")
@limiter.limit("10/minute")
async def get_event_analysis(request: Request, hours: int = 24):
    """Get event pattern analysis"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    with pulse_collector.lock:
        recent_events = [e for e in pulse_collector.events if e.timestamp >= cutoff_time]
    
    analysis = pulse_analytics.analyze_event_patterns(recent_events)
    return analysis


@router.get("/health-report")
@limiter.limit("5/minute")
async def get_health_report(request: Request):
    """Get comprehensive health report"""
    if not pulse_collector:
        raise HTTPException(503, "Pulse system not initialized")
    
    current_metrics = pulse_collector.get_current_metrics()
    recent_events = pulse_collector.get_recent_events(100)
    
    if not current_metrics:
        raise HTTPException(404, "No metrics available")
    
    report = pulse_analytics.generate_health_report(current_metrics, recent_events)
    return report


@router.get("/dashboard.html")
async def get_dashboard_html(request: Request):
    """Get HTML dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Apex Orchestrator Pulse Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric-value { font-size: 2em; font-weight: bold; color: #2c3e50; }
            .metric-label { color: #7f8c8d; margin-top: 5px; }
            .chart-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .status-good { color: #27ae60; }
            .status-warning { color: #f39c12; }
            .status-critical { color: #e74c3c; }
            .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
            .refresh-btn:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Apex Orchestrator Pulse Dashboard</h1>
                <p>Real-time system monitoring and analytics</p>
                <button class="refresh-btn" onclick="refreshDashboard()">Refresh</button>
            </div>
            
            <div class="metrics-grid" id="metricsGrid">
                <!-- Metrics will be populated here -->
            </div>
            
            <div class="chart-container">
                <h3>System Performance Trends</h3>
                <canvas id="performanceChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>Recent Events</h3>
                <div id="eventsList">
                    <!-- Events will be populated here -->
                </div>
            </div>
        </div>

        <script>
            let performanceChart;
            
            async function refreshDashboard() {
                try {
                    const response = await fetch('/pulse/dashboard');
                    const data = await response.json();
                    updateMetrics(data);
                    updateChart(data);
                    updateEvents(data);
                } catch (error) {
                    console.error('Error refreshing dashboard:', error);
                }
            }
            
            function updateMetrics(data) {
                const metricsGrid = document.getElementById('metricsGrid');
                const metrics = data.current_metrics;
                
                if (!metrics) return;
                
                metricsGrid.innerHTML = `
                    <div class="metric-card">
                        <div class="metric-value ${getStatusClass(metrics.system.cpu_percent, 80)}">${metrics.system.cpu_percent.toFixed(1)}%</div>
                        <div class="metric-label">CPU Usage</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value ${getStatusClass(metrics.system.memory_percent, 85)}">${metrics.system.memory_percent.toFixed(1)}%</div>
                        <div class="metric-label">Memory Usage</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value ${getStatusClass(metrics.system.response_time_avg, 1000)}">${metrics.system.response_time_avg.toFixed(0)}ms</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value ${getStatusClass(metrics.system.error_rate, 5)}">${metrics.system.error_rate.toFixed(2)}%</div>
                        <div class="metric-label">Error Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${metrics.system.requests_per_second.toFixed(1)}</div>
                        <div class="metric-label">Requests/sec</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.health_score.toFixed(0)}</div>
                        <div class="metric-label">Health Score</div>
                    </div>
                `;
            }
            
            function getStatusClass(value, threshold) {
                if (value > threshold) return 'status-critical';
                if (value > threshold * 0.8) return 'status-warning';
                return 'status-good';
            }
            
            function updateChart(data) {
                const ctx = document.getElementById('performanceChart').getContext('2d');
                
                if (performanceChart) {
                    performanceChart.destroy();
                }
                
                const historical = data.historical_metrics || [];
                const labels = historical.map(m => new Date(m.timestamp).toLocaleTimeString());
                const cpuData = historical.map(m => m.system.cpu_percent);
                const memoryData = historical.map(m => m.system.memory_percent);
                
                performanceChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'CPU %',
                            data: cpuData,
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            tension: 0.4
                        }, {
                            label: 'Memory %',
                            data: memoryData,
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }
            
            function updateEvents(data) {
                const eventsList = document.getElementById('eventsList');
                const events = data.recent_events || [];
                
                eventsList.innerHTML = events.slice(0, 10).map(event => `
                    <div style="padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;">
                        <div>
                            <strong>${event.event_type}</strong> - ${event.message}
                            <br><small>${event.source} • ${new Date(event.timestamp).toLocaleString()}</small>
                        </div>
                        <div class="${getSeverityClass(event.severity)}">${event.severity.toUpperCase()}</div>
                    </div>
                `).join('');
            }
            
            function getSeverityClass(severity) {
                switch(severity) {
                    case 'critical': return 'status-critical';
                    case 'high': return 'status-warning';
                    default: return 'status-good';
                }
            }
            
            // Initial load and auto-refresh
            refreshDashboard();
            setInterval(refreshDashboard, 30000); // Refresh every 30 seconds
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Send periodic updates
            if pulse_collector:
                dashboard_data = pulse_collector.get_dashboard_data()
                await websocket.send_text(json.dumps(dashboard_data, default=str))
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


async def broadcast_update(data: Dict[str, Any]):
    """Broadcast update to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    message = json.dumps(data, default=str)
    disconnected = []
    
    for websocket in websocket_connections:
        try:
            await websocket.send_text(message)
        except:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for websocket in disconnected:
        websocket_connections.remove(websocket)


def record_pulse_event(event: PulseEvent):
    """Record a pulse event"""
    if pulse_collector:
        pulse_collector.record_event(event)
        
        # Broadcast update to WebSocket clients
        asyncio.create_task(broadcast_update({
            "type": "event",
            "data": event.dict()
        }))