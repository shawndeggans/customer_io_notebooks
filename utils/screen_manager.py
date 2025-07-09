"""
Re-export of src.pipelines_api.screen_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.screen_manager instead of src.pipelines_api.screen_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.screen_manager import track_screen, track_screenview

from src.pipelines_api.screen_manager import *

__all__ = ["track_screen", "track_screenview"]
