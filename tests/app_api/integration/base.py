"""
Base class for Customer.IO App API integration tests.

Provides common functionality for App API integration tests including:
- Setup and teardown methods
- Helper methods for API assertions
- Test data management with mode support
- Data restoration utilities
"""

import time
import pytest
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timezone

from src.app_api.auth import AppAPIAuth
from src.app_api import client as app_client


class BaseAppAPIIntegrationTest:
    """
    Base class for Customer.IO App API integration tests.
    
    Provides common setup, teardown, and utility methods for testing
    against the real Customer.IO App API with support for different
    test data modes.
    """
    
    # Track resources and modifications
    created_customers: Set[str] = set()
    modified_customers: Dict[str, Dict[str, Any]] = {}  # customer_id -> original_state
    
    @classmethod
    def setup_class(cls):
        """Set up test class with resource tracking."""
        cls.created_customers = set()
        cls.modified_customers = {}
    
    @classmethod
    def teardown_class(cls):
        """Report any remaining test resources."""
        if cls.created_customers or cls.modified_customers:
            print(f"\nWarning: Uncleaned App API test resources detected:")
            print(f"  Created customers: {len(cls.created_customers)}")
            print(f"  Modified customers: {len(cls.modified_customers)}")
    
    def track_created_customer(self, customer_id: str):
        """
        Track a created customer for cleanup.
        
        Parameters
        ----------
        customer_id : str
            Customer ID that was created
        """
        self.created_customers.add(customer_id)
    
    def track_customer_modification(self, customer_id: str, original_state: Dict[str, Any]):
        """
        Track customer modification for restoration.
        
        Parameters
        ----------
        customer_id : str
            Customer ID that was modified
        original_state : dict
            Original customer state to restore
        """
        self.modified_customers[customer_id] = original_state
    
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
        # App API typically returns specific response structures
        # Check for error indicators
        assert "error" not in response, f"Error in response: {response.get('error')}"
        assert "errors" not in response, f"Errors in response: {response.get('errors')}"
        
        # Many successful responses have meta information
        if "meta" in response:
            assert response["meta"].get("error") is None, "Error in meta field"
    
    def get_customer_state(self, auth: AppAPIAuth, customer_id: str) -> Dict[str, Any]:
        """
        Get current customer state for backup/restoration.
        
        Parameters
        ----------
        auth : AppAPIAuth
            Authenticated App API auth object
        customer_id : str
            Customer ID to get state for
            
        Returns
        -------
        dict
            Current customer state
        """
        try:
            customer_data = app_client.get_customer(auth, customer_id)
            # Also get attributes separately if needed
            attributes_data = app_client.get_customer_attributes(auth, customer_id)
            
            return {
                "customer": customer_data.get("customer", {}),
                "attributes": attributes_data.get("customer", {}).get("attributes", {})
            }
        except Exception as e:
            print(f"Warning: Could not get customer state for {customer_id}: {e}")
            return {}
    
    def restore_customer_state(
        self, 
        auth: AppAPIAuth, 
        customer_id: str, 
        original_state: Dict[str, Any]
    ):
        """
        Restore customer to original state.
        
        Parameters
        ----------
        auth : AppAPIAuth
            Authenticated App API auth object
        customer_id : str
            Customer ID to restore
        original_state : dict
            Original state to restore
        """
        try:
            if original_state and "attributes" in original_state:
                # Restore attributes
                app_client.update_customer(
                    auth,
                    customer_id,
                    attributes=original_state["attributes"]
                )
            self.modified_customers.pop(customer_id, None)
        except Exception as e:
            print(f"Warning: Could not restore customer {customer_id}: {e}")
    
    def cleanup_created_customer(self, auth: AppAPIAuth, customer_id: str):
        """
        Clean up a created test customer.
        
        Parameters
        ----------
        auth : AppAPIAuth
            Authenticated App API auth object
        customer_id : str
            Customer ID to delete
        """
        try:
            app_client.delete_customer(auth, customer_id)
            self.created_customers.discard(customer_id)
        except Exception as e:
            # Customer might already be deleted
            if "404" not in str(e) and "not found" not in str(e).lower():
                print(f"Warning: Failed to cleanup customer {customer_id}: {e}")
    
    def cleanup_all_resources(self, auth: AppAPIAuth):
        """
        Clean up all tracked resources.
        
        Parameters
        ----------
        auth : AppAPIAuth
            Authenticated App API auth object
        """
        # Restore modified customers first
        for customer_id, original_state in list(self.modified_customers.items()):
            self.restore_customer_state(auth, customer_id, original_state)
        
        # Then delete created customers
        for customer_id in list(self.created_customers):
            self.cleanup_created_customer(auth, customer_id)
    
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
    
    def handle_api_error(self, error: Exception, context: str = "API call"):
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
                "Please check your CUSTOMERIO_APP_API_TOKEN in .env file. "
                "Get a valid token from Customer.IO UI: Settings > API Credentials > App API Keys"
            )
        elif "404" in error_str or "not found" in error_str.lower():
            pytest.fail(
                f"{context} failed: Resource not found. "
                "Check that the requested resource exists in your Customer.IO workspace."
            )
        elif "403" in error_str or "forbidden" in error_str.lower():
            pytest.fail(
                f"{context} failed: Permission denied. "
                "Your API token may not have sufficient permissions for this operation."
            )
        elif "429" in error_str or "rate limit" in error_str.lower():
            pytest.fail(
                f"{context} failed: Rate limit exceeded. "
                "Tests are running too fast - this should be handled automatically."
            )
        else:
            pytest.fail(f"{context} failed: {error}")
    
    def assert_customer_exists(self, auth: AppAPIAuth, customer_id: str):
        """
        Assert that a customer exists in the system.
        
        Parameters
        ----------
        auth : AppAPIAuth
            Authenticated App API auth object
        customer_id : str
            Customer ID to check
        """
        try:
            result = app_client.get_customer(auth, customer_id)
            assert "customer" in result, "Customer data not found in response"
            assert result["customer"]["id"] == customer_id, "Customer ID mismatch"
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                pytest.fail(f"Authentication failed - check your CUSTOMERIO_APP_API_TOKEN: {e}")
            elif "404" in str(e) or "not found" in str(e).lower():
                pytest.fail(f"Customer {customer_id} does not exist in your Customer.IO workspace")
            else:
                pytest.fail(f"Customer {customer_id} could not be accessed: {e}")
    
    def assert_customer_not_exists(self, auth: AppAPIAuth, customer_id: str):
        """
        Assert that a customer does not exist in the system.
        
        Parameters
        ----------
        auth : AppAPIAuth
            Authenticated App API auth object
        customer_id : str
            Customer ID to check
        """
        with pytest.raises(Exception) as exc_info:
            app_client.get_customer(auth, customer_id)
        
        # Check that it's a 404 error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
    
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
        # Handle various timestamp formats
        if timestamp.endswith('Z'):
            timestamp = timestamp[:-1] + '+00:00'
        
        actual = datetime.fromisoformat(timestamp)
        diff = abs((actual - expected).total_seconds())
        assert diff <= tolerance_seconds, (
            f"Timestamp {timestamp} not within {tolerance_seconds}s of expected"
        )
    
    def ensure_test_customer_exists(
        self, 
        auth: AppAPIAuth, 
        customer_id: str,
        email: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Ensure a test customer exists (for existing mode).
        
        Parameters
        ----------
        auth : AppAPIAuth
            Authenticated App API auth object
        customer_id : str
            Customer ID to ensure exists
        email : str
            Customer email
        attributes : dict, optional
            Additional attributes to set
        """
        try:
            # Check if customer exists
            app_client.get_customer(auth, customer_id)
            return  # Customer exists, we're done
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                self.handle_api_error(e, f"Checking customer {customer_id}")
            elif "404" in str(e) or "not found" in str(e).lower():
                # Customer doesn't exist, try to create it
                try:
                    app_client.create_customer(
                        auth,
                        email=email,
                        id=customer_id,
                        attributes=attributes or {}
                    )
                    self.track_created_customer(customer_id)
                except Exception as create_error:
                    if "409" in str(create_error):  # Already exists (race condition)
                        pass
                    else:
                        self.handle_api_error(create_error, f"Creating customer {customer_id}")
            else:
                self.handle_api_error(e, f"Checking customer {customer_id}")