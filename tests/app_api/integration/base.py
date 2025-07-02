"""
Helper functions for Customer.IO App API integration tests.

Simple utility functions without base class complexity.
"""

import pytest
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def assert_api_response(
    response: Dict[str, Any], 
    expected_keys: Optional[List[str]] = None,
    expected_values: Optional[Dict[str, Any]] = None
):
    """
    Assert API response structure and values.
    
    Parameters
    ----------
    response : dict
        API response to validate
    expected_keys : list, optional
        Keys that should be present in response
    expected_values : dict, optional
        Expected values for specific keys
    """
    assert isinstance(response, dict), "Response should be a dictionary"
    
    if expected_keys:
        for key in expected_keys:
            assert key in response, f"Expected key '{key}' not found in response"
    
    if expected_values:
        for key, value in expected_values.items():
            assert key in response, f"Key '{key}' not found in response"
            assert response[key] == value, f"Expected {key}={value}, got {response[key]}"


def assert_successful_response(response: Dict[str, Any]):
    """
    Assert that API response indicates success.
    
    Parameters
    ----------
    response : dict
        API response to validate
    """
    # App API typically returns specific response structures
    # Check for error indicators
    assert "error" not in response, f"Error in response: {response.get('error')}"
    assert "errors" not in response, f"Errors in response: {response.get('errors')}"
    
    # Many successful responses have meta information
    if "meta" in response:
        assert response["meta"].get("error") is None, "Error in meta field"


def handle_api_error(error: Exception, context: str = "API call"):
    """
    Handle and provide helpful error messages for common API errors.
    
    Parameters
    ----------
    error : Exception
        The caught exception
    context : str
        Context description for the error
    """
    error_str = str(error)
    
    if "401" in error_str or "unauthorized" in error_str.lower():
        pytest.fail(
            f"{context} failed: Authentication error. "
            "Please check your CUSTOMERIO_APP_API_TOKEN in .env file."
        )
    elif "404" in error_str or "not found" in error_str.lower():
        pytest.fail(
            f"{context} failed: Resource not found. "
            "Check that the requested resource exists."
        )
    elif "403" in error_str or "forbidden" in error_str.lower():
        pytest.fail(
            f"{context} failed: Permission denied. "
            "Your API token may not have sufficient permissions."
        )
    elif "429" in error_str or "rate limit" in error_str.lower():
        pytest.fail(
            f"{context} failed: Rate limit exceeded."
        )
    else:
        pytest.fail(f"{context} failed: {error}")


def generate_test_timestamp() -> str:
    """
    Generate ISO format timestamp for testing.
    
    Returns
    -------
    str
        Current timestamp in ISO format
    """
    return datetime.now(timezone.utc).isoformat()


def assert_within_time_range(
    timestamp: str, 
    expected: datetime, 
    tolerance_seconds: int = 60
):
    """
    Assert timestamp is within expected range.
    
    Parameters
    ----------
    timestamp : str
        ISO format timestamp to check
    expected : datetime
        Expected timestamp
    tolerance_seconds : int
        Acceptable difference in seconds
    """
    # Handle various timestamp formats
    if timestamp.endswith('Z'):
        timestamp = timestamp[:-1] + '+00:00'
    
    actual = datetime.fromisoformat(timestamp)
    diff = abs((actual - expected).total_seconds())
    assert diff <= tolerance_seconds, (
        f"Timestamp {timestamp} not within {tolerance_seconds}s of expected"
    )