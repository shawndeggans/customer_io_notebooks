"""
Re-export of src.pipelines_api.gdpr_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.gdpr_manager instead of src.pipelines_api.gdpr_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.gdpr_manager import (
        track_user_deleted,
        track_user_suppressed,
        track_user_unsuppressed,
        track_device_deleted,
        track_object_deleted,
        track_relationship_deleted,
        track_report_delivery_event,
    )

from src.pipelines_api.gdpr_manager import *

__all__ = [
    "track_user_deleted",
    "track_user_suppressed",
    "track_user_unsuppressed",
    "track_device_deleted",
    "track_object_deleted",
    "track_relationship_deleted",
    "track_report_delivery_event",
]
