"""
Eternal Test Data Configuration for Customer.IO Integration Tests

This module defines a fixed set of test data that exists permanently 
in the Customer.IO workspace. Tests use this data for read-only operations,
eliminating the need to create/delete data during test runs.

The data is designed to be:
- Comprehensive: Covers all test scenarios
- Permanent: Never deleted, always available
- Isolated: Clearly marked as test data
- Deterministic: Same data every time
"""

from typing import Dict, Any, List
from datetime import datetime, timezone

# Timestamp for when this data configuration was created
ETERNAL_DATA_VERSION = "2025_01_02_v1"

# Base prefix for all eternal test data
ETERNAL_PREFIX = "eternal_test"

# Eternal test data configuration
ETERNAL_TEST_DATA = {
    # Users for various test scenarios
    "users": {
        # Basic user with minimal data
        "basic": {
            "id": f"{ETERNAL_PREFIX}_user_basic",
            "email": f"{ETERNAL_PREFIX}_user_basic@eternal.test",
            "traits": {
                "first_name": "Basic",
                "last_name": "User",
                "plan": "free",
                "status": "active",
                "created_at": "2025-01-01T00:00:00Z",
                "test_category": "basic",
                "eternal_data": True
            }
        },
        
        # Premium user with rich data
        "premium": {
            "id": f"{ETERNAL_PREFIX}_user_premium", 
            "email": f"{ETERNAL_PREFIX}_user_premium@eternal.test",
            "traits": {
                "first_name": "Premium",
                "last_name": "User",
                "plan": "premium",
                "status": "active",
                "company": "Eternal Test Corp",
                "location": "Test City",
                "signup_date": "2024-12-01T00:00:00Z",
                "lifetime_value": 1000,
                "test_category": "premium",
                "eternal_data": True
            }
        },
        
        # Inactive user for testing edge cases
        "inactive": {
            "id": f"{ETERNAL_PREFIX}_user_inactive",
            "email": f"{ETERNAL_PREFIX}_user_inactive@eternal.test", 
            "traits": {
                "first_name": "Inactive",
                "last_name": "User",
                "plan": "free",
                "status": "inactive",
                "last_seen": "2024-06-01T00:00:00Z",
                "test_category": "inactive",
                "eternal_data": True
            }
        },
        
        # User for suppression testing
        "suppression": {
            "id": f"{ETERNAL_PREFIX}_user_suppression",
            "email": f"{ETERNAL_PREFIX}_user_suppression@eternal.test",
            "traits": {
                "first_name": "Suppression",
                "last_name": "Test",
                "plan": "basic",
                "status": "active",
                "test_category": "suppression",
                "eternal_data": True
            }
        },
        
        # User for alias testing
        "alias_primary": {
            "id": f"{ETERNAL_PREFIX}_user_alias_primary",
            "email": f"{ETERNAL_PREFIX}_user_alias_primary@eternal.test",
            "traits": {
                "first_name": "Alias",
                "last_name": "Primary",
                "test_category": "alias",
                "eternal_data": True
            }
        },
        
        # User for GDPR testing
        "gdpr": {
            "id": f"{ETERNAL_PREFIX}_user_gdpr",
            "email": f"{ETERNAL_PREFIX}_user_gdpr@eternal.test",
            "traits": {
                "first_name": "GDPR",
                "last_name": "Test",
                "gdpr_compliant": True,
                "test_category": "gdpr",
                "eternal_data": True
            }
        }
    },
    
    # Devices for mobile/push testing
    "devices": {
        "ios_basic": {
            "id": f"{ETERNAL_PREFIX}_device_ios_basic",
            "platform": "ios",
            "last_used": "2025-01-01T00:00:00Z",
            "eternal_data": True
        },
        
        "android_basic": {
            "id": f"{ETERNAL_PREFIX}_device_android_basic", 
            "platform": "android",
            "last_used": "2025-01-01T00:00:00Z",
            "eternal_data": True
        },
        
        "web_basic": {
            "id": f"{ETERNAL_PREFIX}_device_web_basic",
            "platform": "web", 
            "last_used": "2025-01-01T00:00:00Z",
            "eternal_data": True
        }
    },
    
    # Objects for relationship testing
    "objects": {
        "company_a": {
            "type": "company",
            "id": f"{ETERNAL_PREFIX}_company_a",
            "attributes": {
                "name": "Eternal Test Company A",
                "industry": "Technology",
                "size": "medium",
                "eternal_data": True
            }
        },
        
        "company_b": {
            "type": "company", 
            "id": f"{ETERNAL_PREFIX}_company_b",
            "attributes": {
                "name": "Eternal Test Company B",
                "industry": "Finance",
                "size": "large",
                "eternal_data": True
            }
        },
        
        "product_x": {
            "type": "product",
            "id": f"{ETERNAL_PREFIX}_product_x",
            "attributes": {
                "name": "Eternal Test Product X",
                "category": "Software",
                "price": 99.99,
                "eternal_data": True
            }
        },
        
        "product_y": {
            "type": "product",
            "id": f"{ETERNAL_PREFIX}_product_y", 
            "attributes": {
                "name": "Eternal Test Product Y",
                "category": "Hardware",
                "price": 199.99,
                "eternal_data": True
            }
        }
    },
    
    # Events for testing event tracking
    "events": {
        "purchase": {
            "name": "eternal_test_purchase",
            "properties": {
                "product": "eternal_test_product",
                "amount": 50.00,
                "currency": "USD",
                "eternal_data": True
            }
        },
        
        "login": {
            "name": "eternal_test_login",
            "properties": {
                "method": "email",
                "source": "web",
                "eternal_data": True
            }
        },
        
        "page_view": {
            "name": "eternal_test_page_view",
            "properties": {
                "url": "/eternal-test-page",
                "title": "Eternal Test Page",
                "eternal_data": True
            }
        }
    },
    
    # Relationships between entities
    "relationships": [
        # User to Company relationships
        {
            "user_id": f"{ETERNAL_PREFIX}_user_basic",
            "object_type": "company",
            "object_id": f"{ETERNAL_PREFIX}_company_a",
            "relationship": "employee"
        },
        {
            "user_id": f"{ETERNAL_PREFIX}_user_premium", 
            "object_type": "company",
            "object_id": f"{ETERNAL_PREFIX}_company_b",
            "relationship": "admin"
        },
        
        # User to Product relationships
        {
            "user_id": f"{ETERNAL_PREFIX}_user_premium",
            "object_type": "product", 
            "object_id": f"{ETERNAL_PREFIX}_product_x",
            "relationship": "purchased"
        },
        {
            "user_id": f"{ETERNAL_PREFIX}_user_basic",
            "object_type": "product",
            "object_id": f"{ETERNAL_PREFIX}_product_y", 
            "relationship": "viewed"
        }
    ],
    
    # Test aliases for alias testing
    "aliases": [
        {
            "user_id": f"{ETERNAL_PREFIX}_user_alias_primary",
            "previous_id": f"{ETERNAL_PREFIX}_user_alias_secondary"
        }
    ]
}

