"""
Comprehensive tests for Customer.IO error handlers.

Tests cover:
- Custom exception classes and their behavior
- Error handling decorators (retry_on_error, handle_api_errors)
- ErrorContext context manager
- Circuit breaker pattern implementation
- Error analysis and utility functions
- Edge cases and error scenarios
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from utils.error_handlers import (
    # Exception Classes
    CustomerIOError,
    ValidationError,
    RateLimitError,
    NetworkError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ServerError,
    
    # Decorators
    retry_on_error,
    handle_api_errors,
    
    # Context Manager
    ErrorContext,
    
    # Utility Functions
    categorize_error,
    is_retryable_error,
    get_retry_delay,
    
    # Circuit Breaker
    CircuitBreaker
)


class TestCustomerIOError:
    """Test base CustomerIOError exception class."""
    
    def test_basic_initialization(self):
        """Test basic CustomerIOError initialization."""
        error = CustomerIOError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.response_data is None
        assert error.request_id is None
    
    def test_full_initialization(self):
        """Test CustomerIOError with all parameters."""
        response_data = {"error": "details"}
        error = CustomerIOError(
            message="API error",
            status_code=400,
            response_data=response_data,
            request_id="req_123"
        )
        
        assert error.message == "API error"
        assert error.status_code == 400
        assert error.response_data == response_data
        assert error.request_id == "req_123"
    
    def test_string_representation_with_status_code(self):
        """Test string representation includes status code."""
        error = CustomerIOError("Bad request", status_code=400)
        
        assert str(error) == "[400] Bad request"
    
    def test_string_representation_with_request_id(self):
        """Test string representation includes request ID."""
        error = CustomerIOError("API error", request_id="req_456")
        
        assert str(error) == "API error (Request ID: req_456)"
    
    def test_string_representation_full(self):
        """Test string representation with all details."""
        error = CustomerIOError(
            "Server error",
            status_code=500,
            request_id="req_789"
        )
        
        assert str(error) == "[500] Server error (Request ID: req_789)"


class TestValidationError:
    """Test ValidationError exception class."""
    
    def test_basic_validation_error(self):
        """Test basic ValidationError."""
        error = ValidationError("Invalid input")
        
        assert str(error) == "Validation error: Invalid input"
        assert error.field is None
        assert error.value is None
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field information."""
        error = ValidationError("Field is required", field="email")
        
        assert str(error) == "Validation error for field 'email': Field is required"
        assert error.field == "email"
    
    def test_validation_error_with_field_and_value(self):
        """Test ValidationError with field and value."""
        error = ValidationError("Invalid email format", field="email", value="invalid-email")
        
        assert error.field == "email"
        assert error.value == "invalid-email"


