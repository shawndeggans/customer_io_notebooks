"""
Unit tests for Customer.IO API client.
"""

import json
import time
from unittest.mock import Mock, patch, MagicMock
import pytest
import httpx

from utils.api_client import CustomerIOClient
from utils.exceptions import (
    CustomerIOError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NetworkError
)


class TestCustomerIOClient:
    """Test CustomerIO API client initialization and configuration."""
    
    def test_client_initialization_us_region(self):
        """Test client initialization with US region."""
        client = CustomerIOClient(api_key="test_key", region="us")
        
        assert client.api_key == "test_key"
        assert client.region == "us"
        assert client.base_url == "https://cdp.customer.io/v1"
    
    def test_client_initialization_eu_region(self):
        """Test client initialization with EU region."""
        client = CustomerIOClient(api_key="test_key", region="eu")
        
        assert client.api_key == "test_key"
        assert client.region == "eu"
        assert client.base_url == "https://cdp-eu.customer.io/v1"
    
    def test_client_initialization_invalid_region(self):
        """Test client initialization with invalid region."""
        with pytest.raises(ValidationError, match="Region must be 'us' or 'eu'"):
            CustomerIOClient(api_key="test_key", region="invalid")
    
    def test_client_initialization_empty_api_key(self):
        """Test client initialization with empty API key."""
        with pytest.raises(ValidationError, match="API key must be a non-empty string"):
            CustomerIOClient(api_key="")
    
    def test_client_initialization_none_api_key(self):
        """Test client initialization with None API key."""
        with pytest.raises(ValidationError, match="API key must be a non-empty string"):
            CustomerIOClient(api_key=None)


class TestAPIClientRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return CustomerIOClient(api_key="test_key")
    
    def test_rate_limit_initialization(self, client):
        """Test rate limit is properly initialized."""
        assert client.rate_limit.max_requests == 3000
        assert client.rate_limit.window_seconds == 3
        assert client.rate_limit.current_requests == 0
    
    def test_rate_limit_can_make_request_initially(self, client):
        """Test that requests can be made initially."""
        assert client.rate_limit.can_make_request() is True
    
    def test_rate_limit_records_requests(self, client):
        """Test that requests are recorded."""
        initial_count = client.rate_limit.current_requests
        client.rate_limit.record_request()
        assert client.rate_limit.current_requests == initial_count + 1
    
    def test_rate_limit_blocks_when_exceeded(self, client):
        """Test that requests are blocked when rate limit exceeded."""
        # Simulate hitting the rate limit
        client.rate_limit.current_requests = 3000
        client.rate_limit.window_start = time.time()  # Set current window
        assert client.rate_limit.can_make_request() is False
    
    @patch('time.time')
    def test_rate_limit_resets_after_window(self, mock_time, client):
        """Test that rate limit resets after time window."""
        # Set initial time
        mock_time.return_value = 1000.0
        client.rate_limit.window_start = 1000.0
        client.rate_limit.current_requests = 3000
        
        # Move time forward past window
        mock_time.return_value = 1004.0  # 4 seconds later
        
        assert client.rate_limit.can_make_request() is True
        assert client.rate_limit.current_requests == 0


