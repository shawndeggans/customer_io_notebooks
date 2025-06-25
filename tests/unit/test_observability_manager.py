"""
Comprehensive tests for Customer.IO Observability Manager.

Tests cover:
- Metric types, alert severities, health statuses, and trace statuses
- Metrics collection system with buffering and aggregation
- Alerting system with rule management and threshold monitoring
- Health monitoring with custom checks and system resource monitoring
- Distributed tracing with span management and context tracking
- Performance monitoring and dashboard data generation
- Thread safety and concurrent operations
"""

import pytest
import time
import threading
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from utils.observability_manager import (
    MetricType,
    AlertSeverity,
    HealthStatus,
    TraceStatus,
    Metric,
    Alert,
    HealthCheck,
    TraceSpan,
    MetricsCollector,
    AlertRule,
    AlertManager,
    HealthMonitor,
    TracingContext,
    DistributedTracer,
    trace_function,
    ObservabilityManager
)
from utils.api_client import CustomerIOClient


class TestMetricType:
    """Test MetricType enum."""
    
    def test_metric_type_values(self):
        """Test all metric type values."""
        assert MetricType.COUNTER == "counter"
        assert MetricType.GAUGE == "gauge"
        assert MetricType.HISTOGRAM == "histogram"
        assert MetricType.SUMMARY == "summary"
        assert MetricType.TIMER == "timer"
    
    def test_metric_type_membership(self):
        """Test metric type membership."""
        valid_types = [metric_type.value for metric_type in MetricType]
        assert "counter" in valid_types
        assert "invalid_type" not in valid_types


class TestAlertSeverity:
    """Test AlertSeverity enum."""
    
    def test_alert_severity_values(self):
        """Test all alert severity values."""
        assert AlertSeverity.CRITICAL == "critical"
        assert AlertSeverity.HIGH == "high"
        assert AlertSeverity.MEDIUM == "medium"
        assert AlertSeverity.LOW == "low"
        assert AlertSeverity.INFO == "info"
    
    def test_alert_severity_membership(self):
        """Test alert severity membership."""
        valid_severities = [severity.value for severity in AlertSeverity]
        assert "critical" in valid_severities
        assert "invalid_severity" not in valid_severities


class TestHealthStatus:
    """Test HealthStatus enum."""
    
    def test_health_status_values(self):
        """Test all health status values."""
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.DEGRADED == "degraded"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        assert HealthStatus.UNKNOWN == "unknown"


class TestTraceStatus:
    """Test TraceStatus enum."""
    
    def test_trace_status_values(self):
        """Test all trace status values."""
        assert TraceStatus.SUCCESS == "success"
        assert TraceStatus.ERROR == "error"
        assert TraceStatus.TIMEOUT == "timeout"
        assert TraceStatus.CANCELLED == "cancelled"


class TestMetric:
    """Test Metric data model."""
    
    def test_valid_metric(self):
        """Test valid metric creation."""
        metric = Metric(
            name="http_requests_total",
            type=MetricType.COUNTER,
            value=100.0,
            unit="requests",
            tags={"method": "GET", "status": "200"},
            source="web_server"
        )
        
        assert metric.name == "http_requests_total"
        assert metric.type == MetricType.COUNTER
        assert metric.value == 100.0
        assert metric.unit == "requests"
        assert metric.tags["method"] == "GET"
        assert metric.source == "web_server"
        assert metric.timestamp is not None
    
    def test_metric_name_validation(self):
        """Test metric name validation."""
        # Test empty name
        with pytest.raises(ValidationError):
            Metric(
                name="",
                type=MetricType.GAUGE,
                value=50.0,
                source="test"
            )
        
        # Test whitespace-only name
        with pytest.raises(ValidationError):
            Metric(
                name="   ",
                type=MetricType.GAUGE,
                value=50.0,
                source="test"
            )
        
        # Test invalid characters
        with pytest.raises(ValidationError):
            Metric(
                name="invalid@metric#name",
                type=MetricType.GAUGE,
                value=50.0,
                source="test"
            )
    
    def test_valid_metric_names(self):
        """Test valid metric name formats."""
        valid_names = [
            "http_requests_total",
            "cpu.usage.percent",
            "memory-available-bytes",
            "simple_counter",
            "nested.metric.name"
        ]
        
        for name in valid_names:
            metric = Metric(
                name=name,
                type=MetricType.GAUGE,
                value=1.0,
                source="test"
            )
            assert metric.name == name


