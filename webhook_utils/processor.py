"""
Re-export of src.webhooks.processor for notebook compatibility.

This module provides backward compatibility for notebooks that import
from webhook_utils.processor instead of src.webhooks.processor.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.webhooks.processor import (
        verify_signature,
        parse_event,
        get_event_type,
        validate_webhook_headers,
        route_webhook_event,
    )

from src.webhooks.processor import *

__all__ = [
    "verify_signature",
    "parse_event",
    "get_event_type",
    "validate_webhook_headers",
    "route_webhook_event",
]
