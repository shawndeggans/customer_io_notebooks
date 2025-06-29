"""
Customer.IO device management functions.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def register_device(
    client: CustomerIOClient,
    user_id: str,
    device_token: str,
    device_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Register a device with Customer.IO (creates or updates).
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    device_token : str
        Device token/identifier
    device_type : str, optional
        Device type ("ios" or "android")
    metadata : dict, optional
        Additional device metadata
    timestamp : datetime, optional
        When the device registration occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, device_token, or device_type are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = register_device(client, "user123", "abc123token", "ios")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    _validate_device_token(device_token)
    
    if device_type is not None:
        _validate_device_type(device_type)
    
    # Build device object
    device = {"token": device_token}
    
    # Add device type if provided
    if device_type:
        device["type"] = device_type
    
    # Add metadata if provided
    if metadata:
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a dictionary")
        device.update(metadata)
    
    # Build request data
    data = {
        "type": "track",
        "event": "Device Created or Updated",
        "userId": user_id,
        "context": {
            "device": device
        }
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def update_device(
    client: CustomerIOClient,
    user_id: str,
    device_token: str,
    device_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Update a device in Customer.IO.
    
    Note: This is an alias for register_device since Customer.IO uses
    upsert behavior for device operations.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    device_token : str
        Device token/identifier
    device_type : str, optional
        Device type ("ios" or "android")
    metadata : dict, optional
        Additional device metadata to update
    timestamp : datetime, optional
        When the device update occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, device_token, or device_type are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = update_device(client, "user123", "abc123token", metadata={"version": "16.0.1"})
    >>> print(result["status"])
    success
    """
    return register_device(
        client=client,
        user_id=user_id,
        device_token=device_token,
        device_type=device_type,
        metadata=metadata,
        timestamp=timestamp
    )


def delete_device(
    client: CustomerIOClient,
    user_id: str,
    device_token: str,
    device_type: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Delete a device from Customer.IO.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    device_token : str
        Device token/identifier
    device_type : str, optional
        Device type ("ios" or "android")
    timestamp : datetime, optional
        When the device deletion occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, device_token, or device_type are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = delete_device(client, "user123", "abc123token")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    _validate_device_token(device_token)
    
    if device_type is not None:
        _validate_device_type(device_type)
    
    # Build device object
    device = {"token": device_token}
    
    # Add device type if provided
    if device_type:
        device["type"] = device_type
    
    # Build request data
    data = {
        "type": "track",
        "event": "Device Deleted",
        "userId": user_id,
        "context": {
            "device": device
        }
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def _validate_device_token(device_token: str) -> None:
    """
    Validate device token.
    
    Parameters
    ----------
    device_token : str
        Device token to validate
        
    Raises
    ------
    ValidationError
        If device token is invalid
    """
    if not device_token or not isinstance(device_token, str):
        raise ValidationError("Device token must be a non-empty string")


def _validate_device_type(device_type: str) -> None:
    """
    Validate device type.
    
    Parameters
    ----------
    device_type : str
        Device type to validate
        
    Raises
    ------
    ValidationError
        If device type is invalid
    """
    valid_types = {"ios", "android"}
    if device_type not in valid_types:
        raise ValidationError("Device type must be 'ios' or 'android'")