"""
Re-export of src.pipelines_api.video_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.video_manager instead of src.pipelines_api.video_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.video_manager import (
        track_video_playback_started,
        track_video_playback_paused,
        track_video_playback_interrupted,
        track_video_playback_buffer_started,
        track_video_playback_buffer_completed,
        track_video_playback_seek_started,
        track_video_playback_seek_completed,
        track_video_playback_resumed,
        track_video_playback_completed,
        track_video_playback_exited,
        track_video_content_started,
        track_video_content_playing,
        track_video_content_completed,
        track_video_ad_started,
        track_video_ad_playing,
        track_video_ad_completed,
    )

from src.pipelines_api.video_manager import *

__all__ = [
    "track_video_playback_started",
    "track_video_playback_paused",
    "track_video_playback_interrupted",
    "track_video_playback_buffer_started",
    "track_video_playback_buffer_completed",
    "track_video_playback_seek_started",
    "track_video_playback_seek_completed",
    "track_video_playback_resumed",
    "track_video_playback_completed",
    "track_video_playback_exited",
    "track_video_content_started",
    "track_video_content_playing",
    "track_video_content_completed",
    "track_video_ad_started",
    "track_video_ad_playing",
    "track_video_ad_completed",
]
