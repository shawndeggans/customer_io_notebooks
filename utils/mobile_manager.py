"""
Re-export of src.pipelines_api.mobile_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.mobile_manager instead of src.pipelines_api.mobile_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.mobile_manager import (
        track_application_installed,
        track_application_opened,
        track_application_backgrounded,
        track_application_foregrounded,
        track_application_updated,
        track_application_uninstalled,
        track_application_crashed,
        track_push_notification_received,
        track_push_notification_tapped,
    )

from src.pipelines_api.mobile_manager import *

__all__ = [
    "track_application_installed",
    "track_application_opened",
    "track_application_backgrounded",
    "track_application_foregrounded",
    "track_application_updated",
    "track_application_uninstalled",
    "track_application_crashed",
    "track_push_notification_received",
    "track_push_notification_tapped",
]
