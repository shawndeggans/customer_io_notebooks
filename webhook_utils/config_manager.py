"""
Re-export of src.webhooks.config_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from webhook_utils.config_manager instead of src.webhooks.config_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.webhooks.config_manager import (
        CustomerIOWebhookManager,
        setup_databricks_webhook,
    )

from src.webhooks.config_manager import *

__all__ = ["CustomerIOWebhookManager", "setup_databricks_webhook"]
