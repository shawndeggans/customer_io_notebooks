"""
Customer.IO GDPR and data operations semantic events.

This module provides functions for tracking GDPR compliance and data operations
semantic events as defined in the Customer.IO Data Pipelines API specification.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def track_user_deleted(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "User Deleted" semantic event for GDPR compliance.
    
    This event removes a person from your Customer.io environment, typically
    when someone cancels their subscription or closes their account.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user being deleted
    properties : dict, optional
        Additional properties for analytics and audit tracking
    timestamp : datetime, optional
        When the deletion occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_user_deleted(
    ...     client, 
    ...     user_id="user123",
    ...     properties={"reason": "subscription_cancelled"}
    ... )
    >>> print(result["status"])
    success
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "User Deleted"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_user_suppressed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "User Suppressed" semantic event for GDPR compliance.
    
    This event removes a person AND prevents them from being re-added with the
    same identifier. This is used for "right to be forgotten" requests under
    GDPR or CAN-SPAM regulations.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user being suppressed
    properties : dict, optional
        Additional properties for compliance tracking (GDPR request details, etc.)
    timestamp : datetime, optional
        When the suppression occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_user_suppressed(
    ...     client, 
    ...     user_id="user123",
    ...     properties={
    ...         "gdpr_request_type": "right_to_be_forgotten",
    ...         "request_source": "email"
    ...     }
    ... )
    >>> print(result["status"])
    success
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "User Suppressed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_user_unsuppressed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "User Unsuppressed" semantic event.
    
    This event allows a previously suppressed userId to be re-added to your
    workspace. Note: This does not restore previous data, only removes the
    suppression block.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user being unsuppressed
    properties : dict, optional
        Additional properties for restoration tracking
    timestamp : datetime, optional
        When the unsuppression occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_user_unsuppressed(
    ...     client, 
    ...     user_id="user123",
    ...     properties={
    ...         "restoration_reason": "false_positive",
    ...         "approved_by": "privacy_officer"
    ...     }
    ... )
    >>> print(result["status"])
    success
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "User Unsuppressed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_device_deleted(
    client: CustomerIOClient,
    user_id: str,
    device_token: str,
    device_type: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Device Deleted" semantic event for mobile privacy compliance.
    
    This event removes a device when a user logs out or removes the app,
    ensuring proper cleanup of push notification tokens.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user who owns the device
    device_token : str
        Device token string to be removed
    device_type : str, optional
        Type of device ("ios" or "android")
    timestamp : datetime, optional
        When the device deletion occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, device_token, or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_device_deleted(
    ...     client, 
    ...     user_id="user123",
    ...     device_token="device_token_string",
    ...     device_type="ios"
    ... )
    >>> print(result["status"])
    success
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not device_token or not isinstance(device_token, str):
        raise ValidationError("Device token must be a non-empty string")
    
    validate_user_id(user_id)
    
    # Build device context
    device_context = {"token": device_token}
    if device_type:
        device_context["type"] = device_type
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Device Deleted",
        "context": {
            "device": device_context
        }
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_object_deleted(
    client: CustomerIOClient,
    object_id: str,
    object_type_id: int = 1,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an "Object Deleted" semantic event for data minimization compliance.
    
    This event removes groups/objects (companies, accounts, classes) from
    Customer.io as part of data retention or GDPR compliance.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    object_id : str
        Unique identifier for the object being deleted
    object_type_id : int, optional
        Object type identifier (defaults to 1)
    timestamp : datetime, optional
        When the object deletion occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If object_id or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_object_deleted(
    ...     client, 
    ...     object_id="company_abc",
    ...     object_type_id=1
    ... )
    >>> print(result["status"])
    success
    """
    # Validate inputs
    if not object_id or not isinstance(object_id, str):
        raise ValidationError("Object ID must be a non-empty string")
    
    # Build request data (uses anonymousId as required by API spec)
    data = {
        "anonymousId": "gdpr_compliance",
        "event": "Object Deleted",
        "properties": {
            "objectId": object_id,
            "objectTypeId": object_type_id
        }
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_relationship_deleted(
    client: CustomerIOClient,
    user_id: str,
    object_id: str,
    object_type_id: int = 1,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Relationship Deleted" semantic event for data minimization.
    
    This event removes relationships between people and objects (companies,
    accounts, classes) as part of data cleanup or GDPR compliance.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    object_id : str
        Unique identifier for the object
    object_type_id : int, optional
        Object type identifier (defaults to 1)
    timestamp : datetime, optional
        When the relationship deletion occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, object_id, or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_relationship_deleted(
    ...     client, 
    ...     user_id="user123",
    ...     object_id="company_abc"
    ... )
    >>> print(result["status"])
    success
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not object_id or not isinstance(object_id, str):
        raise ValidationError("Object ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Relationship Deleted",
        "properties": {
            "objectId": object_id,
            "objectTypeId": object_type_id
        }
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_report_delivery_event(
    client: CustomerIOClient,
    delivery_id: str,
    metric: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Report Delivery Event" for audit and compliance reporting.
    
    This event tracks message delivery metrics for audit trails and compliance
    reporting, providing visibility into communication delivery status.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    delivery_id : str
        Unique identifier for the delivery
    metric : str
        Delivery metric ("delivered", "opened", "clicked", "bounced", etc.)
    properties : dict, optional
        Additional audit and compliance properties
    timestamp : datetime, optional
        When the delivery event occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If delivery_id, metric, or parameters are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_report_delivery_event(
    ...     client, 
    ...     delivery_id="delivery_123",
    ...     metric="delivered",
    ...     properties={"campaign_id": "campaign_456"}
    ... )
    >>> print(result["status"])
    success
    """
    # Validate inputs
    if not delivery_id or not isinstance(delivery_id, str):
        raise ValidationError("Delivery ID must be a non-empty string")
    
    if not metric or not isinstance(metric, str):
        raise ValidationError("Metric must be a non-empty string")
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build properties with required fields
    event_properties = {
        "deliveryId": delivery_id,
        "metric": metric
    }
    
    # Add additional properties if provided
    if properties:
        event_properties.update(properties)
    
    # Build request data (uses anonymousId for system events)
    data = {
        "anonymousId": "system_audit",
        "event": "Report Delivery Event",
        "properties": event_properties
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)