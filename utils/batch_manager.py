"""
Re-export of src.pipelines_api.batch_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.batch_manager instead of src.pipelines_api.batch_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.batch_manager import (
        send_batch,
        create_batch_operations,
        validate_batch_size,
        split_oversized_batch,
    )

from src.pipelines_api.batch_manager import *

__all__ = [
    "send_batch",
    "create_batch_operations",
    "validate_batch_size",
    "split_oversized_batch",
]
