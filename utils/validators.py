"""
Input validation utilities for Customer.IO API.
"""

import re
from typing import Any

from .exceptions import ValidationError


def validate_email(email: str) -> None:
    """
    Validate email format.
    
    Parameters
    ----------
    email : str
        Email address to validate
        
    Raises
    ------
    ValidationError
        If email format is invalid
    """
    if not email or not isinstance(email, str):
        raise ValidationError("Email must be a non-empty string")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError(f"Invalid email format: {email}")


def validate_user_id(user_id: str) -> None:
    """
    Validate user ID format.
    
    Parameters
    ----------
    user_id : str
        User ID to validate
        
    Raises
    ------
    ValidationError
        If user ID is invalid
    """
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    if len(user_id) > 150:
        raise ValidationError("User ID must be 150 characters or less")


def validate_event_name(event_name: str) -> None:
    """
    Validate event name.
    
    Parameters
    ----------
    event_name : str
        Event name to validate
        
    Raises
    ------
    ValidationError
        If event name is invalid
    """
    if not event_name or not isinstance(event_name, str):
        raise ValidationError("Event name must be a non-empty string")
    
    if len(event_name) > 150:
        raise ValidationError("Event name must be 150 characters or less")


def validate_batch_size(batch_data: list[Any], max_size_kb: int = 500) -> None:
    """
    Validate batch size doesn't exceed limits.
    
    Parameters
    ----------
    batch_data : list
        Batch data to validate
    max_size_kb : int
        Maximum size in KB (default 500)
        
    Raises
    ------
    ValidationError
        If batch is too large
    """
    if not isinstance(batch_data, list):
        raise ValidationError("Batch data must be a list")
    
    # Rough estimate of JSON size
    import json
    try:
        json_str = json.dumps(batch_data)
        size_kb = len(json_str.encode('utf-8')) / 1024
        
        if size_kb > max_size_kb:
            raise ValidationError(f"Batch size {size_kb:.1f}KB exceeds {max_size_kb}KB limit")
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Invalid batch data: {e}")


def validate_region(region: str) -> None:
    """
    Validate Customer.IO region.
    
    Parameters
    ----------
    region : str
        Region to validate (us or eu)
        
    Raises
    ------
    ValidationError
        If region is invalid
    """
    if region not in ["us", "eu"]:
        raise ValidationError(f"Region must be 'us' or 'eu', got: {region}")