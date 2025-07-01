"""
Customer.IO Webhook utilities.

This module provides webhook signature verification and event parsing
for Customer.IO reporting webhooks.
"""

from .processor import (
    verify_signature,
    parse_event,
    get_event_type
)

__version__ = "1.0.0"
__all__ = [
    "verify_signature",
    "parse_event",
    "get_event_type"
]