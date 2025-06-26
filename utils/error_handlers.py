"""
Customer.IO API Error Handlers

Custom exception classes and error handling utilities for Customer.IO API interactions.
"""

from typing import Optional, Dict, Any
import time
import functools


class CustomerIOError(Exception):
    """Base exception class for Customer.IO API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.request_id = request_id
    
    def __str__(self) -> str:
        base_msg = self.message
        if self.status_code:
            base_msg = f"[{self.status_code}] {base_msg}"
        if self.request_id:
            base_msg = f"{base_msg} (Request ID: {self.request_id})"
        return base_msg


class ValidationError(CustomerIOError):
    """Exception raised for request validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        super().__init__(message)
        self.field = field
        self.value = value
    
    def __str__(self) -> str:
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class RateLimitError(CustomerIOError):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        current_limit: Optional[int] = None,
        limit_window: Optional[int] = None
    ):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
        self.current_limit = current_limit
        self.limit_window = limit_window
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.retry_after:
            base_msg = f"{base_msg} (Retry after {self.retry_after} seconds)"
        if self.current_limit and self.limit_window:
            base_msg = f"{base_msg} (Limit: {self.current_limit} requests per {self.limit_window} seconds)"
        return base_msg


class NetworkError(CustomerIOError):
    """Exception raised for network-related errors."""
    
    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        is_timeout: bool = False
    ):
        super().__init__(message)
        self.original_error = original_error
        self.is_timeout = is_timeout
    
    def __str__(self) -> str:
        base_msg = f"Network error: {self.message}"
        if self.is_timeout:
            base_msg = f"Timeout error: {self.message}"
        if self.original_error:
            base_msg = f"{base_msg} (Original: {str(self.original_error)})"
        return base_msg


class AuthenticationError(CustomerIOError):
    """Exception raised for authentication-related errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(CustomerIOError):
    """Exception raised for authorization-related errors."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403)


class NotFoundError(CustomerIOError):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ServerError(CustomerIOError):
    """Exception raised for server-side errors (5xx)."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        status_code: int = 500,
        is_temporary: bool = True
    ):
        super().__init__(message, status_code=status_code)
        self.is_temporary = is_temporary


# Error Handler Decorators

def retry_on_error(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    retry_on: tuple = (NetworkError, ServerError, RateLimitError)
):
    """
    Decorator to retry function calls on specific errors.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        retry_on: Tuple of exception types to retry on
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Calculate wait time with exponential backoff
                        wait_time = min(60, backoff_factor ** attempt)
                        
                        # Special handling for rate limit errors
                        if isinstance(e, RateLimitError) and e.retry_after:
                            wait_time = min(wait_time, e.retry_after)
                        
                        time.sleep(wait_time)
                        continue
                    else:
                        # Max retries reached, raise the last exception
                        raise e
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def handle_api_errors(func):
    """
    Decorator to handle and translate API errors into appropriate exceptions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # If it's already a CustomerIOError, re-raise it
            if isinstance(e, CustomerIOError):
                raise e
            
            # Handle specific error patterns
            error_message = str(e).lower()
            
            if "timeout" in error_message:
                raise NetworkError(str(e), original_error=e, is_timeout=True)
            elif "connection" in error_message or "network" in error_message:
                raise NetworkError(str(e), original_error=e)
            elif "unauthorized" in error_message or "401" in error_message:
                raise AuthenticationError(str(e))
            elif "forbidden" in error_message or "403" in error_message:
                raise AuthorizationError(str(e))
            elif "not found" in error_message or "404" in error_message:
                raise NotFoundError(str(e))
            elif "rate limit" in error_message or "429" in error_message:
                raise RateLimitError(str(e))
            elif any(code in error_message for code in ["500", "502", "503", "504"]):
                raise ServerError(str(e))
            else:
                # Generic Customer.IO error for unknown errors
                raise CustomerIOError(str(e), original_error=e)
    
    return wrapper


# Error Context Manager

class ErrorContext:
    """Context manager for handling and logging errors in Customer.IO operations."""
    
    def __init__(
        self,
        operation_name: str,
        logger=None,
        raise_on_error: bool = True,
        default_return=None
    ):
        self.operation_name = operation_name
        self.logger = logger
        self.raise_on_error = raise_on_error
        self.default_return = default_return
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            
            # Log the error if logger is available
            if self.logger:
                self.logger.error(
                    f"Error in {self.operation_name}",
                    error_type=exc_type.__name__,
                    error_message=str(exc_val),
                    operation=self.operation_name
                )
            
            # Suppress the exception if configured to do so
            if not self.raise_on_error:
                return True  # Suppress the exception
        
        return False  # Don't suppress the exception
    
    def get_result(self):
        """Get the default return value if an error occurred."""
        if self.error and not self.raise_on_error:
            return self.default_return
        return None


# Error Analysis Utilities

def categorize_error(error: Exception) -> str:
    """
    Categorize an error for monitoring and analysis purposes.
    
    Args:
        error: Exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(error, ValidationError):
        return "validation"
    elif isinstance(error, RateLimitError):
        return "rate_limit"
    elif isinstance(error, NetworkError):
        if error.is_timeout:
            return "timeout"
        return "network"
    elif isinstance(error, AuthenticationError):
        return "authentication"
    elif isinstance(error, AuthorizationError):
        return "authorization"
    elif isinstance(error, NotFoundError):
        return "not_found"
    elif isinstance(error, ServerError):
        return "server_error"
    elif isinstance(error, CustomerIOError):
        return "api_error"
    else:
        return "unknown"


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable.
    
    Args:
        error: Exception to check
        
    Returns:
        True if the error is retryable, False otherwise
    """
    if isinstance(error, (NetworkError, ServerError, RateLimitError)):
        return True
    
    # Check for specific server errors that might be temporary
    if isinstance(error, CustomerIOError):
        if error.status_code in [500, 502, 503, 504, 429]:
            return True
    
    return False


def get_retry_delay(error: Exception, attempt: int, base_delay: float = 1.0) -> float:
    """
    Calculate appropriate retry delay based on error type and attempt number.
    
    Args:
        error: Exception that occurred
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        
    Returns:
        Delay in seconds before next retry
    """
    if isinstance(error, RateLimitError) and error.retry_after:
        return error.retry_after
    
    # Exponential backoff with jitter
    import random
    delay = base_delay * (2 ** attempt)
    jitter = delay * 0.1 * random.random()  # Add up to 10% jitter
    
    return min(60, delay + jitter)  # Cap at 60 seconds


# Error Recovery Utilities

class CircuitBreaker:
    """
    Circuit breaker pattern implementation for Customer.IO API calls.
    Prevents cascading failures by temporarily disabling calls when
    error rate is too high.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = CustomerIOError
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "open":
                if self._should_attempt_reset():
                    self.state = "half-open"
                else:
                    raise CustomerIOError("Circuit breaker is open")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt a reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.state = "closed"
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"