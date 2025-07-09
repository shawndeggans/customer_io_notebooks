"""
Re-export of src.pipelines_api.people_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.people_manager instead of src.pipelines_api.people_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.people_manager import (
        identify_user,
        delete_user,
        suppress_user,
        unsuppress_user,
    )

from src.pipelines_api.people_manager import *

__all__ = ["identify_user", "delete_user", "suppress_user", "unsuppress_user"]
