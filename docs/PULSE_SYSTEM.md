# Apex Orchestrator Pulse System

A comprehensive real-time monitoring and analytics system similar to ChatGPT Pulse, designed to track system activity, performance metrics, and provide actionable insights.

## Overview

The Pulse system provides:
- **Real-time Monitoring**: Track API calls, tool executions, and system metrics
- **Performance Analytics**: Analyze trends, identify bottlenecks, and generate insights
- **Interactive Dashboard**: Web-based dashboard with charts and real-time updates
- **Alert System**: Configurable alerts for critical conditions
- **WebSocket Support**: Real-time updates for connected clients

## Features

### 📊 Real-time Metrics
- CPU, memory, and disk usage monitoring
- API request/response tracking
- Tool execution performance
- Error rate monitoring
- System uptime tracking

### 📈 Analytics Engine
- Performance trend analysis
- Event pattern recognition
- Health score calculation
- Optimization recommendations
- Historical data analysis

### 🎛️ Interactive Dashboard
- Real-time metrics visualization
- Interactive charts and graphs
- Event timeline
- Alert management
- Export capabilities

### 🔔 Alert System
- Configurable thresholds
- Multiple severity levels
- Real-time notifications
- Alert resolution tracking

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Pulse Data    │    │   Pulse         │    │   Pulse         │
│   Models        │    │   Collector     │    │   Analytics     │
│                 │    │                 │    │                 │
│ • PulseEvent    │───▶│ • System        │───▶│ • Trend         │
│ • PulseMetrics  │    │   Monitoring    │    │   Analysis      │
│ • PulseConfig   │    │ • Event         │    │ • Pattern       │
│ • EventType     │    │   Recording     │    │   Recognition   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Pulse         │
                       │   Dashboard     │
                       │                 │
                       │ • REST API      │
                       │ • WebSocket     │
                       │ • HTML UI       │
                       └─────────────────┘
```

## API Endpoints

### Dashboard
- `GET /pulse/dashboard` - Get comprehensive dashboard data
- `GET /pulse/dashboard.html` - HTML dashboard interface
- `GET /pulse/status` - Pulse system status

### Metrics
- `GET /pulse/metrics/current` - Current system metrics
- `GET /pulse/metrics/historical` - Historical metrics (1-168 hours)

### Events
- `GET /pulse/events/recent` - Recent events (limit: 1-1000)
- `GET /pulse/events/filtered` - Filtered events by type, severity, source

### Alerts
- `GET /pulse/alerts` - Get alerts (resolved/unresolved)
- `POST /pulse/alerts/{alert_id}/resolve` - Resolve an alert

### Analytics
- `GET /pulse/analytics/trends` - Performance trend analysis
- `GET /pulse/analytics/events` - Event pattern analysis
- `GET /pulse/health-report` - Comprehensive health report

### WebSocket
- `WS /pulse/ws` - Real-time updates

## Configuration

The Pulse system is configured via `config/pulse.yaml`:

```yaml
# System Settings
enabled: true
collection_interval: 30  # seconds
retention_days: 7
max_events_per_minute: 1000

# Alert Thresholds
alert_thresholds:
  cpu_percent: 80.0
  memory_percent: 85.0
  error_rate: 10.0
  response_time_avg: 5000.0

# Event Filtering
event_filters:
  min_severity: "low"
  track_event_types:
    - "api_request"
    - "api_response"
    - "agent_execution"
    - "tool_execution"
    - "error"
```

## Event Types

### API Events
- `api_request` - API request received
- `api_response` - API response sent

### Agent Events
- `agent_execution` - Agent operation performed
- `agent_learning` - Learning cycle completed
- `agent_modification` - Code modification applied

### Tool Events
- `tool_execution` - Tool execution completed
- `tool_error` - Tool execution failed

### System Events
- `system_metric` - System metric collected
- `performance` - Performance measurement
- `error` - Error occurred

## Severity Levels

- `low` - Informational events
- `medium` - Warning conditions
- `high` - Error conditions
- `critical` - System-threatening conditions

## Dashboard Usage

### Accessing the Dashboard

1. **Web Interface**: Navigate to `http://localhost:8000/pulse/dashboard.html`
2. **API**: Use `GET /pulse/dashboard` for programmatic access
3. **WebSocket**: Connect to `ws://localhost:8000/pulse/ws` for real-time updates

### Dashboard Features

#### Metrics Cards
- **CPU Usage**: Current CPU utilization percentage
- **Memory Usage**: Current memory utilization percentage
- **Response Time**: Average API response time
- **Error Rate**: Current error rate percentage
- **Requests/sec**: Current request rate
- **Health Score**: Overall system health (0-100)

