"""
Customer.IO event tracking functions.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id, validate_event_name
from .exceptions import ValidationError


def track_event(
    client: CustomerIOClient,
    user_id: str,
    event_name: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a custom event for a user.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    event_name : str
        Name of the event to track
    properties : dict, optional
        Event properties
    timestamp : datetime, optional
        When the event occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id, event_name, or properties are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_event(client, "user123", "product_viewed", {"product_id": "123"})
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    validate_event_name(event_name)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": event_name
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_page_view(
    client: CustomerIOClient,
    user_id: str,
    page_name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a page view for a user.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    page_name : str, optional
        Name of the page viewed
    properties : dict, optional
        Page properties (e.g., URL, referrer)
    timestamp : datetime, optional
        When the page view occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id or properties are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_page_view(client, "user123", "Home Page", {"url": "https://example.com"})
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {"userId": user_id}
    
    # Add page name if provided
    if page_name:
        data["name"] = page_name
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/page", data)


def track_screen_view(
    client: CustomerIOClient,
    user_id: str,
    screen_name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a mobile screen view for a user.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    screen_name : str, optional
        Name of the screen viewed
    properties : dict, optional
        Screen properties
    timestamp : datetime, optional
        When the screen view occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id or properties are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_screen_view(client, "user123", "Product Details")
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {"userId": user_id}
    
    # Add screen name if provided
    if screen_name:
        data["name"] = screen_name
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/screen", data)


# Ecommerce event types mapping
ECOMMERCE_EVENTS = {
    "product_viewed": "Product Viewed",
    "product_added": "Product Added",
    "product_removed": "Product Removed", 
    "cart_viewed": "Cart Viewed",
    "checkout_started": "Checkout Started",
    "order_completed": "Order Completed",
    "order_updated": "Order Updated",
    "order_refunded": "Order Refunded",
    "order_cancelled": "Order Cancelled"
}


def track_ecommerce_event(
    client: CustomerIOClient,
    user_id: str,
    event_type: str,
    data: Dict[str, Any],
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an ecommerce semantic event.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    event_type : str
        Type of ecommerce event (e.g., "product_viewed", "order_completed")
    data : dict
        Event data specific to the ecommerce event type
    timestamp : datetime, optional
        When the event occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If event_type is invalid or data is not a dictionary
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_ecommerce_event(client, "user123", "product_viewed", 
    ...                                {"product_id": "123", "price": 99.99})
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    if event_type not in ECOMMERCE_EVENTS:
        valid_types = ", ".join(ECOMMERCE_EVENTS.keys())
        raise ValidationError(f"Invalid ecommerce event type. Valid types: {valid_types}")
    
    if not isinstance(data, dict):
        raise ValidationError("Event data must be a dictionary")
    
    # Get the proper event name
    event_name = ECOMMERCE_EVENTS[event_type]
    
    return track_event(client, user_id, event_name, data, timestamp)


# Email event types mapping
EMAIL_EVENTS = {
    "email_delivered": "Email Delivered",
    "email_opened": "Email Opened", 
    "email_clicked": "Email Clicked",
    "email_bounced": "Email Bounced",
    "email_unsubscribed": "Email Unsubscribed",
    "email_marked_spam": "Email Marked as Spam"
}


def track_email_event(
    client: CustomerIOClient,
    user_id: str,
    event_type: str,
    data: Dict[str, Any],
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track an email semantic event.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    event_type : str
        Type of email event (e.g., "email_opened", "email_clicked")
    data : dict
        Event data specific to the email event type
    timestamp : datetime, optional
        When the event occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If event_type is invalid or data is not a dictionary
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_email_event(client, "user123", "email_opened", 
    ...                           {"email_id": "123", "campaign_id": "456"})
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    if event_type not in EMAIL_EVENTS:
        valid_types = ", ".join(EMAIL_EVENTS.keys())
        raise ValidationError(f"Invalid email event type. Valid types: {valid_types}")
    
    if not isinstance(data, dict):
        raise ValidationError("Event data must be a dictionary")
    
    # Get the proper event name
    event_name = EMAIL_EVENTS[event_type]
    
    return track_event(client, user_id, event_name, data, timestamp)


# Mobile event types mapping
MOBILE_EVENTS = {
    "push_notification_received": "Push Notification Received",
    "push_notification_tapped": "Push Notification Tapped", 
    "app_installed": "App Installed",
    "app_opened": "App Opened",
    "app_backgrounded": "App Backgrounded"
}


def track_mobile_event(
    client: CustomerIOClient,
    user_id: str,
    event_type: str,
    data: Dict[str, Any],
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a mobile semantic event.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    event_type : str
        Type of mobile event (e.g., "push_notification_received", "app_opened")
    data : dict
        Event data specific to the mobile event type
    timestamp : datetime, optional
        When the event occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If event_type is invalid or data is not a dictionary
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_mobile_event(client, "user123", "app_opened", {"version": "1.2.0"})
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    if event_type not in MOBILE_EVENTS:
        valid_types = ", ".join(MOBILE_EVENTS.keys())
        raise ValidationError(f"Invalid mobile event type. Valid types: {valid_types}")
    
    if not isinstance(data, dict):
        raise ValidationError("Event data must be a dictionary")
    
    # Get the proper event name
    event_name = MOBILE_EVENTS[event_type]
    
    return track_event(client, user_id, event_name, data, timestamp)


# Video event types mapping
VIDEO_EVENTS = {
    "video_started": "Video Started",
    "video_paused": "Video Paused",
    "video_resumed": "Video Resumed",
    "video_completed": "Video Completed",
    "video_seek": "Video Seek"
}


def track_video_event(
    client: CustomerIOClient,
    user_id: str,
    event_type: str,
    data: Dict[str, Any],
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a video semantic event.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    event_type : str
        Type of video event (e.g., "video_started", "video_completed")
    data : dict
        Event data specific to the video event type
    timestamp : datetime, optional
        When the event occurred
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If event_type is invalid or data is not a dictionary
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = track_video_event(client, "user123", "video_started", 
    ...                           {"video_id": "123", "duration": 300})
    >>> print(result["status"])
    success
    """
    # Validate inputs
    validate_user_id(user_id)
    
    if event_type not in VIDEO_EVENTS:
        valid_types = ", ".join(VIDEO_EVENTS.keys())
        raise ValidationError(f"Invalid video event type. Valid types: {valid_types}")
    
    if not isinstance(data, dict):
        raise ValidationError("Event data must be a dictionary")
    
    # Get the proper event name
    event_name = VIDEO_EVENTS[event_type]
    
    return track_event(client, user_id, event_name, data, timestamp)