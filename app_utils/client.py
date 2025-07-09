"""
Re-export of src.app_api.client for notebook compatibility.

This module provides backward compatibility for notebooks that import
from app_utils.client instead of src.app_api.client.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app_api.client import (
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
        manage_customer_suppression,
    )

from src.app_api.client import *

__all__ = [
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
    "manage_customer_suppression",
]
