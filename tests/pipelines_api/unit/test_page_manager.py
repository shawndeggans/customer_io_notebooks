"""
Unit tests for Customer.IO page tracking functions.
"""

from unittest.mock import Mock
import pytest
from datetime import datetime, timezone

from src.pipelines_api.page_manager import (
    track_page,
    track_pageview
)
from src.pipelines_api.exceptions import ValidationError, CustomerIOError
from src.pipelines_api.api_client import CustomerIOClient


class TestTrackPage:
    """Test page tracking functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_page_success(self, mock_client):
        """Test successful page tracking."""
        result = track_page(
            client=mock_client,
            user_id="user123",
            page_name="Home Page",
            properties={"url": "https://example.com", "title": "Welcome"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user123",
                "name": "Home Page",
                "properties": {"url": "https://example.com", "title": "Welcome"}
            }
        )
        assert result == {"status": "success"}
    
    def test_track_page_minimal_params(self, mock_client):
        """Test page tracking with minimal parameters."""
        result = track_page(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user123"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_page_with_timestamp(self, mock_client):
        """Test page tracking with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = track_page(
            client=mock_client,
            user_id="user123",
            page_name="Product Page",
            properties={"url": "https://example.com/product/123"},
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user123",
                "name": "Product Page",
                "properties": {"url": "https://example.com/product/123"},
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_page_with_context(self, mock_client):
        """Test page tracking with context information."""
        context = {
            "ip": "192.168.1.1",
            "userAgent": "Mozilla/5.0 (Test Browser)",
            "page": {
                "url": "https://example.com/contact",
                "title": "Contact Us",
                "referrer": "https://google.com"
            }
        }
        
        result = track_page(
            client=mock_client,
            user_id="user123",
            page_name="Contact Page",
            context=context
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user123",
                "name": "Contact Page",
                "context": context
            }
        )
        assert result == {"status": "success"}
    
    def test_track_page_anonymous_user(self, mock_client):
        """Test page tracking with anonymous user."""
        result = track_page(
            client=mock_client,
            anonymous_id="anon_456",
            page_name="Landing Page",
            properties={"campaign": "email_newsletter"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "anonymousId": "anon_456",
                "name": "Landing Page",
                "properties": {"campaign": "email_newsletter"}
            }
        )
        assert result == {"status": "success"}
    
    def test_track_page_invalid_user_identification(self, mock_client):
        """Test page tracking without user identification."""
        with pytest.raises(ValidationError, match="Either user_id or anonymous_id must be provided"):
            track_page(
                client=mock_client,
                page_name="Test Page"
            )
    
    def test_track_page_both_user_ids(self, mock_client):
        """Test page tracking with both user_id and anonymous_id."""
        with pytest.raises(ValidationError, match="Cannot provide both user_id and anonymous_id"):
            track_page(
                client=mock_client,
                user_id="user123",
                anonymous_id="anon_456",
                page_name="Test Page"
            )
    
    def test_track_page_invalid_user_id(self, mock_client):
        """Test page tracking with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_page(
                client=mock_client,
                user_id="",
                page_name="Test Page"
            )
    
    def test_track_page_invalid_properties(self, mock_client):
        """Test page tracking with invalid properties."""
        with pytest.raises(ValidationError, match="Properties must be a dictionary"):
            track_page(
                client=mock_client,
                user_id="user123",
                properties="invalid"
            )
    
    def test_track_page_invalid_context(self, mock_client):
        """Test page tracking with invalid context."""
        with pytest.raises(ValidationError, match="Context must be a dictionary"):
            track_page(
                client=mock_client,
                user_id="user123",
                context="invalid"
            )
    
    def test_track_page_api_error(self, mock_client):
        """Test page tracking when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            track_page(
                client=mock_client,
                user_id="user123",
                page_name="Test Page"
            )


class TestTrackPageview:
    """Test pageview tracking functionality (alias)."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_pageview_success(self, mock_client):
        """Test successful pageview tracking."""
        result = track_pageview(
            client=mock_client,
            user_id="user123",
            url="https://example.com/about",
            title="About Us"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user123",
                "properties": {
                    "url": "https://example.com/about",
                    "title": "About Us"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_pageview_with_additional_properties(self, mock_client):
        """Test pageview tracking with additional properties."""
        result = track_pageview(
            client=mock_client,
            user_id="user123",
            url="https://example.com/product/456",
            title="Product Details",
            referrer="https://example.com/products",
            search="wireless headphones"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user123",
                "properties": {
                    "url": "https://example.com/product/456",
                    "title": "Product Details",
                    "referrer": "https://example.com/products",
                    "search": "wireless headphones"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_pageview_minimal_params(self, mock_client):
        """Test pageview tracking with minimal parameters."""
        result = track_pageview(
            client=mock_client,
            user_id="user123",
            url="https://example.com"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user123",
                "properties": {
                    "url": "https://example.com"
                }
            }
        )
        assert result == {"status": "success"}


class TestPageManagerIntegration:
    """Test integration scenarios for page tracking."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_user_journey_page_tracking(self, mock_client):
        """Test complete user journey page tracking."""
        user_id = "user123"
        
        # Track landing page
        landing_result = track_page(
            client=mock_client,
            user_id=user_id,
            page_name="Landing Page",
            properties={"campaign": "google_ads", "source": "search"}
        )
        assert landing_result == {"status": "success"}
        
        # Track product page
        product_result = track_pageview(
            client=mock_client,
            user_id=user_id,
            url="https://example.com/product/123",
            title="Wireless Headphones",
            referrer="https://example.com/search?q=headphones"
        )
        assert product_result == {"status": "success"}
        
        # Track checkout page
        checkout_result = track_page(
            client=mock_client,
            user_id=user_id,
            page_name="Checkout",
            properties={"step": "payment", "total": 99.99}
        )
        assert checkout_result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
    
    def test_anonymous_to_identified_user_journey(self, mock_client):
        """Test page tracking for anonymous user becoming identified."""
        anonymous_id = "anon_789"
        user_id = "user456"
        
        # Track anonymous pageview
        anon_result = track_page(
            client=mock_client,
            anonymous_id=anonymous_id,
            page_name="Home Page"
        )
        assert anon_result == {"status": "success"}
        
        # Track after user signs up
        identified_result = track_page(
            client=mock_client,
            user_id=user_id,
            page_name="Dashboard",
            properties={"first_visit": True}
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
    
    def test_batch_page_tracking(self, mock_client):
        """Test tracking multiple pages in sequence."""
        pages = [
            {"name": "Home", "url": "https://example.com"},
            {"name": "Products", "url": "https://example.com/products"},
            {"name": "About", "url": "https://example.com/about"},
            {"name": "Contact", "url": "https://example.com/contact"}
        ]
        
        user_id = "user123"
        
        # Track all pages
        for page in pages:
            result = track_pageview(
                client=mock_client,
                user_id=user_id,
                url=page["url"],
                title=page["name"]
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 4
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/page"
            assert args[2]["userId"] == user_id
            assert args[2]["properties"]["url"] == pages[i]["url"]
            assert args[2]["properties"]["title"] == pages[i]["name"]