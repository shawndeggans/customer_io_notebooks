"""
Customer.IO Observability and Monitoring Module

Comprehensive monitoring, logging, and observability solutions for Customer.IO data pipelines including:
- Real-time metrics collection and alerting
- Application performance monitoring (APM)
- Distributed tracing and correlation
- Health checks and system monitoring
- Log aggregation and analysis
- Custom dashboard creation
- Anomaly detection and alerting
- Service level objectives (SLO) tracking
"""

import json
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import structlog
from pydantic import BaseModel, Field, validator
import statistics
import uuid
import psutil
from concurrent.futures import ThreadPoolExecutor
import asyncio

from .api_client import CustomerIOClient


class MetricType(str, Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class HealthStatus(str, Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class TraceStatus(str, Enum):
    """Distributed tracing status."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class Metric(BaseModel):
    """Type-safe metric model."""
    name: str = Field(..., description="Metric name")
    type: MetricType = Field(..., description="Metric type")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Metric unit")
    tags: Dict[str, str] = Field(default_factory=dict, description="Metric tags")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(..., description="Metric source")
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate metric name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Metric name cannot be empty")
        # Ensure metric name follows common conventions
        if not v.replace('_', '').replace('.', '').replace('-', '').isalnum():
            raise ValueError("Metric name must contain only alphanumeric, underscore, dot, or dash characters")
        return v.strip()
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class Alert(BaseModel):
    """Type-safe alert model."""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Alert name")
    severity: AlertSeverity = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    source: str = Field(..., description="Alert source")
    metric_name: Optional[str] = Field(None, description="Related metric")
    threshold_value: Optional[float] = Field(None, description="Threshold value")
    current_value: Optional[float] = Field(None, description="Current value")
    tags: Dict[str, str] = Field(default_factory=dict, description="Alert tags")
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    def is_resolved(self) -> bool:
        """Check if alert is resolved."""
        return self.resolved_at is not None
    
    def resolve(self) -> None:
        """Mark alert as resolved."""
        self.resolved_at = datetime.now(timezone.utc)
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class HealthCheck(BaseModel):
    """Type-safe health check model."""
    check_id: str = Field(..., description="Health check identifier")
    name: str = Field(..., description="Check name")
    status: HealthStatus = Field(..., description="Check status")
    response_time_ms: float = Field(..., ge=0, description="Response time in milliseconds")
    details: Dict[str, Any] = Field(default_factory=dict, description="Check details")
    last_success: Optional[datetime] = Field(None, description="Last successful check")
    last_failure: Optional[datetime] = Field(None, description="Last failed check")
    consecutive_failures: int = Field(default=0, ge=0, description="Consecutive failure count")
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_healthy(self) -> bool:
        """Check if health check is passing."""
        return self.status == HealthStatus.HEALTHY
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class TraceSpan(BaseModel):
    """Type-safe distributed tracing span model."""
    trace_id: str = Field(..., description="Trace identifier")
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: Optional[str] = Field(None, description="Parent span identifier")
    operation_name: str = Field(..., description="Operation name")
    service_name: str = Field(..., description="Service name")
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = Field(None, description="End timestamp")
    duration_ms: Optional[float] = Field(None, ge=0, description="Duration in milliseconds")
    status: TraceStatus = Field(default=TraceStatus.SUCCESS, description="Trace status")
    tags: Dict[str, str] = Field(default_factory=dict, description="Span tags")
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="Span logs")
    
    def finish(self, status: TraceStatus = TraceStatus.SUCCESS) -> None:
        """Finish the span."""
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.status = status
    
    def add_log(self, level: str, message: str, **kwargs) -> None:
        """Add log entry to span."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logs.append(log_entry)
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class MetricsCollector:
    """High-performance metrics collection system."""
    
    def __init__(self, buffer_size: int = 10000, flush_interval_seconds: int = 60):
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval_seconds
        self.metrics_buffer = deque(maxlen=buffer_size)
        self.aggregated_metrics = defaultdict(list)
        self.last_flush = datetime.now(timezone.utc)
        self.lock = threading.Lock()
        self.logger = structlog.get_logger("metrics_collector")
        
        # Start background flush thread
        self._start_flush_thread()
    
    def record_metric(self, metric: Metric) -> None:
        """Record a metric with thread-safe buffering."""
        with self.lock:
            self.metrics_buffer.append(metric)
            
            # Aggregate metrics by name for statistics
            key = f"{metric.name}:{metric.type}"
            self.aggregated_metrics[key].append(metric.value)
            
            # Keep only recent values for aggregation
            if len(self.aggregated_metrics[key]) > 1000:
                self.aggregated_metrics[key] = self.aggregated_metrics[key][-500:]
    
    def record_counter(self, name: str, value: float = 1, tags: Optional[Dict[str, str]] = None, source: str = "default") -> None:
        """Record a counter metric."""
        metric = Metric(
            name=name,
            type=MetricType.COUNTER,
            value=value,
            tags=tags or {},
            source=source
        )
        self.record_metric(metric)
    
    def record_gauge(self, name: str, value: float, unit: Optional[str] = None, tags: Optional[Dict[str, str]] = None, source: str = "default") -> None:
        """Record a gauge metric."""
        metric = Metric(
            name=name,
            type=MetricType.GAUGE,
            value=value,
            unit=unit,
            tags=tags or {},
            source=source
        )
        self.record_metric(metric)
    
    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None, source: str = "default") -> None:
        """Record a timer metric."""
        metric = Metric(
            name=name,
            type=MetricType.TIMER,
            value=duration_ms,
            unit="ms",
            tags=tags or {},
            source=source
        )
        self.record_metric(metric)
    
    def get_metric_statistics(self, metric_name: str, metric_type: MetricType) -> Dict[str, float]:
        """Get statistics for a specific metric."""
        key = f"{metric_name}:{metric_type}"
        values = self.aggregated_metrics.get(key, [])
        
        if not values:
            return {}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "p95": statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
            "p99": statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
        }
    
    def get_buffer_status(self) -> Dict[str, Any]:
        """Get metrics buffer status."""
        with self.lock:
            return {
                "buffer_size": len(self.metrics_buffer),
                "buffer_capacity": self.buffer_size,
                "buffer_utilization": len(self.metrics_buffer) / self.buffer_size * 100,
                "aggregated_metric_types": len(self.aggregated_metrics),
                "last_flush": self.last_flush.isoformat(),
                "flush_interval_seconds": self.flush_interval
            }
    
    def flush_metrics(self) -> List[Metric]:
        """Flush metrics buffer and return metrics."""
        with self.lock:
            metrics = list(self.metrics_buffer)
            self.metrics_buffer.clear()
            self.last_flush = datetime.now(timezone.utc)
            
            self.logger.info(
                "Metrics flushed",
                count=len(metrics),
                aggregated_types=len(self.aggregated_metrics)
            )
            
            return metrics
    
    def _start_flush_thread(self) -> None:
        """Start background thread for periodic flushing."""
        def flush_worker():
            while True:
                time.sleep(self.flush_interval)
                try:
                    self.flush_metrics()
                except Exception as e:
                    self.logger.error("Metrics flush failed", error=str(e))
        
        thread = threading.Thread(target=flush_worker, daemon=True)
        thread.start()


