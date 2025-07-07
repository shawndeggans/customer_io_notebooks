"""
Customer.IO Webhook utilities.

This module provides webhook signature verification and event parsing
for Customer.IO reporting webhooks.
"""

from .processor import (
    verify_signature,
    parse_event,
    get_event_type,
    validate_webhook_headers,
    route_webhook_event
)
from .event_handlers import (
    BaseEventHandler,
    EmailEventHandler,
    CustomerEventHandler,
    SMSEventHandler,
    PushEventHandler,
    InAppEventHandler,
    SlackEventHandler,
    WebhookEventHandler,
    get_event_handler
)
from .config_manager import (
    CustomerIOWebhookManager,
    setup_databricks_webhook
)

__version__ = "1.0.0"
__all__ = [
    "verify_signature",
    "parse_event",
    "get_event_type",
    "validate_webhook_headers",
    "route_webhook_event",
    "BaseEventHandler",
    "EmailEventHandler",
    "CustomerEventHandler",
    "SMSEventHandler",
    "PushEventHandler",
    "InAppEventHandler",
    "SlackEventHandler",
    "WebhookEventHandler",
    "get_event_handler",
    "CustomerIOWebhookManager",
    "setup_databricks_webhook"
]