"""
Customer.IO alias/profile merging functions.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Union

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def create_alias(
    client: CustomerIOClient,
    user_id: str,
    previous_id: str,
    timestamp: Optional[datetime] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create an alias linking a user ID to a previous ID.
    
    This function creates an alias relationship in Customer.IO, linking
    a new user ID to a previous identifier. This is commonly used when
    anonymous users sign up or when consolidating user identities.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        New/primary user identifier
    previous_id : str
        Previous/secondary user identifier to alias
    timestamp : datetime, optional
        When the alias was created
    context : dict, optional
        Additional context information
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user identifiers are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = create_alias(client, user_id="user123", previous_id="anon_456")
    >>> print(result["status"])
    success
    """
    # Validate required parameters
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if not previous_id or not isinstance(previous_id, str):
        raise ValidationError("Previous ID must be a non-empty string")
    
    # Validate that IDs are different
    if user_id == previous_id:
        raise ValidationError("User ID and previous ID cannot be the same")
    
    # Validate user_id format
    validate_user_id(user_id)
    
    # Validate optional parameters
    if context is not None and not isinstance(context, dict):
        raise ValidationError("Context must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "previousId": previous_id
    }
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    # Add context if provided
    if context:
        data["context"] = context
    
    return client.make_request("POST", "/alias", data)


def merge_profiles(
    client: CustomerIOClient,
    primary_user_id: str,
    secondary_user_id: str,
    merge_reason: Optional[str] = None,
    merge_source: Optional[str] = None,
    confidence_score: Optional[float] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Merge two user profiles by creating an alias.
    
    This is a convenience function that creates an alias while providing
    additional metadata about the merge operation. It's useful for tracking
    why profiles were merged and providing audit information.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    primary_user_id : str
        Primary user ID (the one that will remain)
    secondary_user_id : str
        Secondary user ID (the one being merged into primary)
    merge_reason : str, optional
        Reason for the merge (e.g., "email_identified", "login_detected")
    merge_source : str, optional
        Source system that triggered the merge
    confidence_score : float, optional
        Confidence score of the merge decision (0.0 to 1.0)
    **kwargs
        Additional merge metadata to include in context
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user identifiers are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = merge_profiles(
    ...     client, 
    ...     primary_user_id="user123", 
    ...     secondary_user_id="temp_456",
    ...     merge_reason="email_verification"
    ... )
    >>> print(result["status"])
    success
    """
    # Build context with merge metadata
    context = {}
    
    if merge_reason:
        context["merge_reason"] = merge_reason
    
    if merge_source:
        context["merge_source"] = merge_source
    
    if confidence_score is not None:
        context["confidence_score"] = confidence_score
    
    # Add any additional metadata from kwargs
    context.update(kwargs)
    
    # Use context only if we have any metadata
    context_to_send = context if context else None
    
    return create_alias(
        client=client,
        user_id=primary_user_id,
        previous_id=secondary_user_id,
        context=context_to_send
    )