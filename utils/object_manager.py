"""
Re-export of src.pipelines_api.object_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.object_manager instead of src.pipelines_api.object_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.object_manager import (
        create_object,
        update_object,
        delete_object,
        create_relationship,
        delete_relationship,
    )

from src.pipelines_api.object_manager import *

__all__ = [
    "create_object",
    "update_object",
    "delete_object",
    "create_relationship",
    "delete_relationship",
]
