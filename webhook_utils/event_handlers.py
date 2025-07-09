"""
Re-export of src.webhooks.event_handlers for notebook compatibility.

This module provides backward compatibility for notebooks that import
from webhook_utils.event_handlers instead of src.webhooks.event_handlers.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.webhooks.event_handlers import (
        BaseEventHandler,
        EmailEventHandler,
        CustomerEventHandler,
        SMSEventHandler,
        PushEventHandler,
        InAppEventHandler,
        SlackEventHandler,
        WebhookEventHandler,
        get_event_handler,
    )

from src.webhooks.event_handlers import *

__all__ = [
    "BaseEventHandler",
    "EmailEventHandler",
    "CustomerEventHandler",
    "SMSEventHandler",
    "PushEventHandler",
    "InAppEventHandler",
    "SlackEventHandler",
    "WebhookEventHandler",
    "get_event_handler",
]