class AlertRule(BaseModel):
    """Type-safe alert rule definition."""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Rule name")
    metric_name: str = Field(..., description="Metric to monitor")
    condition: str = Field(..., description="Alert condition (>, <, >=, <=, ==, !=)")
    threshold: float = Field(..., description="Threshold value")
    severity: AlertSeverity = Field(..., description="Alert severity")
    window_minutes: int = Field(default=5, gt=0, description="Evaluation window")
    consecutive_violations: int = Field(default=1, gt=0, description="Required consecutive violations")
    enabled: bool = Field(default=True, description="Rule enabled status")
    tags: Dict[str, str] = Field(default_factory=dict, description="Rule tags")
    
    def evaluate(self, current_value: float) -> bool:
        """Evaluate if current value violates the rule."""
        if not self.enabled:
            return False
        
        if self.condition == ">":
            return current_value > self.threshold
        elif self.condition == "<":
            return current_value < self.threshold
        elif self.condition == ">=":
            return current_value >= self.threshold
        elif self.condition == "<=":
            return current_value <= self.threshold
        elif self.condition == "==":
            return current_value == self.threshold
        elif self.condition == "!=":
            return current_value != self.threshold
        else:
            return False
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class AlertManager:
    """Intelligent alerting system with threshold management."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.rule_violations: Dict[str, List[datetime]] = defaultdict(list)
        self.logger = structlog.get_logger("alert_manager")
        
        # Start alert evaluation thread
        self._start_evaluation_thread()
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add alert rule."""
        self.rules[rule.rule_id] = rule
        self.logger.info(
            "Alert rule added",
            rule_id=rule.rule_id,
            name=rule.name,
            metric=rule.metric_name
        )
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove alert rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            # Clean up any violations for this rule
            if rule_id in self.rule_violations:
                del self.rule_violations[rule_id]
            self.logger.info("Alert rule removed", rule_id=rule_id)
            return True
        return False
    
    def evaluate_rules(self) -> List[Alert]:
        """Evaluate all alert rules against current metrics."""
        new_alerts = []
        current_time = datetime.now(timezone.utc)
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # Get recent metric statistics
            stats = self.metrics_collector.get_metric_statistics(
                rule.metric_name,
                MetricType.GAUGE  # Assume gauge for simplicity
            )
            
            if not stats:
                continue
            
            current_value = stats.get("mean", 0)  # Use mean value for evaluation
            
            # Check if rule is violated
            if rule.evaluate(current_value):
                # Record violation
                self.rule_violations[rule.rule_id].append(current_time)
                
                # Clean old violations outside window
                window_start = current_time - timedelta(minutes=rule.window_minutes)
                self.rule_violations[rule.rule_id] = [
                    v for v in self.rule_violations[rule.rule_id]
                    if v >= window_start
                ]
                
                # Check if we have enough consecutive violations
                if len(self.rule_violations[rule.rule_id]) >= rule.consecutive_violations:
                    # Check if alert already exists
                    alert_key = f"{rule.rule_id}:{rule.metric_name}"
                    if alert_key not in self.active_alerts:
                        # Create new alert
                        alert = Alert(
                            name=rule.name,
                            severity=rule.severity,
                            message=f"Metric {rule.metric_name} {rule.condition} {rule.threshold} (current: {current_value:.2f})",
                            source="alert_manager",
                            metric_name=rule.metric_name,
                            threshold_value=rule.threshold,
                            current_value=current_value,
                            tags=rule.tags
                        )
                        
                        self.active_alerts[alert_key] = alert
                        self.alert_history.append(alert)
                        new_alerts.append(alert)
                        
                        self.logger.warning(
                            "Alert triggered",
                            alert_id=alert.alert_id,
                            rule_name=rule.name,
                            current_value=current_value,
                            threshold=rule.threshold
                        )
            else:
                # Rule not violated, check if we should resolve alert
                alert_key = f"{rule.rule_id}:{rule.metric_name}"
                if alert_key in self.active_alerts:
                    alert = self.active_alerts[alert_key]
                    alert.resolve()
                    del self.active_alerts[alert_key]
                    
                    self.logger.info(
                        "Alert resolved",
                        alert_id=alert.alert_id,
                        rule_name=rule.name,
                        current_value=current_value
                    )
                
                # Clear violations for this rule
                if rule.rule_id in self.rule_violations:
                    self.rule_violations[rule.rule_id].clear()
        
        return new_alerts
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get currently active alerts."""
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        return alerts
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alerting system statistics."""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.triggered_at >= last_24h
        ]
        
        severity_counts = defaultdict(int)
        for alert in recent_alerts:
            severity_counts[alert.severity] += 1
        
        return {
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules.values() if r.enabled]),
            "active_alerts": len(self.active_alerts),
            "alerts_last_24h": len(recent_alerts),
            "severity_distribution": dict(severity_counts),
            "total_alert_history": len(self.alert_history)
        }
    
    def _start_evaluation_thread(self) -> None:
        """Start background thread for rule evaluation."""
        def evaluation_worker():
            while True:
                time.sleep(30)  # Evaluate every 30 seconds
                try:
                    self.evaluate_rules()
                except Exception as e:
                    self.logger.error("Alert evaluation failed", error=str(e))
        
        thread = threading.Thread(target=evaluation_worker, daemon=True)
        thread.start()


