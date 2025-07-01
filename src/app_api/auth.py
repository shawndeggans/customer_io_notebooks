"""App API authentication module."""
import requests
from typing import Dict


class AppAPIAuth:
    """Authentication handler for Customer.IO App API."""
    
    def __init__(self, api_token: str, region: str = "us"):
        """
        Initialize App API authentication.
        
        Parameters
        ----------
        api_token : str
            Bearer token for App API authentication
        region : str
            API region - "us" or "eu"
            
        Raises
        ------
        ValueError
            If region is not "us" or "eu"
        """
        if region not in ["us", "eu"]:
            raise ValueError("Region must be 'us' or 'eu'")
            
        self.api_token = api_token
        self.region = region
        
        if region == "us":
            self.base_url = "https://api.customer.io"
        else:
            self.base_url = "https://api-eu.customer.io"
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns
        -------
        Dict[str, str]
            Headers with Bearer token authentication
        """
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def create_session(self) -> requests.Session:
        """
        Create authenticated requests session.
        
        Returns
        -------
        requests.Session
            Session with authentication headers pre-configured
        """
        session = requests.Session()
        session.headers.update(self.get_headers())
        return session
    
    def get_rate_limit_delay(self, endpoint_type: str) -> float:
        """
        Get rate limit delay for endpoint type.
        
        Parameters
        ----------
        endpoint_type : str
            Type of endpoint - "general", "transactional", or "broadcast"
            
        Returns
        -------
        float
            Delay in seconds between requests
            
        Raises
        ------
        ValueError
            If endpoint_type is not recognized
        """
        rate_limits = {
            "general": 0.1,        # 10 req/sec
            "transactional": 0.01, # 100 req/sec
            "broadcast": 10.0      # 1 req/10 sec
        }
        
        if endpoint_type not in rate_limits:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}")
            
        return rate_limits[endpoint_type]