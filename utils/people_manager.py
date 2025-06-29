"""
Customer.IO people management functions.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id, validate_email
from .exceptions import ValidationError


def identify_user(
    client: CustomerIOClient,
    user_id: str,
    traits: Dict[str, Any],
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Identify a user in Customer.IO with the provided traits.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    traits : dict
        User attributes to store
    timestamp : datetime, optional
        When the identification occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id or traits are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = identify_user(client, "user123", {"email": "user@example.com"})
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    if not isinstance(traits, dict):
        raise ValidationError("Traits must be a dictionary")
    
    if not traits:
        raise ValidationError("Traits cannot be empty")
    
    # Validate email if present
    if "email" in traits:
        validate_email(traits["email"])
    
    # Build request data
    data = {
        "userId": user_id,
        "traits": traits
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/identify", data)


def delete_user(client: CustomerIOClient, user_id: str) -> Dict[str, Any]:
    """
    Delete a user from Customer.IO.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id is invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = delete_user(client, "user123")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    data = {"userId": user_id}
    return client.make_request("DELETE", "/identify", data)


def suppress_user(client: CustomerIOClient, user_id: str) -> Dict[str, Any]:
    """
    Suppress a user from receiving messages.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id is invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = suppress_user(client, "user123")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    data = {
        "userId": user_id,
        "traits": {"unsubscribed": True}
    }
    return client.make_request("POST", "/identify", data)


def unsuppress_user(client: CustomerIOClient, user_id: str) -> Dict[str, Any]:
    """
    Remove suppression from a user, allowing them to receive messages.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id is invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = unsuppress_user(client, "user123")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    data = {
        "userId": user_id,
        "traits": {"unsubscribed": False}
    }
    return client.make_request("POST", "/identify", data)