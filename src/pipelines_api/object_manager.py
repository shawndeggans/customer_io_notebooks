"""
Customer.IO object and relationship management functions.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def create_object(
    client: CustomerIOClient,
    user_id: str,
    object_id: str,
    traits: Dict[str, Any],
    object_type_id: str = "1",
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create an object in Customer.IO and establish a relationship with a user.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    object_id : str
        Unique identifier for the object
    traits : dict
        Object attributes and metadata
    object_type_id : str, optional
        Object type identifier (defaults to "1")
    timestamp : datetime, optional
        When the object creation occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, object_id, traits, or object_type_id are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = create_object(client, "user123", "company_acme", 
    ...                        {"name": "Acme Corp", "industry": "Tech"})
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    _validate_object_id(object_id)
    _validate_traits(traits)
    _validate_object_type_id(object_type_id)
    
    # Build request data
    data = {
        "userId": user_id,
        "type": "group",
        "groupId": object_id,
        "objectTypeId": object_type_id,
        "traits": traits
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/group", data)


def update_object(
    client: CustomerIOClient,
    user_id: str,
    object_id: str,
    traits: Dict[str, Any],
    object_type_id: str = "1",
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Update an object in Customer.IO.
    
    Note: This is an alias for create_object since Customer.IO uses
    upsert behavior for object operations.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    object_id : str
        Unique identifier for the object
    traits : dict
        Object attributes to update
    object_type_id : str, optional
        Object type identifier (defaults to "1")
    timestamp : datetime, optional
        When the object update occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, object_id, traits, or object_type_id are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = update_object(client, "user123", "company_acme", 
    ...                        {"employee_count": 500})
    >>> print(result["status"])
    success
    """
    return create_object(
        client=client,
        user_id=user_id,
        object_id=object_id,
        traits=traits,
        object_type_id=object_type_id,
        timestamp=timestamp
    )


def delete_object(
    client: CustomerIOClient,
    object_id: str,
    object_type_id: str = "1",
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Delete an object from Customer.IO.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    object_id : str
        Unique identifier for the object
    object_type_id : str, optional
        Object type identifier (defaults to "1")
    timestamp : datetime, optional
        When the object deletion occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If object_id or object_type_id are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = delete_object(client, "company_acme")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    _validate_object_id(object_id)
    _validate_object_type_id(object_type_id)
    
    # Build request data
    data = {
        "event": "Object Deleted",
        "anonymousId": "system",
        "properties": {
            "objectId": object_id,
            "objectTypeId": object_type_id
        }
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def create_relationship(
    client: CustomerIOClient,
    user_id: str,
    object_id: str,
    object_type_id: str = "1",
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create a relationship between a user and an object in Customer.IO.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    object_id : str
        Unique identifier for the object
    object_type_id : str, optional
        Object type identifier (defaults to "1")
    timestamp : datetime, optional
        When the relationship creation occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, object_id, or object_type_id are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = create_relationship(client, "user123", "company_acme")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    _validate_object_id(object_id)
    _validate_object_type_id(object_type_id)
    
    # Build request data
    data = {
        "userId": user_id,
        "type": "group",
        "groupId": object_id,
        "objectTypeId": object_type_id,
        "traits": {}
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/group", data)


def delete_relationship(
    client: CustomerIOClient,
    user_id: str,
    object_id: str,
    object_type_id: str = "1",
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Delete a relationship between a user and an object in Customer.IO.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    object_id : str
        Unique identifier for the object
    object_type_id : str, optional
        Object type identifier (defaults to "1")
    timestamp : datetime, optional
        When the relationship deletion occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, object_id, or object_type_id are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = delete_relationship(client, "user123", "company_acme")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    _validate_object_id(object_id)
    _validate_object_type_id(object_type_id)
    
    # Build request data
    data = {
        "event": "Relationship Deleted",
        "userId": user_id,
        "properties": {
            "objectId": object_id,
            "objectTypeId": object_type_id
        }
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def _validate_object_id(object_id: str) -> None:
    """
    Validate object ID.
    
    Parameters
    ----------
    object_id : str
        Object ID to validate
        
    Raises
    ------
    ValidationError
        If object ID is invalid
    """
    if not object_id or not isinstance(object_id, str):
        raise ValidationError("Object ID must be a non-empty string")


def _validate_traits(traits: Dict[str, Any]) -> None:
    """
    Validate traits dictionary.
    
    Parameters
    ----------
    traits : dict
        Traits to validate
        
    Raises
    ------
    ValidationError
        If traits are invalid
    """
    if not isinstance(traits, dict):
        raise ValidationError("Traits must be a dictionary")
    
    if not traits:
        raise ValidationError("Traits cannot be empty")


def _validate_object_type_id(object_type_id: str) -> None:
    """
    Validate object type ID.
    
    Parameters
    ----------
    object_type_id : str
        Object type ID to validate
        
    Raises
    ------
    ValidationError
        If object type ID is invalid
    """
    if not isinstance(object_type_id, str):
        raise ValidationError("Object type ID must be a string")
    
    try:
        int(object_type_id)
    except ValueError:
        raise ValidationError("Object type ID must be a positive integer string")
    
    if int(object_type_id) <= 0:
        raise ValidationError("Object type ID must be a positive integer string")