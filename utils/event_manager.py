"""
Re-export of src.pipelines_api.event_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.event_manager instead of src.pipelines_api.event_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.event_manager import (
        track_event,
        track_page_view,
        track_screen_view,
        track_ecommerce_event,
        track_email_event,
        track_mobile_event,
        track_video_event,
    )

from src.pipelines_api.event_manager import *

__all__ = [
    "track_event",
    "track_page_view",
    "track_screen_view",
    "track_ecommerce_event",
    "track_email_event",
    "track_mobile_event",
    "track_video_event",
]
