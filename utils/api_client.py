"""
Re-export of src.pipelines_api.api_client for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.api_client instead of src.pipelines_api.api_client.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.api_client import CustomerIOClient

from src.pipelines_api.api_client import *

__all__ = ["CustomerIOClient"]
