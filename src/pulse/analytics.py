"""
Pulse Analytics Engine

Analyzes collected pulse data to provide insights, patterns, and recommendations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics

from .models import PulseEvent, PulseMetrics, EventType, EventSeverity

logger = logging.getLogger("apex_orchestrator.pulse.analytics")


class PulseAnalytics:
    """Analytics engine for pulse data"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_performance_trends(self, metrics_history: List[PulseMetrics]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(metrics_history) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        analysis = {
            "time_range": {
                "start": metrics_history[0].timestamp.isoformat(),
                "end": metrics_history[-1].timestamp.isoformat(),
                "duration_hours": (metrics_history[-1].timestamp - metrics_history[0].timestamp).total_seconds() / 3600
            },
            "trends": {},
            "insights": [],
            "recommendations": []
        }
        
        # Extract time series data
        timestamps = [m.timestamp for m in metrics_history]
        cpu_data = [m.system.cpu_percent for m in metrics_history]
        memory_data = [m.system.memory_percent for m in metrics_history]
        response_time_data = [m.system.response_time_avg for m in metrics_history]
        error_rate_data = [m.system.error_rate for m in metrics_history]
        rps_data = [m.system.requests_per_second for m in metrics_history]
        
        # Analyze CPU trends
        analysis["trends"]["cpu"] = self._analyze_metric_trend(
            "CPU Usage", cpu_data, timestamps, threshold=80.0
        )
        
        # Analyze memory trends
        analysis["trends"]["memory"] = self._analyze_metric_trend(
            "Memory Usage", memory_data, timestamps, threshold=85.0
        )
        
        # Analyze response time trends
        analysis["trends"]["response_time"] = self._analyze_metric_trend(
            "Response Time", response_time_data, timestamps, threshold=1000.0
        )
        
        # Analyze error rate trends
        analysis["trends"]["error_rate"] = self._analyze_metric_trend(
            "Error Rate", error_rate_data, timestamps, threshold=5.0
        )
        
        # Analyze request patterns
        analysis["trends"]["requests"] = self._analyze_request_patterns(rps_data, timestamps)
        
        # Generate insights
        analysis["insights"] = self._generate_insights(analysis["trends"])
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis["trends"])
        
        return analysis
    
    def _analyze_metric_trend(self, name: str, data: List[float], timestamps: List[datetime], 
                            threshold: float) -> Dict[str, Any]:
        """Analyze trend for a specific metric"""
        if not data:
            return {"error": f"No data for {name}"}
        
        # Basic statistics
        current_value = data[-1]
        min_value = min(data)
        max_value = max(data)
        avg_value = statistics.mean(data)
        median_value = statistics.median(data)
        
        # Trend direction
        if len(data) >= 2:
            recent_avg = statistics.mean(data[-5:]) if len(data) >= 5 else data[-1]
            earlier_avg = statistics.mean(data[:5]) if len(data) >= 5 else data[0]
            trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing"
            trend_strength = abs(recent_avg - earlier_avg) / earlier_avg * 100 if earlier_avg > 0 else 0
        else:
            trend_direction = "stable"
            trend_strength = 0
        
        # Threshold analysis
        above_threshold_count = sum(1 for v in data if v > threshold)
        threshold_percentage = (above_threshold_count / len(data)) * 100
        
        # Peak analysis
        peaks = self._find_peaks(data)
        
        return {
            "name": name,
            "current": current_value,
            "min": min_value,
            "max": max_value,
            "average": avg_value,
            "median": median_value,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "above_threshold_percentage": threshold_percentage,
            "peaks": peaks,
            "status": "critical" if current_value > threshold else "normal"
        }
    
    def _analyze_request_patterns(self, rps_data: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze request patterns"""
        if not rps_data:
            return {"error": "No request data available"}
        
        # Peak hours analysis
        hourly_rps = defaultdict(list)
        for i, timestamp in enumerate(timestamps):
            hour = timestamp.hour
            hourly_rps[hour].append(rps_data[i])
        
        peak_hours = []
        for hour, values in hourly_rps.items():
            avg_rps = statistics.mean(values)
            if avg_rps > statistics.mean(rps_data) * 1.2:  # 20% above average
                peak_hours.append({"hour": hour, "avg_rps": avg_rps})
        
        peak_hours.sort(key=lambda x: x["avg_rps"], reverse=True)
        
        return {
            "current_rps": rps_data[-1],
            "average_rps": statistics.mean(rps_data),
            "max_rps": max(rps_data),
            "peak_hours": peak_hours[:5],  # Top 5 peak hours
            "pattern": "stable" if len(set(round(x) for x in rps_data)) < len(rps_data) * 0.1 else "variable"
        }
    
    def _find_peaks(self, data: List[float], threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Find peaks in the data"""
        if len(data) < 3:
            return []
        
        peaks = []
        avg_value = statistics.mean(data)
        
        for i in range(1, len(data) - 1):
            if (data[i] > data[i-1] and data[i] > data[i+1] and 
                data[i] > avg_value * (1 + threshold)):
                peaks.append({
                    "index": i,
                    "value": data[i],
                    "significance": (data[i] - avg_value) / avg_value * 100
                })
        
        return sorted(peaks, key=lambda x: x["significance"], reverse=True)[:5]
    
    def _generate_insights(self, trends: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis"""
        insights = []
        
        for metric_name, trend_data in trends.items():
            if isinstance(trend_data, dict) and "error" not in trend_data:
                if trend_data.get("status") == "critical":
                    insights.append(f"⚠️ {trend_data['name']} is currently critical at {trend_data['current']:.1f}%")
                
                if trend_data.get("above_threshold_percentage", 0) > 50:
                    insights.append(f"📈 {trend_data['name']} frequently exceeds threshold ({trend_data['above_threshold_percentage']:.1f}% of time)")
                
                if trend_data.get("trend_direction") == "increasing" and trend_data.get("trend_strength", 0) > 20:
                    insights.append(f"📊 {trend_data['name']} shows strong upward trend ({trend_data['trend_strength']:.1f}% increase)")
                
                if trend_data.get("peaks") and len(trend_data["peaks"]) > 3:
                    insights.append(f"🔍 {trend_data['name']} shows irregular patterns with {len(trend_data['peaks'])} significant peaks")
        
        return insights
    
    def _generate_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on trend analysis"""
        recommendations = []
        
        # CPU recommendations
        cpu_trend = trends.get("cpu", {})
        if cpu_trend.get("status") == "critical":
            recommendations.append("🚀 Consider scaling up CPU resources or optimizing CPU-intensive operations")
        elif cpu_trend.get("trend_direction") == "increasing" and cpu_trend.get("trend_strength", 0) > 10:
            recommendations.append("📊 Monitor CPU usage closely - upward trend detected")
        
        # Memory recommendations
        memory_trend = trends.get("memory", {})
        if memory_trend.get("status") == "critical":
            recommendations.append("💾 Consider increasing memory allocation or optimizing memory usage")
        elif memory_trend.get("above_threshold_percentage", 0) > 30:
            recommendations.append("🔍 Investigate memory leaks or inefficient memory usage patterns")
        
        # Response time recommendations
        response_trend = trends.get("response_time", {})
        if response_trend.get("status") == "critical":
            recommendations.append("⚡ Optimize database queries, add caching, or scale backend services")
        elif response_trend.get("trend_direction") == "increasing":
            recommendations.append("📈 Monitor response times - degradation trend detected")
        
        # Error rate recommendations
        error_trend = trends.get("error_rate", {})
        if error_trend.get("status") == "critical":
            recommendations.append("🐛 Investigate and fix critical errors immediately")
        elif error_trend.get("above_threshold_percentage", 0) > 20:
            recommendations.append("🔧 Review error handling and improve system reliability")
        
        # Request pattern recommendations
        request_trend = trends.get("requests", {})
        if request_trend.get("pattern") == "variable" and request_trend.get("max_rps", 0) > request_trend.get("average_rps", 0) * 2:
            recommendations.append("📊 Consider implementing auto-scaling for variable load patterns")
        
        return recommendations
    
    def analyze_event_patterns(self, events: List[PulseEvent]) -> Dict[str, Any]:
        """Analyze patterns in events"""
        if not events:
            return {"error": "No events to analyze"}
        
        analysis = {
            "summary": {},
            "patterns": {},
            "insights": [],
            "recommendations": []
        }
        
        # Event type distribution
        event_types = Counter(e.event_type for e in events)
        analysis["summary"]["event_types"] = dict(event_types)
        
        # Severity distribution
        severities = Counter(e.severity for e in events)
        analysis["summary"]["severities"] = dict(severities)
        
        # Source distribution
        sources = Counter(e.source for e in events)
        analysis["summary"]["sources"] = dict(sources)
        
        # Time-based patterns
        hourly_events = defaultdict(int)
        for event in events:
            hourly_events[event.timestamp.hour] += 1
        
        analysis["patterns"]["hourly_distribution"] = dict(hourly_events)
        
        # Error analysis
        error_events = [e for e in events if e.event_type == EventType.ERROR]
        if error_events:
            error_sources = Counter(e.source for e in error_events)
            analysis["patterns"]["error_sources"] = dict(error_sources)
            
            # Most common error messages
            error_messages = Counter(e.message for e in error_events)
            analysis["patterns"]["common_errors"] = dict(error_messages.most_common(10))
        
        # Performance events
        perf_events = [e for e in events if e.event_type == EventType.PERFORMANCE]
        if perf_events:
            slow_events = [e for e in perf_events if e.duration_ms and e.duration_ms > 1000]
            analysis["patterns"]["slow_operations"] = len(slow_events)
            
            if slow_events:
                slow_sources = Counter(e.source for e in slow_events)
                analysis["patterns"]["slow_sources"] = dict(slow_sources)
        
        # Generate insights
        analysis["insights"] = self._generate_event_insights(analysis)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_event_recommendations(analysis)
        
        return analysis
    
    def _generate_event_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from event analysis"""
        insights = []
        
        # Error insights
        if analysis["summary"]["severities"].get(EventSeverity.CRITICAL, 0) > 0:
            insights.append(f"🚨 {analysis['summary']['severities'][EventSeverity.CRITICAL]} critical events detected")
        
        if analysis["summary"]["severities"].get(EventSeverity.HIGH, 0) > 10:
            insights.append(f"⚠️ High number of high-severity events: {analysis['summary']['severities'][EventSeverity.HIGH]}")
        
        # Performance insights
        if analysis["patterns"].get("slow_operations", 0) > 0:
            insights.append(f"🐌 {analysis['patterns']['slow_operations']} slow operations detected (>1s)")
        
        # Source insights
        sources = analysis["summary"]["sources"]
        if len(sources) > 1:
            top_source = max(sources, key=sources.get)
            insights.append(f"📊 Most active source: {top_source} ({sources[top_source]} events)")
        
        return insights
    
    def _generate_event_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations from event analysis"""
        recommendations = []
        
        # Error recommendations
        if analysis["summary"]["severities"].get(EventSeverity.CRITICAL, 0) > 0:
            recommendations.append("🚨 Investigate and resolve critical events immediately")
        
        if analysis["patterns"].get("common_errors"):
            recommendations.append("🔧 Focus on fixing the most common error patterns")
        
        # Performance recommendations
        if analysis["patterns"].get("slow_operations", 0) > 5:
            recommendations.append("⚡ Optimize slow operations to improve performance")
        
        if analysis["patterns"].get("slow_sources"):
            top_slow_source = max(analysis["patterns"]["slow_sources"], key=analysis["patterns"]["slow_sources"].get)
            recommendations.append(f"🎯 Focus optimization efforts on {top_slow_source}")
        
        return recommendations
    
    def generate_health_report(self, metrics: PulseMetrics, events: List[PulseEvent]) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": "unknown",
            "health_score": 0,
            "metrics": {},
            "events": {},
            "recommendations": []
        }
        
        # Calculate health score
        health_score = self._calculate_health_score(metrics)
        report["health_score"] = health_score
        
        # Determine overall health
        if health_score >= 90:
            report["overall_health"] = "excellent"
        elif health_score >= 75:
            report["overall_health"] = "good"
        elif health_score >= 50:
            report["overall_health"] = "fair"
        else:
            report["overall_health"] = "poor"
        
        # Analyze metrics
        report["metrics"] = {
            "cpu_status": "critical" if metrics.system.cpu_percent > 80 else "normal",
            "memory_status": "critical" if metrics.system.memory_percent > 85 else "normal",
            "response_time_status": "critical" if metrics.system.response_time_avg > 1000 else "normal",
            "error_rate_status": "critical" if metrics.system.error_rate > 5 else "normal"
        }
        
        # Analyze events
        recent_errors = [e for e in events if e.event_type == EventType.ERROR and 
                        (datetime.utcnow() - e.timestamp).total_seconds() < 3600]
        
        report["events"] = {
            "recent_errors": len(recent_errors),
            "error_rate": len(recent_errors) / max(1, len(events)) * 100,
            "critical_events": len([e for e in recent_errors if e.severity == EventSeverity.CRITICAL])
        }
        
        # Generate recommendations
        recommendations = []
        if metrics.system.cpu_percent > 80:
            recommendations.append("Scale up CPU resources")
        if metrics.system.memory_percent > 85:
            recommendations.append("Increase memory allocation")
        if metrics.system.response_time_avg > 1000:
            recommendations.append("Optimize response times")
        if metrics.system.error_rate > 5:
            recommendations.append("Investigate and fix errors")
        
        report["recommendations"] = recommendations
        
        return report
    
    def _calculate_health_score(self, metrics: PulseMetrics) -> float:
        """Calculate health score based on metrics"""
        score = 100.0
        
        # Deduct for high resource usage
        if metrics.system.cpu_percent > 80:
            score -= (metrics.system.cpu_percent - 80) * 0.5
        if metrics.system.memory_percent > 85:
            score -= (metrics.system.memory_percent - 85) * 0.5
        if metrics.system.disk_usage_percent > 90:
            score -= (metrics.system.disk_usage_percent - 90) * 0.5
        
        # Deduct for high error rate
        if metrics.system.error_rate > 5:
            score -= metrics.system.error_rate * 2
        
        # Deduct for slow response times
        if metrics.system.response_time_avg > 1000:
            score -= (metrics.system.response_time_avg - 1000) / 100
        
        return max(0.0, min(100.0, score))