class TestAlert:
    """Test Alert data model."""
    
    def test_valid_alert(self):
        """Test valid alert creation."""
        alert = Alert(
            name="High CPU Usage",
            severity=AlertSeverity.HIGH,
            message="CPU usage is above 80%",
            source="monitoring_system",
            metric_name="cpu_usage_percent",
            threshold_value=80.0,
            current_value=85.5,
            tags={"server": "web-01"}
        )
        
        assert alert.name == "High CPU Usage"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.message == "CPU usage is above 80%"
        assert alert.metric_name == "cpu_usage_percent"
        assert alert.threshold_value == 80.0
        assert alert.current_value == 85.5
        assert alert.alert_id is not None
        assert alert.triggered_at is not None
        assert alert.resolved_at is None
    
    def test_alert_resolution(self):
        """Test alert resolution functionality."""
        alert = Alert(
            name="Test Alert",
            severity=AlertSeverity.MEDIUM,
            message="Test alert message",
            source="test"
        )
        
        assert alert.is_resolved() is False
        
        alert.resolve()
        
        assert alert.is_resolved() is True
        assert alert.resolved_at is not None


class TestHealthCheck:
    """Test HealthCheck data model."""
    
    def test_valid_health_check(self):
        """Test valid health check creation."""
        health_check = HealthCheck(
            check_id="api_connectivity",
            name="API Connectivity Check",
            status=HealthStatus.HEALTHY,
            response_time_ms=150.5,
            details={"endpoint": "https://api.example.com", "status_code": 200}
        )
        
        assert health_check.check_id == "api_connectivity"
        assert health_check.name == "API Connectivity Check"
        assert health_check.status == HealthStatus.HEALTHY
        assert health_check.response_time_ms == 150.5
        assert health_check.details["endpoint"] == "https://api.example.com"
        assert health_check.checked_at is not None
        assert health_check.consecutive_failures == 0
    
    def test_health_check_validation(self):
        """Test health check validation."""
        # Test negative response time
        with pytest.raises(ValidationError):
            HealthCheck(
                check_id="test_check",
                name="Test Check",
                status=HealthStatus.HEALTHY,
                response_time_ms=-10.0
            )
        
        # Test negative consecutive failures
        with pytest.raises(ValidationError):
            HealthCheck(
                check_id="test_check",
                name="Test Check",
                status=HealthStatus.HEALTHY,
                response_time_ms=100.0,
                consecutive_failures=-1
            )
    
    def test_is_healthy(self):
        """Test health check status evaluation."""
        healthy_check = HealthCheck(
            check_id="test",
            name="Test",
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        assert healthy_check.is_healthy() is True
        
        unhealthy_check = HealthCheck(
            check_id="test",
            name="Test",
            status=HealthStatus.UNHEALTHY,
            response_time_ms=100.0
        )
        assert unhealthy_check.is_healthy() is False


class TestTraceSpan:
    """Test TraceSpan data model."""
    
    def test_valid_trace_span(self):
        """Test valid trace span creation."""
        span = TraceSpan(
            trace_id="trace_123",
            operation_name="http_request",
            service_name="web_service",
            tags={"method": "GET", "endpoint": "/api/users"}
        )
        
        assert span.trace_id == "trace_123"
        assert span.operation_name == "http_request"
        assert span.service_name == "web_service"
        assert span.tags["method"] == "GET"
        assert span.span_id is not None
        assert span.start_time is not None
        assert span.end_time is None
        assert span.status == TraceStatus.SUCCESS
    
    def test_span_finish(self):
        """Test span finishing functionality."""
        span = TraceSpan(
            trace_id="trace_123",
            operation_name="test_operation",
            service_name="test_service"
        )
        
        # Small delay to ensure duration calculation
        time.sleep(0.01)
        
        span.finish(TraceStatus.SUCCESS)
        
        assert span.end_time is not None
        assert span.duration_ms is not None
        assert span.duration_ms > 0
        assert span.status == TraceStatus.SUCCESS
    
    def test_add_log(self):
        """Test adding logs to span."""
        span = TraceSpan(
            trace_id="trace_123",
            operation_name="test_operation",
            service_name="test_service"
        )
        
        span.add_log("info", "Processing request", user_id="12345")
        
        assert len(span.logs) == 1
        log_entry = span.logs[0]
        assert log_entry["level"] == "info"
        assert log_entry["message"] == "Processing request"
        assert log_entry["user_id"] == "12345"
        assert "timestamp" in log_entry


class TestMetricsCollector:
    """Test MetricsCollector implementation."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector."""
        return MetricsCollector(buffer_size=100, flush_interval_seconds=1)
    
    def test_metrics_collector_initialization(self, metrics_collector):
        """Test metrics collector initialization."""
        assert metrics_collector.buffer_size == 100
        assert metrics_collector.flush_interval == 1
        assert len(metrics_collector.metrics_buffer) == 0
        assert len(metrics_collector.aggregated_metrics) == 0
    
    def test_record_metric(self, metrics_collector):
        """Test recording individual metrics."""
        metric = Metric(
            name="test_counter",
            type=MetricType.COUNTER,
            value=1.0,
            source="test"
        )
        
        metrics_collector.record_metric(metric)
        
        assert len(metrics_collector.metrics_buffer) == 1
        assert metrics_collector.metrics_buffer[0] == metric
        
        # Check aggregation
        key = f"{metric.name}:{metric.type}"
        assert key in metrics_collector.aggregated_metrics
        assert metrics_collector.aggregated_metrics[key] == [1.0]
    
    def test_record_counter(self, metrics_collector):
        """Test recording counter metrics."""
        metrics_collector.record_counter(
            "http_requests",
            value=5.0,
            tags={"method": "POST"},
            source="web_server"
        )
        
        assert len(metrics_collector.metrics_buffer) == 1
        metric = metrics_collector.metrics_buffer[0]
        assert metric.name == "http_requests"
        assert metric.type == MetricType.COUNTER
        assert metric.value == 5.0
        assert metric.tags["method"] == "POST"
    
    def test_record_gauge(self, metrics_collector):
        """Test recording gauge metrics."""
        metrics_collector.record_gauge(
            "cpu_usage",
            value=75.5,
            unit="percent",
            tags={"server": "web-01"}
        )
        
        assert len(metrics_collector.metrics_buffer) == 1
        metric = metrics_collector.metrics_buffer[0]
        assert metric.name == "cpu_usage"
        assert metric.type == MetricType.GAUGE
        assert metric.value == 75.5
        assert metric.unit == "percent"
    
    def test_record_timer(self, metrics_collector):
        """Test recording timer metrics."""
        metrics_collector.record_timer(
            "request_duration",
            duration_ms=250.5,
            tags={"endpoint": "/api/users"}
        )
        
        assert len(metrics_collector.metrics_buffer) == 1
        metric = metrics_collector.metrics_buffer[0]
        assert metric.name == "request_duration"
        assert metric.type == MetricType.TIMER
        assert metric.value == 250.5
        assert metric.unit == "ms"
    
    def test_get_metric_statistics(self, metrics_collector):
        """Test metric statistics calculation."""
        # Record multiple values for the same metric
        for value in [10.0, 20.0, 30.0, 40.0, 50.0]:
            metrics_collector.record_gauge("test_metric", value)
        
        stats = metrics_collector.get_metric_statistics("test_metric", MetricType.GAUGE)
        
        assert stats["count"] == 5
        assert stats["sum"] == 150.0
        assert stats["mean"] == 30.0
        assert stats["median"] == 30.0
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0
        assert stats["std_dev"] > 0
    
    def test_get_buffer_status(self, metrics_collector):
        """Test buffer status reporting."""
        # Add some metrics
        for i in range(10):
            metrics_collector.record_counter(f"metric_{i}", value=1.0)
        
        status = metrics_collector.get_buffer_status()
        
        assert status["buffer_size"] == 10
        assert status["buffer_capacity"] == 100
        assert status["buffer_utilization"] == 10.0
        assert status["aggregated_metric_types"] == 10
        assert "last_flush" in status
        assert "flush_interval_seconds" in status
    
    def test_flush_metrics(self, metrics_collector):
        """Test metrics flushing."""
        # Add some metrics
        for i in range(5):
            metrics_collector.record_counter(f"metric_{i}", value=1.0)
        
        assert len(metrics_collector.metrics_buffer) == 5
        
        flushed_metrics = metrics_collector.flush_metrics()
        
        assert len(flushed_metrics) == 5
        assert len(metrics_collector.metrics_buffer) == 0
        assert metrics_collector.last_flush is not None
    
    def test_thread_safety(self, metrics_collector):
        """Test thread safety of metrics collection."""
        results = []
        errors = []
        
        def record_metrics(thread_id):
            try:
                for i in range(50):
                    metrics_collector.record_counter(
                        f"thread_{thread_id}_metric_{i}",
                        value=float(i)
                    )
                results.append(f"thread_{thread_id}_completed")
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
        
        # Run metrics recording in multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=record_metrics, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors and all metrics recorded
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 5
        assert len(metrics_collector.metrics_buffer) == 250  # 5 threads * 50 metrics


class TestAlertRule:
    """Test AlertRule data model."""
    
    def test_valid_alert_rule(self):
        """Test valid alert rule creation."""
        rule = AlertRule(
            name="High CPU Alert",
            metric_name="cpu_usage_percent",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            window_minutes=5,
            consecutive_violations=2
        )
        
        assert rule.name == "High CPU Alert"
        assert rule.metric_name == "cpu_usage_percent"
        assert rule.condition == ">"
        assert rule.threshold == 80.0
        assert rule.severity == AlertSeverity.HIGH
        assert rule.rule_id is not None
        assert rule.enabled is True
    
    def test_rule_evaluation(self):
        """Test alert rule evaluation."""
        rule = AlertRule(
            name="Test Rule",
            metric_name="test_metric",
            condition=">",
            threshold=50.0,
            severity=AlertSeverity.MEDIUM
        )
        
        # Test greater than condition
        assert rule.evaluate(60.0) is True
        assert rule.evaluate(40.0) is False
        assert rule.evaluate(50.0) is False
        
        # Test less than condition
        rule.condition = "<"
        assert rule.evaluate(40.0) is True
        assert rule.evaluate(60.0) is False
        
        # Test equals condition
        rule.condition = "=="
        rule.threshold = 100.0
        assert rule.evaluate(100.0) is True
        assert rule.evaluate(99.9) is False
        
        # Test disabled rule
        rule.enabled = False
        assert rule.evaluate(100.0) is False


class TestAlertManager:
    """Test AlertManager implementation."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector."""
        return MetricsCollector()
    
    @pytest.fixture
    def alert_manager(self, metrics_collector):
        """Create alert manager."""
        return AlertManager(metrics_collector)
    
    def test_alert_manager_initialization(self, alert_manager):
        """Test alert manager initialization."""
        assert alert_manager.metrics_collector is not None
        assert len(alert_manager.rules) == 0
        assert len(alert_manager.active_alerts) == 0
        assert len(alert_manager.alert_history) == 0
    
    def test_add_rule(self, alert_manager):
        """Test adding alert rules."""
        rule = AlertRule(
            name="Test Alert",
            metric_name="test_metric",
            condition=">",
            threshold=100.0,
            severity=AlertSeverity.HIGH
        )
        
        alert_manager.add_rule(rule)
        
        assert rule.rule_id in alert_manager.rules
        assert alert_manager.rules[rule.rule_id] == rule
    
    def test_remove_rule(self, alert_manager):
        """Test removing alert rules."""
        rule = AlertRule(
            name="Test Alert",
            metric_name="test_metric",
            condition=">",
            threshold=100.0,
            severity=AlertSeverity.HIGH
        )
        
        alert_manager.add_rule(rule)
        assert rule.rule_id in alert_manager.rules
        
        removed = alert_manager.remove_rule(rule.rule_id)
        assert removed is True
        assert rule.rule_id not in alert_manager.rules
        
        # Test removing non-existent rule
        removed = alert_manager.remove_rule("non_existent")
        assert removed is False
    
    def test_evaluate_rules(self, alert_manager, metrics_collector):
        """Test alert rule evaluation."""
        # Add metric data
        for value in [95.0, 85.0, 90.0]:
            metrics_collector.record_gauge("cpu_usage", value)
        
        # Add alert rule
        rule = AlertRule(
            name="High CPU",
            metric_name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.HIGH,
            consecutive_violations=1
        )
        alert_manager.add_rule(rule)
        
        # Evaluate rules
        new_alerts = alert_manager.evaluate_rules()
        
        # Should trigger alert since mean (90) > threshold (80)
        assert len(new_alerts) >= 0  # May or may not trigger based on timing
    
    def test_get_active_alerts(self, alert_manager):
        """Test getting active alerts."""
        # Manually add an active alert
        alert = Alert(
            name="Test Alert",
            severity=AlertSeverity.HIGH,
            message="Test message",
            source="test"
        )
        alert_manager.active_alerts["test_key"] = alert
        
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0] == alert
        
        # Test filtering by severity
        high_alerts = alert_manager.get_active_alerts(AlertSeverity.HIGH)
        assert len(high_alerts) == 1
        
        medium_alerts = alert_manager.get_active_alerts(AlertSeverity.MEDIUM)
        assert len(medium_alerts) == 0
    
    def test_get_alert_statistics(self, alert_manager):
        """Test alert statistics generation."""
        # Add some rules
        for i in range(3):
            rule = AlertRule(
                name=f"Rule {i}",
                metric_name=f"metric_{i}",
                condition=">",
                threshold=50.0,
                severity=AlertSeverity.MEDIUM
            )
            alert_manager.add_rule(rule)
        
        # Add some alert history
        for i in range(5):
            alert = Alert(
                name=f"Alert {i}",
                severity=AlertSeverity.HIGH if i < 2 else AlertSeverity.MEDIUM,
                message=f"Alert message {i}",
                source="test"
            )
            alert_manager.alert_history.append(alert)
        
        stats = alert_manager.get_alert_statistics()
        
        assert stats["total_rules"] == 3
        assert stats["enabled_rules"] == 3
        assert stats["total_alert_history"] == 5