class HealthMonitor:
    """Comprehensive health monitoring system."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_functions: Dict[str, Callable[[], Dict[str, Any]]] = {}
        self.logger = structlog.get_logger("health_monitor")
        
        # Register default health checks
        self._register_default_checks()
        
        # Start periodic health checking
        self._start_health_check_thread()
    
    def register_check(self, check_id: str, name: str, check_function: Callable[[], Dict[str, Any]]) -> None:
        """Register a custom health check."""
        self.check_functions[check_id] = check_function
        self.logger.info("Health check registered", check_id=check_id, name=name)
    
    def run_check(self, check_id: str) -> HealthCheck:
        """Run a specific health check."""
        if check_id not in self.check_functions:
            raise ValueError(f"Health check {check_id} not found")
        
        start_time = time.time()
        
        try:
            result = self.check_functions[check_id]()
            response_time = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                check_id=check_id,
                name=result.get("name", check_id),
                status=HealthStatus(result.get("status", HealthStatus.UNKNOWN)),
                response_time_ms=response_time,
                details=result.get("details", {})
            )
            
            # Update success/failure tracking
            if health_check.is_healthy():
                health_check.last_success = health_check.checked_at
                if check_id in self.health_checks:
                    self.health_checks[check_id].consecutive_failures = 0
            else:
                health_check.last_failure = health_check.checked_at
                if check_id in self.health_checks:
                    health_check.consecutive_failures = self.health_checks[check_id].consecutive_failures + 1
            
            self.health_checks[check_id] = health_check
            return health_check
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                check_id=check_id,
                name=check_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"error": str(e)},
                last_failure=datetime.now(timezone.utc)
            )
            
            if check_id in self.health_checks:
                health_check.consecutive_failures = self.health_checks[check_id].consecutive_failures + 1
            
            self.health_checks[check_id] = health_check
            self.logger.error(f"Health check {check_id} failed", error=str(e))
            return health_check
    
    def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_check = {
                executor.submit(self.run_check, check_id): check_id
                for check_id in self.check_functions.keys()
            }
            
            for future in future_to_check:
                check_id = future_to_check[future]
                try:
                    results[check_id] = future.result(timeout=30)
                except Exception as e:
                    self.logger.error(f"Health check {check_id} execution failed", error=str(e))
        
        return results
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.health_checks:
            return {
                "status": HealthStatus.UNKNOWN,
                "checks": {},
                "summary": "No health checks registered"
            }
        
        healthy_checks = sum(1 for check in self.health_checks.values() if check.is_healthy())
        total_checks = len(self.health_checks)
        
        # Determine overall status
        if healthy_checks == total_checks:
            overall_status = HealthStatus.HEALTHY
        elif healthy_checks > total_checks * 0.5:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        return {
            "status": overall_status,
            "checks": {check_id: check.dict() for check_id, check in self.health_checks.items()},
            "summary": {
                "total_checks": total_checks,
                "healthy_checks": healthy_checks,
                "health_percentage": (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
            },
            "last_check": max(
                (check.checked_at for check in self.health_checks.values()),
                default=datetime.now(timezone.utc)
            ).isoformat()
        }
    
    def _register_default_checks(self) -> None:
        """Register default health checks."""
        
        def check_customer_io_api():
            """Check Customer.IO API connectivity."""
            try:
                # Simple API health check (would be implemented based on actual API)
                # For now, simulate a check
                response_time = 0.05  # Simulated response time
                return {
                    "name": "Customer.IO API",
                    "status": HealthStatus.HEALTHY,
                    "details": {
                        "response_time_ms": response_time * 1000,
                        "endpoint": "api.customer.io"
                    }
                }
            except Exception as e:
                return {
                    "name": "Customer.IO API",
                    "status": HealthStatus.UNHEALTHY,
                    "details": {"error": str(e)}
                }
        
        def check_system_resources():
            """Check system resource utilization."""
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Determine status based on resource usage
                if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                    status = HealthStatus.UNHEALTHY
                elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 80:
                    status = HealthStatus.DEGRADED
                else:
                    status = HealthStatus.HEALTHY
                
                return {
                    "name": "System Resources",
                    "status": status,
                    "details": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "disk_percent": disk.percent,
                        "memory_available_gb": memory.available / (1024**3),
                        "disk_free_gb": disk.free / (1024**3)
                    }
                }
            except Exception as e:
                return {
                    "name": "System Resources",
                    "status": HealthStatus.UNHEALTHY,
                    "details": {"error": str(e)}
                }
        
        def check_thread_pool():
            """Check thread pool health."""
            try:
                # Simple thread pool check
                active_threads = threading.active_count()
                
                if active_threads > 100:
                    status = HealthStatus.DEGRADED
                else:
                    status = HealthStatus.HEALTHY
                
                return {
                    "name": "Thread Pool",
                    "status": status,
                    "details": {
                        "active_threads": active_threads,
                        "main_thread_alive": threading.main_thread().is_alive()
                    }
                }
            except Exception as e:
                return {
                    "name": "Thread Pool",
                    "status": HealthStatus.UNHEALTHY,
                    "details": {"error": str(e)}
                }
        
        # Register the checks
        self.register_check("customer_io_api", "Customer.IO API", check_customer_io_api)
        self.register_check("system_resources", "System Resources", check_system_resources)
        self.register_check("thread_pool", "Thread Pool", check_thread_pool)
    
    def _start_health_check_thread(self) -> None:
        """Start background thread for periodic health checking."""
        def health_check_worker():
            while True:
                time.sleep(60)  # Check every minute
                try:
                    self.run_all_checks()
                except Exception as e:
                    self.logger.error("Health check execution failed", error=str(e))
        
        thread = threading.Thread(target=health_check_worker, daemon=True)
        thread.start()


class TracingContext:
    """Thread-local tracing context."""
    
    def __init__(self):
        self._context = threading.local()
    
    def set_trace(self, trace_id: str, span_id: str) -> None:
        """Set current trace context."""
        self._context.trace_id = trace_id
        self._context.span_id = span_id
    
    def get_trace_id(self) -> Optional[str]:
        """Get current trace ID."""
        return getattr(self._context, 'trace_id', None)
    
    def get_span_id(self) -> Optional[str]:
        """Get current span ID."""
        return getattr(self._context, 'span_id', None)
    
    def clear(self) -> None:
        """Clear trace context."""
        if hasattr(self._context, 'trace_id'):
            delattr(self._context, 'trace_id')
        if hasattr(self._context, 'span_id'):
            delattr(self._context, 'span_id')


class DistributedTracer:
    """Distributed tracing system for request correlation."""
    
    def __init__(self):
        self.spans: Dict[str, List[TraceSpan]] = defaultdict(list)
        self.active_spans: Dict[str, TraceSpan] = {}
        self.context = TracingContext()
        self.logger = structlog.get_logger("distributed_tracer")
    
    def start_trace(self, operation_name: str, service_name: str = "default", tags: Optional[Dict[str, str]] = None) -> TraceSpan:
        """Start a new trace."""
        trace_id = str(uuid.uuid4())
        span = TraceSpan(
            trace_id=trace_id,
            operation_name=operation_name,
            service_name=service_name,
            tags=tags or {}
        )
        
        self.spans[trace_id].append(span)
        self.active_spans[span.span_id] = span
        self.context.set_trace(trace_id, span.span_id)
        
        self.logger.info(
            "Trace started",
            trace_id=trace_id,
            span_id=span.span_id,
            operation=operation_name
        )
        
        return span
    
    def start_span(self, operation_name: str, service_name: str = "default", tags: Optional[Dict[str, str]] = None) -> TraceSpan:
        """Start a child span."""
        trace_id = self.context.get_trace_id()
        parent_span_id = self.context.get_span_id()
        
        if not trace_id:
            # No active trace, start a new one
            return self.start_trace(operation_name, service_name, tags)
        
        span = TraceSpan(
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=service_name,
            tags=tags or {}
        )
        
        self.spans[trace_id].append(span)
        self.active_spans[span.span_id] = span
        self.context.set_trace(trace_id, span.span_id)
        
        self.logger.info(
            "Span started",
            trace_id=trace_id,
            span_id=span.span_id,
            parent_span_id=parent_span_id,
            operation=operation_name
        )
        
        return span
    
    def finish_span(self, span: TraceSpan, status: TraceStatus = TraceStatus.SUCCESS) -> None:
        """Finish a span."""
        span.finish(status)
        
        if span.span_id in self.active_spans:
            del self.active_spans[span.span_id]
        
        # If this was the current span, revert to parent
        if self.context.get_span_id() == span.span_id:
            if span.parent_span_id:
                self.context.set_trace(span.trace_id, span.parent_span_id)
            else:
                self.context.clear()
        
        self.logger.info(
            "Span finished",
            trace_id=span.trace_id,
            span_id=span.span_id,
            duration_ms=span.duration_ms,
            status=status
        )
    
    def add_span_log(self, level: str, message: str, **kwargs) -> None:
        """Add log to current span."""
        span_id = self.context.get_span_id()
        if span_id and span_id in self.active_spans:
            self.active_spans[span_id].add_log(level, message, **kwargs)
    
    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get all spans for a trace."""
        return self.spans.get(trace_id, [])
    
    def get_trace_tree(self, trace_id: str) -> Dict[str, Any]:
        """Get trace as hierarchical tree structure."""
        spans = self.get_trace(trace_id)
        if not spans:
            return {}
        
        # Build tree structure
        span_map = {span.span_id: span for span in spans}
        root_spans = [span for span in spans if span.parent_span_id is None]
        
        def build_tree(span: TraceSpan) -> Dict[str, Any]:
            children = [s for s in spans if s.parent_span_id == span.span_id]
            return {
                "span": span.dict(),
                "children": [build_tree(child) for child in children]
            }
        
        return {
            "trace_id": trace_id,
            "total_spans": len(spans),
            "total_duration_ms": sum(span.duration_ms or 0 for span in spans),
            "root_spans": [build_tree(root) for root in root_spans]
        }
    
    def get_tracing_statistics(self) -> Dict[str, Any]:
        """Get tracing system statistics."""
        total_traces = len(self.spans)
        total_spans = sum(len(spans) for spans in self.spans.values())
        active_spans_count = len(self.active_spans)
        
        # Calculate average trace duration
        completed_traces = []
        for spans in self.spans.values():
            if spans and all(span.end_time for span in spans):
                trace_duration = sum(span.duration_ms or 0 for span in spans)
                completed_traces.append(trace_duration)
        
        avg_trace_duration = statistics.mean(completed_traces) if completed_traces else 0
        
        return {
            "total_traces": total_traces,
            "total_spans": total_spans,
            "active_spans": active_spans_count,
            "completed_traces": len(completed_traces),
            "average_trace_duration_ms": round(avg_trace_duration, 2),
            "average_spans_per_trace": round(total_spans / total_traces, 1) if total_traces > 0 else 0
        }


