"""
Configuration and fixtures for Customer.IO App API integration tests.

This module provides:
- Environment variable loading for App API credentials
- Authenticated App API client fixtures
- Test data mode management
- Skip markers for tests based on data mode
"""

import os
import time
import pytest
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from src.app_api.auth import AppAPIAuth
from src.app_api import client as app_client


# Load environment variables from .env file
load_dotenv()


# Test configuration from environment
APP_TEST_CONFIG = {
    "api_token": os.getenv("CUSTOMERIO_APP_API_TOKEN"),
    "region": os.getenv("CUSTOMERIO_REGION", "us"),
    "test_env": os.getenv("TEST_ENVIRONMENT", "test"),
    "debug": os.getenv("DEBUG_INTEGRATION_TESTS", "false").lower() == "true",
    "rate_limit": int(os.getenv("TEST_RATE_LIMIT_PER_SECOND", "10")),
    "skip_if_no_creds": os.getenv("SKIP_IF_NO_CREDENTIALS", "true").lower() == "true",
    "test_data_mode": os.getenv("TEST_DATA_MODE", "create"),
    "show_cleanup_report": os.getenv("SHOW_CLEANUP_REPORT", "true").lower() == "true"
}

# Existing test data configuration
EXISTING_TEST_DATA = {
    "customer_id": os.getenv("TEST_EXISTING_CUSTOMER_ID"),
    "email": os.getenv("TEST_EXISTING_EMAIL"),
    "device_token": os.getenv("TEST_EXISTING_DEVICE_TOKEN"),
    "transactional_message_id": os.getenv("TEST_EXISTING_TRANSACTIONAL_MESSAGE_ID"),
    "broadcast_id": os.getenv("TEST_EXISTING_BROADCAST_ID")
}


def has_valid_app_credentials() -> bool:
    """Check if valid App API credentials are available."""
    token = APP_TEST_CONFIG["api_token"]
    if not token or token == "your_app_api_token_here":
        return False
    
    # Basic format validation - App API tokens should be reasonable length
    if len(token) < 10:
        return False
        
    return True


def validate_api_access() -> bool:
    """
    Validate that API credentials actually work with a test call.
    
    Returns
    -------
    bool
        True if API access is working, False otherwise
    """
    if not has_valid_app_credentials():
        return False
    
    try:
        auth = AppAPIAuth(
            api_token=APP_TEST_CONFIG["api_token"],
            region=APP_TEST_CONFIG["region"]
        )
        
        # Make a minimal API call to test access
        import requests
        session = requests.Session()
        session.headers.update(auth.get_headers())
        
        # Try to get customers with minimal data - this should work with valid credentials
        response = session.get(f"{auth.base_url}/v1/customers", params={"limit": 1})
        
        # 200 = success, 404 = no customers but auth is valid
        return response.status_code in [200, 404]
        
    except Exception:
        return False


# Skip marker for App API integration tests - check both config and actual API access
def _should_skip_api_tests():
    """Determine if API tests should be skipped."""
    if not APP_TEST_CONFIG["skip_if_no_creds"]:
        return False
    
    if not has_valid_app_credentials():
        return True
    
    # Only do expensive API validation check if basic credentials are present
    return not validate_api_access()

skip_without_app_credentials = pytest.mark.skipif(
    _should_skip_api_tests(),
    reason="Customer.IO App API credentials not working. Check CUSTOMERIO_APP_API_TOKEN in .env file."
)

# Skip marker for tests that create/delete data in existing mode
skip_in_existing_mode = pytest.mark.skipif(
    APP_TEST_CONFIG["test_data_mode"] == "existing",
    reason="Test creates/deletes data - skipped in existing data mode"
)

# Skip marker for tests requiring device token
skip_without_device = pytest.mark.skipif(
    not EXISTING_TEST_DATA.get("device_token"),
    reason="No test device token configured"
)