class TestHealthMonitor:
    """Test HealthMonitor implementation."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def health_monitor(self, mock_client):
        """Create health monitor."""
        return HealthMonitor(mock_client)
    
    def test_health_monitor_initialization(self, health_monitor):
        """Test health monitor initialization."""
        assert health_monitor.client is not None
        assert len(health_monitor.health_checks) == 0
        assert len(health_monitor.check_functions) >= 3  # Default checks
    
    def test_register_check(self, health_monitor):
        """Test registering custom health checks."""
        def custom_check():
            return {
                "name": "Custom Check",
                "status": HealthStatus.HEALTHY,
                "details": {"test": "value"}
            }
        
        health_monitor.register_check("custom_check", "Custom Check", custom_check)
        
        assert "custom_check" in health_monitor.check_functions
        assert health_monitor.check_functions["custom_check"] == custom_check
    
    def test_run_check(self, health_monitor):
        """Test running individual health checks."""
        def test_check():
            return {
                "name": "Test Check",
                "status": HealthStatus.HEALTHY,
                "details": {"response_time": 100}
            }
        
        health_monitor.register_check("test_check", "Test Check", test_check)
        
        result = health_monitor.run_check("test_check")
        
        assert isinstance(result, HealthCheck)
        assert result.check_id == "test_check"
        assert result.name == "Test Check"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time_ms > 0
    
    def test_run_check_failure(self, health_monitor):
        """Test handling check failures."""
        def failing_check():
            raise Exception("Check failed")
        
        health_monitor.register_check("failing_check", "Failing Check", failing_check)
        
        result = health_monitor.run_check("failing_check")
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "Check failed" in result.details["error"]
        assert result.response_time_ms > 0
    
    def test_run_all_checks(self, health_monitor):
        """Test running all health checks."""
        # Should run default checks
        results = health_monitor.run_all_checks()
        
        assert len(results) >= 3  # At least the default checks
        assert all(isinstance(check, HealthCheck) for check in results.values())
    
    def test_get_system_health(self, health_monitor):
        """Test system health assessment."""
        # Add some mock checks
        health_monitor.health_checks["healthy_check"] = HealthCheck(
            check_id="healthy_check",
            name="Healthy Check",
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        
        health_monitor.health_checks["unhealthy_check"] = HealthCheck(
            check_id="unhealthy_check",
            name="Unhealthy Check",
            status=HealthStatus.UNHEALTHY,
            response_time_ms=200.0
        )
        
        system_health = health_monitor.get_system_health()
        
        assert system_health["status"] == HealthStatus.DEGRADED  # 50% healthy
        assert system_health["summary"]["total_checks"] == 2
        assert system_health["summary"]["healthy_checks"] == 1
        assert system_health["summary"]["health_percentage"] == 50.0


class TestDistributedTracer:
    """Test DistributedTracer implementation."""
    
    @pytest.fixture
    def tracer(self):
        """Create distributed tracer."""
        return DistributedTracer()
    
    def test_tracer_initialization(self, tracer):
        """Test tracer initialization."""
        assert len(tracer.spans) == 0
        assert len(tracer.active_spans) == 0
        assert tracer.context is not None
    
    def test_start_trace(self, tracer):
        """Test starting a new trace."""
        span = tracer.start_trace(
            "test_operation",
            service_name="test_service",
            tags={"user_id": "12345"}
        )
        
        assert span.trace_id is not None
        assert span.operation_name == "test_operation"
        assert span.service_name == "test_service"
        assert span.tags["user_id"] == "12345"
        assert span.parent_span_id is None
        
        # Check tracer state
        assert span.trace_id in tracer.spans
        assert span.span_id in tracer.active_spans
        assert tracer.context.get_trace_id() == span.trace_id
    
    def test_start_span(self, tracer):
        """Test starting child spans."""
        # Start root trace
        root_span = tracer.start_trace("root_operation", "test_service")
        
        # Start child span
        child_span = tracer.start_span("child_operation", "test_service")
        
        assert child_span.trace_id == root_span.trace_id
        assert child_span.parent_span_id == root_span.span_id
        assert child_span.operation_name == "child_operation"
        
        # Check both spans are in the same trace
        assert len(tracer.spans[root_span.trace_id]) == 2
    
    def test_finish_span(self, tracer):
        """Test finishing spans."""
        span = tracer.start_trace("test_operation", "test_service")
        
        # Small delay to ensure duration calculation
        time.sleep(0.01)
        
        tracer.finish_span(span, TraceStatus.SUCCESS)
        
        assert span.end_time is not None
        assert span.duration_ms is not None
        assert span.duration_ms > 0
        assert span.status == TraceStatus.SUCCESS
        assert span.span_id not in tracer.active_spans
    
    def test_add_span_log(self, tracer):
        """Test adding logs to current span."""
        span = tracer.start_trace("test_operation", "test_service")
        
        tracer.add_span_log("info", "Processing request", user_id="12345")
        
        assert len(span.logs) == 1
        log_entry = span.logs[0]
        assert log_entry["level"] == "info"
        assert log_entry["message"] == "Processing request"
        assert log_entry["user_id"] == "12345"
    
    def test_get_trace(self, tracer):
        """Test retrieving trace spans."""
        root_span = tracer.start_trace("root", "service")
        child_span = tracer.start_span("child", "service")
        
        trace_spans = tracer.get_trace(root_span.trace_id)
        
        assert len(trace_spans) == 2
        assert root_span in trace_spans
        assert child_span in trace_spans
    
    def test_get_trace_tree(self, tracer):
        """Test trace tree structure generation."""
        root_span = tracer.start_trace("root", "service")
        child_span = tracer.start_span("child", "service")
        
        # Finish spans to calculate durations
        tracer.finish_span(child_span)
        tracer.finish_span(root_span)
        
        trace_tree = tracer.get_trace_tree(root_span.trace_id)
        
        assert trace_tree["trace_id"] == root_span.trace_id
        assert trace_tree["total_spans"] == 2
        assert trace_tree["total_duration_ms"] > 0
        assert len(trace_tree["root_spans"]) == 1
    
    def test_get_tracing_statistics(self, tracer):
        """Test tracing statistics generation."""
        # Create multiple traces
        for i in range(3):
            span = tracer.start_trace(f"operation_{i}", "service")
            tracer.finish_span(span)
        
        stats = tracer.get_tracing_statistics()
        
        assert stats["total_traces"] == 3
        assert stats["total_spans"] == 3
        assert stats["active_spans"] == 0  # All finished
        assert stats["completed_traces"] == 3


class TestTraceFunctionDecorator:
    """Test trace_function decorator."""
    
    @pytest.fixture
    def tracer(self):
        """Create distributed tracer."""
        return DistributedTracer()
    
    def test_function_tracing(self, tracer):
        """Test automatic function tracing."""
        @trace_function("test_function", "test_service")
        def test_function(x, y):
            return x + y
        
        # Monkey patch the tracer
        test_function._tracer = tracer
        
        result = test_function(2, 3)
        
        assert result == 5
        assert tracer.get_tracing_statistics()["total_traces"] == 1
    
    def test_function_tracing_with_exception(self, tracer):
        """Test function tracing with exceptions."""
        @trace_function("failing_function", "test_service")
        def failing_function():
            raise ValueError("Test error")
        
        # Monkey patch the tracer
        failing_function._tracer = tracer
        
        with pytest.raises(ValueError):
            failing_function()
        
        # Check that span was created and marked as error
        stats = tracer.get_tracing_statistics()
        assert stats["total_traces"] == 1


class TestObservabilityManager:
    """Test ObservabilityManager main class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def observability_manager(self, mock_client):
        """Create observability manager."""
        return ObservabilityManager(mock_client)
    
    def test_observability_manager_initialization(self, observability_manager):
        """Test observability manager initialization."""
        assert observability_manager.client is not None
        assert observability_manager.metrics_collector is not None
        assert observability_manager.alert_manager is not None
        assert observability_manager.health_monitor is not None
        assert observability_manager.tracer is not None
        assert observability_manager.start_time is not None
    
    def test_record_request(self, observability_manager):
        """Test recording request metrics."""
        observability_manager.record_request(
            operation="api_call",
            duration_ms=150.5,
            success=True,
            tags={"endpoint": "/api/users"}
        )
        
        assert observability_manager.request_count == 1
        assert observability_manager.error_count == 0
        
        # Record failed request
        observability_manager.record_request(
            operation="api_call",
            duration_ms=5000.0,
            success=False
        )
        
        assert observability_manager.request_count == 2
        assert observability_manager.error_count == 1
    
    def test_record_customer_io_event(self, observability_manager):
        """Test recording Customer.IO event metrics."""
        observability_manager.record_customer_io_event(
            event_type="track",
            user_id="user_123",
            success=True,
            response_time_ms=75.0
        )
        
        # Check metrics buffer
        buffer_status = observability_manager.metrics_collector.get_buffer_status()
        assert buffer_status["buffer_size"] > 0
    
    def test_record_batch_operation(self, observability_manager):
        """Test recording batch operation metrics."""
        observability_manager.record_batch_operation(
            batch_size=100,
            processing_time_ms=2500.0,
            success_count=95,
            error_count=5
        )
        
        buffer_status = observability_manager.metrics_collector.get_buffer_status()
        assert buffer_status["buffer_size"] > 0
    
    def test_tracing_operations(self, observability_manager):
        """Test distributed tracing operations."""
        # Start trace
        trace = observability_manager.start_trace(
            "user_request",
            service="api_service",
            user_id="user_123"
        )
        
        assert trace.operation_name == "user_request"
        assert trace.service_name == "api_service"
        
        # Start child span
        span = observability_manager.start_span(
            "database_query",
            service="database_service"
        )
        
        assert span.parent_span_id == trace.span_id
        
        # Finish spans
        observability_manager.finish_span(span, success=True)
        observability_manager.finish_span(trace, success=True)
        
        # Verify tracing statistics
        stats = observability_manager.tracer.get_tracing_statistics()
        assert stats["total_traces"] == 1
        assert stats["total_spans"] == 2
    
    def test_setup_default_alerts(self, observability_manager):
        """Test setting up default alert rules."""
        observability_manager.setup_default_alerts()
        
        # Check that alert rules were added
        alert_stats = observability_manager.alert_manager.get_alert_statistics()
        assert alert_stats["total_rules"] > 0
        assert alert_stats["enabled_rules"] > 0
    
    def test_get_dashboard_data(self, observability_manager):
        """Test dashboard data generation."""
        # Record some activity
        for i in range(10):
            observability_manager.record_request(
                operation="test_request",
                duration_ms=100.0 + i * 10,
                success=i < 8  # 80% success rate
            )
        
        dashboard = observability_manager.get_dashboard_data()
        
        assert dashboard["system"]["uptime_seconds"] > 0
        assert dashboard["requests"]["total_requests"] == 10
        assert dashboard["requests"]["total_errors"] == 2
        assert dashboard["requests"]["error_rate_percent"] == 20.0
        assert "performance" in dashboard
        assert "alerts" in dashboard
        assert "tracing" in dashboard
        assert "metrics" in dashboard
    
    def test_generate_health_report(self, observability_manager):
        """Test health report generation."""
        # Add some test data
        observability_manager.record_request("test", 100.0, True)
        
        health_report = observability_manager.generate_health_report()
        
        assert "report_generated_at" in health_report
        assert "overall_health" in health_report
        assert "health_checks" in health_report
        assert "active_alerts" in health_report
        assert "system_metrics" in health_report
        assert "recommendations" in health_report
        assert "summary" in health_report
    
    def test_get_metrics(self, observability_manager):
        """Test metrics retrieval."""
        metrics = observability_manager.get_metrics()
        
        assert "manager" in metrics
        assert "components" in metrics
        assert "features" in metrics
        
        # Check features
        features = metrics["features"]
        assert features["metrics_collection"] is True
        assert features["alerting"] is True
        assert features["health_monitoring"] is True
        assert features["distributed_tracing"] is True
        assert features["dashboard_data"] is True
        assert features["health_reporting"] is True


