"""
Customer.IO Setup and Configuration Manager

Comprehensive setup management for Customer.IO data pipelines including:
- Environment configuration with type-safe validation
- Database and table creation with optimized schemas
- Synthetic data generation for testing and development
- Circuit breaker patterns for fault tolerance
- Comprehensive validation framework
- Secrets management integration
"""

import json
import os
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Literal, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import uuid
import base64
import secrets
import structlog

# Databricks and Spark imports
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, 
    TimestampType, BooleanType, DoubleType, ArrayType, MapType
)
from pyspark.sql import functions as F
from delta.tables import DeltaTable

# HTTP and validation libraries
import httpx
from pydantic import BaseModel, Field, validator

# Data generation
from faker import Faker
from dateutil import tz

from .api_client import CustomerIOClient
from .error_handlers import retry_on_error, ErrorContext, CustomerIOError, CircuitBreaker


class Environment(str, Enum):
    """Environment types for deployment."""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"


class ValidationStatus(str, Enum):
    """Validation result status."""
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


class CustomerIOConfig(BaseModel):
    """Type-safe configuration for Customer.IO API settings."""
    
    api_key: str = Field(..., description="Customer.IO API key")
    region: Literal["us", "eu"] = Field(default="us", description="API region")
    
    # Rate limiting configuration
    RATE_LIMIT_REQUESTS: int = Field(default=3000, description="Requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=3, description="Rate limit window in seconds")
    
    # Request size limits
    MAX_REQUEST_SIZE: int = Field(default=32 * 1024, description="Max request size in bytes")
    MAX_BATCH_SIZE: int = Field(default=500 * 1024, description="Max batch size in bytes")
    
    # Retry configuration
    MAX_RETRIES: int = Field(default=3, description="Maximum retry attempts")
    RETRY_BACKOFF_FACTOR: float = Field(default=2.0, description="Backoff multiplier")
    
    @validator('api_key')
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("API key cannot be empty")
        if len(v) < 10:
            raise ValueError("API key appears to be too short")
        return v.strip()
    
    @validator('region')
    def validate_region(cls, v: str) -> str:
        """Validate and normalize region."""
        return v.lower()
    
    @property
    def base_url(self) -> str:
        """Get base URL based on region."""
        if self.region == "eu":
            return "https://cdp-eu.customer.io/v1"
        else:
            return "https://cdp.customer.io/v1"
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        auth_string = base64.b64encode(f"{self.api_key}:".encode()).decode()
        
        return {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json",
            "User-Agent": "CustomerIO-Databricks-Setup/1.0.0",
            "Accept": "application/json"
        }
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
        extra = "forbid"


@dataclass
class ValidationResult:
    """Type-safe validation result."""
    status: ValidationStatus
    component: str
    result: str
    error: Optional[Exception] = None
    
    def __str__(self) -> str:
        return f"{self.status.value} {self.component:<25} {self.result}"


@dataclass
class SetupConfiguration:
    """Complete setup configuration."""
    customerio_region: str
    database_name: str
    catalog_name: str
    environment: Environment
    api_key: str
    
    def get_full_database_name(self) -> str:
        """Get full database name."""
        return f"{self.catalog_name}.{self.database_name}"


class SyntheticDataGenerator:
    """Generates realistic synthetic data for testing and development."""
    
    def __init__(self, seed: int = 42):
        """Initialize with reproducible seed."""
        self.fake = Faker()
        self.fake.seed_instance(seed)
        self.logger = structlog.get_logger("synthetic_data")
    
    def generate_customers(self, num_customers: int = 1000, region: str = "us") -> List[Dict[str, Any]]:
        """Generate synthetic customer data."""
        if num_customers <= 0:
            raise ValueError("num_customers must be positive")
        
        customers: List[Dict[str, Any]] = []
        
        try:
            for i in range(num_customers):
                customer_id = str(uuid.uuid4())
                created_at = self.fake.date_time_between(start_date='-2y', end_date='now', tzinfo=tz.UTC)
                
                customer = {
                    "customer_id": customer_id,
                    "user_id": f"user_{i+1:06d}",
                    "anonymous_id": str(uuid.uuid4()) if self.fake.boolean(chance_of_getting_true=30) else None,
                    "email": self.fake.email(),
                    "created_at": created_at,
                    "updated_at": self.fake.date_time_between(start_date=created_at, end_date='now', tzinfo=tz.UTC),
                    "traits": {
                        "first_name": self.fake.first_name(),
                        "last_name": self.fake.last_name(),
                        "age": str(self.fake.random_int(min=18, max=80)),
                        "city": self.fake.city(),
                        "country": self.fake.country(),
                        "plan": self.fake.random_element(["free", "basic", "premium", "enterprise"]),
                        "signup_source": self.fake.random_element(["website", "mobile_app", "referral", "social"])
                    },
                    "custom_attributes": {
                        "lifetime_value": str(round(self.fake.random.uniform(0, 5000), 2)),
                        "last_purchase_amount": str(round(self.fake.random.uniform(10, 500), 2)) if self.fake.boolean(chance_of_getting_true=60) else None,
                        "subscription_status": self.fake.random_element(["active", "canceled", "trial", "expired"])
                    },
                    "is_active": self.fake.boolean(chance_of_getting_true=85),
                    "last_seen": self.fake.date_time_between(start_date='-30d', end_date='now', tzinfo=tz.UTC),
                    "source": "synthetic_data",
                    "region": region
                }
                customers.append(customer)
                
            self.logger.info("Generated customer data", count=len(customers))
            return customers
            
        except Exception as e:
            self.logger.error("Failed to generate customer data", error=str(e))
            raise Exception(f"Failed to generate customer data: {str(e)}")
    
    def generate_events(self, customers: List[Dict[str, Any]], num_events: int = 5000) -> List[Dict[str, Any]]:
        """Generate synthetic event data."""
        if not customers:
            raise ValueError("customers list cannot be empty")
        if num_events <= 0:
            raise ValueError("num_events must be positive")
        
        events: List[Dict[str, Any]] = []
        
        # Define event types and their categories
        event_types = {
            "ecommerce": [
                "Product Viewed", "Product Added", "Cart Viewed", "Checkout Started", 
                "Order Completed", "Product Removed", "Coupon Applied"
            ],
            "engagement": [
                "Page Viewed", "Button Clicked", "Form Submitted", "Video Played", 
                "Document Downloaded", "Search Performed"
            ],
            "lifecycle": [
                "User Registered", "Profile Updated", "Settings Changed", "Account Upgraded", 
                "Subscription Canceled", "Password Reset"
            ],
            "mobile": [
                "Application Opened", "Application Backgrounded", "Push Notification Clicked",
                "Screen Viewed", "Feature Used"
            ]
        }
        
        try:
            for i in range(num_events):
                customer = self.fake.random_element(customers)
                category = self.fake.random_element(list(event_types.keys()))
                event_name = self.fake.random_element(event_types[category])
                
                # Generate event properties based on category
                properties: Dict[str, str] = {}
                if category == "ecommerce":
                    properties.update({
                        "product_id": f"prod_{self.fake.random_int(min=1, max=1000)}",
                        "product_name": self.fake.catch_phrase(),
                        "price": str(round(self.fake.random.uniform(9.99, 299.99), 2)),
                        "currency": "USD",
                        "category": self.fake.random_element(["electronics", "clothing", "books", "home", "sports"])
                    })
                elif category == "engagement":
                    properties.update({
                        "page_url": self.fake.url(),
                        "referrer": self.fake.url() if self.fake.boolean(chance_of_getting_true=30) else "",
                        "session_id": str(uuid.uuid4())
                    })
                
                event = {
                    "event_id": str(uuid.uuid4()),
                    "customer_id": customer["customer_id"],
                    "user_id": customer["user_id"],
                    "anonymous_id": customer.get("anonymous_id"),
                    "event_name": event_name,
                    "timestamp": self.fake.date_time_between(start_date='-90d', end_date='now', tzinfo=tz.UTC),
                    "properties": properties,
                    "context": {
                        "ip": self.fake.ipv4(),
                        "user_agent": self.fake.user_agent(),
                        "locale": self.fake.locale(),
                        "timezone": str(self.fake.timezone())
                    },
                    "is_semantic_event": event_name in [item for sublist in event_types.values() for item in sublist[:3]],
                    "event_category": category,
                    "source": "synthetic_data",
                    "processed_at": datetime.now(tz.UTC)
                }
                events.append(event)
                
            self.logger.info("Generated event data", count=len(events))
            return events
            
        except Exception as e:
            self.logger.error("Failed to generate event data", error=str(e))
            raise Exception(f"Failed to generate event data: {str(e)}")


class SchemaManager:
    """Manages Delta Lake table schemas for Customer.IO data."""
    
    def __init__(self):
        """Initialize schema manager."""
        self.logger = structlog.get_logger("schema_manager")
    
    @property
    def customers_schema(self) -> StructType:
        """Schema for customers table (aligns with /identify endpoint)."""
        return StructType([
            StructField("customer_id", StringType(), False),
            StructField("user_id", StringType(), True),
            StructField("anonymous_id", StringType(), True),
            StructField("email", StringType(), True),
            StructField("created_at", TimestampType(), True),
            StructField("updated_at", TimestampType(), True),
            StructField("traits", MapType(StringType(), StringType()), True),
            StructField("custom_attributes", MapType(StringType(), StringType()), True),
            StructField("is_active", BooleanType(), True),
            StructField("last_seen", TimestampType(), True),
            StructField("source", StringType(), True),
            StructField("region", StringType(), True)
        ])
    
    @property
    def events_schema(self) -> StructType:
        """Schema for events table (aligns with /track endpoint)."""
        return StructType([
            StructField("event_id", StringType(), False),
            StructField("customer_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("anonymous_id", StringType(), True),
            StructField("event_name", StringType(), False),
            StructField("timestamp", TimestampType(), False),
            StructField("properties", MapType(StringType(), StringType()), True),
            StructField("context", MapType(StringType(), StringType()), True),
            StructField("is_semantic_event", BooleanType(), True),
            StructField("event_category", StringType(), True),
            StructField("source", StringType(), True),
            StructField("processed_at", TimestampType(), True)
        ])
    
    @property
    def groups_schema(self) -> StructType:
        """Schema for groups table (aligns with /group endpoint)."""
        return StructType([
            StructField("group_id", StringType(), False),
            StructField("group_type", StringType(), True),
            StructField("name", StringType(), True),
            StructField("created_at", TimestampType(), True),
            StructField("updated_at", TimestampType(), True),
            StructField("traits", MapType(StringType(), StringType()), True),
            StructField("parent_group_id", StringType(), True),
            StructField("is_active", BooleanType(), True)
        ])
    
    @property
    def devices_schema(self) -> StructType:
        """Schema for devices table (device management)."""
        return StructType([
            StructField("device_id", StringType(), False),
            StructField("customer_id", StringType(), False),
            StructField("device_token", StringType(), False),
            StructField("device_type", StringType(), False),
            StructField("platform", StringType(), True),
            StructField("app_version", StringType(), True),
            StructField("os_version", StringType(), True),
            StructField("created_at", TimestampType(), True),
            StructField("last_used", TimestampType(), True),
            StructField("is_active", BooleanType(), True)
        ])
    
    @property
    def api_responses_schema(self) -> StructType:
        """Schema for API responses (logging and monitoring)."""
        return StructType([
            StructField("request_id", StringType(), False),
            StructField("endpoint", StringType(), False),
            StructField("method", StringType(), False),
            StructField("status_code", IntegerType(), False),
            StructField("response_time_ms", IntegerType(), True),
            StructField("request_size_bytes", IntegerType(), True),
            StructField("response_size_bytes", IntegerType(), True),
            StructField("timestamp", TimestampType(), False),
            StructField("error_message", StringType(), True),
            StructField("retry_count", IntegerType(), True),
            StructField("customer_id", StringType(), True)
        ])
    
    @property
    def batch_operations_schema(self) -> StructType:
        """Schema for batch operations tracking."""
        return StructType([
            StructField("batch_id", StringType(), False),
            StructField("operation_type", StringType(), False),
            StructField("total_records", IntegerType(), False),
            StructField("successful_records", IntegerType(), True),
            StructField("failed_records", IntegerType(), True),
            StructField("started_at", TimestampType(), False),
            StructField("completed_at", TimestampType(), True),
            StructField("status", StringType(), False),
            StructField("error_summary", ArrayType(StringType()), True)
        ])
    
    def get_all_schemas(self) -> Dict[str, StructType]:
        """Get all schemas as a dictionary."""
        return {
            "customers": self.customers_schema,
            "events": self.events_schema,
            "groups": self.groups_schema,
            "devices": self.devices_schema,
            "api_responses": self.api_responses_schema,
            "batch_operations": self.batch_operations_schema
        }


class SetupManager:
    """
    Comprehensive setup and configuration manager for Customer.IO data pipelines.
    
    Features:
    - Type-safe configuration management
    - Database and table creation with optimized schemas
    - Synthetic data generation for testing
    - Circuit breaker patterns for fault tolerance
    - Comprehensive validation framework
    - Secrets management integration
    """
    
    def __init__(self, spark: SparkSession):
        """
        Initialize setup manager.
        
        Args:
            spark: Active Spark session
        """
        self.spark = spark
        self.logger = structlog.get_logger("setup_manager")
        self.circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=30)
        self.data_generator = SyntheticDataGenerator()
        self.schema_manager = SchemaManager()
        
        self.logger.info("SetupManager initialized")
    
    def create_configuration_from_widgets(self) -> SetupConfiguration:
        """Create configuration from Databricks widgets."""
        try:
            # Import dbutils (only available in Databricks)
            from pyspark.dbutils import DBUtils
            dbutils = DBUtils(self.spark)
            
            # Get configuration from widgets
            customerio_region = dbutils.widgets.get("customerio_region")
            database_name = dbutils.widgets.get("database_name")
            catalog_name = dbutils.widgets.get("catalog_name")
            environment_str = dbutils.widgets.get("environment")
            
            # Map environment string to enum
            environment = Environment(environment_str.lower())
            
            # Get API key from secrets based on environment
            if environment == Environment.PRODUCTION:
                api_key = dbutils.secrets.get(scope="customerio", key="production_api_key")
            elif environment == Environment.STAGING:
                api_key = dbutils.secrets.get(scope="customerio", key="staging_api_key")
            else:
                # Test environment - use mock key
                api_key = "test_key_demo_12345"
                self.logger.warning("Using test mode with mock API key")
            
            config = SetupConfiguration(
                customerio_region=customerio_region,
                database_name=database_name,
                catalog_name=catalog_name,
                environment=environment,
                api_key=api_key
            )
            
            self.logger.info("Configuration created from widgets", 
                           region=customerio_region, 
                           database=config.get_full_database_name(),
                           environment=environment.value)
            
            return config
            
        except Exception as e:
            self.logger.error("Failed to create configuration", error=str(e))
            # Fallback to test configuration
            return SetupConfiguration(
                customerio_region="us",
                database_name="customerio_demo", 
                catalog_name="main",
                environment=Environment.TESTING,
                api_key="test_key_demo_12345"
            )
    
    def validate_customerio_config(self, config: SetupConfiguration) -> ValidationResult:
        """Validate Customer.IO API configuration."""
        try:
            customerio_config = CustomerIOConfig(
                api_key=config.api_key,
                region=config.customerio_region
            )
            
            # Test header generation
            headers = customerio_config.get_headers()
            if not headers.get("Authorization"):
                return ValidationResult(
                    ValidationStatus.ERROR,
                    "API configuration",
                    "Invalid authorization header"
                )
            
            if config.environment == Environment.TESTING:
                return ValidationResult(
                    ValidationStatus.WARNING,
                    "API configuration", 
                    "Test mode - mock key"
                )
            else:
                return ValidationResult(
                    ValidationStatus.SUCCESS,
                    "API configuration",
                    "Valid"
                )
                
        except Exception as e:
            return ValidationResult(
                ValidationStatus.ERROR,
                "API configuration",
                f"Failed: {str(e)}",
                e
            )
    
    def create_database_and_tables(self, config: SetupConfiguration) -> List[ValidationResult]:
        """Create database and tables with optimized settings."""
        results: List[ValidationResult] = []
        
        try:
            # Create database
            self.spark.sql(f"CREATE DATABASE IF NOT EXISTS {config.get_full_database_name()}")
            self.spark.sql(f"USE {config.get_full_database_name()}")
            
            results.append(ValidationResult(
                ValidationStatus.SUCCESS,
                "Database creation",
                f"Created {config.get_full_database_name()}"
            ))
            
            # Create tables with schemas
            schemas = self.schema_manager.get_all_schemas()
            
            for table_name, schema in schemas.items():
                try:
                    # Create empty DataFrame with schema
                    empty_df = self.spark.createDataFrame([], schema)
                    
                    # Write as Delta table with optimizations
                    (empty_df.write
                     .format("delta")
                     .mode("overwrite")
                     .option("delta.autoOptimize.optimizeWrite", "true")
                     .option("delta.autoOptimize.autoCompact", "true")
                     .saveAsTable(f"{config.get_full_database_name()}.{table_name}"))
                    
                    results.append(ValidationResult(
                        ValidationStatus.SUCCESS,
                        f"Table {table_name}",
                        "Created with Delta optimizations"
                    ))
                    
                except Exception as e:
                    results.append(ValidationResult(
                        ValidationStatus.ERROR,
                        f"Table {table_name}",
                        f"Failed: {str(e)}",
                        e
                    ))
            
            self.logger.info("Database and tables created", 
                           database=config.get_full_database_name(),
                           tables=list(schemas.keys()))
            
        except Exception as e:
            results.append(ValidationResult(
                ValidationStatus.ERROR,
                "Database creation",
                f"Failed: {str(e)}",
                e
            ))
        
        return results
    
    def load_synthetic_data(self, config: SetupConfiguration, 
                           num_customers: int = 1000, 
                           num_events: int = 5000) -> List[ValidationResult]:
        """Load synthetic data into tables for testing."""
        results: List[ValidationResult] = []
        
        try:
            # Generate synthetic data
            customers = self.data_generator.generate_customers(
                num_customers, config.customerio_region
            )
            events = self.data_generator.generate_events(customers, num_events)
            
            # Load customers
            customers_df = self.spark.createDataFrame(
                customers, self.schema_manager.customers_schema
            )
            (customers_df.write
             .format("delta")
             .mode("overwrite")
             .saveAsTable(f"{config.get_full_database_name()}.customers"))
            
            results.append(ValidationResult(
                ValidationStatus.SUCCESS,
                "Customers data",
                f"Loaded {len(customers)} records"
            ))
            
            # Load events
            events_df = self.spark.createDataFrame(
                events, self.schema_manager.events_schema
            )
            (events_df.write
             .format("delta")
             .mode("overwrite")
             .saveAsTable(f"{config.get_full_database_name()}.events"))
            
            results.append(ValidationResult(
                ValidationStatus.SUCCESS,
                "Events data",
                f"Loaded {len(events)} records"
            ))
            
            self.logger.info("Synthetic data loaded",
                           customers=len(customers),
                           events=len(events))
            
        except Exception as e:
            results.append(ValidationResult(
                ValidationStatus.ERROR,
                "Synthetic data",
                f"Failed: {str(e)}",
                e
            ))
        
        return results
    
    def validate_setup(self, config: SetupConfiguration) -> List[ValidationResult]:
        """Comprehensive setup validation with circuit breaker protection."""
        results: List[ValidationResult] = []
        
        # Database validation
        try:
            result = self.circuit_breaker(self._validate_database_access, config)
            results.append(result)
        except Exception as e:
            results.append(ValidationResult(
                ValidationStatus.ERROR,
                "Database access",
                f"Circuit breaker: {str(e)}",
                e
            ))
        
        # Table validation
        required_tables = ["customers", "events", "groups", "devices", "api_responses", "batch_operations"]
        for table in required_tables:
            try:
                result = self.circuit_breaker(self._validate_table_exists, config, table)
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    ValidationStatus.ERROR,
                    f"Table {table}",
                    f"Circuit breaker: {str(e)}",
                    e
                ))
        
        # Data quality validation
        data_tables = ["customers", "events"]
        for table in data_tables:
            try:
                result = self.circuit_breaker(self._validate_data_quality, config, table)
                results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    ValidationStatus.ERROR,
                    f"{table} data",
                    f"Circuit breaker: {str(e)}",
                    e
                ))
        
        # API configuration validation
        try:
            result = self.circuit_breaker(self.validate_customerio_config, config)
            results.append(result)
        except Exception as e:
            results.append(ValidationResult(
                ValidationStatus.ERROR,
                "API configuration",
                f"Circuit breaker: {str(e)}",
                e
            ))
        
        return results
    
    def _validate_database_access(self, config: SetupConfiguration) -> ValidationResult:
        """Validate database access."""
        try:
            self.spark.sql(f"USE {config.get_full_database_name()}")
            return ValidationResult(
                ValidationStatus.SUCCESS,
                "Database access",
                "OK"
            )
        except Exception as e:
            return ValidationResult(
                ValidationStatus.ERROR,
                "Database access",
                f"Failed: {str(e)}",
                e
            )
    
    def _validate_table_exists(self, config: SetupConfiguration, table_name: str) -> ValidationResult:
        """Validate that a table exists."""
        try:
            self.spark.table(f"{config.get_full_database_name()}.{table_name}")
            return ValidationResult(
                ValidationStatus.SUCCESS,
                f"Table {table_name}",
                "Exists"
            )
        except Exception as e:
            return ValidationResult(
                ValidationStatus.ERROR,
                f"Table {table_name}",
                "Missing",
                e
            )
    
    def _validate_data_quality(self, config: SetupConfiguration, table_name: str) -> ValidationResult:
        """Validate data quality in a table."""
        try:
            df = self.spark.table(f"{config.get_full_database_name()}.{table_name}")
            count = df.count()
            
            if count > 0:
                return ValidationResult(
                    ValidationStatus.SUCCESS,
                    f"{table_name} data",
                    f"{count} records"
                )
            else:
                return ValidationResult(
                    ValidationStatus.WARNING,
                    f"{table_name} data",
                    "No records"
                )
        except Exception as e:
            return ValidationResult(
                ValidationStatus.ERROR,
                f"{table_name} data",
                f"Failed: {str(e)}",
                e
            )
    
    def display_validation_results(self, validations: List[ValidationResult]) -> Dict[str, Any]:
        """Display validation results and calculate summary."""
        
        # Print detailed results
        print("Setup Validation Results:")
        print("=" * 60)
        
        for validation in validations:
            print(str(validation))
            if validation.error and validation.status == ValidationStatus.ERROR:
                print(f"    Error: {type(validation.error).__name__}: {str(validation.error)}")
        
        # Calculate summary
        passed = sum(1 for v in validations if v.status == ValidationStatus.SUCCESS)
        warnings = sum(1 for v in validations if v.status == ValidationStatus.WARNING)
        failed = sum(1 for v in validations if v.status == ValidationStatus.ERROR)
        total = len(validations)
        
        print(f"\nValidation Summary:")
        print(f"  SUCCESS: Passed: {passed}")
        print(f"  WARNING: Warnings: {warnings}")
        print(f"  ERROR: Failed: {failed}")
        print(f"  DATA: Total: {total}")
        
        # Determine overall status
        if failed == 0:
            if warnings == 0:
                print("COMPLETED: All validation checks passed! Ready to proceed.")
                overall_status = "success"
            else:
                print("WARNING: Validation passed with warnings. Review before proceeding.")
                overall_status = "warning"
        else:
            print("ERROR: Some validation checks failed. Please fix issues before proceeding.")
            overall_status = "failed"
        
        return {
            "overall_status": overall_status,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "total": total,
            "validations": validations,
            "circuit_breaker_state": self.circuit_breaker.state
        }
    
    def setup_complete_environment(self, num_customers: int = 1000, num_events: int = 5000) -> Dict[str, Any]:
        """Complete environment setup with validation."""
        
        self.logger.info("Starting complete environment setup")
        
        # Create configuration
        config = self.create_configuration_from_widgets()
        
        # Create database and tables
        db_results = self.create_database_and_tables(config)
        
        # Load synthetic data if requested
        data_results = []
        if num_customers > 0:
            data_results = self.load_synthetic_data(config, num_customers, num_events)
        
        # Validate setup
        validation_results = self.validate_setup(config)
        
        # Combine all results
        all_results = db_results + data_results + validation_results
        
        # Display and return summary
        summary = self.display_validation_results(all_results)
        summary["config"] = config
        
        self.logger.info("Complete environment setup finished",
                        overall_status=summary["overall_status"],
                        total_validations=summary["total"])
        
        return summary