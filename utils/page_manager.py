"""
Re-export of src.pipelines_api.page_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.page_manager instead of src.pipelines_api.page_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.page_manager import track_page, track_pageview

from src.pipelines_api.page_manager import *

__all__ = ["track_page", "track_pageview"]
