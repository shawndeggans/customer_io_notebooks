"""
Comprehensive tests for Customer.IO Pipeline Manager.

Tests cover:
- Pipeline stage types, statuses, and execution strategies
- Data quality metrics and validation
- Pipeline stage execution framework
- Pipeline orchestration and dependency management
- Pipeline monitoring and analytics
- Error handling and retry mechanisms
- Performance tracking and optimization
- Thread safety and concurrent execution
"""

import pytest
import asyncio
import threading
import time
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from utils.pipeline_manager import (
    PipelineStageType,
    PipelineStatus,
    ExecutionStrategy,
    DataSourceType,
    DataQualityRule,
    TriggerType,
    DataQualityMetrics,
    PipelineStage,
    PipelineExecution,
    DataExtractionStage,
    DataTransformationStage,
    CustomerIOLoadStage,
    PipelineOrchestrator,
    PipelineMonitor,
    PipelineManager
)
from utils.api_client import CustomerIOClient
from utils.error_handlers import CustomerIOError


class TestPipelineStageType:
    """Test PipelineStageType enum."""
    
    def test_pipeline_stage_type_values(self):
        """Test all pipeline stage type values."""
        assert PipelineStageType.EXTRACT == "extract"
        assert PipelineStageType.TRANSFORM == "transform"
        assert PipelineStageType.LOAD == "load"
        assert PipelineStageType.VALIDATE == "validate"
        assert PipelineStageType.MONITOR == "monitor"
        assert PipelineStageType.NOTIFY == "notify"
    
    def test_pipeline_stage_type_membership(self):
        """Test pipeline stage type membership."""
        valid_types = [stage_type.value for stage_type in PipelineStageType]
        assert "extract" in valid_types
        assert "invalid_type" not in valid_types


class TestPipelineStatus:
    """Test PipelineStatus enum."""
    
    def test_pipeline_status_values(self):
        """Test all pipeline status values."""
        assert PipelineStatus.PENDING == "pending"
        assert PipelineStatus.RUNNING == "running"
        assert PipelineStatus.COMPLETED == "completed"
        assert PipelineStatus.FAILED == "failed"
        assert PipelineStatus.CANCELLED == "cancelled"
        assert PipelineStatus.SKIPPED == "skipped"
    
    def test_pipeline_status_membership(self):
        """Test pipeline status membership."""
        valid_statuses = [status.value for status in PipelineStatus]
        assert "completed" in valid_statuses
        assert "invalid_status" not in valid_statuses


class TestExecutionStrategy:
    """Test ExecutionStrategy enum."""
    
    def test_execution_strategy_values(self):
        """Test all execution strategy values."""
        assert ExecutionStrategy.SEQUENTIAL == "sequential"
        assert ExecutionStrategy.PARALLEL == "parallel"
        assert ExecutionStrategy.CONDITIONAL == "conditional"
        assert ExecutionStrategy.HYBRID == "hybrid"


class TestDataQualityMetrics:
    """Test DataQualityMetrics data model."""
    
    def test_valid_data_quality_metrics(self):
        """Test valid data quality metrics creation."""
        metrics = DataQualityMetrics(
            total_records=1000,
            valid_records=950,
            invalid_records=50,
            duplicate_records=25,
            null_records=15,
            quality_score=95.0,
            completeness_score=98.5,
            accuracy_score=92.0,
            consistency_score=96.5,
            validation_rules_passed=8,
            validation_rules_failed=2,
            data_freshness_hours=2.5
        )
        
        assert metrics.total_records == 1000
        assert metrics.valid_records == 950
        assert metrics.invalid_records == 50
        assert metrics.quality_score == 95.0
        assert metrics.completeness_score == 98.5
        assert metrics.data_freshness_hours == 2.5
    
    def test_data_quality_metrics_validation(self):
        """Test data quality metrics validation."""
        # Test negative values
        with pytest.raises(ValidationError):
            DataQualityMetrics(
                total_records=-1,
                valid_records=100
            )
        
        # Test quality score bounds
        with pytest.raises(ValidationError):
            DataQualityMetrics(
                total_records=100,
                valid_records=90,
                quality_score=150.0  # > 100
            )
        
        with pytest.raises(ValidationError):
            DataQualityMetrics(
                total_records=100,
                valid_records=90,
                quality_score=-10.0  # < 0
            )
    
    def test_calculate_error_rate(self):
        """Test error rate calculation."""
        metrics = DataQualityMetrics(
            total_records=1000,
            valid_records=900,
            invalid_records=100
        )
        
        error_rate = metrics.calculate_error_rate()
        assert error_rate == 10.0  # 100/1000 * 100
        
        # Test zero division
        zero_metrics = DataQualityMetrics(
            total_records=0,
            valid_records=0
        )
        assert zero_metrics.calculate_error_rate() == 0.0
    
    def test_is_quality_acceptable(self):
        """Test quality acceptance check."""
        good_metrics = DataQualityMetrics(
            total_records=1000,
            valid_records=950,
            quality_score=95.0
        )
        assert good_metrics.is_quality_acceptable() is True
        
        poor_metrics = DataQualityMetrics(
            total_records=1000,
            valid_records=700,
            quality_score=70.0
        )
        assert poor_metrics.is_quality_acceptable(threshold=80.0) is False