@pytest.fixture(scope="session")
def app_api_credentials() -> Dict[str, str]:
    """
    Provide App API credentials for integration tests.
    
    Returns
    -------
    dict
        API credentials including token and region
        
    Raises
    ------
    pytest.skip
        If credentials are not available and skip is enabled
    """
    # Check basic credential configuration
    if not has_valid_app_credentials():
        error_msg = "Customer.IO App API credentials not configured. Set CUSTOMERIO_APP_API_TOKEN in .env file."
        if APP_TEST_CONFIG["skip_if_no_creds"]:
            pytest.skip(error_msg)
        else:
            raise ValueError(error_msg)
    
    # Check if credentials actually work
    if not validate_api_access():
        error_msg = (
            "Customer.IO App API credentials are invalid or insufficient permissions. "
            "Please check your CUSTOMERIO_APP_API_TOKEN in .env file. "
            "Get a valid token from Customer.IO UI: Settings > API Credentials > App API Keys"
        )
        if APP_TEST_CONFIG["skip_if_no_creds"]:
            pytest.skip(error_msg)
        else:
            raise ValueError(error_msg)
    
    return {
        "api_token": APP_TEST_CONFIG["api_token"],
        "region": APP_TEST_CONFIG["region"]
    }


@pytest.fixture(scope="session")
def app_auth(app_api_credentials) -> AppAPIAuth:
    """
    Create authenticated App API auth object.
    
    Parameters
    ----------
    app_api_credentials : dict
        API credentials fixture
        
    Returns
    -------
    AppAPIAuth
        Authenticated App API auth instance
    """
    return AppAPIAuth(
        api_token=app_api_credentials["api_token"],
        region=app_api_credentials["region"]
    )


@pytest.fixture
def test_data_mode() -> str:
    """
    Get current test data mode.
    
    Returns
    -------
    str
        Test data mode: "create", "existing", or "hybrid"
    """
    return APP_TEST_CONFIG["test_data_mode"]


@pytest.fixture
def existing_test_data() -> Dict[str, Any]:
    """
    Get existing test data configuration.
    
    Returns
    -------
    dict
        Existing test data IDs and values
    """
    return EXISTING_TEST_DATA.copy()


@pytest.fixture
def validated_test_data(app_auth, test_data_mode, existing_test_data) -> Dict[str, Any]:
    """
    Validate and return test data that actually exists.
    
    Parameters
    ----------
    app_auth : AppAPIAuth
        Authenticated App API auth object
    test_data_mode : str
        Current test data mode
    existing_test_data : dict
        Configured existing test data
        
    Returns
    -------
    dict
        Validated test data with existence flags
    """
    validated = existing_test_data.copy()
    
    # Only validate in existing or hybrid mode
    if test_data_mode in ["existing", "hybrid"]:
        # Validate customer exists
        customer_id = existing_test_data.get("customer_id")
        if customer_id:
            try:
                app_client.get_customer(app_auth, customer_id)
                validated["customer_exists"] = True
            except Exception:
                validated["customer_exists"] = False
        else:
            validated["customer_exists"] = False
    else:
        # In create mode, we'll create what we need
        validated["customer_exists"] = False
    
    return validated


@pytest.fixture
def test_customer_id(test_data_mode, existing_test_data) -> str:
    """
    Provide customer ID based on test data mode.
    
    Parameters
    ----------
    test_data_mode : str
        Current test data mode
    existing_test_data : dict
        Existing test data configuration
        
    Returns
    -------
    str
        Customer ID to use for testing
    """
    if test_data_mode == "existing":
        customer_id = existing_test_data.get("customer_id")
        if not customer_id:
            pytest.skip("No existing customer ID configured for existing mode")
        return customer_id
    else:
        # Generate unique test customer ID
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        return f"{APP_TEST_CONFIG['test_env']}_app_user_{timestamp}_{unique_id}"


@pytest.fixture
def test_email(test_data_mode, existing_test_data, test_customer_id) -> str:
    """
    Provide email address based on test data mode.
    
    Parameters
    ----------
    test_data_mode : str
        Current test data mode
    existing_test_data : dict
        Existing test data configuration
    test_customer_id : str
        Customer ID being used
        
    Returns
    -------
    str
        Email address to use for testing
    """
    if test_data_mode == "existing":
        email = existing_test_data.get("email")
        if not email:
            pytest.skip("No existing email configured for existing mode")
        return email
    else:
        return f"{test_customer_id}@integration-test.example.com"


