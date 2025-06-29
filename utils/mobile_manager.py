"""
Customer.IO comprehensive mobile app lifecycle semantic events.

This module provides functions for tracking all mobile app lifecycle and
push notification semantic events as defined in the Customer.IO Data Pipelines
API specification.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def track_application_installed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an "Application Installed" semantic event.
    
    This event indicates that the mobile application has been installed,
    providing insights into acquisition channels and installation patterns.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (version, build, install_source, device_type, etc.)
    timestamp : datetime, optional
        When the installation occurred
        
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
    >>> result = track_application_installed(
    ...     client, 
    ...     user_id="user123",
    ...     properties={
    ...         "version": "2.1.0",
    ...         "install_source": "app_store",
    ...         "device_type": "ios"
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
        "event": "Application Installed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_application_opened(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an "Application Opened" semantic event.
    
    This event indicates that the mobile application has been opened,
    providing insights into usage patterns and session initiation.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (version, session_id, from_background, launch_source, etc.)
    timestamp : datetime, optional
        When the app was opened
        
    Returns
    -------
    dict
        API response containing operation status
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
        "event": "Application Opened"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_application_backgrounded(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an "Application Backgrounded" semantic event.
    
    This event indicates that the mobile application has been moved to the
    background, providing insights into session duration and engagement patterns.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (session_id, session_duration, screens_viewed, actions_taken, etc.)
    timestamp : datetime, optional
        When the app was backgrounded
        
    Returns
    -------
    dict
        API response containing operation status
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
        "event": "Application Backgrounded"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_application_foregrounded(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an "Application Foregrounded" semantic event.
    
    This event indicates that the mobile application has been brought back
    to the foreground from background state, providing insights into re-engagement
    patterns and attribution.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (session_id, background_duration, return_reason, etc.)
    timestamp : datetime, optional
        When the app was foregrounded
        
    Returns
    -------
    dict
        API response containing operation status
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
        "event": "Application Foregrounded"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_application_updated(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an "Application Updated" semantic event.
    
    This event indicates that the mobile application has been updated to a
    new version, providing insights into update adoption and version distribution.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (previous_version, new_version, update_type, etc.)
    timestamp : datetime, optional
        When the app was updated
        
    Returns
    -------
    dict
        API response containing operation status
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
        "event": "Application Updated"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_application_uninstalled(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an "Application Uninstalled" semantic event.
    
    This event indicates that the mobile application has been uninstalled,
    providing insights into churn patterns and retention analysis.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (version, days_since_install, total_sessions, etc.)
    timestamp : datetime, optional
        When the app was uninstalled
        
    Returns
    -------
    dict
        API response containing operation status
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
        "event": "Application Uninstalled"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_application_crashed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an "Application Crashed" semantic event.
    
    This event indicates that the mobile application has crashed unexpectedly,
    providing insights into app stability and crash patterns for quality improvement.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (version, crash_type, crash_location, stack_trace, etc.)
    timestamp : datetime, optional
        When the app crashed
        
    Returns
    -------
    dict
        API response containing operation status
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
        "event": "Application Crashed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_push_notification_received(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Push Notification Received" semantic event.
    
    This event indicates that a push notification has been delivered to the
    user's device, providing insights into notification delivery rates and timing.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (campaign_id, message_id, notification_type, etc.)
    timestamp : datetime, optional
        When the notification was received
        
    Returns
    -------
    dict
        API response containing operation status
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
        "event": "Push Notification Received"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_push_notification_tapped(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Push Notification Tapped" semantic event.
    
    This event indicates that a user has tapped on a push notification,
    providing insights into notification engagement and conversion rates.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (campaign_id, message_id, action_taken, deep_link, etc.)
    timestamp : datetime, optional
        When the notification was tapped
        
    Returns
    -------
    dict
        API response containing operation status
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
        "event": "Push Notification Tapped"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)