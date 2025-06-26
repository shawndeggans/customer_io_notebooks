"""
Customer.IO Data Pipelines API Client

A production-ready API client for Customer.IO's Data Pipelines API with
rate limiting, retry logic, error handling, and Databricks integration.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import uuid
from dataclasses import dataclass
import base64

import httpx
import structlog
from pydantic import BaseModel, ValidationError

from .error_handlers import (
    CustomerIOError,
    RateLimitError,
    ValidationError as CIOValidationError,
    NetworkError
)


@dataclass
class RateLimit:
    """Rate limiting configuration and state."""
    max_requests: int = 3000
    window_seconds: int = 3
    current_requests: int = 0
    window_start: float = 0.0
    
    def reset_if_needed(self) -> None:
        """Reset rate limit window if time has passed."""
        current_time = time.time()
        if current_time - self.window_start >= self.window_seconds:
            self.current_requests = 0
            self.window_start = current_time
    
    def can_make_request(self) -> bool:
        """Check if a request can be made within rate limits."""
        self.reset_if_needed()
        return self.current_requests < self.max_requests
    
    def record_request(self) -> None:
        """Record that a request was made."""
        self.reset_if_needed()
        self.current_requests += 1
    
    def time_until_reset(self) -> float:
        """Time in seconds until rate limit window resets."""
        elapsed = time.time() - self.window_start
        return max(0, self.window_seconds - elapsed)


class CustomerIOClient:
    """
    Customer.IO Data Pipelines API client for Databricks.
    
    Features:
    - Automatic retry logic with exponential backoff
    - Rate limiting (3000 requests per 3 seconds)
    - Request/response logging to Delta tables
    - Support for both US and EU regions
    - Batch request optimization
    - Error handling and recovery
    """
    
    def __init__(
        self,
        api_key: str,
        region: str = "us",
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 2.0,
        enable_logging: bool = True,
        spark_session = None
    ):
        """
        Initialize Customer.IO API client.
        
        Args:
            api_key: Customer.IO API key
            region: API region ('us' or 'eu')
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_backoff_factor: Backoff multiplier for retries
            enable_logging: Whether to log requests to Delta tables
            spark_session: Spark session for Delta table logging
        """
        self.api_key = api_key
        self.region = region.lower()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.enable_logging = enable_logging
        self.spark = spark_session
        
        # Set base URL based on region
        if self.region == "eu":
            self.base_url = "https://cdp-eu.customer.io/v1"
        else:
            self.base_url = "https://cdp.customer.io/v1"
        
        # Initialize rate limiting
        self.rate_limit = RateLimit()
        
        # Initialize logger
        self.logger = structlog.get_logger("customerio_client")
        
        # Initialize HTTP client
        self._init_http_client()
    
    def _init_http_client(self) -> None:
        """Initialize the HTTP client with proper authentication and headers."""
        # Encode API key for basic auth (API key is username, password is empty)
        auth_string = base64.b64encode(f"{self.api_key}:".encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json",
            "User-Agent": "CustomerIO-Databricks-Client/1.0.0",
            "Accept": "application/json"
        }
        
        self.client = httpx.Client(
            timeout=self.timeout,
            headers=self.headers,
            follow_redirects=True
        )
    
    def _wait_for_rate_limit(self) -> None:
        """Wait if rate limit would be exceeded."""
        if not self.rate_limit.can_make_request():
            wait_time = self.rate_limit.time_until_reset()
            if wait_time > 0:
                self.logger.warning(
                    "Rate limit reached, waiting",
                    wait_time=wait_time,
                    current_requests=self.rate_limit.current_requests,
                    max_requests=self.rate_limit.max_requests
                )
                time.sleep(wait_time + 0.1)  # Small buffer
    
    def _log_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        request_size: int,
        response_size: int,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        customer_id: Optional[str] = None
    ) -> None:
        """Log API request details to Delta table if enabled."""
        if not self.enable_logging or not self.spark:
            return
        
        try:
            log_record = {
                "request_id": str(uuid.uuid4()),
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "request_size_bytes": request_size,
                "response_size_bytes": response_size,
                "timestamp": datetime.now(timezone.utc),
                "error_message": error_message,
                "retry_count": retry_count,
                "customer_id": customer_id
            }
            
            # Create DataFrame and append to api_responses table
            df = self.spark.createDataFrame([log_record])
            df.write.format("delta").mode("append").saveAsTable("api_responses")
            
        except Exception as e:
            self.logger.warning("Failed to log request", error=str(e))
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with rate limiting, retries, and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: URL parameters
            customer_id: Customer ID for logging
            
        Returns:
            Response data as dictionary
            
        Raises:
            CustomerIOError: For API errors
            RateLimitError: For rate limiting issues
            NetworkError: For network connectivity issues
            ValidationError: For request validation errors
        """
        url = f"{self.base_url}{endpoint}"
        request_data = json.dumps(data) if data else None
        request_size = len(request_data.encode()) if request_data else 0
        
        # Check request size limits
        if request_size > 32 * 1024:  # 32KB limit
            raise CIOValidationError(f"Request size {request_size} exceeds 32KB limit")
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Wait for rate limit if needed
                self._wait_for_rate_limit()
                
                # Record the request for rate limiting
                self.rate_limit.record_request()
                
                # Make the request
                start_time = time.time()
                
                response = self.client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                )
                
                response_time_ms = int((time.time() - start_time) * 1000)
                response_size = len(response.content)
                
                # Log successful request
                self._log_request(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    request_size=request_size,
                    response_size=response_size,
                    retry_count=attempt,
                    customer_id=customer_id
                )
                
                # Handle response
                if response.status_code == 200:
                    try:
                        return response.json() if response.content else {}
                    except json.JSONDecodeError:
                        return {"status": "success", "raw_response": response.text}
                
                elif response.status_code == 429:  # Rate limited
                    if attempt < self.max_retries:
                        wait_time = min(60, self.retry_backoff_factor ** attempt)
                        self.logger.warning(
                            "Rate limited, retrying",
                            attempt=attempt + 1,
                            wait_time=wait_time
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded, max retries reached")
                
                elif 400 <= response.status_code < 500:  # Client error
                    error_msg = f"Client error {response.status_code}: {response.text}"
                    self._log_request(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status_code,
                        response_time_ms=response_time_ms,
                        request_size=request_size,
                        response_size=response_size,
                        error_message=error_msg,
                        retry_count=attempt,
                        customer_id=customer_id
                    )
                    raise CustomerIOError(error_msg)
                
                elif 500 <= response.status_code < 600:  # Server error
                    if attempt < self.max_retries:
                        wait_time = min(60, self.retry_backoff_factor ** attempt)
                        self.logger.warning(
                            "Server error, retrying",
                            status_code=response.status_code,
                            attempt=attempt + 1,
                            wait_time=wait_time
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        error_msg = f"Server error {response.status_code}: {response.text}"
                        self._log_request(
                            endpoint=endpoint,
                            method=method,
                            status_code=response.status_code,
                            response_time_ms=response_time_ms,
                            request_size=request_size,
                            response_size=response_size,
                            error_message=error_msg,
                            retry_count=attempt,
                            customer_id=customer_id
                        )
                        raise CustomerIOError(error_msg)
                
            except httpx.TimeoutException as e:
                last_exception = NetworkError(f"Request timeout: {str(e)}")
                if attempt < self.max_retries:
                    wait_time = min(60, self.retry_backoff_factor ** attempt)
                    self.logger.warning(
                        "Request timeout, retrying",
                        attempt=attempt + 1,
                        wait_time=wait_time
                    )
                    time.sleep(wait_time)
                    continue
            
            except httpx.NetworkError as e:
                last_exception = NetworkError(f"Network error: {str(e)}")
                if attempt < self.max_retries:
                    wait_time = min(60, self.retry_backoff_factor ** attempt)
                    self.logger.warning(
                        "Network error, retrying",
                        attempt=attempt + 1,
                        wait_time=wait_time
                    )
                    time.sleep(wait_time)
                    continue
            
            except Exception as e:
                last_exception = CustomerIOError(f"Unexpected error: {str(e)}")
                break
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise CustomerIOError("Request failed after all retries")
    
    # Public API methods
    
    def identify(
        self,
        user_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        traits: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Identify a user in Customer.IO.
        
        Args:
            user_id: Unique user identifier
            anonymous_id: Anonymous user identifier
            traits: User traits/attributes
            timestamp: Event timestamp (defaults to now)
            context: Additional context data
            
        Returns:
            API response
        """
        if not user_id and not anonymous_id:
            raise CIOValidationError("Either user_id or anonymous_id must be provided")
        
        data = {}
        if user_id:
            data["userId"] = user_id
        if anonymous_id:
            data["anonymousId"] = anonymous_id
        if traits:
            data["traits"] = traits
        if timestamp:
            data["timestamp"] = timestamp.isoformat()
        if context:
            data["context"] = context
        
        return self._make_request("POST", "/identify", data, customer_id=user_id)
    
    def track(
        self,
        user_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        event: str = "",
        properties: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track an event for a user.
        
        Args:
            user_id: Unique user identifier
            anonymous_id: Anonymous user identifier
            event: Event name
            properties: Event properties
            timestamp: Event timestamp (defaults to now)
            context: Additional context data
            
        Returns:
            API response
        """
        if not user_id and not anonymous_id:
            raise CIOValidationError("Either user_id or anonymous_id must be provided")
        if not event:
            raise CIOValidationError("Event name is required")
        
        data = {"event": event}
        if user_id:
            data["userId"] = user_id
        if anonymous_id:
            data["anonymousId"] = anonymous_id
        if properties:
            data["properties"] = properties
        if timestamp:
            data["timestamp"] = timestamp.isoformat()
        if context:
            data["context"] = context
        
        return self._make_request("POST", "/track", data, customer_id=user_id)
    
    def group(
        self,
        user_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        group_id: str = "",
        traits: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Associate a user with a group (company/organization).
        
        Args:
            user_id: Unique user identifier
            anonymous_id: Anonymous user identifier
            group_id: Group/company identifier
            traits: Group traits/attributes
            timestamp: Event timestamp (defaults to now)
            context: Additional context data
            
        Returns:
            API response
        """
        if not user_id and not anonymous_id:
            raise CIOValidationError("Either user_id or anonymous_id must be provided")
        if not group_id:
            raise CIOValidationError("Group ID is required")
        
        data = {"groupId": group_id}
        if user_id:
            data["userId"] = user_id
        if anonymous_id:
            data["anonymousId"] = anonymous_id
        if traits:
            data["traits"] = traits
        if timestamp:
            data["timestamp"] = timestamp.isoformat()
        if context:
            data["context"] = context
        
        return self._make_request("POST", "/group", data, customer_id=user_id)
    
    def page(
        self,
        user_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a page view.
        
        Args:
            user_id: Unique user identifier
            anonymous_id: Anonymous user identifier
            name: Page name
            properties: Page properties
            timestamp: Event timestamp (defaults to now)
            context: Additional context data
            
        Returns:
            API response
        """
        if not user_id and not anonymous_id:
            raise CIOValidationError("Either user_id or anonymous_id must be provided")
        
        data = {}
        if user_id:
            data["userId"] = user_id
        if anonymous_id:
            data["anonymousId"] = anonymous_id
        if name:
            data["name"] = name
        if properties:
            data["properties"] = properties
        if timestamp:
            data["timestamp"] = timestamp.isoformat()
        if context:
            data["context"] = context
        
        return self._make_request("POST", "/page", data, customer_id=user_id)
    
    def screen(
        self,
        user_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a mobile screen view.
        
        Args:
            user_id: Unique user identifier
            anonymous_id: Anonymous user identifier
            name: Screen name
            properties: Screen properties
            timestamp: Event timestamp (defaults to now)
            context: Additional context data
            
        Returns:
            API response
        """
        if not user_id and not anonymous_id:
            raise CIOValidationError("Either user_id or anonymous_id must be provided")
        
        data = {}
        if user_id:
            data["userId"] = user_id
        if anonymous_id:
            data["anonymousId"] = anonymous_id
        if name:
            data["name"] = name
        if properties:
            data["properties"] = properties
        if timestamp:
            data["timestamp"] = timestamp.isoformat()
        if context:
            data["context"] = context
        
        return self._make_request("POST", "/screen", data, customer_id=user_id)
    
    def batch(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send multiple requests in a single batch.
        
        Args:
            requests: List of request objects
            
        Returns:
            API response
        """
        if not requests:
            raise CIOValidationError("Batch requests cannot be empty")
        
        # Check batch size limit
        batch_data = json.dumps({"batch": requests})
        if len(batch_data.encode()) > 500 * 1024:  # 500KB limit
            raise CIOValidationError("Batch size exceeds 500KB limit")
        
        data = {"batch": requests}
        return self._make_request("POST", "/batch", data)
    
    def get_region(self) -> Dict[str, Any]:
        """
        Get the region information for the account.
        
        Returns:
            Region information
        """
        return self._make_request("GET", "/region")
    
    def health_check(self) -> bool:
        """
        Check if the API is accessible and responsive.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.get_region()
            return True
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return False
    
    def close(self) -> None:
        """Close the HTTP client connection."""
        if hasattr(self, 'client'):
            self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()