"""
Unit tests for Customer.IO screen tracking functions.
"""

from unittest.mock import Mock, patch
import pytest
from datetime import datetime, timezone

from utils.screen_manager import (
    track_screen,
    track_screenview
)
from utils.exceptions import ValidationError, CustomerIOError
from utils.api_client import CustomerIOClient


class TestTrackScreen:
    """Test screen tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_screen_success(self, mock_client):
        """Test successful screen tracking."""
        result = track_screen(
            client=mock_client,
            user_id="user123",
            screen_name="Product Details",
            properties={"product_id": "prod_456", "category": "electronics"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user123",
                "name": "Product Details",
                "properties": {"product_id": "prod_456", "category": "electronics"}
            }
        )
        assert result == {"status": "success"}
    
    def test_track_screen_minimal_params(self, mock_client):
        """Test screen tracking with minimal parameters."""
        result = track_screen(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user123"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_screen_with_timestamp(self, mock_client):
        """Test screen tracking with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = track_screen(
            client=mock_client,
            user_id="user123",
            screen_name="Settings",
            properties={"section": "notifications"},
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user123",
                "name": "Settings",
                "properties": {"section": "notifications"},
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_screen_with_context(self, mock_client):
        """Test screen tracking with context information."""
        context = {
            "app": {
                "name": "MyApp",
                "version": "2.1.0",
                "build": "123"
            },
            "device": {
                "type": "mobile",
                "model": "iPhone 13",
                "manufacturer": "Apple"
            },
            "os": {
                "name": "iOS",
                "version": "15.0"
            }
        }
        
        result = track_screen(
            client=mock_client,
            user_id="user123",
            screen_name="Dashboard",
            context=context
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user123",
                "name": "Dashboard",
                "context": context
            }
        )
        assert result == {"status": "success"}
    
    def test_track_screen_anonymous_user(self, mock_client):
        """Test screen tracking with anonymous user."""
        result = track_screen(
            client=mock_client,
            anonymous_id="anon_456",
            screen_name="Onboarding",
            properties={"step": 1, "total_steps": 5}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "anonymousId": "anon_456",
                "name": "Onboarding",
                "properties": {"step": 1, "total_steps": 5}
            }
        )
        assert result == {"status": "success"}
    
    def test_track_screen_invalid_user_identification(self, mock_client):
        """Test screen tracking without user identification."""
        with pytest.raises(ValidationError, match="Either user_id or anonymous_id must be provided"):
            track_screen(
                client=mock_client,
                screen_name="Test Screen"
            )
    
    def test_track_screen_both_user_ids(self, mock_client):
        """Test screen tracking with both user_id and anonymous_id."""
        with pytest.raises(ValidationError, match="Cannot provide both user_id and anonymous_id"):
            track_screen(
                client=mock_client,
                user_id="user123",
                anonymous_id="anon_456",
                screen_name="Test Screen"
            )
    
    def test_track_screen_invalid_user_id(self, mock_client):
        """Test screen tracking with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_screen(
                client=mock_client,
                user_id="",
                screen_name="Test Screen"
            )
    
    def test_track_screen_invalid_properties(self, mock_client):
        """Test screen tracking with invalid properties."""
        with pytest.raises(ValidationError, match="Properties must be a dictionary"):
            track_screen(
                client=mock_client,
                user_id="user123",
                properties="invalid"
            )
    
    def test_track_screen_invalid_context(self, mock_client):
        """Test screen tracking with invalid context."""
        with pytest.raises(ValidationError, match="Context must be a dictionary"):
            track_screen(
                client=mock_client,
                user_id="user123",
                context="invalid"
            )
    
    def test_track_screen_api_error(self, mock_client):
        """Test screen tracking when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            track_screen(
                client=mock_client,
                user_id="user123",
                screen_name="Test Screen"
            )


