"""
Comprehensive tests for Customer.IO API client

Tests cover:
- RateLimit class functionality
- CustomerIOClient initialization and configuration
- HTTP request handling with retries and error handling
- All public API methods (identify, track, group, page, screen, batch)
- Rate limiting behavior
- Request logging
- Context manager support
"""

import pytest
import time
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
import httpx

from utils.api_client import RateLimit, CustomerIOClient
from utils.error_handlers import (
    CustomerIOError,
    RateLimitError,
    ValidationError as CIOValidationError,
    NetworkError
)


class TestRateLimit:
    """Test RateLimit class functionality."""
    
    def test_rate_limit_initialization(self):
        """Test RateLimit class initializes with correct defaults."""
        rate_limit = RateLimit()
        
        assert rate_limit.max_requests == 3000
        assert rate_limit.window_seconds == 3
        assert rate_limit.current_requests == 0
        assert rate_limit.window_start == 0.0
    
    def test_rate_limit_custom_values(self):
        """Test RateLimit with custom values."""
        rate_limit = RateLimit(max_requests=100, window_seconds=10)
        
        assert rate_limit.max_requests == 100
        assert rate_limit.window_seconds == 10
    
    def test_can_make_request_when_under_limit(self):
        """Test can_make_request returns True when under limit."""
        rate_limit = RateLimit(max_requests=10, window_seconds=60)
        rate_limit.current_requests = 5
        rate_limit.window_start = time.time()
        
        assert rate_limit.can_make_request() is True
    
    def test_can_make_request_when_at_limit(self):
        """Test can_make_request returns False when at limit."""
        rate_limit = RateLimit(max_requests=10, window_seconds=60)
        rate_limit.current_requests = 10
        rate_limit.window_start = time.time()
        
        assert rate_limit.can_make_request() is False
    
    def test_can_make_request_when_over_limit(self):
        """Test can_make_request returns False when over limit."""
        rate_limit = RateLimit(max_requests=10, window_seconds=60)
        rate_limit.current_requests = 15
        rate_limit.window_start = time.time()
        
        assert rate_limit.can_make_request() is False
    
    def test_record_request_increments_counter(self):
        """Test record_request increments the counter."""
        rate_limit = RateLimit()
        rate_limit.window_start = time.time()
        initial_count = rate_limit.current_requests
        
        rate_limit.record_request()
        
        assert rate_limit.current_requests == initial_count + 1
    
    def test_reset_if_needed_resets_old_window(self):
        """Test reset_if_needed resets when window has expired."""
        rate_limit = RateLimit(window_seconds=1)
        rate_limit.current_requests = 100
        rate_limit.window_start = time.time() - 2  # 2 seconds ago
        
        rate_limit.reset_if_needed()
        
        assert rate_limit.current_requests == 0
        assert rate_limit.window_start > time.time() - 1
    
    def test_reset_if_needed_preserves_current_window(self):
        """Test reset_if_needed preserves current window."""
        rate_limit = RateLimit(window_seconds=60)
        initial_count = 50
        rate_limit.current_requests = initial_count
        rate_limit.window_start = time.time()
        
        rate_limit.reset_if_needed()
        
        assert rate_limit.current_requests == initial_count
    
    def test_time_until_reset_returns_correct_time(self):
        """Test time_until_reset returns correct remaining time."""
        rate_limit = RateLimit(window_seconds=10)
        rate_limit.window_start = time.time() - 3  # 3 seconds ago
        
        remaining = rate_limit.time_until_reset()
        
        assert 6 <= remaining <= 8  # Should be around 7 seconds
    
    def test_time_until_reset_returns_zero_for_expired_window(self):
        """Test time_until_reset returns 0 for expired window."""
        rate_limit = RateLimit(window_seconds=5)
        rate_limit.window_start = time.time() - 10  # 10 seconds ago
        
        remaining = rate_limit.time_until_reset()
        
        assert remaining == 0