class TestAPIClientAuthentication:
    """Test authentication functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return CustomerIOClient(api_key="test_key")
    
    def test_get_auth_headers(self, client):
        """Test authentication headers are properly formatted."""
        headers = client.get_auth_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_key"
        assert headers["Content-Type"] == "application/json"
    
    def test_get_auth_headers_includes_user_agent(self, client):
        """Test that auth headers include user agent."""
        headers = client.get_auth_headers()
        
        assert "User-Agent" in headers
        assert "customerio-python-client" in headers["User-Agent"]


class TestAPIClientRequests:
    """Test API request functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return CustomerIOClient(api_key="test_key")
    
    @patch('httpx.request')
    def test_make_request_success(self, mock_request, client):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        result = client.make_request("POST", "/identify", {"userId": "123"})
        
        assert result == {"status": "success"}
        mock_request.assert_called_once()
    
    @patch('httpx.request')
    def test_make_request_authentication_error(self, mock_request, client):
        """Test API request with authentication error."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )
        mock_request.return_value = mock_response
        
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            client.make_request("POST", "/identify", {"userId": "123"})
    
    @patch('httpx.request')
    def test_make_request_rate_limit_error(self, mock_request, client):
        """Test API request with rate limit error."""
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "429 Too Many Requests", request=Mock(), response=mock_response
        )
        mock_request.return_value = mock_response
        
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            client.make_request("POST", "/identify", {"userId": "123"})
    
    @patch('httpx.request')
    def test_make_request_network_error(self, mock_request, client):
        """Test API request with network error."""
        mock_request.side_effect = httpx.ConnectError("Connection failed")
        
        with pytest.raises(NetworkError, match="Network error"):
            client.make_request("POST", "/identify", {"userId": "123"})
    
    @patch('httpx.request')
    def test_make_request_includes_auth_headers(self, mock_request, client):
        """Test that requests include authentication headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        client.make_request("POST", "/identify", {"userId": "123"})
        
        # Check that request was called with proper headers
        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test_key"
        assert headers["Content-Type"] == "application/json"
    
    def test_make_request_checks_rate_limit(self, client):
        """Test that make_request checks rate limiting."""
        # Block requests by setting rate limit to exceeded
        client.rate_limit.current_requests = 3000
        client.rate_limit.window_start = time.time()  # Set current window
        
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            client.make_request("POST", "/identify", {"userId": "123"})


class TestAPIClientRetryLogic:
    """Test retry functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return CustomerIOClient(api_key="test_key")
    
    @patch('httpx.request')
    @patch('time.sleep')
    def test_make_request_retries_on_server_error(self, mock_sleep, mock_request, client):
        """Test that requests are retried on server errors."""
        # Mock server error on first call, success on second
        error_response = Mock()
        error_response.status_code = 500
        error_response.text = "Internal Server Error"
        error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=error_response
        )
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"status": "success"}
        success_response.raise_for_status.return_value = None
        
        mock_request.side_effect = [error_response, success_response]
        
        result = client.make_request("POST", "/identify", {"userId": "123"})
        
        assert result == {"status": "success"}
        assert mock_request.call_count == 2
        mock_sleep.assert_called_once()  # Should sleep between retries
    
    @patch('httpx.request')
    @patch('time.sleep')
    def test_make_request_max_retries_exceeded(self, mock_sleep, mock_request, client):
        """Test that max retries are respected."""
        # Mock server error for all attempts
        error_response = Mock()
        error_response.status_code = 500
        error_response.text = "Internal Server Error"
        error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=error_response
        )
        mock_request.return_value = error_response
        
        with pytest.raises(CustomerIOError, match="Request failed after"):
            client.make_request("POST", "/identify", {"userId": "123"})
        
        # Should try 3 times (initial + 2 retries)
        assert mock_request.call_count == 3


class TestAPIClientHighLevelMethods:
    """Test high-level API methods."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return CustomerIOClient(api_key="test_key")
    
    @patch.object(CustomerIOClient, 'make_request')
    def test_identify_user(self, mock_make_request, client):
        """Test identify user method."""
        mock_make_request.return_value = {"status": "success"}
        
        result = client.identify("user123", {"email": "test@example.com"})
        
        mock_make_request.assert_called_once_with(
            "POST", 
            "/identify",
            {
                "userId": "user123",
                "traits": {"email": "test@example.com"}
            }
        )
        assert result == {"status": "success"}
    
    @patch.object(CustomerIOClient, 'make_request')
    def test_track_event(self, mock_make_request, client):
        """Test track event method."""
        mock_make_request.return_value = {"status": "success"}
        
        result = client.track("user123", "purchase", {"amount": 99.99})
        
        mock_make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "purchase",
                "properties": {"amount": 99.99}
            }
        )
        assert result == {"status": "success"}
    
    @patch.object(CustomerIOClient, 'make_request')
    def test_delete_user(self, mock_make_request, client):
        """Test delete user method."""
        mock_make_request.return_value = {"status": "success"}
        
        result = client.delete("user123")
        
        mock_make_request.assert_called_once_with(
            "DELETE",
            "/identify",
            {"userId": "user123"}
        )
        assert result == {"status": "success"}