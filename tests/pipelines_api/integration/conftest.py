"""
Configuration and fixtures for Customer.IO integration tests.

This module provides:
- Environment variable loading for test credentials
- Authenticated API client fixtures
- Test data management utilities
- Skip markers for tests requiring real API access
"""

import os
import time
import pytest
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from src.pipelines_api.api_client import CustomerIOClient
from src.pipelines_api.exceptions import CustomerIOError, AuthenticationError
from tests.eternal_config import eternal_config, get_eternal_data_for_test
from tests.eternal_utils import (
    get_test_user_data, 
    get_test_device_data, 
    get_test_object_data,
    skip_if_eternal_data_missing
)


# Load environment variables from .env file
load_dotenv()


# Test configuration from environment
TEST_CONFIG = {
    "api_key": os.getenv("CUSTOMERIO_API_KEY"),
    "region": os.getenv("CUSTOMERIO_REGION", "us"),
    "test_env": os.getenv("TEST_ENVIRONMENT", "test"),
    "debug": os.getenv("DEBUG_INTEGRATION_TESTS", "false").lower() == "true",
    "rate_limit": int(os.getenv("TEST_RATE_LIMIT_PER_SECOND", "10")),
    "retention_hours": int(os.getenv("TEST_DATA_RETENTION_HOURS", "24")),
    "skip_if_no_creds": os.getenv("SKIP_IF_NO_CREDENTIALS", "true").lower() == "true",
    "test_data_mode": os.getenv("TEST_DATA_MODE", "create").lower(),
    "eternal_data_enabled": os.getenv("ETERNAL_DATA_ENABLED", "false").lower() == "true"
}


def has_valid_credentials() -> bool:
    """Check if valid API credentials are available."""
    return bool(TEST_CONFIG["api_key"] and TEST_CONFIG["api_key"] != "your_test_api_key_here")


# Skip marker for integration tests
skip_without_credentials = pytest.mark.skipif(
    not has_valid_credentials() and TEST_CONFIG["skip_if_no_creds"],
    reason="Customer.IO API credentials not configured. Set CUSTOMERIO_API_KEY in .env file."
)


@pytest.fixture(scope="session")
def api_credentials() -> Dict[str, str]:
    """
    Provide API credentials for integration tests.
    
    Returns
    -------
    dict
        API credentials including key and region
        
    Raises
    ------
    pytest.skip
        If credentials are not available and skip is enabled
    """
    if not has_valid_credentials():
        if TEST_CONFIG["skip_if_no_creds"]:
            pytest.skip("Customer.IO API credentials not configured")
        else:
            raise ValueError(
                "Customer.IO API credentials not configured. "
                "Set CUSTOMERIO_API_KEY in .env file."
            )
    
    return {
        "api_key": TEST_CONFIG["api_key"],
        "region": TEST_CONFIG["region"]
    }


@pytest.fixture(scope="session")
def authenticated_client(api_credentials) -> CustomerIOClient:
    """
    Create an authenticated Customer.IO API client for testing.
    
    Parameters
    ----------
    api_credentials : dict
        API credentials fixture
        
    Returns
    -------
    CustomerIOClient
        Authenticated API client instance
    """
    return CustomerIOClient(
        api_key=api_credentials["api_key"],
        region=api_credentials["region"]
    )


@pytest.fixture
def test_user_id() -> str:
    """
    Generate a unique test user ID or return eternal user ID.
    
    Returns
    -------
    str
        User ID for testing (eternal or newly generated)
    """
    # Check if we should use eternal data
    user_data = get_test_user_data("basic")
    if user_data and eternal_config.is_eternal_mode:
        return user_data["id"]
    
    # Generate new ID for create mode
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    return f"{TEST_CONFIG['test_env']}_user_{timestamp}_{unique_id}"


@pytest.fixture
def test_anonymous_id() -> str:
    """
    Generate a unique test anonymous ID.
    
    Returns
    -------
    str
        Unique anonymous ID for testing
    """
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    return f"{TEST_CONFIG['test_env']}_anon_{timestamp}_{unique_id}"


@pytest.fixture
def test_object_id() -> str:
    """
    Generate a unique test object ID.
    
    Returns
    -------
    str
        Unique object ID for testing
    """
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    return f"{TEST_CONFIG['test_env']}_obj_{timestamp}_{unique_id}"


@pytest.fixture
def test_device_id() -> str:
    """
    Generate a unique test device ID or return eternal device ID.
    
    Returns
    -------
    str
        Device ID for testing (eternal or newly generated)
    """
    # Check if we should use eternal data
    device_data = get_test_device_data("ios")
    if device_data and eternal_config.is_eternal_mode:
        return device_data["id"]
    
    # Generate new ID for create mode
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    return f"{TEST_CONFIG['test_env']}_device_{timestamp}_{unique_id}"


