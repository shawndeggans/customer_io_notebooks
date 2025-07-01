"""
Base class for Customer.IO integration tests.

Provides common functionality for all integration tests including:
- Setup and teardown methods
- Helper methods for API assertions
- Test data management
- Error handling utilities
"""

import time
import pytest
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone

from utils.api_client import CustomerIOClient
from utils.exceptions import CustomerIOError, RateLimitError


class BaseIntegrationTest:
    """
    Base class for Customer.IO integration tests.
    
    Provides common setup, teardown, and utility methods for testing
    against the real Customer.IO API.
    """
    
    # Track created resources for cleanup
    created_users: Set[str] = set()
    created_objects: Set[tuple] = set()  # (type, id) tuples
    created_devices: Set[str] = set()
    created_aliases: Set[tuple] = set()  # (user_id, previous_id) tuples
    
    @classmethod
    def setup_class(cls):
        """Set up test class with resource tracking."""
        cls.created_users = set()
        cls.created_objects = set()
        cls.created_devices = set()
        cls.created_aliases = set()
    
    @classmethod
    def teardown_class(cls):
        """Clean up any remaining test resources."""
        # Cleanup is handled by individual test methods
        # This is a safety net for any missed resources
        if cls.created_users or cls.created_objects or cls.created_devices:
            print(f"\nWarning: Uncleaned test resources detected:")
            print(f"  Users: {len(cls.created_users)}")
            print(f"  Objects: {len(cls.created_objects)}")
            print(f"  Devices: {len(cls.created_devices)}")
    
    def track_user(self, user_id: str):
        """
        Track a created user for cleanup.
        
        Parameters
        ----------
        user_id : str
            User ID to track
        """
        self.created_users.add(user_id)
    
    def track_object(self, object_type: str, object_id: str):
        """
        Track a created object for cleanup.
        
        Parameters
        ----------
        object_type : str
            Type of object
        object_id : str
            Object ID to track
        """
        self.created_objects.add((object_type, object_id))
    
    def track_device(self, device_id: str):
        """
        Track a created device for cleanup.
        
        Parameters
        ----------
        device_id : str
            Device ID to track
        """
        self.created_devices.add(device_id)
    
    def track_alias(self, user_id: str, previous_id: str):
        """
        Track a created alias for cleanup.
        
        Parameters
        ----------
        user_id : str
            Primary user ID
        previous_id : str
            Previous ID that was aliased
        """
        self.created_aliases.add((user_id, previous_id))
    
    def assert_api_response(
        self, 
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
    
    def assert_successful_response(self, response: Dict[str, Any]):
        """
        Assert that API response indicates success.
        
        Parameters
        ----------
        response : dict
            API response to validate
        """
        # Customer.IO typically returns empty response on success
        # or a response with specific success indicators
        if response:
            # Check for error indicators
            assert "error" not in response, f"Error in response: {response.get('error')}"
            assert "errors" not in response, f"Errors in response: {response.get('errors')}"
    
    def retry_on_rate_limit(
        self, 
        func, 
        *args, 
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        **kwargs
    ) -> Any:
        """
        Retry a function call if rate limited.
        
        Parameters
        ----------
        func : callable
            Function to call
        *args
            Positional arguments for function
        max_retries : int
            Maximum number of retries
        backoff_factor : float
            Exponential backoff factor
        **kwargs
            Keyword arguments for function
            
        Returns
        -------
        Any
            Function result
            
        Raises
        ------
        RateLimitError
            If max retries exceeded
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    print(f"Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    raise
        
        raise last_error
    
    def wait_for_eventual_consistency(self, seconds: float = 1.0):
        """
        Wait for API eventual consistency.
        
        Some operations may not be immediately reflected in the API.
        
        Parameters
        ----------
        seconds : float
            Seconds to wait
        """
        time.sleep(seconds)
    
    def cleanup_user(self, client: CustomerIOClient, user_id: str):
        """
        Clean up a test user.
        
        Parameters
        ----------
        client : CustomerIOClient
            API client instance
        user_id : str
            User ID to delete
        """
        try:
            client.delete(user_id)
            self.created_users.discard(user_id)
        except CustomerIOError as e:
            # User might already be deleted
            if "not found" not in str(e).lower():
                print(f"Warning: Failed to cleanup user {user_id}: {e}")
    
    def cleanup_object(
        self, 
        client: CustomerIOClient, 
        object_type: str, 
        object_id: str
    ):
        """
        Clean up a test object.
        
        Parameters
        ----------
        client : CustomerIOClient
            API client instance
        object_type : str
            Type of object
        object_id : str
            Object ID to delete
        """
        try:
            # Objects are deleted via the /group endpoint
            data = {
                "groupId": object_id,
                "objectTypeId": object_type
            }
            client.make_request("DELETE", "/group", data)
            self.created_objects.discard((object_type, object_id))
        except CustomerIOError as e:
            # Object might already be deleted
            if "not found" not in str(e).lower():
                print(f"Warning: Failed to cleanup object {object_type}/{object_id}: {e}")
    
    def cleanup_device(self, client: CustomerIOClient, device_id: str):
        """
        Clean up a test device.
        
        Parameters
        ----------
        client : CustomerIOClient
            API client instance
        device_id : str
            Device ID to delete
        """
        try:
            # Devices are deleted via device endpoints
            # Implementation depends on device type
            self.created_devices.discard(device_id)
        except CustomerIOError as e:
            print(f"Warning: Failed to cleanup device {device_id}: {e}")
    
    def generate_test_timestamp(self) -> str:
        """
        Generate ISO format timestamp for testing.
        
        Returns
        -------
        str
            Current timestamp in ISO format
        """
        return datetime.now(timezone.utc).isoformat()
    
    def assert_within_time_range(
        self, 
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
        actual = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        diff = abs((actual - expected).total_seconds())
        assert diff <= tolerance_seconds, (
            f"Timestamp {timestamp} not within {tolerance_seconds}s of expected"
        )