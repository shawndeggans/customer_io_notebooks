"""
Re-export of src.pipelines_api.exceptions for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.exceptions instead of src.pipelines_api.exceptions.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.exceptions import (
        CustomerIOError,
        AuthenticationError,
        RateLimitError,
        ValidationError,
        NetworkError,
    )

from src.pipelines_api.exceptions import *

__all__ = [
    "CustomerIOError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NetworkError",
]
