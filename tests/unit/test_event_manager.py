"""
Unit tests for Customer.IO event tracking functions.
"""

from unittest.mock import Mock, patch
import pytest
from datetime import datetime, timezone

from utils.event_manager import (
    track_event,
    track_page_view,
    track_screen_view,
    track_ecommerce_event,
    track_email_event,
    track_mobile_event,
    track_video_event
)
from utils.exceptions import ValidationError, CustomerIOError
from utils.api_client import CustomerIOClient


class TestTrackEvent:
    """Test custom event tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_event_success(self, mock_client):
        """Test successful event tracking."""
        result = track_event(
            client=mock_client,
            user_id="user123",
            event_name="product_viewed",
            properties={"product_id": "prod_456", "category": "electronics"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "product_viewed",
                "properties": {"product_id": "prod_456", "category": "electronics"}
            }
        )
        assert result == {"status": "success"}
    
    def test_track_event_minimal_params(self, mock_client):
        """Test event tracking with minimal parameters."""
        result = track_event(
            client=mock_client,
            user_id="user123",
            event_name="button_clicked"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "button_clicked"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_event_with_timestamp(self, mock_client):
        """Test event tracking with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = track_event(
            client=mock_client,
            user_id="user123",
            event_name="purchase_completed",
            properties={"amount": 99.99},
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "purchase_completed",
                "properties": {"amount": 99.99},
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_event_invalid_user_id(self, mock_client):
        """Test event tracking with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_event(
                client=mock_client,
                user_id="",
                event_name="test_event"
            )
    
    def test_track_event_invalid_event_name(self, mock_client):
        """Test event tracking with invalid event name."""
        with pytest.raises(ValidationError, match="Event name must be a non-empty string"):
            track_event(
                client=mock_client,
                user_id="user123",
                event_name=""
            )
    
    def test_track_event_long_event_name(self, mock_client):
        """Test event tracking with event name that's too long."""
        long_event_name = "x" * 151
        
        with pytest.raises(ValidationError, match="Event name must be 150 characters or less"):
            track_event(
                client=mock_client,
                user_id="user123",
                event_name=long_event_name
            )
    
    def test_track_event_invalid_properties(self, mock_client):
        """Test event tracking with invalid properties."""
        with pytest.raises(ValidationError, match="Properties must be a dictionary"):
            track_event(
                client=mock_client,
                user_id="user123",
                event_name="test_event",
                properties="invalid"
            )
    
    def test_track_event_api_error(self, mock_client):
        """Test event tracking when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            track_event(
                client=mock_client,
                user_id="user123",
                event_name="test_event"
            )


class TestTrackPageView:
    """Test page view tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_page_view_success(self, mock_client):
        """Test successful page view tracking."""
        result = track_page_view(
            client=mock_client,
            user_id="user123",
            page_name="Home Page",
            properties={"url": "https://example.com", "referrer": "google.com"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user123",
                "name": "Home Page",
                "properties": {"url": "https://example.com", "referrer": "google.com"}
            }
        )
        assert result == {"status": "success"}
    
    def test_track_page_view_minimal_params(self, mock_client):
        """Test page view tracking with minimal parameters."""
        result = track_page_view(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {"userId": "user123"}
        )
        assert result == {"status": "success"}
    
    def test_track_page_view_invalid_user_id(self, mock_client):
        """Test page view tracking with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_page_view(
                client=mock_client,
                user_id=""
            )


class TestTrackScreenView:
    """Test mobile screen view tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_screen_view_success(self, mock_client):
        """Test successful screen view tracking."""
        result = track_screen_view(
            client=mock_client,
            user_id="user123",
            screen_name="Product Details",
            properties={"product_id": "prod_456", "screen_class": "ProductViewController"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user123",
                "name": "Product Details",
                "properties": {"product_id": "prod_456", "screen_class": "ProductViewController"}
            }
        )
        assert result == {"status": "success"}
    
    def test_track_screen_view_minimal_params(self, mock_client):
        """Test screen view tracking with minimal parameters."""
        result = track_screen_view(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {"userId": "user123"}
        )
        assert result == {"status": "success"}


class TestTrackEcommerceEvent:
    """Test ecommerce event tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_product_viewed(self, mock_client):
        """Test product viewed event tracking."""
        result = track_ecommerce_event(
            client=mock_client,
            user_id="user123",
            event_type="product_viewed",
            data={
                "product_id": "prod_456",
                "product_name": "Wireless Headphones",
                "price": 99.99,
                "currency": "USD"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Product Viewed",
                "properties": {
                    "product_id": "prod_456",
                    "product_name": "Wireless Headphones",
                    "price": 99.99,
                    "currency": "USD"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_order_completed(self, mock_client):
        """Test order completed event tracking."""
        result = track_ecommerce_event(
            client=mock_client,
            user_id="user123",
            event_type="order_completed",
            data={
                "order_id": "order_789",
                "total": 149.98,
                "currency": "USD",
                "products": [
                    {"product_id": "prod_1", "price": 75.00},
                    {"product_id": "prod_2", "price": 74.98}
                ]
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Order Completed",
                "properties": {
                    "order_id": "order_789",
                    "total": 149.98,
                    "currency": "USD",
                    "products": [
                        {"product_id": "prod_1", "price": 75.00},
                        {"product_id": "prod_2", "price": 74.98}
                    ]
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_ecommerce_invalid_event_type(self, mock_client):
        """Test ecommerce event tracking with invalid event type."""
        with pytest.raises(ValidationError, match="Invalid ecommerce event type"):
            track_ecommerce_event(
                client=mock_client,
                user_id="user123",
                event_type="invalid_event",
                data={}
            )


class TestTrackEmailEvent:
    """Test email event tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_email_opened(self, mock_client):
        """Test email opened event tracking."""
        result = track_email_event(
            client=mock_client,
            user_id="user123",
            event_type="email_opened",
            data={
                "email_id": "email_456",
                "campaign_id": "campaign_789",
                "subject": "Welcome to our service!"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Email Opened",
                "properties": {
                    "email_id": "email_456",
                    "campaign_id": "campaign_789",
                    "subject": "Welcome to our service!"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_email_invalid_event_type(self, mock_client):
        """Test email event tracking with invalid event type."""
        with pytest.raises(ValidationError, match="Invalid email event type"):
            track_email_event(
                client=mock_client,
                user_id="user123",
                event_type="invalid_event",
                data={}
            )


class TestTrackMobileEvent:
    """Test mobile event tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_push_notification_received(self, mock_client):
        """Test push notification received event tracking."""
        result = track_mobile_event(
            client=mock_client,
            user_id="user123",
            event_type="push_notification_received",
            data={
                "notification_id": "notif_456",
                "campaign_id": "campaign_789",
                "message": "New message waiting for you!"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Push Notification Received",
                "properties": {
                    "notification_id": "notif_456",
                    "campaign_id": "campaign_789",
                    "message": "New message waiting for you!"
                }
            }
        )
        assert result == {"status": "success"}


class TestTrackVideoEvent:
    """Test video event tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_video_started(self, mock_client):
        """Test video started event tracking."""
        result = track_video_event(
            client=mock_client,
            user_id="user123",
            event_type="video_started",
            data={
                "video_id": "video_456",
                "video_title": "Product Demo",
                "duration": 120,
                "quality": "HD"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Video Started",
                "properties": {
                    "video_id": "video_456",
                    "video_title": "Product Demo",
                    "duration": 120,
                    "quality": "HD"
                }
            }
        )
        assert result == {"status": "success"}


class TestEventManagerIntegration:
    """Test integration scenarios for event tracking."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_user_journey_tracking(self, mock_client):
        """Test complete user journey event tracking."""
        user_id = "user123"
        
        # Track page view
        page_result = track_page_view(
            client=mock_client,
            user_id=user_id,
            page_name="Home Page",
            properties={"url": "https://example.com"}
        )
        assert page_result == {"status": "success"}
        
        # Track product view
        product_result = track_ecommerce_event(
            client=mock_client,
            user_id=user_id,
            event_type="product_viewed",
            data={"product_id": "prod_456", "price": 99.99}
        )
        assert product_result == {"status": "success"}
        
        # Track custom event
        custom_result = track_event(
            client=mock_client,
            user_id=user_id,
            event_name="add_to_cart",
            properties={"product_id": "prod_456", "quantity": 1}
        )
        assert custom_result == {"status": "success"}
        
        # Track order completion
        order_result = track_ecommerce_event(
            client=mock_client,
            user_id=user_id,
            event_type="order_completed",
            data={"order_id": "order_789", "total": 99.99}
        )
        assert order_result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 4
    
    def test_batch_event_tracking(self, mock_client):
        """Test tracking multiple events for different users."""
        events = [
            {"user_id": "user1", "event": "signup", "properties": {"source": "web"}},
            {"user_id": "user2", "event": "login", "properties": {"method": "google"}},
            {"user_id": "user3", "event": "purchase", "properties": {"amount": 50.00}}
        ]
        
        # Track all events
        for event in events:
            result = track_event(
                client=mock_client,
                user_id=event["user_id"],
                event_name=event["event"],
                properties=event["properties"]
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/track"
            assert args[2]["userId"] == events[i]["user_id"]
            assert args[2]["event"] == events[i]["event"]
            assert args[2]["properties"] == events[i]["properties"]