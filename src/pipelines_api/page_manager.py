"""
Customer.IO page tracking functions.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def track_page(
    client: CustomerIOClient,
    user_id: Optional[str] = None,
    anonymous_id: Optional[str] = None,
    page_name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a page view in Customer.IO.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str, optional
        Unique identifier for the user
    anonymous_id : str, optional
        Anonymous identifier for the user
    page_name : str, optional
        Name of the page viewed
    properties : dict, optional
        Page properties (URL, title, referrer, etc.)
    context : dict, optional
        Context information (IP, user agent, etc.)
    timestamp : datetime, optional
        When the page view occurred
        
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
    >>> result = track_page(client, user_id="user123", page_name="Home Page",
    ...                     properties={"url": "https://example.com"})
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
    
    # Add page name if provided
    if page_name:
        data["name"] = page_name
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add context if provided
    if context:
        data["context"] = context
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/page", data)


def track_pageview(
    client: CustomerIOClient,
    user_id: Optional[str] = None,
    anonymous_id: Optional[str] = None,
    url: Optional[str] = None,
    title: Optional[str] = None,
    referrer: Optional[str] = None,
    search: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Track a pageview in Customer.IO (convenience function).
    
    This is a convenience function that builds page properties from common
    pageview parameters and calls track_page().
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str, optional
        Unique identifier for the user
    anonymous_id : str, optional
        Anonymous identifier for the user
    url : str, optional
        URL of the page viewed
    title : str, optional
        Title of the page viewed
    referrer : str, optional
        Referrer URL
    search : str, optional
        Search query that led to this page
    timestamp : datetime, optional
        When the page view occurred
    **kwargs
        Additional page properties
        
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
    >>> result = track_pageview(client, user_id="user123", 
    ...                         url="https://example.com/product/123",
    ...                         title="Product Details")
    >>> print(result["status"])
    success
    """
    # Build properties from pageview parameters
    properties = {}
    
    if url:
        properties["url"] = url
    
    if title:
        properties["title"] = title
    
    if referrer:
        properties["referrer"] = referrer
    
    if search:
        properties["search"] = search
    
    # Add any additional properties from kwargs
    properties.update(kwargs)
    
    # Use properties only if we have any
    properties_to_send = properties if properties else None
    
    return track_page(
        client=client,
        user_id=user_id,
        anonymous_id=anonymous_id,
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