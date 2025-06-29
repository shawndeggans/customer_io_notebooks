"""
Customer.IO Data Pipelines API client.
"""

import time
from dataclasses import dataclass
from typing import Dict, Any, Optional
import httpx

from .validators import validate_region
from .exceptions import (
    CustomerIOError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
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
        current_time = time.time()
        if current_time - self.window_start >= self.window_seconds:
            self.current_requests = 0
            self.window_start = current_time
        return self.current_requests < self.max_requests
    
    def record_request(self) -> None:
        """Record that a request was made."""
        self.reset_if_needed()
        self.current_requests += 1


class CustomerIOClient:
    """
    Customer.IO Data Pipelines API client.
    
    Features:
    - Authentication with API key
    - Rate limiting (3000 requests per 3 seconds)
    - Automatic retry with exponential backoff
    - Error handling and custom exceptions
    - Support for US/EU regions
    """
    
    def __init__(self, api_key: str, region: str = "us"):
        """
        Initialize the Customer.IO API client.
        
        Parameters
        ----------
        api_key : str
            Customer.IO API key
        region : str
            Region (us or eu), default: us
            
        Raises
        ------
        ValidationError
            If api_key is empty or region is invalid
        """
        if not api_key or not isinstance(api_key, str):
            raise ValidationError("API key must be a non-empty string")
        
        validate_region(region)
        
        self.api_key = api_key
        self.region = region.lower()
        self.rate_limit = RateLimit()
        
        # Set base URL based on region
        if self.region == "us":
            self.base_url = "https://cdp.customer.io/v1"
        else:  # eu
            self.base_url = "https://cdp-eu.customer.io/v1"
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns
        -------
        dict
            Headers including authorization and content type
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "customerio-python-client/1.0.0"
        }
    
    def make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated API request with error handling and retries.
        
        Parameters
        ----------
        method : str
            HTTP method (GET, POST, PUT, DELETE)
        endpoint : str
            API endpoint (e.g., "/identify")
        data : dict, optional
            Request payload
            
        Returns
        -------
        dict
            API response
            
        Raises
        ------
        RateLimitError
            If rate limit is exceeded
        AuthenticationError
            If authentication fails
        NetworkError
            If network request fails
        CustomerIOError
            For other API errors
        """
        # Check rate limiting
        if not self.rate_limit.can_make_request():
            raise RateLimitError("Rate limit exceeded. Please wait before making more requests.")
        
        url = f"{self.base_url}{endpoint}"
        headers = self.get_auth_headers()
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Record the request for rate limiting
                self.rate_limit.record_request()
                
                # Make the HTTP request
                response = httpx.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                # Handle different response codes
                if response.status_code == 401:
                    raise AuthenticationError("Authentication failed. Check your API key.")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded by server.")
                elif 400 <= response.status_code < 500:
                    raise CustomerIOError(f"Client error {response.status_code}: {response.text}")
                elif response.status_code >= 500:
                    # Server errors are retryable
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        time.sleep(2 ** retry_count)  # Exponential backoff
                        continue
                    else:
                        raise CustomerIOError(f"Request failed after {max_retries} attempts")
                
                # Success case
                response.raise_for_status()
                return response.json()
                
            except httpx.ConnectError as e:
                raise NetworkError(f"Network error: {str(e)}")
            except httpx.TimeoutException as e:
                raise NetworkError(f"Request timeout: {str(e)}")
            except httpx.NetworkError as e:
                raise NetworkError(f"Network error: {str(e)}")
            except httpx.HTTPStatusError as e:
                # Handle HTTP status errors that weren't caught above
                if e.response.status_code == 401:
                    raise AuthenticationError("Authentication failed. Check your API key.")
                elif e.response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded by server.")
                elif e.response.status_code >= 500 and retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(2 ** retry_count)
                    continue
                else:
                    raise CustomerIOError(f"HTTP error {e.response.status_code}: {e.response.text}")
        
        # If we get here, all retries failed
        raise CustomerIOError(f"Request failed after {max_retries} attempts")
    
    def identify(self, user_id: str, traits: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify a user with traits.
        
        Parameters
        ----------
        user_id : str
            Unique identifier for the user
        traits : dict
            User attributes to store
            
        Returns
        -------
        dict
            API response
        """
        data = {
            "userId": user_id,
            "traits": traits
        }
        return self.make_request("POST", "/identify", data)
    
    def track(self, user_id: str, event: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track an event for a user.
        
        Parameters
        ----------
        user_id : str
            Unique identifier for the user
        event : str
            Event name
        properties : dict, optional
            Event properties
            
        Returns
        -------
        dict
            API response
        """
        data = {
            "userId": user_id,
            "event": event
        }
        if properties:
            data["properties"] = properties
        
        return self.make_request("POST", "/track", data)
    
    def delete(self, user_id: str) -> Dict[str, Any]:
        """
        Delete a user.
        
        Parameters
        ----------
        user_id : str
            Unique identifier for the user
            
        Returns
        -------
        dict
            API response
        """
        data = {"userId": user_id}
        return self.make_request("DELETE", "/identify", data)
    
    def page(self, user_id: Optional[str] = None, anonymous_id: Optional[str] = None, 
             name: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track a page view.
        
        Parameters
        ----------
        user_id : str, optional
            Unique identifier for the user
        anonymous_id : str, optional
            Anonymous identifier for the user
        name : str, optional
            Name of the page viewed
        properties : dict, optional
            Page properties
            
        Returns
        -------
        dict
            API response
        """
        data = {}
        
        if user_id:
            data["userId"] = user_id
        elif anonymous_id:
            data["anonymousId"] = anonymous_id
        else:
            raise ValidationError("Either user_id or anonymous_id must be provided")
        
        if name:
            data["name"] = name
        if properties:
            data["properties"] = properties
        
        return self.make_request("POST", "/page", data)
    
    def screen(self, user_id: Optional[str] = None, anonymous_id: Optional[str] = None,
               name: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track a screen view.
        
        Parameters
        ----------
        user_id : str, optional
            Unique identifier for the user
        anonymous_id : str, optional
            Anonymous identifier for the user
        name : str, optional
            Name of the screen viewed
        properties : dict, optional
            Screen properties
            
        Returns
        -------
        dict
            API response
        """
        data = {}
        
        if user_id:
            data["userId"] = user_id
        elif anonymous_id:
            data["anonymousId"] = anonymous_id
        else:
            raise ValidationError("Either user_id or anonymous_id must be provided")
        
        if name:
            data["name"] = name
        if properties:
            data["properties"] = properties
        
        return self.make_request("POST", "/screen", data)
    
    def alias(self, user_id: str, previous_id: str) -> Dict[str, Any]:
        """
        Create an alias linking a user ID to a previous ID.
        
        Parameters
        ----------
        user_id : str
            New/primary user identifier
        previous_id : str
            Previous/secondary user identifier to alias
            
        Returns
        -------
        dict
            API response
        """
        data = {
            "userId": user_id,
            "previousId": previous_id
        }
        return self.make_request("POST", "/alias", data)