"""Tests for App API authentication module."""
import pytest
from unittest.mock import Mock, patch
from src.app_api.auth import AppAPIAuth


class TestAppAPIAuth:
    """Test App API authentication functionality."""
    
    def test_init_with_valid_token(self):
        """Test authentication initialization with valid token."""
        auth = AppAPIAuth(api_token="test_token_123")
        assert auth.api_token == "test_token_123"
        assert auth.base_url == "https://api.customer.io"
    
    def test_init_with_eu_region(self):
        """Test authentication initialization with EU region."""
        auth = AppAPIAuth(api_token="test_token", region="eu")
        assert auth.base_url == "https://api-eu.customer.io"
    
    def test_init_with_invalid_region(self):
        """Test authentication initialization with invalid region."""
        with pytest.raises(ValueError):
            AppAPIAuth(api_token="test_token", region="invalid")
    
    def test_get_headers(self):
        """Test getting authentication headers."""
        auth = AppAPIAuth(api_token="test_token_123")
        headers = auth.get_headers()
        
        expected_headers = {
            "Authorization": "Bearer test_token_123",
            "Content-Type": "application/json"
        }
        assert headers == expected_headers
    
    @patch('requests.Session')
    def test_create_session(self, mock_session_class):
        """Test creating authenticated session."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        auth = AppAPIAuth(api_token="test_token")
        session = auth.create_session()
        
        assert session == mock_session
        mock_session.headers.update.assert_called_once_with({
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        })
    
    def test_rate_limit_delay(self):
        """Test rate limiting delay calculation."""
        auth = AppAPIAuth(api_token="test_token")
        
        # General endpoints: 10 req/sec = 0.1 sec delay
        assert auth.get_rate_limit_delay("general") == 0.1
        
        # Transactional endpoints: 100 req/sec = 0.01 sec delay  
        assert auth.get_rate_limit_delay("transactional") == 0.01
        
        # Broadcast endpoints: 1 req/10 sec = 10 sec delay
        assert auth.get_rate_limit_delay("broadcast") == 10.0
    
    def test_rate_limit_delay_invalid_endpoint(self):
        """Test rate limit delay with invalid endpoint type."""
        auth = AppAPIAuth(api_token="test_token")
        
        with pytest.raises(ValueError):
            auth.get_rate_limit_delay("invalid")