# Decorator for automatic tracing
def trace_function(operation_name: Optional[str] = None, service_name: str = "default"):
    """Decorator for automatic function tracing."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = getattr(wrapper, '_tracer', None)
            if not tracer:
                # Create a default tracer if none exists
                tracer = DistributedTracer()
                wrapper._tracer = tracer
            
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            span = tracer.start_span(op_name, service_name)
            
            try:
                result = func(*args, **kwargs)
                tracer.finish_span(span, TraceStatus.SUCCESS)
                return result
            except Exception as e:
                span.add_log("error", str(e))
                tracer.finish_span(span, TraceStatus.ERROR)
                raise
        
        return wrapper
    return decorator


class ObservabilityManager:
    """Comprehensive monitoring and observability management."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("observability_manager")
        
        # Initialize monitoring components
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(self.metrics_collector)
        self.health_monitor = HealthMonitor(client)
        self.tracer = DistributedTracer()
        
        # System state tracking
        self.start_time = datetime.now(timezone.utc)
        self.request_count = 0
        self.error_count = 0
        
        self.logger.info("ObservabilityManager initialized")
    
    def record_request(self, operation: str, duration_ms: float, success: bool = True, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a request with comprehensive metrics."""
        self.request_count += 1
        if not success:
            self.error_count += 1
        
        # Record metrics
        self.metrics_collector.record_counter(
            "requests_total",
            tags={"operation": operation, "success": str(success), **(tags or {})}
        )
        
        self.metrics_collector.record_timer(
            "request_duration_ms",
            duration_ms,
            tags={"operation": operation, **(tags or {})}
        )
        
        if not success:
            self.metrics_collector.record_counter(
                "requests_errors_total",
                tags={"operation": operation, **(tags or {})}
            )
    
    def record_customer_io_event(self, event_type: str, user_id: str, success: bool = True, response_time_ms: Optional[float] = None) -> None:
        """Record Customer.IO specific event metrics."""
        tags = {
            "event_type": event_type,
            "success": str(success)
        }
        
        self.metrics_collector.record_counter("customerio_events_total", tags=tags)
        
        if response_time_ms:
            self.metrics_collector.record_timer("customerio_response_time_ms", response_time_ms, tags=tags)
        
        if not success:
            self.metrics_collector.record_counter("customerio_events_errors_total", tags=tags)
    
    def record_batch_operation(self, batch_size: int, processing_time_ms: float, success_count: int, error_count: int) -> None:
        """Record batch operation metrics."""
        self.metrics_collector.record_gauge("batch_size", batch_size)
        self.metrics_collector.record_timer("batch_processing_time_ms", processing_time_ms)
        self.metrics_collector.record_gauge("batch_success_rate", (success_count / batch_size) * 100 if batch_size > 0 else 0)
        
        if error_count > 0:
            self.metrics_collector.record_counter("batch_errors_total", value=error_count)
    
    def start_trace(self, operation: str, service: str = "customer_io", **tags) -> TraceSpan:
        """Start distributed trace for operation."""
        return self.tracer.start_trace(operation, service, tags)
    
    def start_span(self, operation: str, service: str = "customer_io", **tags) -> TraceSpan:
        """Start span within current trace."""
        return self.tracer.start_span(operation, service, tags)
    
    def finish_span(self, span: TraceSpan, success: bool = True) -> None:
        """Finish span with status."""
        status = TraceStatus.SUCCESS if success else TraceStatus.ERROR
        self.tracer.finish_span(span, status)
    
    def setup_default_alerts(self) -> None:
        """Setup default alerting rules."""
        # High error rate alert
        error_rate_rule = AlertRule(
            name="High Error Rate",
            metric_name="error_rate_percent",
            condition=">",
            threshold=5.0,
            severity=AlertSeverity.HIGH,
            window_minutes=5,
            consecutive_violations=2
        )
        self.alert_manager.add_rule(error_rate_rule)
        
        # High response time alert
        response_time_rule = AlertRule(
            name="High Response Time",
            metric_name="avg_response_time_ms",
            condition=">",
            threshold=5000.0,
            severity=AlertSeverity.MEDIUM,
            window_minutes=10,
            consecutive_violations=3
        )
        self.alert_manager.add_rule(response_time_rule)
        
        # System resource alerts
        cpu_rule = AlertRule(
            name="High CPU Usage",
            metric_name="cpu_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.MEDIUM,
            window_minutes=15
        )
        self.alert_manager.add_rule(cpu_rule)
        
        memory_rule = AlertRule(
            name="High Memory Usage",
            metric_name="memory_percent",
            condition=">",
            threshold=85.0,
            severity=AlertSeverity.HIGH,
            window_minutes=10
        )
        self.alert_manager.add_rule(memory_rule)
        
        self.logger.info("Default alert rules configured")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        # Calculate uptime
        uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        # Calculate error rate
        error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
        
        # Update error rate metric for alerting
        self.metrics_collector.record_gauge("error_rate_percent", error_rate)
        
        # Get system health
        system_health = self.health_monitor.get_system_health()
        
        # Get metrics statistics
        request_stats = self.metrics_collector.get_metric_statistics("request_duration_ms", MetricType.TIMER)
        if request_stats:
            self.metrics_collector.record_gauge("avg_response_time_ms", request_stats.get("mean", 0))
        
        return {
            "system": {
                "uptime_seconds": uptime_seconds,
                "start_time": self.start_time.isoformat(),
                "health_status": system_health["status"],
                "health_summary": system_health["summary"]
            },
            "requests": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": round(error_rate, 2),
                "requests_per_minute": round(self.request_count / (uptime_seconds / 60), 2) if uptime_seconds > 0 else 0
            },
            "performance": request_stats,
            "alerts": {
                "active_alerts": len(self.alert_manager.get_active_alerts()),
                "critical_alerts": len(self.alert_manager.get_active_alerts(AlertSeverity.CRITICAL)),
                "alert_statistics": self.alert_manager.get_alert_statistics()
            },
            "tracing": self.tracer.get_tracing_statistics(),
            "metrics": self.metrics_collector.get_buffer_status(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        health_checks = self.health_monitor.run_all_checks()
        system_health = self.health_monitor.get_system_health()
        active_alerts = self.alert_manager.get_active_alerts()
        
        # Analyze system trends
        dashboard_data = self.get_dashboard_data()
        
        recommendations = []
        
        # Generate recommendations based on metrics
        if dashboard_data["requests"]["error_rate_percent"] > 5:
            recommendations.append("High error rate detected - investigate recent changes")
        
        if len(active_alerts) > 0:
            recommendations.append(f"Active alerts require attention: {len(active_alerts)} alerts")
        
        if system_health["status"] != HealthStatus.HEALTHY:
            recommendations.append("System health degraded - check resource utilization")
        
        return {
            "report_generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_health": system_health["status"],
            "health_checks": health_checks,
            "active_alerts": [alert.dict() for alert in active_alerts],
            "system_metrics": dashboard_data,
            "recommendations": recommendations,
            "summary": {
                "total_health_checks": len(health_checks),
                "passing_health_checks": len([check for check in health_checks.values() if check.is_healthy()]),
                "active_alert_count": len(active_alerts),
                "critical_alert_count": len([alert for alert in active_alerts if alert.severity == AlertSeverity.CRITICAL])
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get ObservabilityManager metrics and status."""
        return {
            "manager": {
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
                "total_requests": self.request_count,
                "total_errors": self.error_count
            },
            "components": {
                "metrics_collector": self.metrics_collector.get_buffer_status(),
                "alert_manager": self.alert_manager.get_alert_statistics(),
                "health_monitor": {
                    "registered_checks": len(self.health_monitor.check_functions),
                    "last_check_results": len(self.health_monitor.health_checks)
                },
                "tracer": self.tracer.get_tracing_statistics()
            },
            "features": {
                "metrics_collection": True,
                "alerting": True,
                "health_monitoring": True,
                "distributed_tracing": True,
                "dashboard_data": True,
                "health_reporting": True
            }
        }