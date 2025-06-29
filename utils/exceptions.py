"""
Customer.IO API exceptions.
"""


class CustomerIOError(Exception):
    """Base exception for Customer.IO API errors."""
    
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(CustomerIOError):
    """Authentication failed."""
    pass


class RateLimitError(CustomerIOError):
    """Rate limit exceeded."""
    pass


class ValidationError(CustomerIOError):
    """Input validation failed."""
    pass


class NetworkError(CustomerIOError):
    """Network or connection error."""
    pass