class TestPipelineStage:
    """Test PipelineStage data model."""
    
    def test_valid_pipeline_stage(self):
        """Test valid pipeline stage creation."""
        stage = PipelineStage(
            stage_id="extract_001",
            name="Data Extraction Stage",
            stage_type=PipelineStageType.EXTRACT,
            dependencies=["config_validation"],
            configuration={
                "source_type": "database",
                "connection_string": "postgresql://...",
                "query": "SELECT * FROM customers"
            },
            timeout_seconds=300,
            retry_attempts=3,
            parallel_execution=False
        )
        
        assert stage.stage_id == "extract_001"
        assert stage.name == "Data Extraction Stage"
        assert stage.stage_type == PipelineStageType.EXTRACT
        assert stage.timeout_seconds == 300
        assert stage.retry_attempts == 3
        assert stage.parallel_execution is False
        assert "config_validation" in stage.dependencies
    
    def test_pipeline_stage_validation(self):
        """Test pipeline stage validation."""
        # Test empty stage_id
        with pytest.raises(ValidationError):
            PipelineStage(
                stage_id="",
                name="Test Stage",
                stage_type=PipelineStageType.EXTRACT
            )
        
        # Test negative timeout
        with pytest.raises(ValidationError):
            PipelineStage(
                stage_id="test_001",
                name="Test Stage",
                stage_type=PipelineStageType.EXTRACT,
                timeout_seconds=-1
            )
    
    def test_add_dependency(self):
        """Test adding dependencies to pipeline stage."""
        stage = PipelineStage(
            stage_id="test_001",
            name="Test Stage",
            stage_type=PipelineStageType.TRANSFORM
        )
        
        stage.add_dependency("extract_001")
        assert "extract_001" in stage.dependencies
        
        # Test adding duplicate dependency
        stage.add_dependency("extract_001")
        assert stage.dependencies.count("extract_001") == 1
    
    def test_remove_dependency(self):
        """Test removing dependencies from pipeline stage."""
        stage = PipelineStage(
            stage_id="test_001",
            name="Test Stage",
            stage_type=PipelineStageType.TRANSFORM,
            dependencies=["extract_001", "validate_001"]
        )
        
        removed = stage.remove_dependency("extract_001")
        assert removed is True
        assert "extract_001" not in stage.dependencies
        assert "validate_001" in stage.dependencies
        
        # Test removing non-existent dependency
        removed = stage.remove_dependency("non_existent")
        assert removed is False


class TestPipelineExecution:
    """Test PipelineExecution data model."""
    
    def test_valid_pipeline_execution(self):
        """Test valid pipeline execution creation."""
        execution = PipelineExecution(
            execution_id="exec_001",
            pipeline_id="pipeline_001",
            trigger_type=TriggerType.SCHEDULE,
            execution_strategy=ExecutionStrategy.SEQUENTIAL,
            configuration={"batch_size": 1000}
        )
        
        assert execution.execution_id == "exec_001"
        assert execution.pipeline_id == "pipeline_001"
        assert execution.trigger_type == TriggerType.SCHEDULE
        assert execution.status == PipelineStatus.PENDING
        assert execution.configuration["batch_size"] == 1000
    
    def test_pipeline_execution_start_finish(self):
        """Test pipeline execution start and finish."""
        execution = PipelineExecution(
            execution_id="exec_001",
            pipeline_id="pipeline_001",
            trigger_type=TriggerType.MANUAL
        )
        
        # Test start
        execution.start()
        assert execution.status == PipelineStatus.RUNNING
        assert execution.started_at is not None
        
        # Test finish
        execution.finish(PipelineStatus.COMPLETED)
        assert execution.status == PipelineStatus.COMPLETED
        assert execution.completed_at is not None
        assert execution.duration_seconds is not None
        assert execution.duration_seconds > 0
    
    def test_add_stage_result(self):
        """Test adding stage results to execution."""
        execution = PipelineExecution(
            execution_id="exec_001",
            pipeline_id="pipeline_001",
            trigger_type=TriggerType.EVENT
        )
        
        stage_result = {
            "stage_id": "extract_001",
            "status": "completed",
            "duration_seconds": 45.2,
            "records_processed": 1000
        }
        
        execution.add_stage_result("extract_001", stage_result)
        assert "extract_001" in execution.stage_results
        assert execution.stage_results["extract_001"]["records_processed"] == 1000
    
    def test_get_total_records_processed(self):
        """Test calculating total records processed."""
        execution = PipelineExecution(
            execution_id="exec_001",
            pipeline_id="pipeline_001",
            trigger_type=TriggerType.SCHEDULE
        )
        
        execution.add_stage_result("extract_001", {"records_processed": 1000})
        execution.add_stage_result("transform_001", {"records_processed": 950})
        execution.add_stage_result("load_001", {"records_processed": 900})
        
        total = execution.get_total_records_processed()
        assert total == 2850  # Sum of all records processed


