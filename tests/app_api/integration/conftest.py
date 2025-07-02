"""
Simplified configuration and fixtures for Customer.IO App API integration tests.

This module provides:
- Environment variable loading for App API credentials
- Authenticated App API client fixture
- Automatic test data creation and cleanup
"""

import os
import time
import pytest
from dotenv import load_dotenv

from src.app_api.auth import AppAPIAuth


# Load environment variables from .env file
load_dotenv()


# Simple test configuration - just the essentials
APP_API_TOKEN = os.getenv("CUSTOMERIO_APP_API_TOKEN")
APP_API_REGION = os.getenv("CUSTOMERIO_REGION", "us")


def has_valid_credentials() -> bool:
    """Check if API token is configured with a real value."""
    if not APP_API_TOKEN:
        return False
    
    # Check for obvious placeholder patterns
    token_lower = APP_API_TOKEN.lower()
    
    # Common placeholder patterns
    if any(pattern in token_lower for pattern in [
        "your_", "placeholder", "token_here", "example", "test_token"
    ]):
        return False
    
    # Check if it looks like a placeholder format
    if APP_API_TOKEN in ["your_app_api_token_here", "token_here"]:
        return False
        
    return True


# Skip marker for tests without credentials
skip_without_credentials = pytest.mark.skipif(
    not has_valid_credentials(),
    reason="Customer.IO App API token not configured. Set CUSTOMERIO_APP_API_TOKEN in .env file."
)


@pytest.fixture(scope="session")
def app_auth() -> AppAPIAuth:
    """
    Create authenticated App API auth object.
    
    Returns
    -------
    AppAPIAuth
        Authenticated App API auth instance
    """
    if not has_valid_credentials():
        pytest.skip("Customer.IO App API token not configured")
    
    return AppAPIAuth(
        api_token=APP_API_TOKEN,
        region=APP_API_REGION
    )


# Customer fixtures removed - App API focuses on communications only
# Customer management is handled by Pipelines API


@pytest.fixture
def transactional_message_id() -> int:
    """
    Provide a test transactional message ID.
    
    For real tests, this would need to be a valid message ID in your workspace.
    For now, we'll skip tests that need this.
    
    Returns
    -------
    int
        Transactional message ID
    """
    pytest.skip("Real transactional message ID required - set up in Customer.IO UI")


@pytest.fixture
def broadcast_id() -> int:
    """
    Provide a test broadcast ID.
    
    For real tests, this would need to be a valid broadcast ID in your workspace.
    For now, we'll skip tests that need this.
    
    Returns
    -------
    int
        Broadcast ID
    """
    pytest.skip("Real broadcast ID required - set up in Customer.IO UI")


@pytest.fixture(autouse=True)
def rate_limit():
    """
    Simple rate limiting to avoid hitting API limits.
    
    Automatically applied to all tests.
    """
    # Wait 100ms between tests to respect rate limits
    time.sleep(0.1)
    yield


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