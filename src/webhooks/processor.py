"""Webhook processing utilities."""
import json
import hmac
import hashlib
from typing import Dict, Any


def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """
    Verify webhook signature using HMAC SHA256.
    
    Parameters
    ----------
    payload : str
        Raw webhook payload
    signature : str
        Webhook signature header (format: "sha256=<hash>")
    secret : str
        Webhook signing secret
        
    Returns
    -------
    bool
        True if signature is valid, False otherwise
    """
    if not payload or not signature or not secret:
        return False
    
    # Extract hash from signature (remove "sha256=" prefix)
    if not signature.startswith("sha256="):
        return False
    
    received_hash = signature[7:]  # Remove "sha256=" prefix
    
    # Calculate expected hash
    expected_hash = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Use secure comparison to prevent timing attacks
    return hmac.compare_digest(received_hash, expected_hash)


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


def get_event_type(event: Dict[str, Any]) -> str:
    """
    Extract event type from parsed webhook event.
    
    Parameters
    ----------
    event : Dict[str, Any]
        Parsed webhook event data
        
    Returns
    -------
    str
        Event type string
        
    Raises
    ------
    KeyError
        If event_type field is missing
    """
    return event["event_type"]