class TestDataExtractionStage:
    """Test DataExtractionStage implementation."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def extraction_stage(self, mock_client):
        """Create data extraction stage."""
        return DataExtractionStage(mock_client)
    
    def test_extraction_stage_initialization(self, extraction_stage):
        """Test data extraction stage initialization."""
        assert extraction_stage.stage_type == PipelineStageType.EXTRACT
        assert extraction_stage.client is not None
        assert extraction_stage.logger is not None
    
    @pytest.mark.asyncio
    async def test_execute_database_extraction(self, extraction_stage):
        """Test database data extraction."""
        stage_config = PipelineStage(
            stage_id="extract_db_001",
            name="Database Extraction",
            stage_type=PipelineStageType.EXTRACT,
            configuration={
                "source_type": "database",
                "connection_string": "postgresql://test",
                "query": "SELECT * FROM customers LIMIT 100"
            }
        )
        
        # Mock the database extraction
        with patch.object(extraction_stage, '_extract_from_database') as mock_extract:
            mock_extract.return_value = [{"id": 1, "name": "Test"} for _ in range(100)]
            
            result = await extraction_stage.execute(stage_config)
            
            assert result["status"] == "completed"
            assert result["records_extracted"] == 100
            assert result["source_type"] == "database"
            mock_extract.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_api_extraction(self, extraction_stage):
        """Test API data extraction."""
        stage_config = PipelineStage(
            stage_id="extract_api_001",
            name="API Extraction",
            stage_type=PipelineStageType.EXTRACT,
            configuration={
                "source_type": "api",
                "endpoint": "https://api.example.com/customers",
                "headers": {"Authorization": "Bearer token"}
            }
        )
        
        # Mock the API extraction
        with patch.object(extraction_stage, '_extract_from_api') as mock_extract:
            mock_extract.return_value = [{"id": 1, "name": "Test"} for _ in range(50)]
            
            result = await extraction_stage.execute(stage_config)
            
            assert result["status"] == "completed"
            assert result["records_extracted"] == 50
            assert result["source_type"] == "api"
            mock_extract.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_extraction_failure(self, extraction_stage):
        """Test extraction failure handling."""
        stage_config = PipelineStage(
            stage_id="extract_fail_001",
            name="Failed Extraction",
            stage_type=PipelineStageType.EXTRACT,
            configuration={
                "source_type": "database",
                "connection_string": "invalid://connection"
            }
        )
        
        # Mock extraction failure
        with patch.object(extraction_stage, '_extract_from_database') as mock_extract:
            mock_extract.side_effect = Exception("Connection failed")
            
            result = await extraction_stage.execute(stage_config)
            
            assert result["status"] == "failed"
            assert "Connection failed" in result["error_message"]


class TestDataTransformationStage:
    """Test DataTransformationStage implementation."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def transformation_stage(self, mock_client):
        """Create data transformation stage."""
        return DataTransformationStage(mock_client)
    
    def test_transformation_stage_initialization(self, transformation_stage):
        """Test data transformation stage initialization."""
        assert transformation_stage.stage_type == PipelineStageType.TRANSFORM
        assert transformation_stage.client is not None
    
    @pytest.mark.asyncio
    async def test_execute_data_transformation(self, transformation_stage):
        """Test data transformation execution."""
        stage_config = PipelineStage(
            stage_id="transform_001",
            name="Data Transformation",
            stage_type=PipelineStageType.TRANSFORM,
            configuration={
                "transformations": [
                    {"type": "normalize_email", "column": "email"},
                    {"type": "format_phone", "column": "phone"}
                ],
                "validation_rules": ["required_fields", "email_format"]
            }
        )
        
        input_data = [
            {"id": 1, "email": "TEST@EXAMPLE.COM", "phone": "1234567890"},
            {"id": 2, "email": "user@test.com", "phone": "9876543210"}
        ]
        
        # Mock transformation methods
        with patch.object(transformation_stage, '_apply_transformations') as mock_transform:
            mock_transform.return_value = [
                {"id": 1, "email": "test@example.com", "phone": "+1-234-567-8900"},
                {"id": 2, "email": "user@test.com", "phone": "+1-987-654-3210"}
            ]
            
            result = await transformation_stage.execute(stage_config, input_data)
            
            assert result["status"] == "completed"
            assert result["records_transformed"] == 2
            assert len(result["transformed_data"]) == 2
            mock_transform.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_data_validation(self, transformation_stage):
        """Test data validation during transformation."""
        stage_config = PipelineStage(
            stage_id="validate_001",
            name="Data Validation",
            stage_type=PipelineStageType.TRANSFORM,
            configuration={
                "validation_rules": [
                    {"rule": "not_null", "columns": ["id", "email"]},
                    {"rule": "email_format", "column": "email"}
                ]
            }
        )
        
        input_data = [
            {"id": 1, "email": "valid@example.com"},
            {"id": 2, "email": "invalid-email"},
            {"id": None, "email": "test@example.com"}
        ]
        
        with patch.object(transformation_stage, '_validate_data') as mock_validate:
            mock_validate.return_value = {
                "valid_records": 1,
                "invalid_records": 2,
                "validation_errors": ["Invalid email format", "Null ID"]
            }
            
            result = await transformation_stage.execute(stage_config, input_data)
            
            assert result["status"] == "completed"
            assert result["valid_records"] == 1
            assert result["invalid_records"] == 2