class TestRateLimitError:
    """Test RateLimitError exception class."""
    
    def test_basic_rate_limit_error(self):
        """Test basic RateLimitError."""
        error = RateLimitError()
        
        assert str(error) == "[429] Rate limit exceeded"
        assert error.status_code == 429
        assert error.retry_after is None
    
    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry after."""
        error = RateLimitError("Too many requests", retry_after=30)
        
        assert "Retry after 30 seconds" in str(error)
        assert error.retry_after == 30
    
    def test_rate_limit_error_with_limits(self):
        """Test RateLimitError with rate limit information."""
        error = RateLimitError(
            "Rate exceeded",
            current_limit=100,
            limit_window=60
        )
        
        assert "Limit: 100 requests per 60 seconds" in str(error)
        assert error.current_limit == 100
        assert error.limit_window == 60
    
    def test_rate_limit_error_full(self):
        """Test RateLimitError with all parameters."""
        error = RateLimitError(
            "Rate exceeded",
            retry_after=15,
            current_limit=100,
            limit_window=60
        )
        
        error_str = str(error)
        assert "Retry after 15 seconds" in error_str
        assert "Limit: 100 requests per 60 seconds" in error_str


class TestNetworkError:
    """Test NetworkError exception class."""
    
    def test_basic_network_error(self):
        """Test basic NetworkError."""
        error = NetworkError("Connection failed")
        
        assert str(error) == "Network error: Connection failed"
        assert error.original_error is None
        assert error.is_timeout is False
    
    def test_network_error_with_original(self):
        """Test NetworkError with original exception."""
        original = ConnectionError("Socket error")
        error = NetworkError("Connection failed", original_error=original)
        
        assert "Original: Socket error" in str(error)
        assert error.original_error == original
    
    def test_timeout_error(self):
        """Test NetworkError as timeout."""
        error = NetworkError("Request timed out", is_timeout=True)
        
        assert str(error) == "Timeout error: Request timed out"
        assert error.is_timeout is True


class TestSpecificErrors:
    """Test specific error classes."""
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError()
        
        assert error.status_code == 401
        assert str(error) == "[401] Authentication failed"
    
    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid API key")
        
        assert str(error) == "[401] Invalid API key"
    
    def test_authorization_error(self):
        """Test AuthorizationError."""
        error = AuthorizationError()
        
        assert error.status_code == 403
        assert str(error) == "[403] Access denied"
    
    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError()
        
        assert error.status_code == 404
        assert str(error) == "[404] Resource not found"
    
    def test_server_error(self):
        """Test ServerError."""
        error = ServerError()
        
        assert error.status_code == 500
        assert error.is_temporary is True
        assert str(error) == "[500] Internal server error"
    
    def test_server_error_custom(self):
        """Test ServerError with custom parameters."""
        error = ServerError("Bad Gateway", status_code=502, is_temporary=False)
        
        assert error.status_code == 502
        assert error.is_temporary is False
        assert str(error) == "[502] Bad Gateway"


class TestRetryOnErrorDecorator:
    """Test retry_on_error decorator."""
    
    @patch('utils.error_handlers.time.sleep')
    def test_retry_success_after_failure(self, mock_sleep):
        """Test successful retry after initial failure."""
        call_count = 0
        
        @retry_on_error(max_retries=2)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise NetworkError("Connection failed")
            return "success"
        
        result = failing_function()
        
        assert result == "success"
        assert call_count == 2
        mock_sleep.assert_called_once()
    
    @patch('utils.error_handlers.time.sleep')
    def test_retry_max_attempts_reached(self, mock_sleep):
        """Test retry fails after max attempts."""
        @retry_on_error(max_retries=2)
        def always_failing_function():
            raise NetworkError("Always fails")
        
        with pytest.raises(NetworkError, match="Always fails"):
            always_failing_function()
        
        assert mock_sleep.call_count == 2  # 2 retries
    
    @patch('utils.error_handlers.time.sleep')
    def test_retry_rate_limit_with_retry_after(self, mock_sleep):
        """Test retry respects rate limit retry-after."""
        @retry_on_error(max_retries=1)
        def rate_limited_function():
            raise RateLimitError("Rate limited", retry_after=5)
        
        with pytest.raises(RateLimitError):
            rate_limited_function()
        
        # Should use the retry_after value (5) instead of exponential backoff
        mock_sleep.assert_called_with(5)
    
    @patch('utils.error_handlers.time.sleep')
    def test_retry_exponential_backoff(self, mock_sleep):
        """Test exponential backoff calculation."""
        call_count = 0
        
        @retry_on_error(max_retries=3, backoff_factor=2.0)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise ServerError("Server error")
            return "success"
        
        result = failing_function()
        
        assert result == "success"
        assert mock_sleep.call_count == 3
        
        # Check exponential backoff: 2^0=1, 2^1=2, 2^2=4
        expected_calls = [((2.0 ** i,),) for i in range(3)]
        actual_calls = mock_sleep.call_args_list
        
        for i, (expected, actual) in enumerate(zip(expected_calls, actual_calls)):
            assert actual[0][0] == expected[0][0]
    
    def test_no_retry_on_non_retryable_error(self):
        """Test no retry on non-retryable errors."""
        call_count = 0
        
        @retry_on_error(max_retries=2)
        def function_with_validation_error():
            nonlocal call_count
            call_count += 1
            raise ValidationError("Invalid input")
        
        with pytest.raises(ValidationError):
            function_with_validation_error()
        
        assert call_count == 1  # Should not retry
    
    def test_retry_custom_exceptions(self):
        """Test retry with custom exception types."""
        call_count = 0
        
        @retry_on_error(max_retries=1, retry_on=(ValueError,))
        def function_with_value_error():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Custom error")
            return "success"
        
        result = function_with_value_error()
        
        assert result == "success"
        assert call_count == 2


class TestHandleApiErrorsDecorator:
    """Test handle_api_errors decorator."""
    
    def test_pass_through_customerio_error(self):
        """Test that CustomerIOError is passed through unchanged."""
        @handle_api_errors
        def function_with_customerio_error():
            raise AuthenticationError("Auth failed")
        
        with pytest.raises(AuthenticationError, match="Auth failed"):
            function_with_customerio_error()
    
    def test_timeout_error_conversion(self):
        """Test timeout error conversion."""
        @handle_api_errors
        def function_with_timeout():
            raise Exception("Request timeout occurred")
        
        with pytest.raises(NetworkError) as exc_info:
            function_with_timeout()
        
        assert exc_info.value.is_timeout is True
    
    def test_connection_error_conversion(self):
        """Test connection error conversion."""
        @handle_api_errors
        def function_with_connection_error():
            raise Exception("Connection error occurred")
        
        with pytest.raises(NetworkError) as exc_info:
            function_with_connection_error()
        
        assert exc_info.value.is_timeout is False
    
    def test_unauthorized_error_conversion(self):
        """Test unauthorized error conversion."""
        @handle_api_errors
        def function_with_auth_error():
            raise Exception("Unauthorized access")
        
        with pytest.raises(AuthenticationError):
            function_with_auth_error()
    
    def test_forbidden_error_conversion(self):
        """Test forbidden error conversion."""
        @handle_api_errors
        def function_with_forbidden_error():
            raise Exception("Forbidden request")
        
        with pytest.raises(AuthorizationError):
            function_with_forbidden_error()
    
    def test_not_found_error_conversion(self):
        """Test not found error conversion."""
        @handle_api_errors
        def function_with_not_found():
            raise Exception("Resource not found")
        
        with pytest.raises(NotFoundError):
            function_with_not_found()
    
    def test_rate_limit_error_conversion(self):
        """Test rate limit error conversion."""
        @handle_api_errors
        def function_with_rate_limit():
            raise Exception("Rate limit exceeded")
        
        with pytest.raises(RateLimitError):
            function_with_rate_limit()
    
    def test_server_error_conversion(self):
        """Test server error conversion."""
        @handle_api_errors
        def function_with_server_error():
            raise Exception("500 Internal Server Error")
        
        with pytest.raises(ServerError):
            function_with_server_error()
    
    def test_generic_error_conversion(self):
        """Test generic error conversion."""
        @handle_api_errors
        def function_with_generic_error():
            raise Exception("Unknown error")
        
        with pytest.raises(CustomerIOError):
            function_with_generic_error()


class TestErrorContext:
    """Test ErrorContext context manager."""
    
    def test_error_context_success(self):
        """Test ErrorContext with successful operation."""
        mock_logger = Mock()
        
        with ErrorContext("test_operation", logger=mock_logger) as ctx:
            result = "success"
        
        assert ctx.error is None
        mock_logger.error.assert_not_called()
    
    def test_error_context_with_error_raise(self):
        """Test ErrorContext with error and raise_on_error=True."""
        mock_logger = Mock()
        
        with pytest.raises(ValueError):
            with ErrorContext("test_operation", logger=mock_logger, raise_on_error=True):
                raise ValueError("Test error")
    
    def test_error_context_with_error_suppress(self):
        """Test ErrorContext with error and raise_on_error=False."""
        mock_logger = Mock()
        
        with ErrorContext("test_operation", logger=mock_logger, raise_on_error=False) as ctx:
            raise ValueError("Test error")
        
        assert isinstance(ctx.error, ValueError)
        mock_logger.error.assert_called_once()
    
    def test_error_context_logging(self):
        """Test ErrorContext logs error details."""
        mock_logger = Mock()
        
        with ErrorContext("api_call", logger=mock_logger, raise_on_error=False):
            raise RuntimeError("API failed")
        
        mock_logger.error.assert_called_once_with(
            "Error in api_call",
            error_type="RuntimeError",
            error_message="API failed",
            operation="api_call"
        )
    
    def test_error_context_get_result(self):
        """Test ErrorContext get_result method."""
        with ErrorContext("test", raise_on_error=False, default_return="default") as ctx:
            raise ValueError("Error")
        
        assert ctx.get_result() == "default"
    
    def test_error_context_get_result_no_error(self):
        """Test ErrorContext get_result with no error."""
        with ErrorContext("test", raise_on_error=False, default_return="default") as ctx:
            pass
        
        assert ctx.get_result() is None


class TestUtilityFunctions:
    """Test error analysis utility functions."""
    
    def test_categorize_error_validation(self):
        """Test categorizing validation error."""
        error = ValidationError("Invalid input")
        
        assert categorize_error(error) == "validation"
    
    def test_categorize_error_rate_limit(self):
        """Test categorizing rate limit error."""
        error = RateLimitError("Rate exceeded")
        
        assert categorize_error(error) == "rate_limit"
    
    def test_categorize_error_network(self):
        """Test categorizing network error."""
        error = NetworkError("Connection failed")
        
        assert categorize_error(error) == "network"
    
    def test_categorize_error_timeout(self):
        """Test categorizing timeout error."""
        error = NetworkError("Timeout", is_timeout=True)
        
        assert categorize_error(error) == "timeout"
    
    def test_categorize_error_authentication(self):
        """Test categorizing authentication error."""
        error = AuthenticationError("Auth failed")
        
        assert categorize_error(error) == "authentication"
    
    def test_categorize_error_unknown(self):
        """Test categorizing unknown error."""
        error = ValueError("Unknown error")
        
        assert categorize_error(error) == "unknown"
    
    def test_is_retryable_error_network(self):
        """Test retryable network error."""
        error = NetworkError("Connection failed")
        
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_server(self):
        """Test retryable server error."""
        error = ServerError("Internal error")
        
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_validation(self):
        """Test non-retryable validation error."""
        error = ValidationError("Invalid input")
        
        assert is_retryable_error(error) is False
    
    def test_is_retryable_error_by_status_code(self):
        """Test retryable error by status code."""
        error = CustomerIOError("Server error", status_code=503)
        
        assert is_retryable_error(error) is True
    
    def test_get_retry_delay_rate_limit(self):
        """Test retry delay for rate limit error with retry_after."""
        error = RateLimitError("Rate exceeded", retry_after=30)
        
        delay = get_retry_delay(error, attempt=0)
        
        assert delay == 30
    
    @patch('utils.error_handlers.random.random', return_value=0.5)
    def test_get_retry_delay_exponential_backoff(self, mock_random):
        """Test exponential backoff retry delay."""
        error = NetworkError("Connection failed")
        
        # First attempt (0): base_delay * (2^0) + jitter = 1 * 1 + 0.05 = 1.05
        delay = get_retry_delay(error, attempt=0, base_delay=1.0)
        expected = 1.0 + (1.0 * 0.1 * 0.5)  # 1.0 + jitter
        assert delay == expected
        
        # Second attempt (1): base_delay * (2^1) + jitter = 1 * 2 + 0.1 = 2.1
        delay = get_retry_delay(error, attempt=1, base_delay=1.0)
        expected = 2.0 + (2.0 * 0.1 * 0.5)  # 2.0 + jitter
        assert delay == expected
    
    @patch('utils.error_handlers.random.random', return_value=0.5)
    def test_get_retry_delay_max_cap(self, mock_random):
        """Test retry delay maximum cap."""
        error = NetworkError("Connection failed")
        
        # Large attempt number should be capped at 60 seconds
        delay = get_retry_delay(error, attempt=10, base_delay=1.0)
        
        assert delay <= 60


class TestCircuitBreaker:
    """Test CircuitBreaker implementation."""
    
    def test_circuit_breaker_success(self):
        """Test circuit breaker with successful calls."""
        breaker = CircuitBreaker(failure_threshold=2)
        
        @breaker
        def successful_function():
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        assert breaker.state == "closed"
        assert breaker.failure_count == 0
    
    def test_circuit_breaker_failure_threshold(self):
        """Test circuit breaker opens after failure threshold."""
        breaker = CircuitBreaker(failure_threshold=2)
        
        @breaker
        def failing_function():
            raise CustomerIOError("API error")
        
        # First failure
        with pytest.raises(CustomerIOError):
            failing_function()
        assert breaker.state == "closed"
        assert breaker.failure_count == 1
        
        # Second failure - should open circuit
        with pytest.raises(CustomerIOError):
            failing_function()
        assert breaker.state == "open"
        assert breaker.failure_count == 2
    
    def test_circuit_breaker_open_state(self):
        """Test circuit breaker blocks calls when open."""
        breaker = CircuitBreaker(failure_threshold=1)
        
        @breaker
        def failing_function():
            raise CustomerIOError("API error")
        
        # Trigger failure to open circuit
        with pytest.raises(CustomerIOError):
            failing_function()
        
        # Next call should be blocked
        with pytest.raises(CustomerIOError, match="Circuit breaker is open"):
            failing_function()
    
    @patch('utils.error_handlers.time.time')
    def test_circuit_breaker_recovery(self, mock_time):
        """Test circuit breaker recovery after timeout."""
        mock_time.side_effect = [0, 1, 61, 62]  # Simulate time progression
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        
        call_count = 0
        
        @breaker
        def sometimes_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise CustomerIOError("API error")
            return "success"
        
        # First call fails, opens circuit
        with pytest.raises(CustomerIOError, match="API error"):
            sometimes_failing_function()
        assert breaker.state == "open"
        
        # Second call blocked (circuit still open)
        with pytest.raises(CustomerIOError, match="Circuit breaker is open"):
            sometimes_failing_function()
        
        # Third call after timeout - should succeed and close circuit
        result = sometimes_failing_function()
        assert result == "success"
        assert breaker.state == "closed"
        assert breaker.failure_count == 0
    
    def test_circuit_breaker_half_open_failure(self):
        """Test circuit breaker goes back to open on half-open failure."""
        breaker = CircuitBreaker(failure_threshold=1)
        
        # Manually set to half-open state
        breaker.state = "half-open"
        breaker.failure_count = 1
        
        @breaker
        def failing_function():
            raise CustomerIOError("Still failing")
        
        with pytest.raises(CustomerIOError, match="Still failing"):
            failing_function()
        
        assert breaker.state == "open"
        assert breaker.failure_count == 2
    
    def test_circuit_breaker_custom_exception(self):
        """Test circuit breaker with custom expected exception."""
        breaker = CircuitBreaker(failure_threshold=1, expected_exception=ValueError)
        
        @breaker
        def function_with_different_error():
            raise RuntimeError("Different error")
        
        # Should not trigger circuit breaker (different exception type)
        with pytest.raises(RuntimeError):
            function_with_different_error()
        
        assert breaker.state == "closed"
        assert breaker.failure_count == 0