"""
Integration tests for Customer.IO Video Tracking API.

Tests real API interactions for:
- Video playback events (start, pause, resume, complete)
- Video content tracking
- Video advertising events
- Video quality and buffering events
"""

import pytest
from datetime import datetime, timezone

from tests.integration.base import BaseIntegrationTest
from tests.integration.utils import generate_test_email
from utils.video_manager import (
    track_video_playback_started,
    track_video_playback_paused,
    track_video_playback_resumed,
    track_video_playback_completed,
    track_video_playback_exited,
    track_video_playback_buffer_started,
    track_video_playback_buffer_completed,
    track_video_content_started,
    track_video_content_completed,
    track_video_ad_started,
    track_video_ad_completed
)
from utils.people_manager import identify_user
from utils.exceptions import CustomerIOError, ValidationError


@pytest.mark.integration
class TestVideoIntegration(BaseIntegrationTest):
    """Integration tests for video tracking functionality."""
    
    def test_track_video_playback_lifecycle(self, authenticated_client, test_user_id):
        """Test complete video playback lifecycle."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("video"),
            "name": "Video Test User"
        })
        self.track_user(test_user_id)
        
        video_id = "VIDEO_001"
        
        # Act & Assert - Start playback
        start_result = track_video_playback_started(
            authenticated_client,
            test_user_id,
            video_id,
            {
                "title": "Integration Test Video",
                "duration": 120,
                "quality": "1080p",
                "position": 0
            }
        )
        self.assert_successful_response(start_result)
        
        # Pause playback
        pause_result = track_video_playback_paused(
            authenticated_client,
            test_user_id,
            video_id,
            {"position": 30}
        )
        self.assert_successful_response(pause_result)
        
        # Resume playback
        resume_result = track_video_playback_resumed(
            authenticated_client,
            test_user_id,
            video_id,
            {"position": 30}
        )
        self.assert_successful_response(resume_result)
        
        # Complete playback
        complete_result = track_video_playback_completed(
            authenticated_client,
            test_user_id,
            video_id,
            {"position": 120}
        )
        self.assert_successful_response(complete_result)
    
    def test_track_video_buffering_events(self, authenticated_client, test_user_id):
        """Test video buffering event tracking."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("buffer"),
            "name": "Buffer Test User"
        })
        self.track_user(test_user_id)
        
        video_id = "BUFFER_VIDEO_001"
        
        # Act & Assert - Buffer started
        buffer_start_result = track_video_playback_buffer_started(
            authenticated_client,
            test_user_id,
            video_id,
            {
                "title": "Buffer Test Video",
                "position": 45,
                "quality": "720p"
            }
        )
        self.assert_successful_response(buffer_start_result)
        
        # Buffer completed
        buffer_complete_result = track_video_playback_buffer_completed(
            authenticated_client,
            test_user_id,
            video_id,
            {
                "position": 45,
                "buffer_duration": 2.5
            }
        )
        self.assert_successful_response(buffer_complete_result)
    
    def test_track_video_content_events(self, authenticated_client, test_user_id):
        """Test video content event tracking."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("content"),
            "name": "Content Test User"
        })
        self.track_user(test_user_id)
        
        video_id = "CONTENT_VIDEO_001"
        
        # Act & Assert - Content started
        content_start_result = track_video_content_started(
            authenticated_client,
            test_user_id,
            video_id,
            {
                "title": "Content Test Video",
                "content_id": "EPISODE_123",
                "season": 1,
                "episode": 5,
                "series": "Test Series",
                "genre": "Technology"
            }
        )
        self.assert_successful_response(content_start_result)
        
        # Content completed
        content_complete_result = track_video_content_completed(
            authenticated_client,
            test_user_id,
            video_id,
            {
                "content_id": "EPISODE_123",
                "position": 180,
                "completion_rate": 1.0
            }
        )
        self.assert_successful_response(content_complete_result)
    
    def test_track_video_advertising_events(self, authenticated_client, test_user_id):
        """Test video advertising event tracking."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("ads"),
            "name": "Ads Test User"
        })
        self.track_user(test_user_id)
        
        video_id = "AD_VIDEO_001"
        
        # Act & Assert - Ad started
        ad_start_result = track_video_ad_started(
            authenticated_client,
            test_user_id,
            video_id,
            {
                "ad_id": "AD_123",
                "ad_type": "pre-roll",
                "ad_duration": 30,
                "advertiser": "Test Brand",
                "campaign": "Summer 2024"
            }
        )
        self.assert_successful_response(ad_start_result)
        
        # Ad completed
        ad_complete_result = track_video_ad_completed(
            authenticated_client,
            test_user_id,
            video_id,
            {
                "ad_id": "AD_123",
                "position": 30,
                "completion_rate": 1.0
            }
        )
        self.assert_successful_response(ad_complete_result)
    
    def test_track_video_exit_event(self, authenticated_client, test_user_id):
        """Test video exit event tracking."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("exit"),
            "name": "Exit Test User"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_video_playback_exited(
            authenticated_client,
            test_user_id,
            "EXIT_VIDEO_001",
            {
                "title": "Exit Test Video",
                "position": 75,
                "exit_reason": "user_action",
                "completion_rate": 0.625
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_video_with_timestamps(self, authenticated_client, test_user_id):
        """Test video events with custom timestamps."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("timestamp"),
            "name": "Timestamp Test User"
        })
        self.track_user(test_user_id)
        
        custom_timestamp = datetime.now(timezone.utc)
        
        # Act
        result = track_video_playback_started(
            authenticated_client,
            test_user_id,
            "TIMESTAMP_VIDEO_001",
            {
                "title": "Historical Video Event",
                "is_historical": True
            },
            timestamp=custom_timestamp
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_video_validation_errors(self, authenticated_client):
        """Test video event validation."""
        # Test empty user ID
        with pytest.raises(ValidationError):
            track_video_playback_started(authenticated_client, "", "video123")
        
        # Test empty video ID
        with pytest.raises(ValidationError):
            track_video_playback_started(authenticated_client, "user123", "")
    
    def test_video_streaming_session(self, authenticated_client, test_user_id):
        """Test a complete video streaming session with multiple events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("session"),
            "name": "Session Test User"
        })
        self.track_user(test_user_id)
        
        video_id = "SESSION_VIDEO_001"
        session_id = f"SESSION_{int(datetime.now().timestamp())}"
        
        # Simulate a realistic viewing session
        session_events = [
            ("start", lambda: track_video_playback_started(
                authenticated_client, test_user_id, video_id,
                {
                    "title": "Full Session Video",
                    "session_id": session_id,
                    "quality": "1080p"
                }
            )),
            ("ad_start", lambda: track_video_ad_started(
                authenticated_client, test_user_id, video_id,
                {
                    "ad_id": "PREROLL_AD",
                    "ad_type": "pre-roll",
                    "session_id": session_id
                }
            )),
            ("ad_complete", lambda: track_video_ad_completed(
                authenticated_client, test_user_id, video_id,
                {
                    "ad_id": "PREROLL_AD",
                    "session_id": session_id
                }
            )),
            ("content_start", lambda: track_video_content_started(
                authenticated_client, test_user_id, video_id,
                {
                    "content_id": "MAIN_CONTENT",
                    "session_id": session_id
                }
            )),
            ("buffer", lambda: track_video_playback_buffer_started(
                authenticated_client, test_user_id, video_id,
                {
                    "position": 45,
                    "session_id": session_id
                }
            )),
            ("buffer_complete", lambda: track_video_playback_buffer_completed(
                authenticated_client, test_user_id, video_id,
                {
                    "position": 45,
                    "session_id": session_id
                }
            )),
            ("pause", lambda: track_video_playback_paused(
                authenticated_client, test_user_id, video_id,
                {
                    "position": 90,
                    "session_id": session_id
                }
            )),
            ("resume", lambda: track_video_playback_resumed(
                authenticated_client, test_user_id, video_id,
                {
                    "position": 90,
                    "session_id": session_id
                }
            )),
            ("complete", lambda: track_video_playback_completed(
                authenticated_client, test_user_id, video_id,
                {
                    "position": 180,
                    "session_id": session_id,
                    "completion_rate": 1.0
                }
            ))
        ]
        
        # Execute session with delays for rate limiting
        for event_name, event_func in session_events:
            result = event_func()
            self.assert_successful_response(result)
            self.wait_for_eventual_consistency(0.15)
    
    @pytest.mark.slow
    def test_high_volume_video_events(self, authenticated_client, test_user_id):
        """Test tracking multiple video events for load testing."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("volume"),
            "name": "Volume Test User"
        })
        self.track_user(test_user_id)
        
        # Act - Track 10 video starts with rate limiting
        for i in range(10):
            result = track_video_playback_started(
                authenticated_client,
                test_user_id,
                f"VOLUME_VIDEO_{i}",
                {
                    "title": f"Volume Test Video {i}",
                    "quality": "720p",
                    "index": i
                }
            )
            self.assert_successful_response(result)
            
            # Rate limiting
            if i % 3 == 0:
                self.wait_for_eventual_consistency(0.2)