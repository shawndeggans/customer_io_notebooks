"""
Unit tests for Customer.IO comprehensive mobile app lifecycle semantic events.
"""

from unittest.mock import Mock
import pytest

from src.pipelines_api.mobile_manager import (
    track_application_installed,
    track_application_opened,
    track_application_backgrounded,
    track_application_foregrounded,
    track_application_updated,
    track_application_uninstalled,
    track_application_crashed,
    track_push_notification_received,
    track_push_notification_tapped
)
from src.pipelines_api.exceptions import ValidationError, CustomerIOError
from src.pipelines_api.api_client import CustomerIOClient


class TestApplicationLifecycleEvents:
    """Test application lifecycle semantic events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_application_installed_success(self, mock_client):
        """Test successful Application Installed event tracking."""
        result = track_application_installed(
            client=mock_client,
            user_id="user123",
            properties={
                "version": "2.1.0",
                "build": "2023120801",
                "install_source": "app_store",
                "device_type": "ios"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Application Installed",
                "properties": {
                    "version": "2.1.0",
                    "build": "2023120801",
                    "install_source": "app_store",
                    "device_type": "ios"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_application_opened_success(self, mock_client):
        """Test successful Application Opened event tracking."""
        result = track_application_opened(
            client=mock_client,
            user_id="user123",
            properties={
                "version": "2.1.0",
                "session_id": "session_456",
                "from_background": False,
                "launch_source": "direct"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Application Opened",
                "properties": {
                    "version": "2.1.0",
                    "session_id": "session_456",
                    "from_background": False,
                    "launch_source": "direct"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_application_backgrounded_success(self, mock_client):
        """Test successful Application Backgrounded event tracking."""
        result = track_application_backgrounded(
            client=mock_client,
            user_id="user123",
            properties={
                "session_id": "session_456",
                "session_duration": 300.5,
                "screens_viewed": 5,
                "actions_taken": 12
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Application Backgrounded",
                "properties": {
                    "session_id": "session_456",
                    "session_duration": 300.5,
                    "screens_viewed": 5,
                    "actions_taken": 12
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_application_foregrounded_success(self, mock_client):
        """Test successful Application Foregrounded event tracking."""
        result = track_application_foregrounded(
            client=mock_client,
            user_id="user123",
            properties={
                "session_id": "session_789",
                "background_duration": 45.2,
                "return_reason": "push_notification",
                "previous_session": "session_456"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Application Foregrounded",
                "properties": {
                    "session_id": "session_789",
                    "background_duration": 45.2,
                    "return_reason": "push_notification",
                    "previous_session": "session_456"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_application_updated_success(self, mock_client):
        """Test successful Application Updated event tracking."""
        result = track_application_updated(
            client=mock_client,
            user_id="user123",
            properties={
                "previous_version": "2.0.5",
                "new_version": "2.1.0",
                "previous_build": "2023110101",
                "new_build": "2023120801",
                "update_type": "minor"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Application Updated",
                "properties": {
                    "previous_version": "2.0.5",
                    "new_version": "2.1.0",
                    "previous_build": "2023110101",
                    "new_build": "2023120801",
                    "update_type": "minor"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_application_uninstalled_success(self, mock_client):
        """Test successful Application Uninstalled event tracking."""
        result = track_application_uninstalled(
            client=mock_client,
            user_id="user123",
            properties={
                "version": "2.1.0",
                "days_since_install": 45,
                "total_sessions": 87,
                "last_session_date": "2024-01-15T10:30:00Z"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Application Uninstalled",
                "properties": {
                    "version": "2.1.0",
                    "days_since_install": 45,
                    "total_sessions": 87,
                    "last_session_date": "2024-01-15T10:30:00Z"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_application_crashed_success(self, mock_client):
        """Test successful Application Crashed event tracking."""
        result = track_application_crashed(
            client=mock_client,
            user_id="user123",
            properties={
                "version": "2.1.0",
                "crash_type": "segmentation_fault",
                "crash_location": "MainActivity.onCreate",
                "stack_trace": "java.lang.NullPointerException at...",
                "device_model": "iPhone 13"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Application Crashed",
                "properties": {
                    "version": "2.1.0",
                    "crash_type": "segmentation_fault",
                    "crash_location": "MainActivity.onCreate",
                    "stack_trace": "java.lang.NullPointerException at...",
                    "device_model": "iPhone 13"
                }
            }
        )
        assert result == {"status": "success"}


class TestPushNotificationEvents:
    """Test push notification semantic events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_push_notification_received_success(self, mock_client):
        """Test successful Push Notification Received event tracking."""
        result = track_push_notification_received(
            client=mock_client,
            user_id="user123",
            properties={
                "campaign_id": "campaign_456",
                "message_id": "message_789",
                "notification_type": "promotional",
                "delivery_id": "delivery_123"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Push Notification Received",
                "properties": {
                    "campaign_id": "campaign_456",
                    "message_id": "message_789",
                    "notification_type": "promotional",
                    "delivery_id": "delivery_123"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_push_notification_tapped_success(self, mock_client):
        """Test successful Push Notification Tapped event tracking."""
        result = track_push_notification_tapped(
            client=mock_client,
            user_id="user123",
            properties={
                "campaign_id": "campaign_456",
                "message_id": "message_789",
                "action_taken": "open_app",
                "deep_link": "myapp://product/123"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Push Notification Tapped",
                "properties": {
                    "campaign_id": "campaign_456",
                    "message_id": "message_789",
                    "action_taken": "open_app",
                    "deep_link": "myapp://product/123"
                }
            }
        )
        assert result == {"status": "success"}


class TestMobileManagerValidation:
    """Test validation scenarios for mobile events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_invalid_user_id(self, mock_client):
        """Test mobile event with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_application_installed(
                client=mock_client,
                user_id=""
            )
    
    def test_none_user_id(self, mock_client):
        """Test mobile event with None user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_application_opened(
                client=mock_client,
                user_id=None
            )
    
    def test_invalid_properties(self, mock_client):
        """Test mobile event with invalid properties."""
        with pytest.raises(ValidationError, match="Properties must be a dictionary"):
            track_application_backgrounded(
                client=mock_client,
                user_id="user123",
                properties="invalid"
            )
    
    def test_api_error(self, mock_client):
        """Test mobile event when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            track_application_foregrounded(
                client=mock_client,
                user_id="user123"
            )


class TestMobileManagerIntegration:
    """Test integration scenarios for comprehensive mobile app analytics."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_complete_app_installation_and_first_session(self, mock_client):
        """Test complete app installation and first session workflow."""
        user_id = "user123"
        
        # App installation
        install_result = track_application_installed(
            client=mock_client,
            user_id=user_id,
            properties={
                "version": "1.0.0",
                "install_source": "app_store",
                "device_type": "ios",
                "device_model": "iPhone 13"
            }
        )
        assert install_result == {"status": "success"}
        
        # First app open
        open_result = track_application_opened(
            client=mock_client,
            user_id=user_id,
            properties={
                "version": "1.0.0",
                "session_id": "session_001",
                "from_background": False,
                "launch_source": "first_launch"
            }
        )
        assert open_result == {"status": "success"}
        
        # App backgrounded after first session
        background_result = track_application_backgrounded(
            client=mock_client,
            user_id=user_id,
            properties={
                "session_id": "session_001",
                "session_duration": 180.5,
                "screens_viewed": 3,
                "actions_taken": 5
            }
        )
        assert background_result == {"status": "success"}
        
        # Verify all events were tracked
        assert mock_client.make_request.call_count == 3
    
    def test_app_lifecycle_with_push_notifications(self, mock_client):
        """Test app lifecycle including push notification interactions."""
        user_id = "user123"
        
        # App backgrounded
        background_result = track_application_backgrounded(
            client=mock_client,
            user_id=user_id,
            properties={
                "session_id": "session_002",
                "session_duration": 120.0
            }
        )
        assert background_result == {"status": "success"}
        
        # Push notification received while backgrounded
        notification_received = track_push_notification_received(
            client=mock_client,
            user_id=user_id,
            properties={
                "campaign_id": "promo_campaign",
                "message_id": "msg_123",
                "notification_type": "promotional"
            }
        )
        assert notification_received == {"status": "success"}
        
        # User taps the notification
        notification_tapped = track_push_notification_tapped(
            client=mock_client,
            user_id=user_id,
            properties={
                "campaign_id": "promo_campaign",
                "message_id": "msg_123",
                "action_taken": "open_app",
                "deep_link": "myapp://promotion"
            }
        )
        assert notification_tapped == {"status": "success"}
        
        # App foregrounded due to notification tap
        foreground_result = track_application_foregrounded(
            client=mock_client,
            user_id=user_id,
            properties={
                "session_id": "session_003",
                "background_duration": 3600.0,
                "return_reason": "push_notification",
                "campaign_attribution": "promo_campaign"
            }
        )
        assert foreground_result == {"status": "success"}
        
        # Verify all events were tracked
        assert mock_client.make_request.call_count == 4
    
    def test_app_update_workflow(self, mock_client):
        """Test application update workflow."""
        user_id = "user123"
        
        # User updates the app
        update_result = track_application_updated(
            client=mock_client,
            user_id=user_id,
            properties={
                "previous_version": "1.5.2",
                "new_version": "2.0.0",
                "update_type": "major",
                "update_source": "auto_update",
                "release_notes_viewed": True
            }
        )
        assert update_result == {"status": "success"}
        
        # First open after update
        open_result = track_application_opened(
            client=mock_client,
            user_id=user_id,
            properties={
                "version": "2.0.0",
                "session_id": "session_post_update",
                "from_background": False,
                "launch_source": "post_update",
                "first_launch_new_version": True
            }
        )
        assert open_result == {"status": "success"}
        
        # Verify both events were tracked
        assert mock_client.make_request.call_count == 2
    
    def test_app_crash_and_recovery_workflow(self, mock_client):
        """Test application crash and recovery workflow."""
        user_id = "user123"
        
        # App crashes during use
        crash_result = track_application_crashed(
            client=mock_client,
            user_id=user_id,
            properties={
                "version": "2.0.0",
                "crash_type": "out_of_memory",
                "crash_location": "ImageProcessor.loadLargeImage",
                "memory_usage": "850MB",
                "device_model": "iPhone 12"
            }
        )
        assert crash_result == {"status": "success"}
        
        # User reopens app after crash
        recovery_open = track_application_opened(
            client=mock_client,
            user_id=user_id,
            properties={
                "version": "2.0.0",
                "session_id": "session_recovery",
                "from_background": False,
                "launch_source": "crash_recovery",
                "previous_session_crashed": True
            }
        )
        assert recovery_open == {"status": "success"}
        
        # Verify both events were tracked
        assert mock_client.make_request.call_count == 2
    
    def test_app_uninstall_workflow(self, mock_client):
        """Test application uninstall tracking."""
        user_id = "user123"
        
        # Final app backgrounding before uninstall
        final_background = track_application_backgrounded(
            client=mock_client,
            user_id=user_id,
            properties={
                "session_id": "session_final",
                "session_duration": 30.0,
                "screens_viewed": 1,
                "actions_taken": 0
            }
        )
        assert final_background == {"status": "success"}
        
        # App uninstall event (typically triggered by server-side detection)
        uninstall_result = track_application_uninstalled(
            client=mock_client,
            user_id=user_id,
            properties={
                "version": "2.0.0",
                "days_since_install": 180,
                "total_sessions": 145,
                "total_session_time": 25200,  # 7 hours
                "last_session_date": "2024-01-15T08:30:00Z",
                "uninstall_reason_inferred": "low_engagement"
            }
        )
        assert uninstall_result == {"status": "success"}
        
        # Verify both events were tracked
        assert mock_client.make_request.call_count == 2
    
    def test_session_pattern_tracking(self, mock_client):
        """Test typical user session pattern tracking."""
        user_id = "user123"
        sessions = [
            {"id": "morning_session", "duration": 240.0, "screens": 8, "actions": 15},
            {"id": "lunch_session", "duration": 60.0, "screens": 2, "actions": 3},
            {"id": "evening_session", "duration": 480.0, "screens": 12, "actions": 25}
        ]
        
        for session in sessions:
            # App opened
            open_result = track_application_opened(
                client=mock_client,
                user_id=user_id,
                properties={
                    "session_id": session["id"],
                    "from_background": False,
                    "launch_source": "direct"
                }
            )
            assert open_result == {"status": "success"}
            
            # App backgrounded
            background_result = track_application_backgrounded(
                client=mock_client,
                user_id=user_id,
                properties={
                    "session_id": session["id"],
                    "session_duration": session["duration"],
                    "screens_viewed": session["screens"],
                    "actions_taken": session["actions"]
                }
            )
            assert background_result == {"status": "success"}
        
        # Verify all session events were tracked (3 sessions × 2 events each)
        assert mock_client.make_request.call_count == 6