#### Charts
- **Performance Trends**: CPU and memory usage over time
- **Response Time**: API response time trends
- **Error Patterns**: Error frequency and types

#### Event Timeline
- Recent events with timestamps
- Event severity indicators
- Source and type information

### Real-time Updates

The dashboard automatically refreshes every 30 seconds. For real-time updates:

1. **WebSocket Connection**: Connect to `/pulse/ws` for live updates
2. **Manual Refresh**: Click the "Refresh" button
3. **Auto-refresh**: Dashboard updates automatically

## Alert Management

### Alert Conditions

Alerts are triggered when metrics exceed configured thresholds:

- **CPU Usage** > 80%
- **Memory Usage** > 85%
- **Error Rate** > 10%
- **Response Time** > 5000ms
- **Disk Usage** > 90%

### Alert Severity

- **High**: Critical system conditions
- **Medium**: Warning conditions
- **Low**: Informational alerts

### Resolving Alerts

1. **Via API**: `POST /pulse/alerts/{alert_id}/resolve`
2. **Via Dashboard**: Click "Resolve" on alert cards
3. **Automatic**: Alerts auto-resolve when conditions improve

## Integration

### Recording Custom Events

```python
from pulse import record_pulse_event, PulseEvent, EventType, EventSeverity

# Record a custom event
event = PulseEvent(
    id="custom_event_123",
    event_type=EventType.USER_ACTION,
    source="custom_module",
    message="Custom action performed",
    data={"action": "custom_action", "value": 42},
    severity=EventSeverity.LOW
)
record_pulse_event(event)
```

### WebSocket Integration

```javascript
// Connect to Pulse WebSocket
const ws = new WebSocket('ws://localhost:8000/pulse/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Pulse update:', data);
};

ws.onopen = function() {
    console.log('Connected to Pulse WebSocket');
};
```

## Performance Considerations

### Data Retention
- Events: 1 hour buffer (configurable)
- Metrics: 24 hours at 1-minute intervals
- Historical data: 7 days (configurable)

### Rate Limiting
- Dashboard API: 20-30 requests/minute
- WebSocket: 100 concurrent connections
- Event recording: 1000 events/minute

### Resource Usage
- Memory: ~50MB for 24 hours of data
- CPU: <1% during normal operation
- Disk: ~10MB/day for logs and metrics

## Troubleshooting

### Common Issues

#### Pulse System Not Starting
```bash
# Check configuration
python -c "from src.pulse.models import PulseConfig; print(PulseConfig())"

# Check logs
tail -f logs/apex_orchestrator.log | grep -i pulse
```

#### Dashboard Not Loading
```bash
# Check if Pulse routes are registered
curl http://localhost:8000/pulse/status

# Check WebSocket connection
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" http://localhost:8000/pulse/ws
```

#### Missing Metrics
```bash
# Check if data collection is running
curl http://localhost:8000/pulse/metrics/current

# Check event recording
curl http://localhost:8000/pulse/events/recent?limit=10
```

### Debug Mode

Enable debug logging by setting `log_level: "DEBUG"` in `config/pulse.yaml`.

## Security

### Access Control
- Dashboard access: No authentication required by default
- API endpoints: Rate limited
- WebSocket: No authentication required

### Data Privacy
- No sensitive data stored in events
- Configurable data retention
- Automatic cleanup of old data

## Monitoring Best Practices

### Key Metrics to Watch
1. **Health Score**: Overall system health indicator
2. **Error Rate**: Should stay below 5%
3. **Response Time**: Should stay below 1000ms
4. **Resource Usage**: CPU < 80%, Memory < 85%

### Alert Thresholds
- Set conservative thresholds initially
- Adjust based on normal operating patterns
- Monitor alert frequency and adjust accordingly

### Regular Maintenance
- Review and resolve alerts promptly
- Monitor data retention and cleanup
- Check dashboard performance regularly

## Future Enhancements

### Planned Features
- **Custom Dashboards**: User-configurable dashboard layouts
- **Advanced Analytics**: Machine learning-based insights
- **Integration APIs**: Third-party monitoring tool integration
- **Mobile Dashboard**: Mobile-optimized interface
- **Historical Reporting**: Automated report generation

### Extensibility
- Custom event types
- Custom metrics collectors
- Custom alert handlers
- Custom dashboard widgets

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `logs/apex_orchestrator.log`
3. Check Pulse system status: `GET /pulse/status`
4. Contact the development team for critical issues