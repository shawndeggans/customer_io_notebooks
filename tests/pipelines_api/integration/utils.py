"""
Utilities for Customer.IO integration tests.

Provides helper functions for:
- Random test data generation
- API response validation
- Test data cleanup
- Rate limit management
"""

import random
import string
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from faker import Faker

from src.pipelines_api.api_client import CustomerIOClient
from src.pipelines_api.exceptions import CustomerIOError


# Initialize Faker for test data generation
fake = Faker()


def generate_test_email(prefix: str = "test") -> str:
    """
    Generate a unique test email address.
    
    Parameters
    ----------
    prefix : str
        Prefix for the email address
        
    Returns
    -------
    str
        Unique test email address
    """
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:6]
    return f"{prefix}_{timestamp}_{unique_id}@integration-test.example.com"


def generate_test_phone(country_code: str = "+1") -> str:
    """
    Generate a test phone number.
    
    Parameters
    ----------
    country_code : str
        Country code prefix
        
    Returns
    -------
    str
        Test phone number
    """
    # Generate a clearly fake number
    area_code = "555"
    prefix = "01"
    line = "".join(random.choices(string.digits, k=2))
    return f"{country_code}{area_code}{prefix}{line}"


def generate_test_traits(include_pii: bool = True) -> Dict[str, Any]:
    """
    Generate random user traits for testing.
    
    Parameters
    ----------
    include_pii : bool
        Whether to include PII fields
        
    Returns
    -------
    dict
        User traits dictionary
    """
    traits = {
        "plan": random.choice(["free", "basic", "premium", "enterprise"]),
        "status": random.choice(["active", "inactive", "trial"]),
        "score": random.randint(0, 100),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_test": True,
        "test_id": uuid.uuid4().hex
    }
    
    if include_pii:
        traits.update({
            "email": generate_test_email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone": generate_test_phone(),
            "company": fake.company(),
            "city": fake.city(),
            "country": fake.country_code()
        })
    
    return traits


def generate_test_event_properties() -> Dict[str, Any]:
    """
    Generate random event properties for testing.
    
    Returns
    -------
    dict
        Event properties dictionary
    """
    return {
        "source": "integration_test",
        "test_id": uuid.uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "random_string": fake.sentence(),
        "random_number": random.randint(1, 1000),
        "random_float": round(random.uniform(0, 100), 2),
        "random_bool": random.choice([True, False]),
        "random_array": [fake.word() for _ in range(3)],
        "nested_object": {
            "key1": fake.word(),
            "key2": random.randint(1, 100)
        }
    }


