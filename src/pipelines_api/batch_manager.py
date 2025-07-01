"""
Customer.IO batch operations functions.
"""

import json
from typing import Dict, Any, List, Optional

from .api_client import CustomerIOClient
from .exceptions import ValidationError


# Batch size limits based on Customer.IO API
MAX_BATCH_SIZE_BYTES = 500 * 1024  # 500KB
MAX_OPERATION_SIZE_BYTES = 32 * 1024  # 32KB


def send_batch(
    client: CustomerIOClient,
    operations: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
    integrations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a batch of operations to Customer.IO.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    operations : list
        List of operations to send in batch
    context : dict, optional
        Context information to apply to all operations
    integrations : dict, optional
        Integration settings to apply to all operations
        
    Returns
    -------
    dict
        API response (empty dict for successful batches)
        
    Raises
    ------
    ValidationError
        If operations are invalid or batch is too large
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> operations = [
    ...     {"type": "identify", "userId": "user123", "traits": {"email": "user@example.com"}},
    ...     {"type": "track", "userId": "user123", "event": "Login", "properties": {}}
    ... ]
    >>> result = send_batch(client, operations)
    >>> print(result)
    {}
    """
    # Validate inputs
    _validate_operations(operations)
    validate_batch_size(operations)
    
    # Build request data
    data = {"batch": operations}
    
    # Add context if provided
    if context:
        data["context"] = context
    
    # Add integrations if provided
    if integrations:
        data["integrations"] = integrations
    
    return client.make_request("POST", "/batch", data)


def create_batch_operations(
    operation_type: str,
    data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Create a list of operations for batch processing.
    
    Parameters
    ----------
    operation_type : str
        Type of operations to create ("identify", "track", "group", "page", "screen")
    data : list
        List of data for creating operations
        
    Returns
    -------
    list
        List of formatted operations ready for batch processing
        
    Raises
    ------
    ValidationError
        If operation_type is invalid or data is empty
        
    Example
    -------
    >>> users = [
    ...     {"user_id": "user1", "traits": {"email": "user1@example.com"}},
    ...     {"user_id": "user2", "traits": {"email": "user2@example.com"}}
    ... ]
    >>> operations = create_batch_operations("identify", users)
    >>> print(len(operations))
    2
    """
    # Validate inputs
    if operation_type not in ["identify", "track", "group", "page", "screen"]:
        raise ValidationError(f"Invalid operation type: {operation_type}")
    
    if not data:
        raise ValidationError("Data list cannot be empty")
    
    operations = []
    
    for item in data:
        if operation_type == "identify":
            operations.append(_create_identify_operation(item))
        elif operation_type == "track":
            operations.append(_create_track_operation(item))
        elif operation_type == "group":
            operations.append(_create_group_operation(item))
        elif operation_type == "page":
            operations.append(_create_page_operation(item))
        elif operation_type == "screen":
            operations.append(_create_screen_operation(item))
    
    return operations


def validate_batch_size(operations: List[Dict[str, Any]]) -> None:
    """
    Validate that batch size is within Customer.IO limits.
    
    Parameters
    ----------
    operations : list
        List of operations to validate
        
    Raises
    ------
    ValidationError
        If batch or individual operations exceed size limits
        
    Example
    -------
    >>> operations = [{"type": "identify", "userId": "user123", "traits": {}}]
    >>> validate_batch_size(operations)  # Should not raise exception
    """
    if not operations:
        raise ValidationError("Operations list cannot be empty")
    
    # Calculate total batch size
    batch_json = json.dumps({"batch": operations})
    batch_size = len(batch_json.encode('utf-8'))
    
    if batch_size > MAX_BATCH_SIZE_BYTES:
        raise ValidationError(
            f"Batch size {batch_size} bytes exceeds maximum allowed size "
            f"{MAX_BATCH_SIZE_BYTES} bytes"
        )
    
    # Validate individual operation sizes
    for i, operation in enumerate(operations):
        operation_json = json.dumps(operation)
        operation_size = len(operation_json.encode('utf-8'))
        
        if operation_size > MAX_OPERATION_SIZE_BYTES:
            raise ValidationError(
                f"Operation {i} size {operation_size} bytes exceeds maximum size "
                f"{MAX_OPERATION_SIZE_BYTES} bytes"
            )


def split_oversized_batch(operations: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Split an oversized batch into multiple smaller batches.
    
    Parameters
    ----------
    operations : list
        List of operations to potentially split
        
    Returns
    -------
    list
        List of batches, each within size limits
        
    Raises
    ------
    ValidationError
        If individual operations exceed size limits
        
    Example
    -------
    >>> large_operations = [...]  # List that exceeds 500KB
    >>> batches = split_oversized_batch(large_operations)
    >>> print(f"Split into {len(batches)} batches")
    Split into 3 batches
    """
    if not operations:
        return []
    
    # Check if any individual operation is too large
    for i, operation in enumerate(operations):
        operation_json = json.dumps(operation)
        operation_size = len(operation_json.encode('utf-8'))
        
        if operation_size > MAX_OPERATION_SIZE_BYTES:
            raise ValidationError(
                f"Individual operation exceeds maximum size "
                f"({operation_size} > {MAX_OPERATION_SIZE_BYTES} bytes). "
                f"Cannot split further."
            )
    
    batches = []
    current_batch = []
    current_size = 0
    
    # Base size for batch wrapper
    base_batch_size = len(json.dumps({"batch": []}).encode('utf-8'))
    
    for operation in operations:
        operation_json = json.dumps(operation)
        operation_size = len(operation_json.encode('utf-8'))
        
        # Calculate what total size would be with this operation
        # Include comma separator if not first operation in batch
        separator_size = 1 if current_batch else 0
        projected_size = base_batch_size + current_size + separator_size + operation_size
        
        if projected_size > MAX_BATCH_SIZE_BYTES and current_batch:
            # Start new batch
            batches.append(current_batch)
            current_batch = [operation]
            current_size = operation_size
        else:
            # Add to current batch
            current_batch.append(operation)
            current_size += separator_size + operation_size
    
    # Add final batch if not empty
    if current_batch:
        batches.append(current_batch)
    
    return batches


def _validate_operations(operations: List[Dict[str, Any]]) -> None:
    """
    Validate operations list.
    
    Parameters
    ----------
    operations : list
        Operations to validate
        
    Raises
    ------
    ValidationError
        If operations are invalid
    """
    if not isinstance(operations, list):
        raise ValidationError("Operations must be a list")
    
    if not operations:
        raise ValidationError("Operations list cannot be empty")


def _create_identify_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an identify operation from data.
    
    Parameters
    ----------
    data : dict
        Data containing user_id and traits
        
    Returns
    -------
    dict
        Formatted identify operation
    """
    operation = {
        "type": "identify",
        "userId": data["user_id"],
        "traits": data["traits"]
    }
    
    return operation


def _create_track_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a track operation from data.
    
    Parameters
    ----------
    data : dict
        Data containing user_id, event, and properties
        
    Returns
    -------
    dict
        Formatted track operation
    """
    operation = {
        "type": "track",
        "userId": data["user_id"],
        "event": data["event"],
        "properties": data["properties"]
    }
    
    return operation


def _create_group_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a group operation from data.
    
    Parameters
    ----------
    data : dict
        Data containing user_id, group_id, and traits
        
    Returns
    -------
    dict
        Formatted group operation
    """
    operation = {
        "type": "group",
        "userId": data["user_id"],
        "groupId": data["group_id"],
        "traits": data["traits"]
    }
    
    return operation


def _create_page_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a page operation from data.
    
    Parameters
    ----------
    data : dict
        Data containing user_id, name, and properties
        
    Returns
    -------
    dict
        Formatted page operation
    """
    operation = {
        "type": "page",
        "userId": data["user_id"],
        "name": data["name"],
        "properties": data["properties"]
    }
    
    return operation


def _create_screen_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a screen operation from data.
    
    Parameters
    ----------
    data : dict
        Data containing user_id, name, and properties
        
    Returns
    -------
    dict
        Formatted screen operation
    """
    operation = {
        "type": "screen",
        "userId": data["user_id"],
        "name": data["name"],
        "properties": data["properties"]
    }
    
    return operation