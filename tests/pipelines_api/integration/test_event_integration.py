"""
Integration tests for Customer.IO Event Tracking API.

Tests real API interactions for:
- Custom event tracking
- Page view tracking  
- Screen view tracking
- Various event types with properties
- Error handling
"""

import pytest
from datetime import datetime, timezone

from tests.pipelines_api.integration.base import BaseIntegrationTest
from tests.pipelines_api.integration.utils import (
    generate_test_email,
    generate_test_event_properties
)
from src.pipelines_api.event_manager import (
    track_event,
    track_page_view,
    track_screen_view,
    track_ecommerce_event,
    track_email_event,
    track_mobile_event,
    track_video_event
)
from src.pipelines_api.people_manager import identify_user
from src.pipelines_api.exceptions import CustomerIOError, ValidationError


@pytest.mark.integration
class TestEventIntegration(BaseIntegrationTest):
    """Integration tests for event tracking functionality."""
    
    def test_track_custom_event_basic(self, authenticated_client, test_user_id):
        """Test tracking a basic custom event."""
        # Arrange - Create user first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("event"),
            "name": "Event Test User"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_event(
            authenticated_client,
            test_user_id,
            "Integration Test Event",
            {"test_type": "basic", "integration": True}
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_event_with_properties(self, authenticated_client, test_user_id):
        """Test tracking event with complex properties."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("props"),
            "name": "Properties Test"
        })
        self.track_user(test_user_id)
        
        properties = {
            "product_id": "test-123",
            "category": "electronics",
            "price": 99.99,
            "quantity": 2,
            "nested": {
                "location": "warehouse_a",
                "priority": "high"
            },
            "tags": ["integration", "test", "api"]
        }
        
        # Act
        result = track_event(
            authenticated_client,
            test_user_id,
            "Product Purchase",
            properties
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_event_with_timestamp(self, authenticated_client, test_user_id):
        """Test tracking event with custom timestamp."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("timestamp"),
            "name": "Timestamp Test"
        })
        self.track_user(test_user_id)
        
        custom_timestamp = datetime.now(timezone.utc)
        
        # Act
        result = track_event(
            authenticated_client,
            test_user_id,
            "Historical Event",
            {"source": "backfill"},
            timestamp=custom_timestamp
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_page_view(self, authenticated_client, test_user_id):
        """Test tracking page views."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("page"),
            "name": "Page Test"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_page_view(
            authenticated_client,
            test_user_id,
            "/integration/test",
            {"title": "Integration Test Page", "category": "testing"}
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_screen_view(self, authenticated_client, test_user_id):
        """Test tracking screen views."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("screen"),
            "name": "Screen Test"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_screen_view(
            authenticated_client,
            test_user_id,
            "Settings Screen",
            {"app_version": "1.0.0", "platform": "ios"}
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_multiple_events_sequence(self, authenticated_client, test_user_id):
        """Test tracking multiple events in sequence."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("sequence"),
            "name": "Sequence Test"
        })
        self.track_user(test_user_id)
        
        events = [
            ("App Opened", {"source": "push_notification"}),
            ("Page Viewed", {"page": "dashboard"}),
            ("Button Clicked", {"button_id": "upgrade_now"}),
            ("Purchase Started", {"plan": "premium"})
        ]
        
        # Act & Assert
        for event_name, properties in events:
            result = track_event(
                authenticated_client,
                test_user_id,
                event_name,
                properties
            )
            self.assert_successful_response(result)
            # Small delay to respect rate limits
            self.wait_for_eventual_consistency(0.1)
    
    def test_track_event_anonymous_user(self, authenticated_client, test_anonymous_id):
        """Test tracking events for anonymous users."""
        # Note: For anonymous users, we typically use userId with anonymous ID
        # This tests the pattern where anonymous_id is used as user_id
        
        # Act
        result = track_event(
            authenticated_client,
            test_anonymous_id,  # Using anonymous ID as user ID
            "Anonymous Browsing",
            {"page": "landing", "source": "google"}
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_event_validation_errors(self, authenticated_client):
        """Test event tracking validation."""
        # Test empty event name
        with pytest.raises(ValidationError):
            track_event(authenticated_client, "user123", "", {})
        
        # Test empty user ID
        with pytest.raises(ValidationError):
            track_event(authenticated_client, "", "Test Event", {})
    
    def test_track_event_with_special_characters(self, authenticated_client, test_user_id):
        """Test tracking events with special characters and unicode."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("unicode"),
            "name": "Unicode Test 测试"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_event(
            authenticated_client,
            test_user_id,
            "Special Event 🎉",
            {
                "description": "Event with émojis and spëcial chars",
                "unicode_text": "Hello 世界 🌍",
                "symbols": "!@#$%^&*()",
                "url": "https://example.com/path?param=value&other=123"
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    @pytest.mark.slow
    def test_high_volume_events(self, authenticated_client, test_user_id):
        """Test tracking multiple events for load testing."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("volume"),
            "name": "Volume Test"
        })
        self.track_user(test_user_id)
        
        # Act - Track 20 events with rate limiting
        for i in range(20):
            result = track_event(
                authenticated_client,
                test_user_id,
                f"Volume Test Event {i}",
                {"index": i, "batch": "high_volume"}
            )
            self.assert_successful_response(result)
            
            # Rate limiting - respect API limits
            if i % 5 == 0:
                self.wait_for_eventual_consistency(0.2)