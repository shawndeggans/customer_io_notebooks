"""
Re-export of src.pipelines_api.device_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.device_manager instead of src.pipelines_api.device_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.device_manager import (
        register_device,
        update_device,
        delete_device,
    )

from src.pipelines_api.device_manager import *

__all__ = ["register_device", "update_device", "delete_device"]