class TestCustomerIOLoadStage:
    """Test CustomerIOLoadStage implementation."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.batch.return_value = {"success": True, "processed": 100}
        return client
    
    @pytest.fixture
    def load_stage(self, mock_client):
        """Create Customer.IO load stage."""
        return CustomerIOLoadStage(mock_client)
    
    def test_load_stage_initialization(self, load_stage):
        """Test Customer.IO load stage initialization."""
        assert load_stage.stage_type == PipelineStageType.LOAD
        assert load_stage.client is not None
    
    @pytest.mark.asyncio
    async def test_execute_customer_load(self, load_stage, mock_client):
        """Test customer data loading to Customer.IO."""
        stage_config = PipelineStage(
            stage_id="load_customers_001",
            name="Load Customers",
            stage_type=PipelineStageType.LOAD,
            configuration={
                "operation": "identify",
                "batch_size": 50,
                "rate_limit_delay": 0.1
            }
        )
        
        customer_data = [
            {"userId": "user_001", "traits": {"email": "test1@example.com"}},
            {"userId": "user_002", "traits": {"email": "test2@example.com"}}
        ]
        
        result = await load_stage.execute(stage_config, customer_data)
        
        assert result["status"] == "completed"
        assert result["records_loaded"] == 2
        assert result["operation"] == "identify"
        assert mock_client.batch.called
    
    @pytest.mark.asyncio
    async def test_execute_event_load(self, load_stage, mock_client):
        """Test event data loading to Customer.IO."""
        stage_config = PipelineStage(
            stage_id="load_events_001",
            name="Load Events",
            stage_type=PipelineStageType.LOAD,
            configuration={
                "operation": "track",
                "batch_size": 100
            }
        )
        
        event_data = [
            {"userId": "user_001", "event": "Product Viewed", "properties": {"product_id": "123"}},
            {"userId": "user_002", "event": "Purchase", "properties": {"amount": 99.99}}
        ]
        
        result = await load_stage.execute(stage_config, event_data)
        
        assert result["status"] == "completed"
        assert result["records_loaded"] == 2
        assert result["operation"] == "track"
    
    @pytest.mark.asyncio
    async def test_execute_load_failure(self, load_stage, mock_client):
        """Test load failure handling."""
        stage_config = PipelineStage(
            stage_id="load_fail_001",
            name="Failed Load",
            stage_type=PipelineStageType.LOAD,
            configuration={"operation": "identify"}
        )
        
        # Mock API failure
        mock_client.batch.side_effect = CustomerIOError("API limit exceeded")
        
        customer_data = [{"userId": "user_001", "traits": {"email": "test@example.com"}}]
        
        result = await load_stage.execute(stage_config, customer_data)
        
        assert result["status"] == "failed"
        assert "API limit exceeded" in result["error_message"]


class TestPipelineOrchestrator:
    """Test PipelineOrchestrator implementation."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def orchestrator(self, mock_client):
        """Create pipeline orchestrator."""
        return PipelineOrchestrator(mock_client)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test pipeline orchestrator initialization."""
        assert orchestrator.client is not None
        assert orchestrator.stage_executors is not None
        assert len(orchestrator.stage_executors) > 0
    
    def test_register_pipeline(self, orchestrator):
        """Test pipeline registration."""
        stages = [
            PipelineStage(
                stage_id="extract_001",
                name="Extract Data",
                stage_type=PipelineStageType.EXTRACT
            ),
            PipelineStage(
                stage_id="transform_001",
                name="Transform Data",
                stage_type=PipelineStageType.TRANSFORM,
                dependencies=["extract_001"]
            )
        ]
        
        pipeline_id = orchestrator.register_pipeline("test_pipeline", stages)
        
        assert pipeline_id in orchestrator.registered_pipelines
        assert len(orchestrator.registered_pipelines[pipeline_id]) == 2
    
    def test_validate_pipeline_dag(self, orchestrator):
        """Test pipeline DAG validation."""
        # Valid DAG
        valid_stages = [
            PipelineStage(stage_id="stage_1", name="Stage 1", stage_type=PipelineStageType.EXTRACT),
            PipelineStage(stage_id="stage_2", name="Stage 2", stage_type=PipelineStageType.TRANSFORM, dependencies=["stage_1"]),
            PipelineStage(stage_id="stage_3", name="Stage 3", stage_type=PipelineStageType.LOAD, dependencies=["stage_2"])
        ]
        
        is_valid, error = orchestrator.validate_pipeline_dag(valid_stages)
        assert is_valid is True
        assert error is None
        
        # Circular dependency
        circular_stages = [
            PipelineStage(stage_id="stage_1", name="Stage 1", stage_type=PipelineStageType.EXTRACT, dependencies=["stage_2"]),
            PipelineStage(stage_id="stage_2", name="Stage 2", stage_type=PipelineStageType.TRANSFORM, dependencies=["stage_1"])
        ]
        
        is_valid, error = orchestrator.validate_pipeline_dag(circular_stages)
        assert is_valid is False
        assert "circular dependency" in error.lower()
    
    @pytest.mark.asyncio
    async def test_execute_pipeline(self, orchestrator):
        """Test pipeline execution."""
        stages = [
            PipelineStage(
                stage_id="extract_001",
                name="Extract Data",
                stage_type=PipelineStageType.EXTRACT,
                configuration={"source_type": "database"}
            ),
            PipelineStage(
                stage_id="transform_001",
                name="Transform Data",
                stage_type=PipelineStageType.TRANSFORM,
                dependencies=["extract_001"]
            )
        ]
        
        pipeline_id = orchestrator.register_pipeline("test_pipeline", stages)
        
        # Mock stage executions
        with patch.object(orchestrator.stage_executors[PipelineStageType.EXTRACT], 'execute') as mock_extract, \
             patch.object(orchestrator.stage_executors[PipelineStageType.TRANSFORM], 'execute') as mock_transform:
            
            mock_extract.return_value = {"status": "completed", "records_extracted": 100}
            mock_transform.return_value = {"status": "completed", "records_transformed": 95}
            
            execution = await orchestrator.execute_pipeline(
                pipeline_id,
                execution_strategy=ExecutionStrategy.SEQUENTIAL,
                trigger_type=TriggerType.MANUAL
            )
            
            assert execution.status == PipelineStatus.COMPLETED
            assert len(execution.stage_results) == 2
            assert mock_extract.called
            assert mock_transform.called


class TestPipelineMonitor:
    """Test PipelineMonitor implementation."""
    
    @pytest.fixture
    def monitor(self):
        """Create pipeline monitor."""
        return PipelineMonitor()
    
    def test_monitor_initialization(self, monitor):
        """Test pipeline monitor initialization."""
        assert monitor.execution_history == []
        assert monitor.performance_metrics == {}
        assert monitor.alert_thresholds is not None
    
    def test_record_execution(self, monitor):
        """Test recording pipeline execution."""
        execution = PipelineExecution(
            execution_id="exec_001",
            pipeline_id="pipeline_001",
            trigger_type=TriggerType.SCHEDULE
        )
        execution.start()
        execution.finish(PipelineStatus.COMPLETED)
        
        monitor.record_execution(execution)
        
        assert len(monitor.execution_history) == 1
        assert monitor.execution_history[0] == execution
    
    def test_calculate_success_rate(self, monitor):
        """Test success rate calculation."""
        # Create executions with different statuses
        executions = []
        for i in range(10):
            execution = PipelineExecution(
                execution_id=f"exec_{i:03d}",
                pipeline_id="pipeline_001",
                trigger_type=TriggerType.SCHEDULE
            )
            execution.start()
            # 8 successful, 2 failed
            status = PipelineStatus.COMPLETED if i < 8 else PipelineStatus.FAILED
            execution.finish(status)
            monitor.record_execution(execution)
        
        success_rate = monitor.calculate_success_rate("pipeline_001")
        assert success_rate == 80.0  # 8/10 * 100
        
        # Test pipeline with no executions
        empty_rate = monitor.calculate_success_rate("nonexistent_pipeline")
        assert empty_rate == 0.0
    
    def test_get_average_duration(self, monitor):
        """Test average duration calculation."""
        durations = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        for i, duration in enumerate(durations):
            execution = PipelineExecution(
                execution_id=f"exec_{i:03d}",
                pipeline_id="pipeline_001",
                trigger_type=TriggerType.SCHEDULE
            )
            execution.start()
            time.sleep(0.01)  # Small delay to ensure duration
            execution.finish(PipelineStatus.COMPLETED)
            # Override duration for testing
            execution.duration_seconds = duration
            monitor.record_execution(execution)
        
        avg_duration = monitor.get_average_duration("pipeline_001")
        assert avg_duration == 30.0  # Average of durations
    
    def test_check_performance_alerts(self, monitor):
        """Test performance alert checking."""
        # Set alert thresholds
        monitor.alert_thresholds = {
            "max_duration_seconds": 60.0,
            "min_success_rate_percent": 90.0
        }
        
        # Create execution that exceeds duration threshold
        long_execution = PipelineExecution(
            execution_id="long_exec",
            pipeline_id="pipeline_001",
            trigger_type=TriggerType.SCHEDULE
        )
        long_execution.start()
        long_execution.finish(PipelineStatus.COMPLETED)
        long_execution.duration_seconds = 120.0
        monitor.record_execution(long_execution)
        
        alerts = monitor.check_performance_alerts("pipeline_001")
        
        assert len(alerts) > 0
        duration_alerts = [alert for alert in alerts if "duration" in alert["type"]]
        assert len(duration_alerts) > 0
    
    def test_get_pipeline_analytics(self, monitor):
        """Test pipeline analytics generation."""
        # Create sample executions
        for i in range(5):
            execution = PipelineExecution(
                execution_id=f"exec_{i:03d}",
                pipeline_id="pipeline_001",
                trigger_type=TriggerType.SCHEDULE
            )
            execution.start()
            execution.finish(PipelineStatus.COMPLETED)
            execution.duration_seconds = 10.0 + i * 5  # 10, 15, 20, 25, 30
            monitor.record_execution(execution)
        
        analytics = monitor.get_pipeline_analytics("pipeline_001")
        
        assert analytics["pipeline_id"] == "pipeline_001"
        assert analytics["total_executions"] == 5
        assert analytics["success_rate"] == 100.0
        assert analytics["average_duration"] == 20.0  # (10+15+20+25+30)/5
        assert analytics["last_execution_status"] == PipelineStatus.COMPLETED


class TestPipelineManager:
    """Test PipelineManager main class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.batch.return_value = {"success": True}
        return client
    
    @pytest.fixture
    def pipeline_manager(self, mock_client):
        """Create pipeline manager."""
        return PipelineManager(mock_client)
    
    def test_pipeline_manager_initialization(self, pipeline_manager):
        """Test pipeline manager initialization."""
        assert pipeline_manager.client is not None
        assert pipeline_manager.orchestrator is not None
        assert pipeline_manager.monitor is not None
        assert pipeline_manager.logger is not None
    
    def test_create_pipeline(self, pipeline_manager):
        """Test pipeline creation."""
        pipeline_config = {
            "name": "Customer Data Pipeline",
            "description": "Process customer data from database to Customer.IO",
            "stages": [
                {
                    "stage_id": "extract_customers",
                    "name": "Extract Customer Data",
                    "stage_type": "extract",
                    "configuration": {"source": "database", "table": "customers"}
                },
                {
                    "stage_id": "transform_customers",
                    "name": "Transform Customer Data",
                    "stage_type": "transform",
                    "dependencies": ["extract_customers"]
                },
                {
                    "stage_id": "load_customers",
                    "name": "Load to Customer.IO",
                    "stage_type": "load",
                    "dependencies": ["transform_customers"]
                }
            ]
        }
        
        pipeline_id = pipeline_manager.create_pipeline(pipeline_config)
        
        assert pipeline_id is not None
        assert pipeline_id in pipeline_manager.orchestrator.registered_pipelines
        assert len(pipeline_manager.orchestrator.registered_pipelines[pipeline_id]) == 3
    
    @pytest.mark.asyncio
    async def test_run_pipeline(self, pipeline_manager):
        """Test pipeline execution."""
        # Create a simple pipeline
        pipeline_config = {
            "name": "Test Pipeline",
            "stages": [
                {
                    "stage_id": "extract_test",
                    "name": "Extract Test Data",
                    "stage_type": "extract",
                    "configuration": {"source_type": "database"}
                }
            ]
        }
        
        pipeline_id = pipeline_manager.create_pipeline(pipeline_config)
        
        # Mock the orchestrator execution
        with patch.object(pipeline_manager.orchestrator, 'execute_pipeline') as mock_execute:
            mock_execution = Mock()
            mock_execution.status = PipelineStatus.COMPLETED
            mock_execution.execution_id = "exec_001"
            mock_execute.return_value = mock_execution
            
            result = await pipeline_manager.run_pipeline(
                pipeline_id,
                trigger_type=TriggerType.MANUAL,
                execution_strategy=ExecutionStrategy.SEQUENTIAL
            )
            
            assert result.status == PipelineStatus.COMPLETED
            mock_execute.assert_called_once()
    
    def test_get_pipeline_status(self, pipeline_manager):
        """Test getting pipeline status."""
        # Mock an execution in the monitor
        execution = PipelineExecution(
            execution_id="exec_001",
            pipeline_id="pipeline_001",
            trigger_type=TriggerType.SCHEDULE
        )
        execution.start()
        execution.finish(PipelineStatus.COMPLETED)
        pipeline_manager.monitor.record_execution(execution)
        
        status = pipeline_manager.get_pipeline_status("pipeline_001")
        
        assert status["pipeline_id"] == "pipeline_001"
        assert status["last_execution_status"] == PipelineStatus.COMPLETED
        assert "total_executions" in status
        assert "success_rate" in status
    
    def test_list_pipelines(self, pipeline_manager):
        """Test listing registered pipelines."""
        # Register multiple pipelines
        for i in range(3):
            config = {
                "name": f"Pipeline {i}",
                "stages": [{
                    "stage_id": f"stage_{i}",
                    "name": f"Stage {i}",
                    "stage_type": "extract"
                }]
            }
            pipeline_manager.create_pipeline(config)
        
        pipelines = pipeline_manager.list_pipelines()
        
        assert len(pipelines) == 3
        assert all("pipeline_id" in p for p in pipelines)
        assert all("name" in p for p in pipelines)
    
    def test_get_pipeline_analytics(self, pipeline_manager):
        """Test getting pipeline analytics."""
        # Create and record some executions
        pipeline_id = "test_pipeline_001"
        
        for i in range(5):
            execution = PipelineExecution(
                execution_id=f"exec_{i:03d}",
                pipeline_id=pipeline_id,
                trigger_type=TriggerType.SCHEDULE
            )
            execution.start()
            execution.finish(PipelineStatus.COMPLETED if i < 4 else PipelineStatus.FAILED)
            pipeline_manager.monitor.record_execution(execution)
        
        analytics = pipeline_manager.get_pipeline_analytics(pipeline_id)
        
        assert analytics["pipeline_id"] == pipeline_id
        assert analytics["total_executions"] == 5
        assert analytics["success_rate"] == 80.0  # 4/5 * 100
        assert "average_duration" in analytics
        assert "performance_trends" in analytics
    
    def test_get_metrics(self, pipeline_manager):
        """Test getting pipeline manager metrics."""
        metrics = pipeline_manager.get_metrics()
        
        assert "orchestrator" in metrics
        assert "monitor" in metrics
        assert "features" in metrics
        assert metrics["features"]["pipeline_orchestration"] is True
        assert metrics["features"]["data_quality_monitoring"] is True
        assert metrics["features"]["stage_execution_framework"] is True