class TestCustomerIOClientInitialization:
    """Test CustomerIOClient initialization and configuration."""
    
    def test_client_initialization_with_defaults(self, mock_spark_session):
        """Test client initializes with default values."""
        client = CustomerIOClient(
            api_key="test_key",
            spark_session=mock_spark_session
        )
        
        assert client.api_key == "test_key"
        assert client.region == "us"
        assert client.base_url == "https://cdp.customer.io/v1"
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.retry_backoff_factor == 2.0
        assert client.enable_logging is True
        assert isinstance(client.rate_limit, RateLimit)
    
    def test_client_initialization_with_custom_values(self, mock_spark_session):
        """Test client initializes with custom values."""
        client = CustomerIOClient(
            api_key="custom_key",
            region="EU",
            timeout=60,
            max_retries=5,
            retry_backoff_factor=1.5,
            enable_logging=False,
            spark_session=mock_spark_session
        )
        
        assert client.api_key == "custom_key"
        assert client.region == "eu"  # Should be lowercased
        assert client.base_url == "https://cdp-eu.customer.io/v1"
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.retry_backoff_factor == 1.5
        assert client.enable_logging is False
    
    def test_client_sets_correct_us_url(self, mock_spark_session):
        """Test client sets correct US URL."""
        client = CustomerIOClient(
            api_key="test_key",
            region="us",
            spark_session=mock_spark_session
        )
        
        assert client.base_url == "https://cdp.customer.io/v1"
    
    def test_client_sets_correct_eu_url(self, mock_spark_session):
        """Test client sets correct EU URL."""
        client = CustomerIOClient(
            api_key="test_key",
            region="eu",
            spark_session=mock_spark_session
        )
        
        assert client.base_url == "https://cdp-eu.customer.io/v1"
    
    def test_client_headers_include_auth(self, mock_spark_session):
        """Test client headers include proper authentication."""
        client = CustomerIOClient(
            api_key="test_key_123",
            spark_session=mock_spark_session
        )
        
        assert "Authorization" in client.headers
        assert client.headers["Authorization"].startswith("Basic ")
        assert client.headers["Content-Type"] == "application/json"
        assert client.headers["User-Agent"] == "CustomerIO-Databricks-Client/1.0.0"
        assert client.headers["Accept"] == "application/json"
    
    @patch('utils.api_client.httpx.Client')
    def test_http_client_initialization(self, mock_httpx_client, mock_spark_session):
        """Test HTTP client is properly initialized."""
        client = CustomerIOClient(
            api_key="test_key",
            timeout=45,
            spark_session=mock_spark_session
        )
        
        mock_httpx_client.assert_called_once_with(
            timeout=45,
            headers=client.headers,
            follow_redirects=True
        )


