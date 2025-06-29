"""
Customer.IO Data Pipelines API Utilities

This module provides utility classes and functions for working with
Customer.IO's Data Pipelines API in Databricks environments.
"""

from .api_client import CustomerIOClient
from .validators import (
    IdentifyRequest,
    TrackRequest,
    GroupRequest,
    AliasRequest,
    DeviceRequest,
    BatchRequest
)
from .transformers import (
    CustomerTransformer,
    EventTransformer,
    GroupTransformer
)
from .people_manager import PeopleManager
from .event_manager import EventManager
from .device_manager import DeviceManager
from .error_handlers import (
    CustomerIOError,
    RateLimitError,
    ValidationError,
    NetworkError
)

__version__ = "1.0.0"
__all__ = [
    "CustomerIOClient",
    "IdentifyRequest",
    "TrackRequest", 
    "GroupRequest",
    "AliasRequest",
    "DeviceRequest",
    "BatchRequest",
    "CustomerTransformer",
    "EventTransformer",
    "GroupTransformer",
    "PeopleManager",
    "EventManager",
    "DeviceManager",
    "CustomerIOError",
    "RateLimitError",
    "ValidationError",
    "NetworkError"
]