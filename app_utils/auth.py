"""
Re-export of src.app_api.auth for notebook compatibility.

This module provides backward compatibility for notebooks that import
from app_utils.auth instead of src.app_api.auth.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app_api.auth import AppAPIAuth

from src.app_api.auth import *

__all__ = ["AppAPIAuth"]
