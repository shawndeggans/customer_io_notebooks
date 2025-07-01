"""
Customer.IO screen tracking functions.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def track_screen(
    client: CustomerIOClient,
    user_id: Optional[str] = None,
    anonymous_id: Optional[str] = None,
    screen_name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a screen view in Customer.IO.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str, optional
        Unique identifier for the user
    anonymous_id : str, optional
        Anonymous identifier for the user
    screen_name : str, optional
        Name of the screen viewed
    properties : dict, optional
        Screen properties (class, category, data, etc.)
    context : dict, optional
        Context information (app, device, OS, etc.)
    timestamp : datetime, optional
        When the screen view occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user identification or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_screen(client, user_id="user123", screen_name="Product Details",
    ...                       properties={"product_id": "123", "category": "electronics"})
    >>> print(result["status"])
    success
    """
    # Validate user identification
    _validate_user_identification(user_id, anonymous_id)
    
    # Validate optional parameters
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    if context is not None and not isinstance(context, dict):
        raise ValidationError("Context must be a dictionary")
    
    # Build request data
    data = {}
    
    # Add user identification
    if user_id:
        validate_user_id(user_id)
        data["userId"] = user_id
    else:
        data["anonymousId"] = anonymous_id
    
    # Add screen name if provided
    if screen_name:
        data["name"] = screen_name
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add context if provided
    if context:
        data["context"] = context
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/screen", data)


def track_screenview(
    client: CustomerIOClient,
    user_id: Optional[str] = None,
    anonymous_id: Optional[str] = None,
    screen_name: Optional[str] = None,
    screen_class: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Track a screenview in Customer.IO (convenience function).
    
    This is a convenience function that builds screen properties from common
    screenview parameters and calls track_screen().
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str, optional
        Unique identifier for the user
    anonymous_id : str, optional
        Anonymous identifier for the user
    screen_name : str, optional
        Name of the screen viewed
    screen_class : str, optional
        Screen class or view controller name
    timestamp : datetime, optional
        When the screen view occurred
    **kwargs
        Additional screen properties
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user identification is invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_screenview(client, user_id="user123", 
    ...                          screen_name="Settings",
    ...                          screen_class="SettingsViewController")
    >>> print(result["status"])
    success
    """
    # Build properties from screenview parameters
    properties = {}
    
    if screen_class:
        properties["screen_class"] = screen_class
    
    # Add any additional properties from kwargs
    properties.update(kwargs)
    
    # Use properties only if we have any
    properties_to_send = properties if properties else None
    
    return track_screen(
        client=client,
        user_id=user_id,
        anonymous_id=anonymous_id,
        screen_name=screen_name,
        properties=properties_to_send,
        timestamp=timestamp
    )


def _validate_user_identification(user_id: Optional[str], anonymous_id: Optional[str]) -> None:
    """
    Validate user identification parameters.
    
    Parameters
    ----------
    user_id : str, optional
        User ID to validate
    anonymous_id : str, optional
        Anonymous ID to validate
        
    Raises
    ------
    ValidationError
        If user identification is invalid
    """
    # Check for specific validation cases first
    if user_id is not None and (not user_id or not isinstance(user_id, str)):
        raise ValidationError("User ID must be a non-empty string")
    
    if anonymous_id is not None and (not anonymous_id or not isinstance(anonymous_id, str)):
        raise ValidationError("Anonymous ID must be a non-empty string")
    
    # Check that we have at least one valid ID
    if not user_id and not anonymous_id:
        raise ValidationError("Either user_id or anonymous_id must be provided")
    
    # Check that we don't have both
    if user_id and anonymous_id:
        raise ValidationError("Cannot provide both user_id and anonymous_id")