"""
Utility modules for Customer.IO Pipelines API.
Re-exports from src.pipelines_api for notebook compatibility.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api import *

from src.pipelines_api import *
