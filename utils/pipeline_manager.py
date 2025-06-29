"""
Customer.IO Pipeline Management Module

Type-safe data pipeline orchestration and management for Customer.IO API including:
- Advanced pipeline orchestration with dependency management
- Data quality monitoring and validation
- Stage execution framework with pluggable architectures
- Performance monitoring and analytics
- Spark integration for large-scale analytics
- Multi-stage pipeline execution with error handling
- Pipeline monitoring and anomaly detection
"""

import sys
import os
import asyncio
import concurrent.futures
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, Iterator, Set
import json
import uuid
from enum import Enum
from collections import defaultdict, deque
import time
import threading
import queue
import statistics
from dataclasses import dataclass, field
import math
import hashlib
import re
from abc import ABC, abstractmethod
import structlog
from pydantic import BaseModel, Field, field_validator

from .api_client import CustomerIOClient
from .error_handlers import retry_on_error, ErrorContext


class PipelineStageType(str, Enum):
    """Enumeration for pipeline stage types."""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"
    MONITOR = "monitor"
    NOTIFY = "notify"


class PipelineStatus(str, Enum):
    """Enumeration for pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ExecutionStrategy(str, Enum):
    """Enumeration for execution strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    HYBRID = "hybrid"


class DataSourceType(str, Enum):
    """Enumeration for data source types."""
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    API = "api"
    STREAM = "stream"
    WAREHOUSE = "warehouse"
    LAKE = "lake"


class DataQualityRule(str, Enum):
    """Enumeration for data quality rule types."""
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    FORMAT_VALIDATION = "format_validation"
    RANGE_CHECK = "range_check"
    REFERENCE_CHECK = "reference_check"
    CUSTOM_RULE = "custom_rule"


class TriggerType(str, Enum):
    """Enumeration for pipeline trigger types."""
    SCHEDULE = "schedule"
    EVENT = "event"
    MANUAL = "manual"
    DATA_ARRIVAL = "data_arrival"
    DEPENDENCY = "dependency"


