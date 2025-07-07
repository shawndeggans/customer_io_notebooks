"""Webhook processing utilities for Customer.io webhooks."""
import json
import hmac
import hashlib
import time
from typing import Dict, Any, Optional


def verify_signature(payload: str, signature: str, timestamp: str, secret: str) -> bool:
    """
    Verify Customer.io webhook signature using HMAC SHA256.
    
    Customer.io uses the format: v0:timestamp:body
    
    Parameters
    ----------
    payload : str
        Raw webhook payload body
    signature : str
        Webhook signature header (format: "v0=<hash>")
    timestamp : str
        Webhook timestamp header
    secret : str
        Webhook signing secret
        
    Returns
    -------
    bool
        True if signature is valid, False otherwise
    """
    if not all([payload, signature, timestamp, secret]):
        return False
    
    # Validate signature format
    if not signature.startswith("v0="):
        return False
    
    # Validate timestamp (must be within 5 minutes)
    try:
        timestamp_int = int(timestamp)
        current_time = int(time.time())
        if abs(current_time - timestamp_int) > 300:  # 5 minute tolerance
            return False
    except (ValueError, TypeError):
        return False
    
    # Create signature string: v0:timestamp:body
    signature_string = f"v0:{timestamp}:{payload}"
    
    # Calculate expected signature
    expected_hash = hmac.new(
        secret.encode('utf-8'),
        signature_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Full expected signature with v0= prefix
    expected_signature = f"v0={expected_hash}"
    
    # Use secure comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, signature)


def parse_event(payload: str) -> Dict[str, Any]:
    """
    Parse webhook event payload from JSON.
    
    Parameters
    ----------
    payload : str
        JSON webhook payload
        
    Returns
    -------
    Dict[str, Any]
        Parsed event data
        
    Raises
    ------
    ValueError
        If payload is empty or invalid JSON
    """
    if not payload:
        raise ValueError("Payload cannot be empty")
    
    try:
        return json.loads(payload)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON payload: {e}")


def get_event_type(event: Dict[str, Any]) -> tuple[str, str]:
    """
    Extract object type and metric from Customer.io webhook event.
    
    Customer.io uses object_type as discriminator and metric for specific event.
    
    Parameters
    ----------
    event : Dict[str, Any]
        Parsed webhook event data
        
    Returns
    -------
    tuple[str, str]
        Tuple of (object_type, metric)
        
    Raises
    ------
    KeyError
        If object_type field is missing
    """
    object_type = event.get("object_type")
    if not object_type:
        raise KeyError("Missing required field: object_type")
    
    metric = event.get("metric", "")
    return object_type, metric


def validate_webhook_headers(headers: Dict[str, str]) -> tuple[str, str]:
    """
    Validate required Customer.io webhook headers.
    
    Parameters
    ----------
    headers : Dict[str, str]
        HTTP headers dictionary
        
    Returns
    -------
    tuple[str, str]
        Tuple of (timestamp, signature)
        
    Raises
    ------
    ValueError
        If required headers are missing or invalid
    """
    timestamp = headers.get('X-CIO-Timestamp', headers.get('x-cio-timestamp'))
    signature = headers.get('X-CIO-Signature', headers.get('x-cio-signature'))
    
    if not timestamp or not signature:
        raise ValueError("Missing required headers: x-cio-timestamp or x-cio-signature")
    
    # Validate timestamp format (should be unix timestamp)
    try:
        int(timestamp)
    except ValueError:
        raise ValueError("x-cio-timestamp must be unix timestamp integer")
    
    # Validate signature format
    if not signature.startswith('v0='):
        raise ValueError("x-cio-signature must start with 'v0='")
    
    return timestamp, signature


def route_webhook_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route webhook event based on object_type discriminator.
    
    Parameters
    ----------
    event : Dict[str, Any]
        Parsed webhook event
        
    Returns
    -------
    Dict[str, Any]
        Event data with type information
        
    Raises
    ------
    ValueError
        If object_type is not supported
    """
    object_type, metric = get_event_type(event)
    
    # Supported object types per OpenAPI spec
    supported_types = ["customer", "email", "push", "in_app", "sms", "slack", "webhook"]
    
    if object_type not in supported_types:
        raise ValueError(f"Unsupported object_type: {object_type}")
    
    return {
        "object_type": object_type,
        "metric": metric,
        "event": event
    }