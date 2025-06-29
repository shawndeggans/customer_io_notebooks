"""
Customer.IO Data Pipelines API Utilities

This module provides utility classes and functions for working with
Customer.IO's Data Pipelines API.
"""

from .api_client import CustomerIOClient
from .exceptions import (
    CustomerIOError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NetworkError
)
from .validators import (
    validate_email,
    validate_user_id,
    validate_event_name,
    validate_batch_size,
    validate_region
)
from .people_manager import (
    identify_user,
    delete_user,
    suppress_user,
    unsuppress_user
)
from .event_manager import (
    track_event,
    track_page_view,
    track_screen_view,
    track_ecommerce_event,
    track_email_event,
    track_mobile_event,
    track_video_event
)
from .device_manager import (
    register_device,
    update_device,
    delete_device
)
from .object_manager import (
    create_object,
    update_object,
    delete_object,
    create_relationship,
    delete_relationship
)
from .batch_manager import (
    send_batch,
    create_batch_operations,
    validate_batch_size,
    split_oversized_batch
)

__version__ = "1.0.0"
__all__ = [
    "CustomerIOClient",
    "CustomerIOError",
    "AuthenticationError", 
    "RateLimitError",
    "ValidationError",
    "NetworkError",
    "validate_email",
    "validate_user_id",
    "validate_event_name",
    "validate_batch_size",
    "validate_region",
    "identify_user",
    "delete_user",
    "suppress_user",
    "unsuppress_user",
    "track_event",
    "track_page_view",
    "track_screen_view",
    "track_ecommerce_event",
    "track_email_event",
    "track_mobile_event",
    "track_video_event",
    "register_device",
    "update_device",
    "delete_device",
    "create_object",
    "update_object",
    "delete_object",
    "create_relationship",
    "delete_relationship",
    "send_batch",
    "create_batch_operations",
    "validate_batch_size",
    "split_oversized_batch"
]