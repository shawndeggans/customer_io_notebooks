"""
Re-export of src.pipelines_api.validators for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.validators instead of src.pipelines_api.validators.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.validators import (
        validate_email,
        validate_user_id,
        validate_event_name,
        validate_batch_size,
        validate_region,
    )

from src.pipelines_api.validators import *

__all__ = [
    "validate_email",
    "validate_user_id",
    "validate_event_name",
    "validate_batch_size",
    "validate_region",
]