@pytest.fixture
def test_customer_data(test_customer_id, test_email, test_data_mode) -> Dict[str, Any]:
    """
    Generate test customer data.
    
    Parameters
    ----------
    test_customer_id : str
        Customer ID to use
    test_email : str
        Email address to use
    test_data_mode : str
        Current test data mode
        
    Returns
    -------
    dict
        Customer data for testing
    """
    return {
        "id": test_customer_id,
        "email": test_email,
        "attributes": {
            "first_name": "Integration",
            "last_name": "Test",
            "plan": "test",
            "test_mode": test_data_mode,
            "test_environment": APP_TEST_CONFIG["test_env"],
            "is_test_data": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    }


@pytest.fixture
def transactional_message_id(test_data_mode, existing_test_data) -> Optional[int]:
    """
    Provide transactional message ID based on mode.
    
    Parameters
    ----------
    test_data_mode : str
        Current test data mode
    existing_test_data : dict
        Existing test data configuration
        
    Returns
    -------
    int or None
        Transactional message ID if available
    """
    if test_data_mode in ["existing", "hybrid"]:
        msg_id = existing_test_data.get("transactional_message_id")
        if msg_id:
            return int(msg_id)
    return None


@pytest.fixture
def broadcast_id(test_data_mode, existing_test_data) -> Optional[int]:
    """
    Provide broadcast ID based on mode.
    
    Parameters
    ----------
    test_data_mode : str
        Current test data mode
    existing_test_data : dict
        Existing test data configuration
        
    Returns
    -------
    int or None
        Broadcast ID if available
    """
    if test_data_mode in ["existing", "hybrid"]:
        b_id = existing_test_data.get("broadcast_id")
        if b_id:
            return int(b_id)
    return None


@pytest.fixture
def device_token(test_data_mode, existing_test_data) -> Optional[str]:
    """
    Provide device token based on mode.
    
    Parameters
    ----------
    test_data_mode : str
        Current test data mode
    existing_test_data : dict
        Existing test data configuration
        
    Returns
    -------
    str or None
        Device token if available
    """
    if test_data_mode in ["existing", "hybrid"]:
        return existing_test_data.get("device_token")
    return None


@pytest.fixture
def cleanup_tracker():
    """
    Track resources created during tests for cleanup.
    
    Yields
    ------
    dict
        Dictionary to track created resources
    """
    created_resources = {
        "customers": [],
        "modifications": []  # Track modifications to restore
    }
    
    yield created_resources
    
    # Report will be handled by cleanup_report fixture


@pytest.fixture(scope="session", autouse=True)
def cleanup_report(request):
    """
    Report on test data created/modified during session.
    """
    session_resources = {
        "created": 0,
        "modified": 0,
        "mode": APP_TEST_CONFIG["test_data_mode"]
    }
    
    def report():
        if APP_TEST_CONFIG["show_cleanup_report"]:
            print(f"\n{'='*60}")
            print(f"App API Integration Test Summary")
            print(f"{'='*60}")
            print(f"Test Data Mode: {session_resources['mode']}")
            print(f"Resources Created: {session_resources['created']}")
            print(f"Resources Modified: {session_resources['modified']}")
            print(f"{'='*60}\n")
    
    request.addfinalizer(report)
    return session_resources


@pytest.fixture
def rate_limiter():
    """
    Rate limiter for App API requests.
    
    Returns
    -------
    callable
        Function to call before API requests
    """
    last_request_time = [0.0]
    min_interval = 1.0 / APP_TEST_CONFIG["rate_limit"]
    
    def wait_if_needed():
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        elapsed = current_time - last_request_time[0]
        
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            if APP_TEST_CONFIG["debug"]:
                print(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        last_request_time[0] = time.time()
    
    return wait_if_needed


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
    
    yield
    
    # Test cleanup handled by individual tests


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
        "app_integration: mark test as App API integration test"
    )
    config.addinivalue_line(
        "markers",
        "requires_existing_data: mark test as requiring existing test data"
    )
    config.addinivalue_line(
        "markers",
        "modifies_data: mark test as modifying existing data"
    )
    config.addinivalue_line(
        "markers",
        "creates_data: mark test as creating new data"
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
        # Add app_integration marker to all tests in this directory
        if "app_api/integration" in str(item.fspath):
            item.add_marker(pytest.mark.app_integration)
            
        # Add skip marker if no credentials
        if not has_valid_app_credentials() and APP_TEST_CONFIG["skip_if_no_creds"]:
            skip_marker = pytest.mark.skip(
                reason="Customer.IO App API credentials not configured"
            )
            item.add_marker(skip_marker)