class TestPipelineManagerIntegration:
    """Integration tests for PipelineManager."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.batch.return_value = {"success": True, "processed": 100}
        return client
    
    @pytest.fixture
    def pipeline_manager(self, mock_client):
        """Create pipeline manager."""
        return PipelineManager(mock_client)
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_flow(self, pipeline_manager):
        """Test complete pipeline flow from creation to execution."""
        # Create comprehensive pipeline
        pipeline_config = {
            "name": "Customer Onboarding Pipeline",
            "description": "Complete customer onboarding data flow",
            "stages": [
                {
                    "stage_id": "extract_new_customers",
                    "name": "Extract New Customers",
                    "stage_type": "extract",
                    "configuration": {
                        "source_type": "database",
                        "query": "SELECT * FROM customers WHERE created_at > NOW() - INTERVAL '1 DAY'"
                    },
                    "timeout_seconds": 300
                },
                {
                    "stage_id": "validate_customer_data",
                    "name": "Validate Customer Data",
                    "stage_type": "validate",
                    "dependencies": ["extract_new_customers"],
                    "configuration": {
                        "validation_rules": ["email_format", "required_fields"]
                    }
                },
                {
                    "stage_id": "transform_for_customerio",
                    "name": "Transform for Customer.IO",
                    "stage_type": "transform",
                    "dependencies": ["validate_customer_data"],
                    "configuration": {
                        "transformations": ["normalize_email", "format_phone"]
                    }
                },
                {
                    "stage_id": "load_to_customerio",
                    "name": "Load to Customer.IO",
                    "stage_type": "load",
                    "dependencies": ["transform_for_customerio"],
                    "configuration": {
                        "operation": "identify",
                        "batch_size": 100
                    }
                }
            ]
        }
        
        # Create pipeline
        pipeline_id = pipeline_manager.create_pipeline(pipeline_config)
        assert pipeline_id is not None
        
        # Mock stage executions to simulate successful flow
        with patch.object(pipeline_manager.orchestrator.stage_executors[PipelineStageType.EXTRACT], 'execute') as mock_extract, \
             patch.object(pipeline_manager.orchestrator.stage_executors[PipelineStageType.VALIDATE], 'execute') as mock_validate, \
             patch.object(pipeline_manager.orchestrator.stage_executors[PipelineStageType.TRANSFORM], 'execute') as mock_transform, \
             patch.object(pipeline_manager.orchestrator.stage_executors[PipelineStageType.LOAD], 'execute') as mock_load:
            
            # Configure mock returns
            mock_extract.return_value = {
                "status": "completed",
                "records_extracted": 150,
                "extraction_time": 45.2
            }
            
            mock_validate.return_value = {
                "status": "completed",
                "records_validated": 150,
                "valid_records": 145,
                "invalid_records": 5
            }
            
            mock_transform.return_value = {
                "status": "completed",
                "records_transformed": 145,
                "transformation_time": 23.8
            }
            
            mock_load.return_value = {
                "status": "completed",
                "records_loaded": 145,
                "load_time": 67.1
            }
            
            # Execute pipeline
            execution = await pipeline_manager.run_pipeline(
                pipeline_id,
                trigger_type=TriggerType.SCHEDULE,
                execution_strategy=ExecutionStrategy.SEQUENTIAL
            )
            
            # Verify execution completed successfully
            assert execution.status == PipelineStatus.COMPLETED
            assert len(execution.stage_results) == 4
            
            # Verify all stages were called
            assert mock_extract.called
            assert mock_validate.called
            assert mock_transform.called
            assert mock_load.called
            
            # Verify stage execution order (sequential)
            call_order = [
                mock_extract.call_args[0][0].stage_id,
                mock_validate.call_args[0][0].stage_id,
                mock_transform.call_args[0][0].stage_id,
                mock_load.call_args[0][0].stage_id
            ]
            
            expected_order = [
                "extract_new_customers",
                "validate_customer_data", 
                "transform_for_customerio",
                "load_to_customerio"
            ]
            
            assert call_order == expected_order
        
        # Get pipeline status and verify analytics
        status = pipeline_manager.get_pipeline_status(pipeline_id)
        assert status["last_execution_status"] == PipelineStatus.COMPLETED
        assert status["total_executions"] == 1
        assert status["success_rate"] == 100.0
        
        # Get detailed analytics
        analytics = pipeline_manager.get_pipeline_analytics(pipeline_id)
        assert analytics["total_executions"] == 1
        assert analytics["success_rate"] == 100.0
        assert "stage_performance" in analytics
    
    def test_concurrent_pipeline_execution(self, pipeline_manager):
        """Test concurrent pipeline execution."""
        # Create multiple simple pipelines
        pipeline_ids = []
        for i in range(3):
            config = {
                "name": f"Concurrent Pipeline {i}",
                "stages": [{
                    "stage_id": f"extract_{i}",
                    "name": f"Extract {i}",
                    "stage_type": "extract",
                    "configuration": {"source_type": "api"}
                }]
            }
            pipeline_id = pipeline_manager.create_pipeline(config)
            pipeline_ids.append(pipeline_id)
        
        # Mock executions
        async def mock_pipeline_execution(pipeline_id, **kwargs):
            execution = PipelineExecution(
                execution_id=f"exec_{pipeline_id}",
                pipeline_id=pipeline_id,
                trigger_type=TriggerType.MANUAL
            )
            execution.start()
            # Simulate some work
            await asyncio.sleep(0.1)
            execution.finish(PipelineStatus.COMPLETED)
            return execution
        
        async def test_concurrent_execution():
            with patch.object(pipeline_manager.orchestrator, 'execute_pipeline', side_effect=mock_pipeline_execution):
                # Run pipelines concurrently
                tasks = [
                    pipeline_manager.run_pipeline(
                        pipeline_id,
                        trigger_type=TriggerType.MANUAL
                    )
                    for pipeline_id in pipeline_ids
                ]
                
                results = await asyncio.gather(*tasks)
                
                # Verify all completed successfully
                assert len(results) == 3
                assert all(r.status == PipelineStatus.COMPLETED for r in results)
        
        # Run the concurrent test
        asyncio.run(test_concurrent_execution())
    
    def test_pipeline_failure_and_recovery(self, pipeline_manager):
        """Test pipeline failure handling and recovery."""
        # Create pipeline with potential failure point
        pipeline_config = {
            "name": "Failure Test Pipeline",
            "stages": [
                {
                    "stage_id": "extract_data",
                    "name": "Extract Data",
                    "stage_type": "extract",
                    "retry_attempts": 2
                },
                {
                    "stage_id": "process_data",
                    "name": "Process Data", 
                    "stage_type": "transform",
                    "dependencies": ["extract_data"]
                }
            ]
        }
        
        pipeline_id = pipeline_manager.create_pipeline(pipeline_config)
        
        async def test_failure_recovery():
            call_count = 0
            
            async def mock_failing_extract(stage_config, input_data=None):
                nonlocal call_count
                call_count += 1
                if call_count < 2:  # Fail first time, succeed second
                    raise Exception("Temporary extraction failure")
                return {"status": "completed", "records_extracted": 100}
            
            async def mock_successful_transform(stage_config, input_data=None):
                return {"status": "completed", "records_transformed": 100}
            
            with patch.object(pipeline_manager.orchestrator.stage_executors[PipelineStageType.EXTRACT], 'execute', side_effect=mock_failing_extract), \
                 patch.object(pipeline_manager.orchestrator.stage_executors[PipelineStageType.TRANSFORM], 'execute', side_effect=mock_successful_transform):
                
                execution = await pipeline_manager.run_pipeline(
                    pipeline_id,
                    trigger_type=TriggerType.MANUAL
                )
                
                # Should succeed after retry
                assert execution.status == PipelineStatus.COMPLETED
                assert call_count == 2  # Failed once, then succeeded
        
        asyncio.run(test_failure_recovery())


class TestPipelineManagerPerformance:
    """Performance tests for PipelineManager."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def pipeline_manager(self, mock_client):
        """Create pipeline manager."""
        return PipelineManager(mock_client)
    
    def test_pipeline_creation_performance(self, pipeline_manager):
        """Test performance of pipeline creation."""
        import time
        
        start_time = time.time()
        
        # Create 100 pipelines
        for i in range(100):
            config = {
                "name": f"Performance Pipeline {i}",
                "stages": [
                    {
                        "stage_id": f"extract_{i}",
                        "name": f"Extract {i}",
                        "stage_type": "extract"
                    },
                    {
                        "stage_id": f"transform_{i}",
                        "name": f"Transform {i}",
                        "stage_type": "transform",
                        "dependencies": [f"extract_{i}"]
                    }
                ]
            }
            pipeline_manager.create_pipeline(config)
        
        creation_time = time.time() - start_time
        
        # Should create 100 pipelines in under 1 second
        assert creation_time < 1.0
        assert len(pipeline_manager.orchestrator.registered_pipelines) == 100
    
    def test_monitoring_performance_with_large_history(self, pipeline_manager):
        """Test monitoring performance with large execution history."""
        import time
        
        # Add many executions to history
        for i in range(1000):
            execution = PipelineExecution(
                execution_id=f"perf_exec_{i:04d}",
                pipeline_id="performance_pipeline",
                trigger_type=TriggerType.SCHEDULE
            )
            execution.start()
            execution.finish(PipelineStatus.COMPLETED)
            pipeline_manager.monitor.record_execution(execution)
        
        # Test analytics performance
        start_time = time.time()
        analytics = pipeline_manager.get_pipeline_analytics("performance_pipeline")
        analytics_time = time.time() - start_time
        
        # Should calculate analytics for 1000 executions quickly
        assert analytics_time < 0.1  # Under 100ms
        assert analytics["total_executions"] == 1000
        assert analytics["success_rate"] == 100.0
    
    def test_thread_safety(self, pipeline_manager):
        """Test thread safety of pipeline manager operations."""
        results = {}
        errors = []
        
        def create_pipelines(thread_id):
            try:
                for i in range(10):
                    config = {
                        "name": f"Thread {thread_id} Pipeline {i}",
                        "stages": [{
                            "stage_id": f"thread_{thread_id}_stage_{i}",
                            "name": f"Thread {thread_id} Stage {i}",
                            "stage_type": "extract"
                        }]
                    }
                    pipeline_id = pipeline_manager.create_pipeline(config)
                    results[f"thread_{thread_id}_pipeline_{i}"] = pipeline_id
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
        
        # Run pipeline creation in multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=create_pipelines, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors and all pipelines created
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 50  # 5 threads * 10 pipelines each
        assert len(pipeline_manager.orchestrator.registered_pipelines) == 50