def generate_ecommerce_event_properties(event_type: str) -> Dict[str, Any]:
    """
    Generate ecommerce event properties for testing.
    
    Parameters
    ----------
    event_type : str
        Type of ecommerce event
        
    Returns
    -------
    dict
        Ecommerce event properties
    """
    base_props = {
        "test_id": uuid.uuid4().hex,
        "currency": "USD",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if event_type in ["Order Started", "Order Updated", "Order Completed"]:
        base_props.update({
            "order_id": f"test_order_{uuid.uuid4().hex[:8]}",
            "total": round(random.uniform(10, 500), 2),
            "subtotal": round(random.uniform(10, 400), 2),
            "tax": round(random.uniform(0, 50), 2),
            "shipping": round(random.uniform(0, 20), 2),
            "items": [
                {
                    "product_id": f"test_prod_{i}",
                    "name": fake.catch_phrase(),
                    "price": round(random.uniform(10, 100), 2),
                    "quantity": random.randint(1, 5)
                }
                for i in range(random.randint(1, 3))
            ]
        })
    elif event_type == "Product Viewed":
        base_props.update({
            "product_id": f"test_prod_{uuid.uuid4().hex[:8]}",
            "name": fake.catch_phrase(),
            "price": round(random.uniform(10, 500), 2),
            "category": fake.word(),
            "brand": fake.company()
        })
    elif event_type == "Cart Updated":
        base_props.update({
            "cart_id": f"test_cart_{uuid.uuid4().hex[:8]}",
            "total": round(random.uniform(10, 500), 2),
            "item_count": random.randint(1, 10),
            "action": random.choice(["add", "remove", "update"])
        })
    
    return base_props


def generate_device_data(platform: str = None) -> Dict[str, Any]:
    """
    Generate device data for testing.
    
    Parameters
    ----------
    platform : str, optional
        Device platform (ios, android, web)
        
    Returns
    -------
    dict
        Device data dictionary
    """
    if platform is None:
        platform = random.choice(["ios", "android", "web"])
    
    device_data = {
        "id": f"test_device_{uuid.uuid4().hex[:12]}",
        "platform": platform,
        "last_used": datetime.now(timezone.utc).isoformat(),
        "test_device": True
    }
    
    if platform == "ios":
        device_data.update({
            "model": random.choice(["iPhone 12", "iPhone 13", "iPhone 14", "iPad Pro"]),
            "os_version": f"{random.randint(14, 17)}.{random.randint(0, 5)}"
        })
    elif platform == "android":
        device_data.update({
            "model": random.choice(["Pixel 6", "Galaxy S22", "OnePlus 9"]),
            "os_version": f"{random.randint(10, 13)}.0"
        })
    elif platform == "web":
        device_data.update({
            "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
            "browser_version": f"{random.randint(90, 120)}.0"
        })
    
    return device_data


def validate_batch_response(response: Dict[str, Any], expected_count: int):
    """
    Validate a batch API response.
    
    Parameters
    ----------
    response : dict
        Batch API response
    expected_count : int
        Expected number of processed items
        
    Raises
    ------
    AssertionError
        If validation fails
    """
    assert "processed" in response, "Batch response missing 'processed' count"
    assert response["processed"] == expected_count, (
        f"Expected {expected_count} processed, got {response['processed']}"
    )
    
    if "failed" in response:
        assert response["failed"] == 0, f"Batch had {response['failed']} failures"


def cleanup_test_users(
    client: CustomerIOClient, 
    user_ids: List[str],
    ignore_errors: bool = True
) -> Dict[str, Any]:
    """
    Clean up multiple test users.
    
    Parameters
    ----------
    client : CustomerIOClient
        API client instance
    user_ids : list
        List of user IDs to delete
    ignore_errors : bool
        Whether to ignore deletion errors
        
    Returns
    -------
    dict
        Cleanup results
    """
    results = {
        "deleted": [],
        "failed": [],
        "errors": []
    }
    
    for user_id in user_ids:
        try:
            client.delete(user_id)
            results["deleted"].append(user_id)
        except CustomerIOError as e:
            results["failed"].append(user_id)
            results["errors"].append(str(e))
            if not ignore_errors:
                raise
    
    return results


def wait_with_jitter(
    base_delay: float = 1.0, 
    max_delay: float = 5.0,
    jitter_factor: float = 0.1
) -> float:
    """
    Wait with random jitter to avoid thundering herd.
    
    Parameters
    ----------
    base_delay : float
        Base delay in seconds
    max_delay : float
        Maximum delay in seconds
    jitter_factor : float
        Jitter factor (0-1)
        
    Returns
    -------
    float
        Actual wait time
    """
    jitter = base_delay * jitter_factor * (2 * random.random() - 1)
    actual_delay = min(base_delay + jitter, max_delay)
    time.sleep(actual_delay)
    return actual_delay


def assert_user_traits_match(
    actual: Dict[str, Any], 
    expected: Dict[str, Any],
    ignore_fields: Optional[List[str]] = None
):
    """
    Assert that user traits match expected values.
    
    Parameters
    ----------
    actual : dict
        Actual traits from API
    expected : dict
        Expected traits
    ignore_fields : list, optional
        Fields to ignore in comparison
    """
    ignore_fields = ignore_fields or ["created_at", "updated_at", "last_seen"]
    
    for key, value in expected.items():
        if key in ignore_fields:
            continue
            
        assert key in actual, f"Expected trait '{key}' not found"
        assert actual[key] == value, f"Trait '{key}' mismatch: {actual[key]} != {value}"


def generate_page_view_data(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate page view event data.
    
    Parameters
    ----------
    user_id : str, optional
        User ID for the event
        
    Returns
    -------
    dict
        Page view event data
    """
    data = {
        "name": fake.catch_phrase(),
        "properties": {
            "url": fake.url(),
            "path": f"/{fake.word()}/{fake.word()}",
            "referrer": fake.url() if random.choice([True, False]) else None,
            "title": fake.sentence(),
            "test_event": True
        }
    }
    
    if user_id:
        data["userId"] = user_id
    else:
        data["anonymousId"] = f"anon_{uuid.uuid4().hex[:12]}"
    
    return data


def generate_screen_view_data(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate screen view event data.
    
    Parameters
    ----------  
    user_id : str, optional
        User ID for the event
        
    Returns
    -------
    dict
        Screen view event data
    """
    data = {
        "name": fake.catch_phrase(),
        "properties": {
            "screen_class": f"{fake.word().capitalize()}Screen",
            "previous_screen": f"{fake.word().capitalize()}Screen" if random.choice([True, False]) else None,
            "test_event": True
        }
    }
    
    if user_id:
        data["userId"] = user_id
    else:
        data["anonymousId"] = f"anon_{uuid.uuid4().hex[:12]}"
    
    return data