class TestCustomerIOClientRequestHandling:
    """Test HTTP request handling, retries, and error handling."""
    
    @pytest.fixture
    def client(self, mock_spark_session):
        """Create a test client."""
        return CustomerIOClient(
            api_key="test_key",
            spark_session=mock_spark_session
        )
    
    @patch('utils.api_client.time.sleep')  # Mock sleep to speed up tests
    def test_make_request_success(self, mock_sleep, client, mock_httpx_client):
        """Test successful request handling."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.content = b'{"status": "success"}'
        
        client.client = mock_httpx_client
        mock_httpx_client.request.return_value = mock_response
        
        result = client._make_request("POST", "/test", {"data": "test"})
        
        assert result == {"status": "success"}
        mock_httpx_client.request.assert_called_once()
    
    @patch('utils.api_client.time.sleep')
    def test_make_request_handles_rate_limit_with_retry(self, mock_sleep, client, mock_httpx_client):
        """Test request handling with rate limit and retry."""
        # First call returns 429, second call succeeds
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.text = "Rate limited"
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"status": "success"}
        success_response.content = b'{"status": "success"}'
        
        client.client = mock_httpx_client
        mock_httpx_client.request.side_effect = [rate_limit_response, success_response]
        
        result = client._make_request("POST", "/test", {"data": "test"})
        
        assert result == {"status": "success"}
        assert mock_httpx_client.request.call_count == 2
        mock_sleep.assert_called_once()
    
    @patch('utils.api_client.time.sleep')
    def test_make_request_raises_rate_limit_error_after_max_retries(self, mock_sleep, client, mock_httpx_client):
        """Test rate limit error raised after max retries."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limited"
        
        client.client = mock_httpx_client
        mock_httpx_client.request.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            client._make_request("POST", "/test", {"data": "test"})
    
    def test_make_request_raises_validation_error_for_large_request(self, client):
        """Test validation error for requests exceeding size limit."""
        large_data = {"data": "x" * (33 * 1024)}  # Exceeds 32KB limit
        
        with pytest.raises(CIOValidationError, match="Request size .* exceeds 32KB limit"):
            client._make_request("POST", "/test", large_data)
    
    def test_make_request_handles_client_error(self, client, mock_httpx_client):
        """Test handling of 4xx client errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.content = b"Bad request"
        
        client.client = mock_httpx_client
        mock_httpx_client.request.return_value = mock_response
        
        with pytest.raises(CustomerIOError, match="Client error 400"):
            client._make_request("POST", "/test", {"data": "test"})
    
    @patch('utils.api_client.time.sleep')
    def test_make_request_handles_server_error_with_retry(self, mock_sleep, client, mock_httpx_client):
        """Test handling of 5xx server errors with retry."""
        server_error_response = Mock()
        server_error_response.status_code = 500
        server_error_response.text = "Internal server error"
        server_error_response.content = b"Internal server error"
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"status": "success"}
        success_response.content = b'{"status": "success"}'
        
        client.client = mock_httpx_client
        mock_httpx_client.request.side_effect = [server_error_response, success_response]
        
        result = client._make_request("POST", "/test", {"data": "test"})
        
        assert result == {"status": "success"}
        mock_sleep.assert_called_once()
    
    @patch('utils.api_client.time.sleep')
    def test_make_request_handles_network_timeout(self, mock_sleep, client, mock_httpx_client):
        """Test handling of network timeout."""
        client.client = mock_httpx_client
        mock_httpx_client.request.side_effect = httpx.TimeoutException("Request timeout")
        
        with pytest.raises(NetworkError, match="Request timeout"):
            client._make_request("POST", "/test", {"data": "test"})
    
    @patch('utils.api_client.time.sleep')
    def test_make_request_handles_network_error(self, mock_sleep, client, mock_httpx_client):
        """Test handling of network connectivity error."""
        client.client = mock_httpx_client
        mock_httpx_client.request.side_effect = httpx.NetworkError("Network error")
        
        with pytest.raises(NetworkError, match="Network error"):
            client._make_request("POST", "/test", {"data": "test"})


class TestCustomerIOClientPublicMethods:
    """Test public API methods."""
    
    @pytest.fixture
    def client(self, mock_spark_session):
        """Create a test client with mocked _make_request."""
        client = CustomerIOClient(api_key="test_key", spark_session=mock_spark_session)
        client._make_request = Mock(return_value={"status": "success"})
        return client
    
    def test_identify_with_user_id(self, client):
        """Test identify method with user_id."""
        result = client.identify(
            user_id="user_123",
            traits={"email": "test@example.com", "name": "Test User"}
        )
        
        assert result == {"status": "success"}
        client._make_request.assert_called_once_with(
            "POST",
            "/identify",
            {
                "userId": "user_123",
                "traits": {"email": "test@example.com", "name": "Test User"}
            },
            customer_id="user_123"
        )
    
    def test_identify_with_anonymous_id(self, client):
        """Test identify method with anonymous_id."""
        result = client.identify(
            anonymous_id="anon_123",
            traits={"email": "test@example.com"}
        )
        
        assert result == {"status": "success"}
        client._make_request.assert_called_once_with(
            "POST",
            "/identify",
            {
                "anonymousId": "anon_123",
                "traits": {"email": "test@example.com"}
            },
            customer_id=None
        )
    
    def test_identify_with_timestamp(self, client):
        """Test identify method includes timestamp when provided."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        client.identify(
            user_id="user_123",
            traits={"email": "test@example.com"},
            timestamp=timestamp
        )
        
        expected_data = {
            "userId": "user_123",
            "traits": {"email": "test@example.com"},
            "timestamp": "2024-01-15T12:30:00+00:00"
        }
        client._make_request.assert_called_once_with(
            "POST", "/identify", expected_data, customer_id="user_123"
        )
    
    def test_identify_requires_user_identification(self, client):
        """Test identify raises error when no user identification provided."""
        with pytest.raises(CIOValidationError, match="Either user_id or anonymous_id must be provided"):
            client.identify(traits={"email": "test@example.com"})
    
    def test_track_with_required_params(self, client):
        """Test track method with required parameters."""
        result = client.track(
            user_id="user_123",
            event="Product Viewed",
            properties={"product_id": "prod_123"}
        )
        
        assert result == {"status": "success"}
        client._make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "event": "Product Viewed",
                "userId": "user_123",
                "properties": {"product_id": "prod_123"}
            },
            customer_id="user_123"
        )
    
    def test_track_requires_user_identification(self, client):
        """Test track raises error when no user identification provided."""
        with pytest.raises(CIOValidationError, match="Either user_id or anonymous_id must be provided"):
            client.track(event="Test Event")
    
    def test_track_requires_event_name(self, client):
        """Test track raises error when no event name provided."""
        with pytest.raises(CIOValidationError, match="Event name is required"):
            client.track(user_id="user_123", event="")
    
    def test_group_with_required_params(self, client):
        """Test group method with required parameters."""
        result = client.group(
            user_id="user_123",
            group_id="company_456",
            traits={"name": "Acme Corp"}
        )
        
        assert result == {"status": "success"}
        client._make_request.assert_called_once_with(
            "POST",
            "/group",
            {
                "groupId": "company_456",
                "userId": "user_123",
                "traits": {"name": "Acme Corp"}
            },
            customer_id="user_123"
        )
    
    def test_group_requires_user_identification(self, client):
        """Test group raises error when no user identification provided."""
        with pytest.raises(CIOValidationError, match="Either user_id or anonymous_id must be provided"):
            client.group(group_id="company_456")
    
    def test_group_requires_group_id(self, client):
        """Test group raises error when no group ID provided."""
        with pytest.raises(CIOValidationError, match="Group ID is required"):
            client.group(user_id="user_123", group_id="")
    
    def test_page_with_params(self, client):
        """Test page method with parameters."""
        result = client.page(
            user_id="user_123",
            name="Home Page",
            properties={"url": "https://example.com"}
        )
        
        assert result == {"status": "success"}
        client._make_request.assert_called_once_with(
            "POST",
            "/page",
            {
                "userId": "user_123",
                "name": "Home Page",
                "properties": {"url": "https://example.com"}
            },
            customer_id="user_123"
        )
    
    def test_screen_with_params(self, client):
        """Test screen method with parameters."""
        result = client.screen(
            user_id="user_123",
            name="Product Details",
            properties={"product_id": "prod_123"}
        )
        
        assert result == {"status": "success"}
        client._make_request.assert_called_once_with(
            "POST",
            "/screen",
            {
                "userId": "user_123",
                "name": "Product Details",
                "properties": {"product_id": "prod_123"}
            },
            customer_id="user_123"
        )
    
    def test_batch_with_requests(self, client):
        """Test batch method with request list."""
        requests = [
            {"type": "identify", "userId": "user_1", "traits": {"email": "user1@example.com"}},
            {"type": "track", "userId": "user_2", "event": "Product Viewed"}
        ]
        
        result = client.batch(requests)
        
        assert result == {"status": "success"}
        client._make_request.assert_called_once_with(
            "POST",
            "/batch",
            {"batch": requests}
        )
    
    def test_batch_requires_non_empty_requests(self, client):
        """Test batch raises error for empty request list."""
        with pytest.raises(CIOValidationError, match="Batch requests cannot be empty"):
            client.batch([])
    
    @patch('utils.api_client.json.dumps')
    def test_batch_validates_size_limit(self, mock_json_dumps, client):
        """Test batch validates 500KB size limit."""
        # Mock json.dumps to return a large string
        mock_json_dumps.return_value = "x" * (501 * 1024)  # 501KB
        
        requests = [{"type": "identify", "userId": "user_1"}]
        
        with pytest.raises(CIOValidationError, match="Batch size exceeds 500KB limit"):
            client.batch(requests)
    
    def test_get_region(self, client):
        """Test get_region method."""
        result = client.get_region()
        
        assert result == {"status": "success"}
        client._make_request.assert_called_once_with("GET", "/region")
    
    def test_health_check_success(self, client):
        """Test health_check returns True when region call succeeds."""
        result = client.health_check()
        
        assert result is True
        client._make_request.assert_called_once_with("GET", "/region")
    
    def test_health_check_failure(self, client):
        """Test health_check returns False when region call fails."""
        client._make_request.side_effect = CustomerIOError("API error")
        
        result = client.health_check()
        
        assert result is False


