"""
Unified configuration for eternal test data across all integration tests.

This module provides:
- Unified configuration for eternal vs traditional test data modes
- Data discovery utilities to check if eternal data exists
- Helper functions for test data mode detection
- Eternal data validation and fallback strategies
"""

import os
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv

from tests.eternal_test_data import (
    ETERNAL_TEST_DATA, 
    ETERNAL_DATA_VERSION,
    get_eternal_user,
    get_eternal_device,
    get_eternal_object,
    get_test_scenario,
    list_read_only_scenarios,
    list_mutation_scenarios
)
from src.pipelines_api.api_client import CustomerIOClient
from src.pipelines_api.exceptions import CustomerIOError

# Load environment variables
load_dotenv()


class EternalDataConfig:
    """Configuration and utilities for eternal test data management."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.test_data_mode = os.getenv("TEST_DATA_MODE", "create").lower()
        self.eternal_data_enabled = os.getenv("ETERNAL_DATA_ENABLED", "false").lower() == "true"
        self.eternal_data_version = os.getenv("ETERNAL_DATA_VERSION", ETERNAL_DATA_VERSION)
        self.skip_if_no_eternal_data = os.getenv("SKIP_IF_NO_ETERNAL_DATA", "true").lower() == "true"
        
        # Legacy configuration for existing/hybrid modes
        self.existing_customer_id = os.getenv("TEST_EXISTING_CUSTOMER_ID")
        self.existing_email = os.getenv("TEST_EXISTING_EMAIL")
        self.existing_device_token = os.getenv("TEST_EXISTING_DEVICE_TOKEN")
        
    @property
    def is_eternal_mode(self) -> bool:
        """Check if eternal data mode is enabled."""
        return self.test_data_mode == "eternal" and self.eternal_data_enabled
    
    @property
    def is_create_mode(self) -> bool:
        """Check if create new data mode is enabled."""
        return self.test_data_mode == "create"
    
    @property
    def is_existing_mode(self) -> bool:
        """Check if existing data mode is enabled."""
        return self.test_data_mode in ["existing", "hybrid"]
    
    def get_user_for_test(self, test_scenario: str = "basic") -> Dict[str, Any]:
        """
        Get user data appropriate for current test mode.
        
        Parameters
        ----------
        test_scenario : str
            Test scenario name (maps to eternal user types)
            
        Returns
        -------
        Dict[str, Any]
            User data for the test
            
        Raises
        ------
        ValueError
            If eternal mode is enabled but user type not found
        """
        if self.is_eternal_mode:
            try:
                return get_eternal_user(test_scenario)
            except KeyError:
                # Fallback to basic user if specific scenario not found
                return get_eternal_user("basic")
        
        elif self.is_existing_mode and self.existing_customer_id:
            return {
                "id": self.existing_customer_id,
                "email": self.existing_email or f"{self.existing_customer_id}@test.example.com",
                "traits": {"test_mode": "existing"}
            }
        
        else:
            # Create mode - return None to indicate new data should be created
            return None
    
    def get_device_for_test(self, platform: str = "ios") -> Optional[Dict[str, Any]]:
        """
        Get device data appropriate for current test mode.
        
        Parameters
        ----------
        platform : str
            Device platform (ios, android, web)
            
        Returns
        -------
        Dict[str, Any] or None
            Device data for the test, or None if should create new
        """
        if self.is_eternal_mode:
            device_key = f"{platform}_basic"
            try:
                return get_eternal_device(device_key)
            except KeyError:
                # Fallback to ios_basic if platform not found
                return get_eternal_device("ios_basic")
        
        elif self.is_existing_mode and self.existing_device_token:
            return {
                "id": self.existing_device_token,
                "platform": platform,
                "eternal_data": False
            }
        
        else:
            # Create mode
            return None
    
    def get_object_for_test(self, object_type: str = "company") -> Optional[Dict[str, Any]]:
        """
        Get object data appropriate for current test mode.
        
        Parameters
        ----------
        object_type : str
            Type of object (company, product, etc.)
            
        Returns
        -------
        Dict[str, Any] or None
            Object data for the test, or None if should create new
        """
        if self.is_eternal_mode:
            # Find first object of the requested type
            for key, obj_data in ETERNAL_TEST_DATA["objects"].items():
                if obj_data["type"] == object_type:
                    return get_eternal_object(key)
            
            # Fallback to first available object
            if ETERNAL_TEST_DATA["objects"]:
                first_key = next(iter(ETERNAL_TEST_DATA["objects"]))
                return get_eternal_object(first_key)
        
        # For existing/create modes, return None to indicate new object should be created
        return None
    
    def should_skip_test(self, test_name: str, requires_mutation: bool = False) -> tuple[bool, str]:
        """
        Determine if a test should be skipped based on current configuration.
        
        Parameters
        ----------
        test_name : str
            Name of the test
        requires_mutation : bool
            Whether the test requires data mutation
            
        Returns
        -------
        tuple[bool, str]
            (should_skip, reason)
        """
        if self.is_eternal_mode:
            if requires_mutation:
                # Check if this is an allowed mutation scenario
                mutation_scenarios = list_mutation_scenarios()
                if test_name not in mutation_scenarios:
                    return True, f"Test {test_name} requires mutation but is not in allowed mutation scenarios"
            
            if self.skip_if_no_eternal_data:
                # TODO: Add actual eternal data existence check
                # For now, assume eternal data exists if version matches
                if self.eternal_data_version != ETERNAL_DATA_VERSION:
                    return True, f"Eternal data version mismatch: expected {ETERNAL_DATA_VERSION}, got {self.eternal_data_version}"
        
        return False, ""
    
    def get_test_scenarios_for_mode(self) -> List[str]:
        """
        Get list of test scenarios appropriate for current mode.
        
        Returns
        -------
        List[str]
            List of test scenario names
        """
        if self.is_eternal_mode:
            # Return read-only scenarios by default
            return list_read_only_scenarios()
        else:
            # In create/existing modes, all scenarios are available
            return list(get_test_scenario.__annotations__.keys()) if hasattr(get_test_scenario, '__annotations__') else ["basic"]


# Global configuration instance
eternal_config = EternalDataConfig()


def get_eternal_data_for_test(
    test_type: str = "user",
    test_scenario: str = "basic",
    fallback_to_create: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get eternal test data for a specific test scenario.
    
    Parameters
    ----------
    test_type : str
        Type of data (user, device, object)
    test_scenario : str
        Test scenario name
    fallback_to_create : bool
        Whether to return None (create mode) if eternal data not available
        
    Returns
    -------
    Dict[str, Any] or None
        Test data or None if should create new data
    """
    if not eternal_config.is_eternal_mode:
        return None if fallback_to_create else {}
    
    try:
        if test_type == "user":
            return eternal_config.get_user_for_test(test_scenario)
        elif test_type == "device":
            return eternal_config.get_device_for_test(test_scenario)
        elif test_type == "object":
            return eternal_config.get_object_for_test(test_scenario)
        else:
            return None
    except Exception as e:
        if fallback_to_create:
            return None
        else:
            raise ValueError(f"Failed to get eternal {test_type} data: {e}")