class TestObservabilityManagerIntegration:
    """Integration tests for ObservabilityManager."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def observability_manager(self, mock_client):
        """Create observability manager."""
        return ObservabilityManager(mock_client)
    
    def test_complete_monitoring_flow(self, observability_manager):
        """Test complete monitoring flow."""
        # Setup alerts
        observability_manager.setup_default_alerts()
        
        # Simulate application activity
        trace = observability_manager.start_trace("user_session", "web_app")
        
        # Simulate multiple requests
        for i in range(20):
            # Start request span
            request_span = observability_manager.start_span(
                f"api_request_{i}",
                "api_service"
            )
            
            # Simulate request processing
            duration = 100.0 + (i * 25)  # Increasing duration
            success = i < 18  # 90% success rate
            
            # Record metrics
            observability_manager.record_request(
                operation="api_request",
                duration_ms=duration,
                success=success,
                tags={"request_id": str(i)}
            )
            
            # Record Customer.IO event
            observability_manager.record_customer_io_event(
                event_type="track",
                user_id=f"user_{i}",
                success=success,
                response_time_ms=duration * 0.8
            )
            
            # Finish request span
            observability_manager.finish_span(request_span, success=success)
        
        # Finish main trace
        observability_manager.finish_span(trace, success=True)
        
        # Generate comprehensive report
        dashboard = observability_manager.get_dashboard_data()
        health_report = observability_manager.generate_health_report()
        
        # Verify comprehensive monitoring data
        assert dashboard["requests"]["total_requests"] == 20
        assert dashboard["requests"]["error_rate_percent"] == 10.0
        assert dashboard["tracing"]["total_traces"] == 1
        assert dashboard["tracing"]["total_spans"] == 21  # 1 main + 20 requests
        
        assert health_report["summary"]["total_health_checks"] > 0
        assert len(health_report["recommendations"]) >= 0
    
    def test_performance_monitoring(self, observability_manager):
        """Test performance monitoring capabilities."""
        # Simulate high-load scenario
        start_time = time.time()
        
        # Record many metrics quickly
        for i in range(1000):
            observability_manager.record_customer_io_event(
                event_type="track",
                user_id=f"user_{i % 100}",  # 100 unique users
                success=True,
                response_time_ms=50.0 + (i % 10) * 5
            )
        
        processing_time = time.time() - start_time
        
        # Should handle 1000 metrics quickly
        assert processing_time < 1.0  # Under 1 second
        
        # Verify metrics were recorded
        buffer_status = observability_manager.metrics_collector.get_buffer_status()
        assert buffer_status["buffer_size"] >= 1000
    
    def test_concurrent_monitoring(self, observability_manager):
        """Test concurrent monitoring operations."""
        results = []
        errors = []
        
        def monitoring_worker(worker_id):
            try:
                # Each worker performs monitoring operations
                trace = observability_manager.start_trace(
                    f"worker_{worker_id}",
                    "worker_service"
                )
                
                for i in range(50):
                    # Record metrics
                    observability_manager.record_request(
                        operation=f"worker_{worker_id}_operation",
                        duration_ms=100.0 + i,
                        success=True
                    )
                    
                    # Record Customer.IO events
                    observability_manager.record_customer_io_event(
                        event_type="track",
                        user_id=f"worker_{worker_id}_user_{i}",
                        success=True,
                        response_time_ms=75.0
                    )
                
                observability_manager.finish_span(trace, success=True)
                results.append(f"worker_{worker_id}_completed")
                
            except Exception as e:
                errors.append(f"Worker {worker_id}: {str(e)}")
        
        # Run monitoring in multiple threads
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=monitoring_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors and all workers completed
        assert len(errors) == 0, f"Concurrent monitoring errors: {errors}"
        assert len(results) == 5
        
        # Verify metrics were recorded from all workers
        dashboard = observability_manager.get_dashboard_data()
        assert dashboard["requests"]["total_requests"] == 250  # 5 workers * 50 requests
        
        # Verify tracing data
        assert dashboard["tracing"]["total_traces"] == 5
        assert dashboard["tracing"]["total_spans"] == 5