# Test scenarios that map to specific data combinations
TEST_SCENARIOS = {
    "user_identification": {
        "description": "Test user identification with various user types",
        "users": ["basic", "premium", "inactive"],
        "read_only": True
    },
    
    "event_tracking": {
        "description": "Test event tracking with different event types", 
        "users": ["basic", "premium"],
        "events": ["purchase", "login", "page_view"],
        "read_only": True
    },
    
    "device_management": {
        "description": "Test device registration and management",
        "users": ["basic"],
        "devices": ["ios_basic", "android_basic", "web_basic"],
        "read_only": True
    },
    
    "object_relationships": {
        "description": "Test object creation and relationship management",
        "users": ["basic", "premium"],
        "objects": ["company_a", "company_b", "product_x", "product_y"],
        "relationships": True,
        "read_only": True
    },
    
    "user_suppression": {
        "description": "Test user suppression and unsuppression",
        "users": ["suppression"],
        "read_only": False,  # Modifies suppression status
        "mutates_data": True
    },
    
    "alias_management": {
        "description": "Test user aliasing functionality",
        "users": ["alias_primary"],
        "aliases": True,
        "read_only": False,  # Creates/modifies aliases
        "mutates_data": True
    },
    
    "gdpr_compliance": {
        "description": "Test GDPR compliance features",
        "users": ["gdpr"],
        "read_only": False,  # Tests deletion/suppression
        "mutates_data": True
    }
}

def get_eternal_user(user_type: str) -> Dict[str, Any]:
    """
    Get eternal test user data by type.
    
    Parameters
    ----------
    user_type : str
        Type of user (basic, premium, inactive, etc.)
        
    Returns
    -------
    Dict[str, Any]
        User data dictionary
        
    Raises
    ------
    KeyError
        If user type not found
    """
    if user_type not in ETERNAL_TEST_DATA["users"]:
        raise KeyError(f"Eternal user type '{user_type}' not found. Available: {list(ETERNAL_TEST_DATA['users'].keys())}")
    
    return ETERNAL_TEST_DATA["users"][user_type]

def get_eternal_device(device_type: str) -> Dict[str, Any]:
    """
    Get eternal test device data by type.
    
    Parameters
    ----------
    device_type : str
        Type of device (ios_basic, android_basic, etc.)
        
    Returns
    -------
    Dict[str, Any]
        Device data dictionary
    """
    if device_type not in ETERNAL_TEST_DATA["devices"]:
        raise KeyError(f"Eternal device type '{device_type}' not found. Available: {list(ETERNAL_TEST_DATA['devices'].keys())}")
    
    return ETERNAL_TEST_DATA["devices"][device_type]

def get_eternal_object(object_key: str) -> Dict[str, Any]:
    """
    Get eternal test object data by key.
    
    Parameters
    ---------- 
    object_key : str
        Object key (company_a, product_x, etc.)
        
    Returns
    -------
    Dict[str, Any]
        Object data dictionary
    """
    if object_key not in ETERNAL_TEST_DATA["objects"]:
        raise KeyError(f"Eternal object '{object_key}' not found. Available: {list(ETERNAL_TEST_DATA['objects'].keys())}")
    
    return ETERNAL_TEST_DATA["objects"][object_key]

def get_test_scenario(scenario_name: str) -> Dict[str, Any]:
    """
    Get test scenario configuration.
    
    Parameters
    ----------
    scenario_name : str
        Name of test scenario
        
    Returns
    -------
    Dict[str, Any]
        Scenario configuration
    """
    if scenario_name not in TEST_SCENARIOS:
        raise KeyError(f"Test scenario '{scenario_name}' not found. Available: {list(TEST_SCENARIOS.keys())}")
    
    return TEST_SCENARIOS[scenario_name]

def list_read_only_scenarios() -> List[str]:
    """Get list of read-only test scenarios."""
    return [name for name, config in TEST_SCENARIOS.items() if config.get("read_only", False)]

def list_mutation_scenarios() -> List[str]:
    """Get list of scenarios that mutate data."""
    return [name for name, config in TEST_SCENARIOS.items() if config.get("mutates_data", False)]