"""
Re-export of src.pipelines_api.alias_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.alias_manager instead of src.pipelines_api.alias_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.alias_manager import create_alias, merge_profiles

from src.pipelines_api.alias_manager import *

__all__ = ["create_alias", "merge_profiles"]
