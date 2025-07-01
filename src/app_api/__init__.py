"""
Customer.IO App API utilities.

This module provides direct access to Customer.IO App API endpoints
for messaging, campaigns, and basic data operations.
"""

from .auth import AppAPIAuth
from .client import (
    send_transactional,
    trigger_broadcast,
    send_push,
    search_customers,
    get_customer,
    get_customer_activities,
    get_customer_attributes,
    get_customer_messages,
    get_customer_segments,
    delete_customer,
    update_customer,
    create_customer,
    manage_customer_suppression
)

__version__ = "1.0.0"
__all__ = [
    "AppAPIAuth",
    "send_transactional",
    "trigger_broadcast", 
    "send_push",
    "search_customers",
    "get_customer",
    "get_customer_activities",
    "get_customer_attributes",
    "get_customer_messages",
    "get_customer_segments",
    "delete_customer",
    "update_customer",
    "create_customer",
    "manage_customer_suppression"
]