class TestCustomerIOClientContextManager:
    """Test context manager functionality."""
    
    def test_context_manager_entry(self, mock_spark_session):
        """Test context manager __enter__ method."""
        client = CustomerIOClient(api_key="test_key", spark_session=mock_spark_session)
        
        with client as ctx_client:
            assert ctx_client is client
    
    def test_context_manager_exit_calls_close(self, mock_spark_session):
        """Test context manager __exit__ calls close method."""
        client = CustomerIOClient(api_key="test_key", spark_session=mock_spark_session)
        client.close = Mock()
        
        with client:
            pass
        
        client.close.assert_called_once()


class TestCustomerIOClientRateLimiting:
    """Test rate limiting integration."""
    
    @pytest.fixture
    def client(self, mock_spark_session):
        """Create client with fast rate limiting for testing."""
        client = CustomerIOClient(
            api_key="test_key",
            spark_session=mock_spark_session
        )
        # Set fast rate limiting for testing
        client.rate_limit = RateLimit(max_requests=2, window_seconds=1)
        return client
    
    @patch('utils.api_client.time.sleep')
    def test_rate_limiting_waits_when_limit_reached(self, mock_sleep, client, mock_httpx_client):
        """Test that client waits when rate limit is reached."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.content = b'{"status": "success"}'
        
        client.client = mock_httpx_client
        mock_httpx_client.request.return_value = mock_response
        
        # Fill up the rate limit
        client.rate_limit.current_requests = 2
        client.rate_limit.window_start = time.time()
        
        # This should trigger rate limiting wait
        client._make_request("POST", "/test", {"data": "test"})
        
        # Should have slept to wait for rate limit reset
        mock_sleep.assert_called_once()


class TestCustomerIOClientLogging:
    """Test request logging functionality."""
    
    @pytest.fixture
    def client_with_logging(self, mock_spark_session):
        """Create client with logging enabled."""
        return CustomerIOClient(
            api_key="test_key",
            enable_logging=True,
            spark_session=mock_spark_session
        )
    
    @pytest.fixture
    def client_without_logging(self, mock_spark_session):
        """Create client with logging disabled."""
        return CustomerIOClient(
            api_key="test_key",
            enable_logging=False,
            spark_session=mock_spark_session
        )
    
    def test_logging_disabled_client_does_not_log(self, client_without_logging):
        """Test that client with logging disabled doesn't attempt to log."""
        # This should not raise any errors or attempt to access Spark
        client_without_logging._log_request(
            endpoint="/test",
            method="POST",
            status_code=200,
            response_time_ms=100,
            request_size=50,
            response_size=25
        )
        # If we get here without errors, logging was properly skipped
    
    def test_logging_enabled_client_creates_dataframe(self, client_with_logging, mock_spark_session):
        """Test that client with logging enabled creates DataFrame."""
        mock_df = Mock()
        mock_spark_session.createDataFrame.return_value = mock_df
        
        client_with_logging._log_request(
            endpoint="/test",
            method="POST",
            status_code=200,
            response_time_ms=100,
            request_size=50,
            response_size=25,
            customer_id="user_123"
        )
        
        # Verify DataFrame creation and write
        mock_spark_session.createDataFrame.assert_called_once()
        mock_df.write.format.assert_called_once_with("delta")
        mock_df.write.format.return_value.mode.assert_called_once_with("append")
        mock_df.write.format.return_value.mode.return_value.saveAsTable.assert_called_once_with("api_responses")
    
    def test_logging_handles_spark_errors_gracefully(self, client_with_logging, mock_spark_session):
        """Test that logging errors don't break the client."""
        mock_spark_session.createDataFrame.side_effect = Exception("Spark error")
        
        # This should not raise an exception
        client_with_logging._log_request(
            endpoint="/test",
            method="POST",
            status_code=200,
            response_time_ms=100,
            request_size=50,
            response_size=25
        )