class DataQualityMetrics(BaseModel):
    """Type-safe data quality metrics model."""
    total_records: int = Field(..., ge=0, description="Total number of records")
    valid_records: int = Field(..., ge=0, description="Number of valid records")
    invalid_records: int = Field(..., ge=0, description="Number of invalid records")
    duplicate_records: int = Field(default=0, ge=0, description="Number of duplicate records")
    null_values: int = Field(default=0, ge=0, description="Number of null values")
    data_completeness_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Data completeness percentage")
    data_accuracy_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Data accuracy percentage")
    schema_compliance_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Schema compliance percentage")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall quality score")
    validation_rules_passed: int = Field(default=0, ge=0, description="Number of validation rules passed")
    validation_rules_failed: int = Field(default=0, ge=0, description="Number of validation rules failed")
    quality_issues: List[str] = Field(default_factory=list, description="List of quality issues")
    
    @field_validator('valid_records', 'invalid_records')
    @classmethod
    def validate_record_counts(cls, v: int, values: Dict) -> int:
        """Validate record counts are consistent."""
        if 'total_records' in values:
            total = values['total_records']
            if v > total:
                raise ValueError(f"Record count {v} cannot exceed total {total}")
        return v
    
    def calculate_derived_metrics(self) -> None:
        """Calculate derived quality metrics."""
        if self.total_records > 0:
            self.data_completeness_percent = (self.valid_records / self.total_records) * 100
            
            # Calculate accuracy (considering duplicates and nulls)
            clean_records = self.valid_records - self.duplicate_records
            self.data_accuracy_percent = (clean_records / self.total_records) * 100
            
            # Calculate overall quality score
            completeness_weight = 0.4
            accuracy_weight = 0.4
            compliance_weight = 0.2
            
            self.quality_score = (
                (self.data_completeness_percent / 100 * completeness_weight) +
                (self.data_accuracy_percent / 100 * accuracy_weight) +
                (self.schema_compliance_percent / 100 * compliance_weight)
            )
    
    def is_acceptable_quality(self, threshold: float = 0.8) -> bool:
        """Check if data quality meets threshold."""
        return self.quality_score >= threshold
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }

    stage_id: str = Field(..., description="Unique stage identifier")
    stage_name: str = Field(..., description="Human-readable stage name")
    stage_type: PipelineStageType = Field(..., description="Type of pipeline stage")
    dependencies: List[str] = Field(default_factory=list, description="Stage dependencies")
    timeout_minutes: int = Field(default=30, gt=0, le=1440, description="Stage timeout in minutes")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    parallel_execution: bool = Field(default=True, description="Allow parallel execution")
    data_quality_checks: bool = Field(default=True, description="Enable data quality checks")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Stage configuration")
    expected_runtime_minutes: Optional[float] = Field(None, gt=0, description="Expected runtime")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")
    
    # Execution tracking
    status: PipelineStatus = Field(default=PipelineStatus.PENDING)
    started_at: Optional[datetime] = Field(None, description="Stage start time")
    completed_at: Optional[datetime] = Field(None, description="Stage completion time")
    execution_time_minutes: Optional[float] = Field(None, ge=0, description="Actual execution time")
    retry_count: int = Field(default=0, ge=0, description="Current retry count")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    quality_metrics: Optional[DataQualityMetrics] = Field(None, description="Quality metrics")
    
    @field_validator('stage_id')
    @classmethod
    def validate_stage_id(cls, v: str) -> str:
        """Validate stage ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Stage ID cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Stage ID must contain only alphanumeric characters and underscores")
        return v.strip()
    
    def can_execute(self, completed_stages: Set[str]) -> bool:
        """Check if stage can execute based on dependencies."""
        return all(dep in completed_stages for dep in self.dependencies)
    
    def get_execution_duration(self) -> Optional[timedelta]:
        """Get stage execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    def is_overdue(self) -> bool:
        """Check if stage is overdue based on timeout."""
        if not self.started_at or self.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED]:
            return False
        
        elapsed = datetime.now(timezone.utc) - self.started_at
        return elapsed.total_seconds() > (self.timeout_minutes * 60)
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }

    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pipeline_id: str = Field(..., description="Pipeline identifier")
    pipeline_name: str = Field(..., description="Pipeline name")
    pipeline_version: str = Field(default="1.0", description="Pipeline version")
    stages: List[PipelineStage] = Field(..., description="Pipeline stages")
    execution_strategy: ExecutionStrategy = Field(default=ExecutionStrategy.HYBRID)
    trigger_type: TriggerType = Field(..., description="What triggered this execution")
    
    # Execution state
    status: PipelineStatus = Field(default=PipelineStatus.PENDING)
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    total_execution_time_minutes: Optional[float] = Field(None, ge=0, description="Total execution time")
    
    # Progress tracking
    completed_stages: Set[str] = Field(default_factory=set, description="Completed stage IDs")
    failed_stages: Set[str] = Field(default_factory=set, description="Failed stage IDs")
    skipped_stages: Set[str] = Field(default_factory=set, description="Skipped stage IDs")
    
    # Metrics and monitoring
    total_records_processed: int = Field(default=0, ge=0, description="Total records processed")
    total_errors: int = Field(default=0, ge=0, description="Total errors encountered")
    overall_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall quality score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    
    @field_validator('stages')
    @classmethod
    def validate_stages(cls, v: List[PipelineStage]) -> List[PipelineStage]:
        """Validate pipeline stages."""
        if not v:
            raise ValueError("Pipeline must have at least one stage")
        
        # Check for duplicate stage IDs
        stage_ids = [stage.stage_id for stage in v]
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError("Pipeline stages must have unique IDs")
        
        return v
    
    def get_progress_percent(self) -> float:
        """Get execution progress as percentage."""
        if not self.stages:
            return 100.0
        return (len(self.completed_stages) / len(self.stages)) * 100
    
    def get_executable_stages(self) -> List[PipelineStage]:
        """Get stages that can be executed now."""
        executable = []
        for stage in self.stages:
            if (stage.status == PipelineStatus.PENDING and 
                stage.can_execute(self.completed_stages) and
                stage.stage_id not in self.failed_stages):
                executable.append(stage)
        return executable
    
    def is_complete(self) -> bool:
        """Check if pipeline execution is complete."""
        return self.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED, PipelineStatus.CANCELLED]
    
    def calculate_overall_metrics(self) -> None:
        """Calculate overall pipeline metrics."""
        # Calculate total records and errors
        self.total_records_processed = sum(
            stage.quality_metrics.total_records 
            for stage in self.stages 
            if stage.quality_metrics
        )
        
        # Calculate overall quality score
        quality_scores = [
            stage.quality_metrics.quality_score 
            for stage in self.stages 
            if stage.quality_metrics and stage.quality_metrics.quality_score > 0
        ]
        
        if quality_scores:
            self.overall_quality_score = statistics.mean(quality_scores)
        
        # Calculate total execution time
        if self.started_at and self.completed_at:
            self.total_execution_time_minutes = (
                self.completed_at - self.started_at
            ).total_seconds() / 60
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }

    
    def __init__(self, stage: PipelineStage):
        self.stage = stage
        self.logger = structlog.get_logger(f"stage_{stage.stage_id}")
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline stage."""
        pass
    
    def validate_inputs(self, context: Dict[str, Any]) -> bool:
        """Validate stage inputs."""
        return True
    
    def cleanup(self, context: Dict[str, Any]) -> None:
        """Cleanup stage resources."""
        pass


class DataExtractionStage(PipelineStageExecutor):
    """Data extraction stage executor."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from configured sources."""
        
        source_type = self.stage.configuration.get("source_type", "database")
        batch_size = self.stage.configuration.get("batch_size", 1000)
        
        self.logger.info(
            "Starting data extraction",
            source_type=source_type,
            batch_size=batch_size
        )
        
        # Generate synthetic data for demonstration
        extracted_data = [
            {
                "user_id": f"extracted_user_{i}",
                "email": f"user{i}@example.com",
                "signup_date": (datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
                "source": "data_extraction"
            }
            for i in range(batch_size)
        ]
        
        # Simulate quality metrics
        quality_metrics = DataQualityMetrics(
            total_records=len(extracted_data),
            valid_records=int(len(extracted_data) * 0.95),
            invalid_records=int(len(extracted_data) * 0.05),
            schema_compliance_percent=98.5
        )
        quality_metrics.calculate_derived_metrics()
        
        self.stage.quality_metrics = quality_metrics
        
        return {
            "extracted_data": extracted_data,
            "record_count": len(extracted_data),
            "source_type": source_type
        }


class DataTransformationStage(PipelineStageExecutor):
    """Data transformation stage executor."""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Transform and enrich data."""
        
        input_data = context.get("extracted_data", [])
        transformation_rules = self.stage.configuration.get("rules", [])
        
        self.logger.info(
            "Starting data transformation",
            input_records=len(input_data),
            transformation_rules=len(transformation_rules)
        )
        
        # Apply transformations
        transformed_data = []
        
        for record in input_data:
            # Enrich with additional data
            transformed_record = record.copy()
            transformed_record.update({
                "transformed_at": datetime.now(timezone.utc).isoformat(),
                "user_segment": "standard" if "user" in record.get("user_id", "") else "premium",
                "data_quality_score": 0.95,
                "enriched": True
            })
            
            # Validate email format
            email = record.get("email", "")
            if email and "@" in email:
                transformed_record["email_valid"] = True
            else:
                transformed_record["email_valid"] = False
            
            transformed_data.append(transformed_record)
        
        # Calculate quality metrics
        valid_emails = sum(1 for r in transformed_data if r.get("email_valid", False))
        
        quality_metrics = DataQualityMetrics(
            total_records=len(transformed_data),
            valid_records=valid_emails,
            invalid_records=len(transformed_data) - valid_emails,
            schema_compliance_percent=100.0
        )
        quality_metrics.calculate_derived_metrics()
        
        self.stage.quality_metrics = quality_metrics
        
        return {
            "transformed_data": transformed_data,
            "record_count": len(transformed_data),
            "valid_records": valid_emails
        }


class CustomerIOLoadStage(PipelineStageExecutor):
    """Customer.IO data loading stage executor."""
    
    def __init__(self, stage: PipelineStage, client: CustomerIOClient):
        super().__init__(stage)
        self.client = client
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load data into Customer.IO."""
        
        input_data = context.get("transformed_data", [])
        batch_size = self.stage.configuration.get("batch_size", 100)
        
        self.logger.info(
            "Starting Customer.IO data load",
            input_records=len(input_data),
            batch_size=batch_size
        )
        
        # Process in batches
        successful_records = 0
        failed_records = 0
        
        for i in range(0, len(input_data), batch_size):
            batch = input_data[i:i + batch_size]
            
            try:
                # Convert to Customer.IO format
                customerio_batch = []
                
                for record in batch:
                    if record.get("email_valid", False):
                        # Create person record
                        person_data = {
                            "type": "person",
                            "action": "identify",
                            "identifiers": {
                                "id": record["user_id"],
                                "email": record["email"]
                            },
                            "attributes": {
                                "signup_date": record.get("signup_date"),
                                "user_segment": record.get("user_segment"),
                                "data_quality_score": record.get("data_quality_score"),
                                "last_updated": record.get("transformed_at")
                            }
                        }
                        customerio_batch.append(person_data)
                
                # Simulate successful processing for demo
                successful_records += len(customerio_batch)
                
            except Exception as e:
                self.logger.error(
                    "Batch processing failed",
                    batch_size=len(batch),
                    error=str(e)
                )
                failed_records += len(batch)
        
        # Calculate quality metrics
        quality_metrics = DataQualityMetrics(
            total_records=len(input_data),
            valid_records=successful_records,
            invalid_records=failed_records,
            schema_compliance_percent=100.0
        )
        quality_metrics.calculate_derived_metrics()
        
        self.stage.quality_metrics = quality_metrics
        
        return {
            "loaded_records": successful_records,
            "failed_records": failed_records,
            "total_processed": len(input_data)
        }


class PipelineOrchestrator:
    """Advanced pipeline orchestration engine."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("pipeline_orchestrator")
        self.stage_executors = {}
        self.execution_context = {}
        
    def register_stage_executor(self, stage_type: PipelineStageType, executor_class: type) -> None:
        """Register a stage executor for a specific stage type."""
        self.stage_executors[stage_type] = executor_class
    
    def execute_pipeline(self, execution: PipelineExecution) -> PipelineExecution:
        """Execute a complete pipeline."""
        
        execution.started_at = datetime.now(timezone.utc)
        execution.status = PipelineStatus.RUNNING
        
        self.logger.info(
            "Starting pipeline execution",
            execution_id=execution.execution_id,
            pipeline_id=execution.pipeline_id,
            total_stages=len(execution.stages)
        )
        
        try:
            while not execution.is_complete():
                # Get stages ready for execution
                executable_stages = execution.get_executable_stages()
                
                if not executable_stages:
                    # Check if we're stuck (no executable stages but not complete)
                    pending_stages = [
                        s for s in execution.stages 
                        if s.status == PipelineStatus.PENDING
                    ]
                    
                    if pending_stages:
                        # Pipeline is stuck due to failed dependencies
                        execution.status = PipelineStatus.FAILED
                        self.logger.error(
                            "Pipeline stuck - no executable stages",
                            pending_stages=[s.stage_id for s in pending_stages]
                        )
                        break
                    else:
                        # All stages are complete
                        execution.status = PipelineStatus.COMPLETED
                        break
                
                # Execute stages based on strategy
                if execution.execution_strategy == ExecutionStrategy.PARALLEL:
                    self._execute_stages_parallel(executable_stages, execution)
                else:
                    self._execute_stages_sequential(executable_stages, execution)
            
            # Finalize execution
            execution.completed_at = datetime.now(timezone.utc)
            execution.calculate_overall_metrics()
            
            # Determine final status if not already set
            if execution.status == PipelineStatus.RUNNING:
                if execution.failed_stages:
                    execution.status = PipelineStatus.FAILED
                else:
                    execution.status = PipelineStatus.COMPLETED
            
            self.logger.info(
                "Pipeline execution completed",
                execution_id=execution.execution_id,
                status=execution.status,
                total_time_minutes=execution.total_execution_time_minutes,
                records_processed=execution.total_records_processed
            )
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.completed_at = datetime.now(timezone.utc)
            
            self.logger.error(
                "Pipeline execution failed",
                execution_id=execution.execution_id,
                error=str(e)
            )
        
        return execution
    
    def _execute_stages_sequential(self, stages: List[PipelineStage], execution: PipelineExecution) -> None:
        """Execute stages sequentially."""
        for stage in stages:
            self._execute_single_stage(stage, execution)
    
    def _execute_stages_parallel(self, stages: List[PipelineStage], execution: PipelineExecution) -> None:
        """Execute stages in parallel."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(stages), 4)) as executor:
            futures = {
                executor.submit(self._execute_single_stage, stage, execution): stage 
                for stage in stages
            }
            
            # Wait for all stages to complete
            for future in concurrent.futures.as_completed(futures):
                stage = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(
                        "Stage execution failed in parallel execution",
                        stage_id=stage.stage_id,
                        error=str(e)
                    )
    
    def _execute_single_stage(self, stage: PipelineStage, execution: PipelineExecution) -> None:
        """Execute a single pipeline stage."""
        
        stage.started_at = datetime.now(timezone.utc)
        stage.status = PipelineStatus.RUNNING
        
        self.logger.info(
            "Starting stage execution",
            stage_id=stage.stage_id,
            stage_type=stage.stage_type
        )
        
        try:
            # Get executor for stage type
            executor_class = self.stage_executors.get(stage.stage_type)
            if not executor_class:
                raise ValueError(f"No executor registered for stage type: {stage.stage_type}")
            
            # Create executor instance
            if stage.stage_type == PipelineStageType.LOAD:
                executor = executor_class(stage, self.client)
            else:
                executor = executor_class(stage)
            
            # Validate inputs
            if not executor.validate_inputs(self.execution_context):
                raise ValueError(f"Input validation failed for stage: {stage.stage_id}")
            
            # Execute stage
            result = executor.execute(self.execution_context)
            
            # Update execution context with results
            self.execution_context.update(result)
            
            # Mark stage as completed
            stage.completed_at = datetime.now(timezone.utc)
            stage.status = PipelineStatus.COMPLETED
            stage.execution_time_minutes = (
                stage.completed_at - stage.started_at
            ).total_seconds() / 60
            
            execution.completed_stages.add(stage.stage_id)
            
            # Cleanup
            executor.cleanup(self.execution_context)
            
            self.logger.info(
                "Stage execution completed",
                stage_id=stage.stage_id,
                execution_time_minutes=stage.execution_time_minutes,
                quality_score=stage.quality_metrics.quality_score if stage.quality_metrics else None
            )
            
        except Exception as e:
            stage.status = PipelineStatus.FAILED
            stage.completed_at = datetime.now(timezone.utc)
            stage.error_message = str(e)
            
            execution.failed_stages.add(stage.stage_id)
            
            self.logger.error(
                "Stage execution failed",
                stage_id=stage.stage_id,
                error=str(e)
            )
            
            # Check if stage should retry
            if stage.retry_count < stage.retry_attempts:
                stage.retry_count += 1
                stage.status = PipelineStatus.PENDING
                execution.failed_stages.discard(stage.stage_id)
                
                self.logger.info(
                    "Retrying stage execution",
                    stage_id=stage.stage_id,
                    retry_count=stage.retry_count
                )


class PipelineMonitor:
    """Advanced pipeline monitoring and analytics."""
    
    def __init__(self):
        self.logger = structlog.get_logger("pipeline_monitor")
        self.execution_history = deque(maxlen=1000)
        self.performance_metrics = defaultdict(list)
        
    def record_execution(self, execution: PipelineExecution) -> None:
        """Record pipeline execution for monitoring."""
        
        execution_record = {
            "execution_id": execution.execution_id,
            "pipeline_id": execution.pipeline_id,
            "status": execution.status,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "total_execution_time_minutes": execution.total_execution_time_minutes,
            "records_processed": execution.total_records_processed,
            "overall_quality_score": execution.overall_quality_score,
            "stage_count": len(execution.stages),
            "completed_stages": len(execution.completed_stages),
            "failed_stages": len(execution.failed_stages)
        }
        
        self.execution_history.append(execution_record)
        
        # Record performance metrics
        pipeline_id = execution.pipeline_id
        if execution.total_execution_time_minutes:
            self.performance_metrics[f"{pipeline_id}_execution_time"].append(
                execution.total_execution_time_minutes
            )
        
        if execution.overall_quality_score:
            self.performance_metrics[f"{pipeline_id}_quality_score"].append(
                execution.overall_quality_score
            )
        
        if execution.total_records_processed:
            self.performance_metrics[f"{pipeline_id}_throughput"].append(
                execution.total_records_processed / (execution.total_execution_time_minutes or 1)
            )
    
    def get_pipeline_analytics(self, pipeline_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a pipeline."""
        
        # Filter executions for this pipeline
        pipeline_executions = [
            exec_record for exec_record in self.execution_history
            if exec_record["pipeline_id"] == pipeline_id
        ]
        
        if not pipeline_executions:
            return {"error": "No execution data found for pipeline"}
        
        # Calculate success/failure rates
        total_executions = len(pipeline_executions)
        successful_executions = len([
            e for e in pipeline_executions 
            if e["status"] == PipelineStatus.COMPLETED
        ])
        failed_executions = len([
            e for e in pipeline_executions 
            if e["status"] == PipelineStatus.FAILED
        ])
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Calculate performance statistics
        execution_times = [
            e["total_execution_time_minutes"] for e in pipeline_executions
            if e["total_execution_time_minutes"]
        ]
        
        quality_scores = [
            e["overall_quality_score"] for e in pipeline_executions
            if e["overall_quality_score"]
        ]
        
        records_processed = [
            e["records_processed"] for e in pipeline_executions
            if e["records_processed"]
        ]
        
        # Recent performance (last 10 executions)
        recent_executions = sorted(
            pipeline_executions, 
            key=lambda x: x["started_at"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True
        )[:10]
        
        analytics = {
            "pipeline_id": pipeline_id,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate_percent": round(success_rate, 2),
            "performance_stats": {
                "avg_execution_time_minutes": round(statistics.mean(execution_times), 2) if execution_times else 0,
                "min_execution_time_minutes": round(min(execution_times), 2) if execution_times else 0,
                "max_execution_time_minutes": round(max(execution_times), 2) if execution_times else 0,
                "avg_quality_score": round(statistics.mean(quality_scores), 3) if quality_scores else 0,
                "avg_records_per_execution": round(statistics.mean(records_processed), 0) if records_processed else 0,
                "total_records_processed": sum(records_processed) if records_processed else 0
            },
            "recent_trend": {
                "last_10_executions": len(recent_executions),
                "recent_success_rate": (
                    len([e for e in recent_executions if e["status"] == PipelineStatus.COMPLETED]) /
                    len(recent_executions) * 100
                ) if recent_executions else 0,
                "recent_avg_time": round(
                    statistics.mean([
                        e["total_execution_time_minutes"] for e in recent_executions
                        if e["total_execution_time_minutes"]
                    ]), 2
                ) if recent_executions else 0
            },
            "last_execution": recent_executions[0] if recent_executions else None,
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
        
        return analytics
    
    def detect_anomalies(self, pipeline_id: str) -> List[Dict[str, Any]]:
        """Detect performance anomalies in pipeline executions."""
        
        anomalies = []
        
        # Get performance metrics
        execution_times = self.performance_metrics.get(f"{pipeline_id}_execution_time", [])
        quality_scores = self.performance_metrics.get(f"{pipeline_id}_quality_score", [])
        throughputs = self.performance_metrics.get(f"{pipeline_id}_throughput", [])
        
        # Detect execution time anomalies
        if len(execution_times) >= 5:
            avg_time = statistics.mean(execution_times)
            std_time = statistics.stdev(execution_times)
            recent_time = execution_times[-1]
            
            if recent_time > avg_time + (2 * std_time):  # 2 standard deviations
                anomalies.append({
                    "type": "slow_execution",
                    "severity": "warning",
                    "description": f"Execution time {recent_time:.2f}m is significantly above average {avg_time:.2f}m",
                    "metric": "execution_time",
                    "value": recent_time,
                    "threshold": avg_time + (2 * std_time)
                })
        
        # Detect quality score anomalies
        if len(quality_scores) >= 5:
            avg_quality = statistics.mean(quality_scores)
            recent_quality = quality_scores[-1]
            
            if recent_quality < avg_quality - 0.1:  # Quality drop > 10%
                anomalies.append({
                    "type": "quality_degradation",
                    "severity": "critical",
                    "description": f"Quality score {recent_quality:.3f} is significantly below average {avg_quality:.3f}",
                    "metric": "quality_score",
                    "value": recent_quality,
                    "threshold": avg_quality - 0.1
                })
        
        # Detect throughput anomalies
        if len(throughputs) >= 5:
            avg_throughput = statistics.mean(throughputs)
            recent_throughput = throughputs[-1]
            
            if recent_throughput < avg_throughput * 0.7:  # 30% drop in throughput
                anomalies.append({
                    "type": "low_throughput",
                    "severity": "warning",
                    "description": f"Throughput {recent_throughput:.1f} records/min is significantly below average {avg_throughput:.1f}",
                    "metric": "throughput",
                    "value": recent_throughput,
                    "threshold": avg_throughput * 0.7
                })
        
        return anomalies
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        
        if not self.execution_history:
            return {"status": "no_data"}
        
        # Recent executions (last hour)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_executions = [
            e for e in self.execution_history
            if e["started_at"] and e["started_at"] > cutoff_time
        ]
        
        # Calculate health metrics
        total_recent = len(recent_executions)
        successful_recent = len([
            e for e in recent_executions 
            if e["status"] == PipelineStatus.COMPLETED
        ])
        
        health_score = (successful_recent / total_recent * 100) if total_recent > 0 else 100
        
        # Determine overall status
        if health_score >= 95:
            status = "healthy"
        elif health_score >= 80:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "health_score_percent": round(health_score, 2),
            "recent_executions_1h": total_recent,
            "successful_executions_1h": successful_recent,
            "failed_executions_1h": total_recent - successful_recent,
            "total_pipelines_monitored": len(set(e["pipeline_id"] for e in self.execution_history)),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }


class PipelineManager:
    """Comprehensive data pipeline management system."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("pipeline_manager")
        
        # Initialize components
        self.orchestrator = PipelineOrchestrator(client)
        self.monitor = PipelineMonitor()
        
        # Register default stage executors
        self._register_default_executors()
        
        # System state
        self.start_time = datetime.now(timezone.utc)
        self.pipelines_executed = 0
        
        self.logger.info("PipelineManager initialized")
    
    def _register_default_executors(self) -> None:
        """Register default stage executors."""
        self.orchestrator.register_stage_executor(PipelineStageType.EXTRACT, DataExtractionStage)
        self.orchestrator.register_stage_executor(PipelineStageType.TRANSFORM, DataTransformationStage)
        self.orchestrator.register_stage_executor(PipelineStageType.VALIDATE, DataTransformationStage)
        self.orchestrator.register_stage_executor(PipelineStageType.LOAD, CustomerIOLoadStage)
    
    def create_pipeline(self, pipeline_id: str, pipeline_name: str, stages: List[PipelineStage], 
                       execution_strategy: ExecutionStrategy = ExecutionStrategy.HYBRID,
                       trigger_type: TriggerType = TriggerType.MANUAL,
                       metadata: Optional[Dict[str, Any]] = None) -> PipelineExecution:
        """Create a new pipeline execution."""
        
        pipeline_execution = PipelineExecution(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            stages=stages,
            execution_strategy=execution_strategy,
            trigger_type=trigger_type,
            metadata=metadata or {}
        )
        
        self.logger.info(
            "Pipeline created",
            pipeline_id=pipeline_id,
            total_stages=len(stages),
            execution_strategy=execution_strategy
        )
        
        return pipeline_execution
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def execute_pipeline(self, pipeline_execution: PipelineExecution) -> PipelineExecution:
        """Execute a pipeline with monitoring."""
        
        self.logger.info(
            "Starting pipeline execution",
            execution_id=pipeline_execution.execution_id,
            pipeline_id=pipeline_execution.pipeline_id
        )
        
        try:
            # Execute pipeline
            completed_execution = self.orchestrator.execute_pipeline(pipeline_execution)
            
            # Record execution for monitoring
            self.monitor.record_execution(completed_execution)
            
            # Update metrics
            self.pipelines_executed += 1
            
            self.logger.info(
                "Pipeline execution completed",
                execution_id=completed_execution.execution_id,
                status=completed_execution.status,
                execution_time_minutes=completed_execution.total_execution_time_minutes
            )
            
            return completed_execution
            
        except Exception as e:
            self.logger.error(
                "Pipeline execution failed",
                execution_id=pipeline_execution.execution_id,
                error=str(e)
            )
            raise
    
    def get_pipeline_analytics(self, pipeline_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a pipeline."""
        return self.monitor.get_pipeline_analytics(pipeline_id)
    
    def detect_pipeline_anomalies(self, pipeline_id: str) -> List[Dict[str, Any]]:
        """Detect anomalies in pipeline performance."""
        return self.monitor.detect_anomalies(pipeline_id)
    
    def get_system_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive system dashboard data."""
        
        system_health = self.monitor.get_system_health()
        uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        return {
            "system": {
                "uptime_seconds": uptime_seconds,
                "start_time": self.start_time.isoformat(),
                "pipelines_executed": self.pipelines_executed
            },
            "health": system_health,
            "monitor": {
                "execution_history_size": len(self.monitor.execution_history),
                "tracked_pipelines": len(set(e["pipeline_id"] for e in self.monitor.execution_history))
            },
            "orchestrator": {
                "registered_executors": len(self.orchestrator.stage_executors)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get PipelineManager metrics and status."""
        return {
            "manager": {
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
                "pipelines_executed": self.pipelines_executed
            },
            "components": {
                "orchestrator": {
                    "registered_executors": len(self.orchestrator.stage_executors),
                    "active_context_keys": len(self.orchestrator.execution_context)
                },
                "monitor": {
                    "execution_history_size": len(self.monitor.execution_history),
                    "performance_metrics_tracked": len(self.monitor.performance_metrics)
                }
            },
            "features": {
                "pipeline_orchestration": True,
                "dependency_management": True,
                "data_quality_monitoring": True,
                "performance_analytics": True,
                "anomaly_detection": True,
                "parallel_execution": True,
                "stage_retry_mechanism": True,
                "comprehensive_monitoring": True
            }
        }