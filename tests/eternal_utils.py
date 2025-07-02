"""
Utility functions for eternal test data discovery and management.

This module provides:
- Data discovery functions to check if eternal data exists
- Test data selection helpers
- Eternal data validation utilities
- Migration helpers for transitioning from create mode to eternal mode
"""

import pytest
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone

from tests.eternal_config import eternal_config, get_eternal_data_for_test
from tests.eternal_test_data import (
    ETERNAL_TEST_DATA,
    get_eternal_user,
    get_eternal_device,
    get_eternal_object,
    get_test_scenario
)
from src.pipelines_api.api_client import CustomerIOClient
from src.pipelines_api.exceptions import CustomerIOError


def discover_eternal_user(
    client: CustomerIOClient,
    user_type: str = "basic"
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Discover if an eternal test user exists in the workspace.
    
    Parameters
    ----------
    client : CustomerIOClient
        API client for checking user existence
    user_type : str
        Type of eternal user to check
        
    Returns
    -------
    Tuple[bool, Optional[Dict]]
        (exists, user_data) - whether user exists and user data if found
    """
    try:
        user_data = get_eternal_user(user_type)
        user_id = user_data["id"]
        
        # Try to make a minimal API call to check user existence
        # Note: Customer.IO doesn't have a direct "get user" endpoint
        # This is a placeholder for the actual implementation
        
        # For now, assume user exists if we can get the configuration
        return True, user_data
        
    except KeyError:
        return False, None
    except Exception as e:
        print(f"Warning: Could not check eternal user existence: {e}")
        return False, None


def discover_eternal_device(
    client: CustomerIOClient,
    device_type: str = "ios_basic"
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Discover if an eternal test device exists.
    
    Parameters
    ----------
    client : CustomerIOClient
        API client for checking device existence
    device_type : str
        Type of eternal device to check
        
    Returns
    -------
    Tuple[bool, Optional[Dict]]
        (exists, device_data) - whether device exists and device data if found
    """
    try:
        device_data = get_eternal_device(device_type)
        
        # For now, assume device exists if we can get the configuration
        return True, device_data
        
    except KeyError:
        return False, None
    except Exception as e:
        print(f"Warning: Could not check eternal device existence: {e}")
        return False, None


def discover_eternal_object(
    client: CustomerIOClient,
    object_key: str = "company_a"
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Discover if an eternal test object exists.
    
    Parameters
    ----------
    client : CustomerIOClient
        API client for checking object existence
    object_key : str
        Key of eternal object to check
        
    Returns
    -------
    Tuple[bool, Optional[Dict]]
        (exists, object_data) - whether object exists and object data if found
    """
    try:
        object_data = get_eternal_object(object_key)
        
        # For now, assume object exists if we can get the configuration
        return True, object_data
        
    except KeyError:
        return False, None
    except Exception as e:
        print(f"Warning: Could not check eternal object existence: {e}")
        return False, None


def get_test_user_data(
    test_scenario: str = "basic",
    fallback_to_new: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get user data for testing based on current configuration.
    
    Parameters
    ----------
    test_scenario : str
        Test scenario name
    fallback_to_new : bool
        Whether to return None (create new) if eternal data not available
        
    Returns
    -------
    Dict[str, Any] or None
        User data or None if should create new
    """
    if eternal_config.is_eternal_mode:
        try:
            return get_eternal_user(test_scenario)
        except KeyError:
            if fallback_to_new:
                return None
            else:
                # Fallback to basic user
                return get_eternal_user("basic")
    
    # Non-eternal modes
    return eternal_config.get_user_for_test(test_scenario)


def get_test_device_data(
    platform: str = "ios",
    fallback_to_new: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get device data for testing based on current configuration.
    
    Parameters
    ----------
    platform : str
        Device platform
    fallback_to_new : bool
        Whether to return None (create new) if eternal data not available
        
    Returns
    -------
    Dict[str, Any] or None
        Device data or None if should create new
    """
    if eternal_config.is_eternal_mode:
        device_key = f"{platform}_basic"
        try:
            return get_eternal_device(device_key)
        except KeyError:
            if fallback_to_new:
                return None
            else:
                # Fallback to ios_basic
                return get_eternal_device("ios_basic")
    
    # Non-eternal modes
    return eternal_config.get_device_for_test(platform)


def get_test_object_data(
    object_type: str = "company",
    fallback_to_new: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get object data for testing based on current configuration.
    
    Parameters
    ----------
    object_type : str
        Type of object
    fallback_to_new : bool
        Whether to return None (create new) if eternal data not available
        
    Returns
    -------
    Dict[str, Any] or None
        Object data or None if should create new
    """
    if eternal_config.is_eternal_mode:
        # Find object of requested type
        for key, obj_data in ETERNAL_TEST_DATA["objects"].items():
            if obj_data["type"] == object_type:
                return get_eternal_object(key)
        
        if fallback_to_new:
            return None
        else:
            # Return first available object
            first_key = next(iter(ETERNAL_TEST_DATA["objects"]))
            return get_eternal_object(first_key)
    
    # Non-eternal modes
    return eternal_config.get_object_for_test(object_type)


def skip_if_eternal_data_missing(
    client: CustomerIOClient,
    required_data: List[str]
) -> Optional[str]:
    """
    Check if test should be skipped due to missing eternal data.
    
    Parameters
    ----------
    client : CustomerIOClient
        API client for data validation
    required_data : List[str]
        List of required data types (user, device, object)
        
    Returns
    -------
    str or None
        Skip reason if should skip, None if should proceed
    """
    if not eternal_config.is_eternal_mode:
        return None
    
    if not eternal_config.skip_if_no_eternal_data:
        return None
    
    # Check each required data type
    for data_type in required_data:
        if data_type == "user":
            exists, _ = discover_eternal_user(client)
            if not exists:
                return f"Eternal test user data not found"
        
        elif data_type == "device":
            exists, _ = discover_eternal_device(client)
            if not exists:
                return f"Eternal test device data not found"
        
        elif data_type == "object":
            exists, _ = discover_eternal_object(client)
            if not exists:
                return f"Eternal test object data not found"
    
    return None


def validate_eternal_data_integrity(client: CustomerIOClient) -> Dict[str, Any]:
    """
    Validate the integrity of eternal test data.
    
    Parameters
    ----------
    client : CustomerIOClient
        API client for validation
        
    Returns
    -------
    Dict[str, Any]
        Validation report
    """
    report = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "data_counts": {
            "users": len(ETERNAL_TEST_DATA["users"]),
            "devices": len(ETERNAL_TEST_DATA["devices"]),
            "objects": len(ETERNAL_TEST_DATA["objects"]),
            "relationships": len(ETERNAL_TEST_DATA["relationships"])
        },
        "checks_performed": []
    }
    
    if not eternal_config.is_eternal_mode:
        report["warnings"].append("Not in eternal data mode - skipping validation")
        return report
    
    try:
        # Check user data consistency
        report["checks_performed"].append("user_data_consistency")
        for user_type, user_data in ETERNAL_TEST_DATA["users"].items():
            if not user_data.get("id"):
                report["errors"].append(f"User {user_type} missing ID")
                report["valid"] = False
            
            if not user_data.get("email"):
                report["errors"].append(f"User {user_type} missing email")
                report["valid"] = False
        
        # Check device data consistency
        report["checks_performed"].append("device_data_consistency")
        for device_type, device_data in ETERNAL_TEST_DATA["devices"].items():
            if not device_data.get("id"):
                report["errors"].append(f"Device {device_type} missing ID")
                report["valid"] = False
            
            if not device_data.get("platform"):
                report["errors"].append(f"Device {device_type} missing platform")
                report["valid"] = False
        
        # Check object data consistency
        report["checks_performed"].append("object_data_consistency")
        for object_key, object_data in ETERNAL_TEST_DATA["objects"].items():
            if not object_data.get("id"):
                report["errors"].append(f"Object {object_key} missing ID")
                report["valid"] = False
            
            if not object_data.get("type"):
                report["errors"].append(f"Object {object_key} missing type")
                report["valid"] = False
        
        # Check relationship data consistency
        report["checks_performed"].append("relationship_data_consistency")
        for i, rel_data in enumerate(ETERNAL_TEST_DATA["relationships"]):
            if not rel_data.get("user_id"):
                report["errors"].append(f"Relationship {i+1} missing user_id")
                report["valid"] = False
            
            if not rel_data.get("object_id"):
                report["errors"].append(f"Relationship {i+1} missing object_id")
                report["valid"] = False
        
    except Exception as e:
        report["errors"].append(f"Validation failed with error: {e}")
        report["valid"] = False
    
    return report


def get_eternal_data_summary() -> Dict[str, Any]:
    """
    Get a summary of available eternal test data.
    
    Returns
    -------
    Dict[str, Any]
        Summary of eternal data configuration
    """
    summary = {
        "enabled": eternal_config.is_eternal_mode,
        "version": eternal_config.eternal_data_version,
        "data_counts": {},
        "user_types": [],
        "device_types": [],
        "object_types": [],
        "test_scenarios": []
    }
    
    if eternal_config.is_eternal_mode:
        summary["data_counts"] = {
            "users": len(ETERNAL_TEST_DATA["users"]),
            "devices": len(ETERNAL_TEST_DATA["devices"]),
            "objects": len(ETERNAL_TEST_DATA["objects"]),
            "relationships": len(ETERNAL_TEST_DATA["relationships"])
        }
        
        summary["user_types"] = list(ETERNAL_TEST_DATA["users"].keys())
        summary["device_types"] = list(ETERNAL_TEST_DATA["devices"].keys())
        summary["object_types"] = list(set(
            obj["type"] for obj in ETERNAL_TEST_DATA["objects"].values()
        ))
        
        # Get available test scenarios
        try:
            from tests.eternal_test_data import TEST_SCENARIOS
            summary["test_scenarios"] = list(TEST_SCENARIOS.keys())
        except ImportError:
            summary["test_scenarios"] = []
    
    return summary


def migrate_to_eternal_data_suggestions(client: CustomerIOClient) -> List[str]:
    """
    Provide suggestions for migrating from create mode to eternal data mode.
    
    Parameters
    ----------
    client : CustomerIOClient
        API client for analysis
        
    Returns
    -------
    List[str]
        List of migration suggestions
    """
    suggestions = []
    
    if eternal_config.is_eternal_mode:
        suggestions.append("Already in eternal data mode")
        return suggestions
    
    suggestions.extend([
        "1. Run 'python setup_eternal_data.py --dry-run' to preview eternal data creation",
        "2. Run 'python setup_eternal_data.py --create' to create eternal test data",
        "3. Update TEST_DATA_MODE=eternal in your .env file",
        "4. Update ETERNAL_DATA_ENABLED=true in your .env file",
        "5. Run tests with pytest -m 'read_only' to test eternal data",
        "6. Update individual test files to use eternal_utils.get_test_*_data() functions",
        "7. Add pytest markers for read_only vs mutation tests"
    ])
    
    return suggestions