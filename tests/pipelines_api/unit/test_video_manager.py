"""
Unit tests for Customer.IO comprehensive video tracking semantic events.
"""

from unittest.mock import Mock
import pytest

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
    track_video_ad_completed
)
from src.pipelines_api.exceptions import ValidationError, CustomerIOError
from src.pipelines_api.api_client import CustomerIOClient


class TestVideoPlaybackEvents:
    """Test video playback lifecycle events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_video_playback_started_success(self, mock_client):
        """Test successful Video Playback Started event tracking."""
        result = track_video_playback_started(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "title": "Introduction to AI",
                "duration": 300,
                "quality": "1080p"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Started",
                "properties": {
                    "video_id": "video_456",
                    "title": "Introduction to AI",
                    "duration": 300,
                    "quality": "1080p"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_paused_success(self, mock_client):
        """Test successful Video Playback Paused event tracking."""
        result = track_video_playback_paused(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "position": 45.5,
                "duration": 300,
                "percentage_watched": 15.17
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Paused",
                "properties": {
                    "video_id": "video_456",
                    "position": 45.5,
                    "duration": 300,
                    "percentage_watched": 15.17
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_interrupted_success(self, mock_client):
        """Test successful Video Playback Interrupted event tracking."""
        result = track_video_playback_interrupted(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "position": 120.0,
                "interruption_reason": "network_error",
                "error_code": "NET_001"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Interrupted",
                "properties": {
                    "video_id": "video_456",
                    "position": 120.0,
                    "interruption_reason": "network_error",
                    "error_code": "NET_001"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_buffer_started_success(self, mock_client):
        """Test successful Video Playback Buffer Started event tracking."""
        result = track_video_playback_buffer_started(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "position": 75.0,
                "bitrate": "1080p",
                "buffer_reason": "network_congestion"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Buffer Started",
                "properties": {
                    "video_id": "video_456",
                    "position": 75.0,
                    "bitrate": "1080p",
                    "buffer_reason": "network_congestion"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_buffer_completed_success(self, mock_client):
        """Test successful Video Playback Buffer Completed event tracking."""
        result = track_video_playback_buffer_completed(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "position": 75.0,
                "buffer_duration": 2.5,
                "new_bitrate": "720p"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Buffer Completed",
                "properties": {
                    "video_id": "video_456",
                    "position": 75.0,
                    "buffer_duration": 2.5,
                    "new_bitrate": "720p"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_seek_started_success(self, mock_client):
        """Test successful Video Playback Seek Started event tracking."""
        result = track_video_playback_seek_started(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "position": 60.0,
                "seek_position": 120.0,
                "seek_type": "forward"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Seek Started",
                "properties": {
                    "video_id": "video_456",
                    "position": 60.0,
                    "seek_position": 120.0,
                    "seek_type": "forward"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_seek_completed_success(self, mock_client):
        """Test successful Video Playback Seek Completed event tracking."""
        result = track_video_playback_seek_completed(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "previous_position": 60.0,
                "new_position": 120.0,
                "seek_duration": 0.5
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Seek Completed",
                "properties": {
                    "video_id": "video_456",
                    "previous_position": 60.0,
                    "new_position": 120.0,
                    "seek_duration": 0.5
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_resumed_success(self, mock_client):
        """Test successful Video Playback Resumed event tracking."""
        result = track_video_playback_resumed(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "position": 45.5,
                "pause_duration": 30.0,
                "resume_trigger": "user_action"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Resumed",
                "properties": {
                    "video_id": "video_456",
                    "position": 45.5,
                    "pause_duration": 30.0,
                    "resume_trigger": "user_action"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_completed_success(self, mock_client):
        """Test successful Video Playback Completed event tracking."""
        result = track_video_playback_completed(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "duration": 300,
                "completion_rate": 100.0,
                "total_watch_time": 280.5
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Completed",
                "properties": {
                    "video_id": "video_456",
                    "duration": 300,
                    "completion_rate": 100.0,
                    "total_watch_time": 280.5
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_playback_exited_success(self, mock_client):
        """Test successful Video Playback Exited event tracking."""
        result = track_video_playback_exited(
            client=mock_client,
            user_id="user123",
            video_id="video_456",
            properties={
                "position": 150.0,
                "duration": 300,
                "completion_rate": 50.0,
                "exit_reason": "user_closed"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Playback Exited",
                "properties": {
                    "video_id": "video_456",
                    "position": 150.0,
                    "duration": 300,
                    "completion_rate": 50.0,
                    "exit_reason": "user_closed"
                }
            }
        )
        assert result == {"status": "success"}


class TestVideoContentEvents:
    """Test video content tracking events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_video_content_started_success(self, mock_client):
        """Test successful Video Content Started event tracking."""
        result = track_video_content_started(
            client=mock_client,
            user_id="user123",
            content_id="content_789",
            properties={
                "title": "Machine Learning Basics",
                "category": "education",
                "duration": 1800,
                "series": "AI Fundamentals"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Content Started",
                "properties": {
                    "content_id": "content_789",
                    "title": "Machine Learning Basics",
                    "category": "education",
                    "duration": 1800,
                    "series": "AI Fundamentals"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_content_playing_success(self, mock_client):
        """Test successful Video Content Playing event tracking."""
        result = track_video_content_playing(
            client=mock_client,
            user_id="user123",
            content_id="content_789",
            properties={
                "position": 300.0,
                "duration": 1800,
                "playback_speed": 1.5,
                "quality": "1080p"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Content Playing",
                "properties": {
                    "content_id": "content_789",
                    "position": 300.0,
                    "duration": 1800,
                    "playback_speed": 1.5,
                    "quality": "1080p"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_content_completed_success(self, mock_client):
        """Test successful Video Content Completed event tracking."""
        result = track_video_content_completed(
            client=mock_client,
            user_id="user123",
            content_id="content_789",
            properties={
                "duration": 1800,
                "completion_rate": 98.5,
                "total_watch_time": 1773.0,
                "engagement_score": 85.2
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Content Completed",
                "properties": {
                    "content_id": "content_789",
                    "duration": 1800,
                    "completion_rate": 98.5,
                    "total_watch_time": 1773.0,
                    "engagement_score": 85.2
                }
            }
        )
        assert result == {"status": "success"}


class TestVideoAdEvents:
    """Test video advertisement tracking events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_video_ad_started_success(self, mock_client):
        """Test successful Video Ad Started event tracking."""
        result = track_video_ad_started(
            client=mock_client,
            user_id="user123",
            ad_id="ad_123",
            properties={
                "ad_type": "pre_roll",
                "advertiser": "TechCorp",
                "duration": 30,
                "content_id": "content_789"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Ad Started",
                "properties": {
                    "ad_id": "ad_123",
                    "ad_type": "pre_roll",
                    "advertiser": "TechCorp",
                    "duration": 30,
                    "content_id": "content_789"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_ad_playing_success(self, mock_client):
        """Test successful Video Ad Playing event tracking."""
        result = track_video_ad_playing(
            client=mock_client,
            user_id="user123",
            ad_id="ad_123",
            properties={
                "position": 15.0,
                "duration": 30,
                "quartile": "midpoint",
                "engagement_events": 2
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Ad Playing",
                "properties": {
                    "ad_id": "ad_123",
                    "position": 15.0,
                    "duration": 30,
                    "quartile": "midpoint",
                    "engagement_events": 2
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_video_ad_completed_success(self, mock_client):
        """Test successful Video Ad Completed event tracking."""
        result = track_video_ad_completed(
            client=mock_client,
            user_id="user123",
            ad_id="ad_123",
            properties={
                "duration": 30,
                "completion_rate": 100.0,
                "clicked": True,
                "skipped": False
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Ad Completed",
                "properties": {
                    "ad_id": "ad_123",
                    "duration": 30,
                    "completion_rate": 100.0,
                    "clicked": True,
                    "skipped": False
                }
            }
        )
        assert result == {"status": "success"}


class TestVideoManagerValidation:
    """Test validation scenarios for video events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_invalid_user_id(self, mock_client):
        """Test video event with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_video_playback_started(
                client=mock_client,
                user_id="",
                video_id="video_456"
            )
    
    def test_invalid_video_id(self, mock_client):
        """Test video event with invalid video ID."""
        with pytest.raises(ValidationError, match="Video ID must be a non-empty string"):
            track_video_playback_started(
                client=mock_client,
                user_id="user123",
                video_id=""
            )
    
    def test_invalid_content_id(self, mock_client):
        """Test content event with invalid content ID."""
        with pytest.raises(ValidationError, match="Content ID must be a non-empty string"):
            track_video_content_started(
                client=mock_client,
                user_id="user123",
                content_id=""
            )
    
    def test_invalid_ad_id(self, mock_client):
        """Test ad event with invalid ad ID."""
        with pytest.raises(ValidationError, match="Ad ID must be a non-empty string"):
            track_video_ad_started(
                client=mock_client,
                user_id="user123",
                ad_id=""
            )
    
    def test_invalid_properties(self, mock_client):
        """Test video event with invalid properties."""
        with pytest.raises(ValidationError, match="Properties must be a dictionary"):
            track_video_playback_started(
                client=mock_client,
                user_id="user123",
                video_id="video_456",
                properties="invalid"
            )
    
    def test_api_error(self, mock_client):
        """Test video event when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            track_video_playback_started(
                client=mock_client,
                user_id="user123",
                video_id="video_456"
            )


class TestVideoManagerIntegration:
    """Test integration scenarios for comprehensive video analytics."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_complete_video_playback_lifecycle(self, mock_client):
        """Test complete video playback lifecycle tracking."""
        user_id = "user123"
        video_id = "video_456"
        
        # Start playback
        start_result = track_video_playback_started(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"title": "Tutorial Video", "duration": 300}
        )
        assert start_result == {"status": "success"}
        
        # Buffer event
        buffer_start = track_video_playback_buffer_started(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"position": 30.0, "buffer_reason": "quality_change"}
        )
        assert buffer_start == {"status": "success"}
        
        # Buffer completed
        buffer_complete = track_video_playback_buffer_completed(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"position": 30.0, "buffer_duration": 1.5}
        )
        assert buffer_complete == {"status": "success"}
        
        # Pause event
        pause_result = track_video_playback_paused(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"position": 120.0, "percentage_watched": 40.0}
        )
        assert pause_result == {"status": "success"}
        
        # Resume event
        resume_result = track_video_playback_resumed(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"position": 120.0, "pause_duration": 15.0}
        )
        assert resume_result == {"status": "success"}
        
        # Seek events
        seek_start = track_video_playback_seek_started(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"position": 150.0, "seek_position": 200.0}
        )
        assert seek_start == {"status": "success"}
        
        seek_complete = track_video_playback_seek_completed(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"previous_position": 150.0, "new_position": 200.0}
        )
        assert seek_complete == {"status": "success"}
        
        # Complete playback
        complete_result = track_video_playback_completed(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"duration": 300, "completion_rate": 100.0}
        )
        assert complete_result == {"status": "success"}
        
        # Verify all events were tracked
        assert mock_client.make_request.call_count == 8
    
    def test_video_content_with_ads_workflow(self, mock_client):
        """Test video content viewing with advertisement workflow."""
        user_id = "user123"
        content_id = "content_789"
        ad_id = "ad_123"
        
        # Start content
        content_start = track_video_content_started(
            client=mock_client,
            user_id=user_id,
            content_id=content_id,
            properties={"title": "Educational Content", "category": "learning"}
        )
        assert content_start == {"status": "success"}
        
        # Pre-roll ad starts
        ad_start = track_video_ad_started(
            client=mock_client,
            user_id=user_id,
            ad_id=ad_id,
            properties={"ad_type": "pre_roll", "duration": 15}
        )
        assert ad_start == {"status": "success"}
        
        # Ad playing
        ad_playing = track_video_ad_playing(
            client=mock_client,
            user_id=user_id,
            ad_id=ad_id,
            properties={"position": 7.5, "quartile": "midpoint"}
        )
        assert ad_playing == {"status": "success"}
        
        # Ad completed
        ad_complete = track_video_ad_completed(
            client=mock_client,
            user_id=user_id,
            ad_id=ad_id,
            properties={"completion_rate": 100.0, "clicked": False}
        )
        assert ad_complete == {"status": "success"}
        
        # Content playing
        content_playing = track_video_content_playing(
            client=mock_client,
            user_id=user_id,
            content_id=content_id,
            properties={"position": 300.0, "quality": "720p"}
        )
        assert content_playing == {"status": "success"}
        
        # Content completed
        content_complete = track_video_content_completed(
            client=mock_client,
            user_id=user_id,
            content_id=content_id,
            properties={"completion_rate": 95.0, "engagement_score": 78.5}
        )
        assert content_complete == {"status": "success"}
        
        # Verify all events were tracked
        assert mock_client.make_request.call_count == 6
    
    def test_video_playback_interruption_and_recovery(self, mock_client):
        """Test video playback interruption and recovery scenario."""
        user_id = "user123"
        video_id = "video_456"
        
        # Start playback
        start_result = track_video_playback_started(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"title": "Live Stream", "duration": None}
        )
        assert start_result == {"status": "success"}
        
        # Playback interrupted
        interrupt_result = track_video_playback_interrupted(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={
                "position": 180.0,
                "interruption_reason": "network_timeout",
                "error_code": "NET_TIMEOUT"
            }
        )
        assert interrupt_result == {"status": "success"}
        
        # Buffer to recover
        buffer_start = track_video_playback_buffer_started(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"position": 180.0, "buffer_reason": "reconnecting"}
        )
        assert buffer_start == {"status": "success"}
        
        # Buffer completed - recovery successful
        buffer_complete = track_video_playback_buffer_completed(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"position": 180.0, "buffer_duration": 5.0}
        )
        assert buffer_complete == {"status": "success"}
        
        # Resume playback
        resume_result = track_video_playback_resumed(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={"position": 180.0, "resume_trigger": "auto_recovery"}
        )
        assert resume_result == {"status": "success"}
        
        # User exits due to poor experience
        exit_result = track_video_playback_exited(
            client=mock_client,
            user_id=user_id,
            video_id=video_id,
            properties={
                "position": 200.0,
                "exit_reason": "poor_quality",
                "completion_rate": 20.0
            }
        )
        assert exit_result == {"status": "success"}
        
        # Verify all events were tracked
        assert mock_client.make_request.call_count == 6