class TestTrackScreenview:
    """Test screenview tracking functionality (alias)."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_screenview_success(self, mock_client):
        """Test successful screenview tracking."""
        result = track_screenview(
            client=mock_client,
            user_id="user123",
            screen_name="Product List",
            screen_class="ProductListViewController"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user123",
                "name": "Product List",
                "properties": {
                    "screen_class": "ProductListViewController"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_screenview_with_additional_properties(self, mock_client):
        """Test screenview tracking with additional properties."""
        result = track_screenview(
            client=mock_client,
            user_id="user123",
            screen_name="Search Results",
            screen_class="SearchResultsViewController",
            query="wireless headphones",
            results_count=25,
            load_time=0.45
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user123",
                "name": "Search Results",
                "properties": {
                    "screen_class": "SearchResultsViewController",
                    "query": "wireless headphones",
                    "results_count": 25,
                    "load_time": 0.45
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_screenview_minimal_params(self, mock_client):
        """Test screenview tracking with minimal parameters."""
        result = track_screenview(
            client=mock_client,
            user_id="user123",
            screen_name="Home"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user123",
                "name": "Home"
            }
        )
        assert result == {"status": "success"}


class TestScreenManagerIntegration:
    """Test integration scenarios for screen tracking."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_mobile_app_navigation_flow(self, mock_client):
        """Test mobile app navigation flow tracking."""
        user_id = "user123"
        
        # Track app launch screen
        launch_result = track_screen(
            client=mock_client,
            user_id=user_id,
            screen_name="Splash Screen",
            properties={"app_version": "2.1.0", "first_launch": False}
        )
        assert launch_result == {"status": "success"}
        
        # Track home screen
        home_result = track_screenview(
            client=mock_client,
            user_id=user_id,
            screen_name="Home",
            screen_class="HomeViewController",
            tab="featured"
        )
        assert home_result == {"status": "success"}
        
        # Track product screen
        product_result = track_screen(
            client=mock_client,
            user_id=user_id,
            screen_name="Product Details",
            properties={"product_id": "prod_789", "category": "electronics", "price": 299.99}
        )
        assert product_result == {"status": "success"}
        
        # Track cart screen
        cart_result = track_screenview(
            client=mock_client,
            user_id=user_id,
            screen_name="Shopping Cart",
            screen_class="CartViewController",
            items_count=3,
            total_value=897.97
        )
        assert cart_result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 4
    
    def test_anonymous_to_identified_mobile_flow(self, mock_client):
        """Test screen tracking for anonymous user becoming identified."""
        anonymous_id = "anon_789"
        user_id = "user456"
        
        # Track anonymous app usage
        anon_result = track_screen(
            client=mock_client,
            anonymous_id=anonymous_id,
            screen_name="Welcome Screen"
        )
        assert anon_result == {"status": "success"}
        
        # Track after user signs up
        identified_result = track_screen(
            client=mock_client,
            user_id=user_id,
            screen_name="Profile Setup",
            properties={"signup_method": "email", "first_time": True}
        )
        assert identified_result == {"status": "success"}
        
        # Verify calls
        assert mock_client.make_request.call_count == 2
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        
        # First call (anonymous)
        assert calls[0][0][2]["anonymousId"] == anonymous_id
        assert "userId" not in calls[0][0][2]
        
        # Second call (identified)
        assert calls[1][0][2]["userId"] == user_id
        assert "anonymousId" not in calls[1][0][2]
    
    def test_app_session_tracking(self, mock_client):
        """Test tracking a complete app session."""
        screens = [
            {"name": "Launch Screen", "class": "LaunchViewController"},
            {"name": "Home", "class": "HomeViewController"},
            {"name": "Category List", "class": "CategoryListViewController"},
            {"name": "Product List", "class": "ProductListViewController"},
            {"name": "Product Details", "class": "ProductDetailsViewController"},
            {"name": "Reviews", "class": "ReviewsViewController"}
        ]
        
        user_id = "user123"
        session_id = "session_456"
        
        # Track all screens in session
        for i, screen in enumerate(screens):
            result = track_screenview(
                client=mock_client,
                user_id=user_id,
                screen_name=screen["name"],
                screen_class=screen["class"],
                session_id=session_id,
                screen_order=i + 1
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 6
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/screen"
            assert args[2]["userId"] == user_id
            assert args[2]["name"] == screens[i]["name"]
            assert args[2]["properties"]["screen_class"] == screens[i]["class"]
            assert args[2]["properties"]["session_id"] == session_id
            assert args[2]["properties"]["screen_order"] == i + 1
    
    def test_error_screen_tracking(self, mock_client):
        """Test tracking error and crash screens."""
        user_id = "user123"
        
        # Track error screen
        error_result = track_screen(
            client=mock_client,
            user_id=user_id,
            screen_name="Error Screen",
            properties={
                "error_type": "network_timeout",
                "error_code": "TIMEOUT_001",
                "previous_screen": "Product List",
                "retry_count": 2
            }
        )
        assert error_result == {"status": "success"}
        
        # Track crash screen
        crash_result = track_screenview(
            client=mock_client,
            user_id=user_id,
            screen_name="Crash Report",
            screen_class="CrashReportViewController",
            crash_type="segmentation_fault",
            app_version="2.1.0",
            device_model="iPhone 13"
        )
        assert crash_result == {"status": "success"}
        
        # Verify calls
        assert mock_client.make_request.call_count == 2