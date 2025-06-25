"""
pytest configuration and fixtures for Customer.IO tests

Provides common fixtures for testing utils modules without requiring
actual Spark sessions or API credentials.
"""

import json
import pytest
from datetime import datetime, timezone
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock
import tempfile
import os

# Mock Spark session for testing without actual Databricks environment
@pytest.fixture
def mock_spark_session():
    """Mock Spark session for testing without Databricks."""
    spark = Mock()
    
    # Mock DataFrame operations
    mock_df = Mock()
    mock_df.count.return_value = 100
    mock_df.collect.return_value = []
    mock_df.show.return_value = None
    mock_df.limit.return_value = mock_df
    mock_df.filter.return_value = mock_df
    mock_df.select.return_value = mock_df
    
    # Mock Spark SQL operations
    spark.table.return_value = mock_df
    spark.sql.return_value = mock_df
    spark.createDataFrame.return_value = mock_df
    
    return spark

@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing transformers."""
    return [
        {
            "customer_id": "customer_001",
            "user_id": "user_001",
            "email": "test1@example.com",
            "traits": {
                "first_name": "John",
                "last_name": "Doe",
                "plan": "premium"
            },
            "is_active": True,
            "created_at": datetime(2024, 1, 15, tzinfo=timezone.utc),
            "region": "us"
        },
        {
            "customer_id": "customer_002", 
            "user_id": "user_002",
            "email": "test2@example.com",
            "traits": {
                "first_name": "Jane",
                "last_name": "Smith", 
                "plan": "basic"
            },
            "is_active": False,
            "created_at": datetime(2024, 2, 20, tzinfo=timezone.utc),
            "region": "us"
        }
    ]

@pytest.fixture
def sample_event_data():
    """Sample event data for testing transformers."""
    return [
        {
            "event_id": "event_001",
            "customer_id": "customer_001",
            "user_id": "user_001",
            "event_name": "Product Viewed",
            "timestamp": datetime(2024, 3, 10, tzinfo=timezone.utc),
            "properties": {
                "product_id": "prod_123",
                "price": "29.99",
                "category": "electronics"
            },
            "event_category": "ecommerce"
        },
        {
            "event_id": "event_002", 
            "customer_id": "customer_002",
            "user_id": "user_002",
            "event_name": "Page Viewed",
            "timestamp": datetime(2024, 3, 11, tzinfo=timezone.utc),
            "properties": {
                "page_name": "Home",
                "url": "https://example.com"
            },
            "event_category": "engagement"
        }
    ]

@pytest.fixture
def mock_api_responses():
    """Mock API responses for testing API client."""
    return {
        "identify_success": {
            "status_code": 200,
            "json": {"status": "success", "message": "User identified"}
        },
        "track_success": {
            "status_code": 200,
            "json": {"status": "success", "message": "Event tracked"}
        },
        "batch_success": {
            "status_code": 200,
            "json": {
                "status": "success", 
                "processed": 10,
                "failed": 0
            }
        },
        "rate_limit_error": {
            "status_code": 429,
            "json": {"error": "Rate limit exceeded"},
            "headers": {"retry-after": "3"}
        },
        "validation_error": {
            "status_code": 400,
            "json": {"error": "Invalid request format"}
        },
        "server_error": {
            "status_code": 500,
            "json": {"error": "Internal server error"}
        }
    }

@pytest.fixture
def temp_credentials():
    """Temporary credentials for testing."""
    return {
        "api_key": "test_api_key_12345",
        "region": "us",
        "base_url": "https://cdp.customer.io/v1"
    }

@pytest.fixture
def valid_identify_request():
    """Valid identify request for testing validators."""
    return {
        "userId": "user_12345",
        "traits": {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "plan": "premium"
        },
        "timestamp": datetime.now(timezone.utc)
    }

@pytest.fixture
def valid_track_request():
    """Valid track request for testing validators.""" 
    return {
        "userId": "user_12345",
        "event": "Product Viewed",
        "properties": {
            "product_id": "prod_123",
            "product_name": "Test Product",
            "price": 29.99
        },
        "timestamp": datetime.now(timezone.utc)
    }

@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing API calls."""
    client = Mock()
    
    # Default successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.raise_for_status.return_value = None
    
    client.request.return_value = mock_response
    client.post.return_value = mock_response
    client.get.return_value = mock_response
    
    return client

@pytest.fixture
def mock_logger():
    """Mock structured logger for testing."""
    logger = Mock()
    logger.info.return_value = None
    logger.error.return_value = None
    logger.warning.return_value = None
    logger.debug.return_value = None
    return logger