@pytest.fixture
def test_user_data(test_user_id) -> Dict[str, Any]:
    """
    Generate test user data with traits or return eternal user data.
    
    Parameters
    ----------
    test_user_id : str
        Test user ID (eternal or newly generated)
        
    Returns
    -------
    dict
        User data including ID and traits
    """
    # Check if we should use eternal data
    user_data = get_test_user_data("basic")
    if user_data and eternal_config.is_eternal_mode:
        return {
            "userId": user_data["id"],
            "traits": user_data["traits"]
        }
    
    # Generate new data for create mode
    return {
        "userId": test_user_id,
        "traits": {
            "email": f"{test_user_id}@integration-test.example.com",
            "first_name": "Integration",
            "last_name": "Test",
            "plan": "test",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "test_environment": TEST_CONFIG["test_env"],
            "is_test_data": True
        }
    }


@pytest.fixture
def test_event_data(test_user_id) -> Dict[str, Any]:
    """
    Generate test event data.
    
    Parameters
    ----------
    test_user_id : str
        Unique test user ID
        
    Returns
    -------
    dict
        Event data including user ID and properties
    """
    return {
        "userId": test_user_id,
        "event": "Integration Test Event",
        "properties": {
            "test_id": uuid.uuid4().hex,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": TEST_CONFIG["test_env"],
            "is_test": True
        }
    }


@pytest.fixture
def rate_limiter():
    """
    Rate limiter to respect API limits during testing.
    
    Yields
    ------
    callable
        Function to call before each API request
    """
    last_request_time = [0.0]
    min_interval = 1.0 / TEST_CONFIG["rate_limit"]
    
    def wait_if_needed():
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        elapsed = current_time - last_request_time[0]
        
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            if TEST_CONFIG["debug"]:
                print(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        last_request_time[0] = time.time()
    
    return wait_if_needed


@pytest.fixture
def cleanup_tracker():
    """
    Track test data for cleanup after tests.
    
    Yields
    ------
    dict
        Dictionary to track created resources
    """
    created_resources = {
        "users": [],
        "objects": [],
        "devices": [],
        "aliases": []
    }
    
    yield created_resources
    
    # Cleanup is handled by individual test fixtures
    # This tracker is for manual cleanup if needed


@pytest.fixture
def eternal_data_check(authenticated_client, request):
    """
    Check if eternal data is available and skip test if needed.
    
    Parameters
    ----------
    authenticated_client : CustomerIOClient
        API client for data validation
    request : pytest.FixtureRequest
        Pytest request object to access test markers
    """
    if eternal_config.is_eternal_mode:
        # Check if test requires specific data types
        required_data = getattr(request.node.get_closest_marker("eternal_data"), "args", []) if request.node.get_closest_marker("eternal_data") else ["user"]
        
        skip_reason = skip_if_eternal_data_missing(authenticated_client, required_data)
        if skip_reason:
            pytest.skip(skip_reason)
    
    return True


@pytest.fixture(autouse=True)
def test_isolation(rate_limiter):
    """
    Ensure test isolation with rate limiting.
    
    Parameters
    ----------
    rate_limiter : callable
        Rate limiting function
    """
    # Apply rate limiting before each test
    rate_limiter()
    
    # Test runs here
    yield
    
    # Optional: Add post-test cleanup if needed


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    
    Parameters
    ----------
    config : pytest.Config
        Pytest configuration object
    """
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test requiring API access"
    )
    config.addinivalue_line(
        "markers", 
        "slow: mark test as slow (taking more than 1 second)"
    )
    config.addinivalue_line(
        "markers",
        "cleanup: mark test as requiring cleanup of test data"
    )
    config.addinivalue_line(
        "markers",
        "read_only: mark test as read-only (safe for eternal data)"
    )
    config.addinivalue_line(
        "markers",
        "mutation: mark test as mutating data (requires careful eternal data handling)"
    )
    config.addinivalue_line(
        "markers",
        "eternal_data: mark test as requiring specific eternal data types (user, device, object)"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers.
    
    Parameters
    ----------
    config : pytest.Config
        Pytest configuration object
    items : list
        List of test items
    """
    for item in items:
        # Add integration marker to all tests in this directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            
        # Add skip marker if no credentials
        if not has_valid_credentials() and TEST_CONFIG["skip_if_no_creds"]:
            skip_marker = pytest.mark.skip(
                reason="Customer.IO API credentials not configured"
            )
            item.add_marker(skip_marker)
        
        # Add read_only marker to tests that don't modify data
        if eternal_config.is_eternal_mode:
            # Check if test looks like it modifies data
            test_name = item.name.lower()
            if any(keyword in test_name for keyword in ["delete", "suppress", "unsuppress", "create", "update", "modify"]):
                item.add_marker(pytest.mark.mutation)
            else:
                item.add_marker(pytest.mark.read_only)