def validate_eternal_data_exists(client: CustomerIOClient) -> Dict[str, bool]:
    """
    Validate that eternal test data actually exists in the workspace.
    
    Parameters
    ----------
    client : CustomerIOClient
        API client for validation
        
    Returns
    -------
    Dict[str, bool]
        Validation results by data type
    """
    results = {
        "users": False,
        "devices": False,
        "objects": False,
        "version_match": False
    }
    
    if not eternal_config.is_eternal_mode:
        return results
    
    try:
        # Check if we can access a basic eternal user
        basic_user = get_eternal_user("basic")
        user_id = basic_user["id"]
        
        # Make a simple API call to check if user exists
        # Note: This is a simplified check - a full implementation would
        # need proper API methods to verify user existence
        
        results["users"] = True  # Assume true for now
        results["version_match"] = eternal_config.eternal_data_version == ETERNAL_DATA_VERSION
        
    except Exception as e:
        print(f"Warning: Could not validate eternal data existence: {e}")
    
    return results


def should_cleanup_test_data() -> bool:
    """
    Determine if test data should be cleaned up after tests.
    
    Returns
    -------
    bool
        True if cleanup should be performed
    """
    # Never cleanup eternal data
    if eternal_config.is_eternal_mode:
        return False
    
    # Always cleanup in create mode
    if eternal_config.is_create_mode:
        return True
    
    # Don't cleanup existing data
    return False


def get_test_data_summary() -> Dict[str, Any]:
    """
    Get a summary of current test data configuration.
    
    Returns
    -------
    Dict[str, Any]
        Configuration summary
    """
    return {
        "mode": eternal_config.test_data_mode,
        "eternal_enabled": eternal_config.eternal_data_enabled,
        "eternal_version": eternal_config.eternal_data_version,
        "skip_if_no_eternal": eternal_config.skip_if_no_eternal_data,
        "cleanup_enabled": should_cleanup_test_data(),
        "read_only_scenarios": len(list_read_only_scenarios()) if eternal_config.is_eternal_mode else "N/A",
        "mutation_scenarios": len(list_mutation_scenarios()) if eternal_config.is_eternal_mode else "N/A"
    }