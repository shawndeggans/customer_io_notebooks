"""
Comprehensive tests for Customer.IO Authentication Manager.

Tests cover:
- Authentication methods and connection status enums
- Authentication configuration validation
- Connection establishment and health checks
- Rate limit tracking and management
- Metrics collection and reporting
- Error handling and retry logic
- Context manager functionality
"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from utils.authentication_manager import (
    AuthenticationMethod,
    ConnectionStatus,
    AuthenticationConfig,
    ConnectionMetrics,
    HealthCheckResult,
    AuthenticationManager
)
from utils.api_client import CustomerIOClient
from utils.error_handlers import CustomerIOError, NetworkError, RateLimitError


class TestAuthenticationMethod:
    """Test AuthenticationMethod enum."""
    
    def test_authentication_method_values(self):
        """Test all authentication method values."""
        assert AuthenticationMethod.API_KEY == "api_key"
        assert AuthenticationMethod.OAUTH == "oauth"
        assert AuthenticationMethod.SERVICE_ACCOUNT == "service_account"
    
    def test_authentication_method_membership(self):
        """Test authentication method membership."""
        valid_methods = [method.value for method in AuthenticationMethod]
        assert "api_key" in valid_methods
        assert "invalid_method" not in valid_methods


class TestConnectionStatus:
    """Test ConnectionStatus enum."""
    
    def test_connection_status_values(self):
        """Test all connection status values."""
        assert ConnectionStatus.CONNECTED == "connected"
        assert ConnectionStatus.DISCONNECTED == "disconnected"
        assert ConnectionStatus.ERROR == "error"
        assert ConnectionStatus.RATE_LIMITED == "rate_limited"
        assert ConnectionStatus.UNKNOWN == "unknown"


class TestAuthenticationConfig:
    """Test AuthenticationConfig model."""
    
    def test_valid_config(self):
        """Test creating valid authentication config."""
        config = AuthenticationConfig(
            api_key="test_key_12345678901234567890",
            region="us",
            method=AuthenticationMethod.API_KEY,
            environment="production"
        )
        
        assert config.api_key == "test_key_12345678901234567890"
        assert config.region == "us"
        assert config.method == AuthenticationMethod.API_KEY
        assert config.environment == "production"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.enable_logging is True
    
    def test_invalid_api_key(self):
        """Test validation of invalid API key."""
        # Empty API key
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationConfig(api_key="", region="us")
        assert "API key cannot be empty" in str(exc_info.value)
        
        # Too short API key
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationConfig(api_key="short", region="us")
        assert "API key appears to be invalid" in str(exc_info.value)
    
    def test_invalid_region(self):
        """Test validation of invalid region."""
        with pytest.raises(ValidationError) as exc_info:
            AuthenticationConfig(
                api_key="test_key_valid_length",
                region="invalid"
            )
        assert "Region must be one of" in str(exc_info.value)
    
    def test_region_normalization(self):
        """Test region normalization to lowercase."""
        config = AuthenticationConfig(
            api_key="test_key_valid_length",
            region="US"
        )
        assert config.region == "us"


class TestConnectionMetrics:
    """Test ConnectionMetrics model."""
    
    def test_default_metrics(self):
        """Test default metric values."""
        metrics = ConnectionMetrics()
        
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.rate_limited_requests == 0
        assert metrics.total_retries == 0
        assert metrics.average_response_time == 0.0
        assert metrics.last_request_time is None
        assert metrics.last_error_time is None
        assert metrics.last_error_message is None
        assert metrics.connection_established is None
        assert metrics.uptime_seconds == 0.0
    
    def test_metrics_update(self):
        """Test updating metrics."""
        metrics = ConnectionMetrics()
        
        # Update counters
        metrics.total_requests = 100
        metrics.successful_requests = 95
        metrics.failed_requests = 5
        metrics.average_response_time = 125.5
        
        # Update timestamps
        now = datetime.now(timezone.utc)
        metrics.last_request_time = now
        metrics.connection_established = now - timedelta(hours=1)
        metrics.uptime_seconds = 3600.0
        
        assert metrics.total_requests == 100
        assert metrics.successful_requests == 95
        assert metrics.failed_requests == 5
        assert metrics.average_response_time == 125.5
        assert metrics.last_request_time == now
        assert metrics.uptime_seconds == 3600.0


class TestHealthCheckResult:
    """Test HealthCheckResult model."""
    
    def test_healthy_result(self):
        """Test creating healthy result."""
        result = HealthCheckResult(
            status=ConnectionStatus.CONNECTED,
            is_healthy=True,
            region="us",
            api_reachable=True,
            auth_valid=True,
            rate_limit_ok=True,
            response_time_ms=45.2
        )
        
        assert result.status == ConnectionStatus.CONNECTED
        assert result.is_healthy is True
        assert result.api_reachable is True
        assert result.auth_valid is True
        assert result.rate_limit_ok is True
        assert result.response_time_ms == 45.2
        assert result.error_message is None
    
    def test_unhealthy_result(self):
        """Test creating unhealthy result."""
        result = HealthCheckResult(
            status=ConnectionStatus.ERROR,
            is_healthy=False,
            region="us",
            api_reachable=False,
            auth_valid=False,
            error_message="Connection refused"
        )
        
        assert result.status == ConnectionStatus.ERROR
        assert result.is_healthy is False
        assert result.api_reachable is False
        assert result.auth_valid is False
        assert result.error_message == "Connection refused"


class TestAuthenticationManager:
    """Test AuthenticationManager operations."""
    
    @pytest.fixture
    def auth_config(self):
        """Create test authentication config."""
        return AuthenticationConfig(
            api_key="test_key_valid_length_12345",
            region="us",
            environment="test",
            timeout=30,
            max_retries=3
        )
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.rate_limit = Mock()
        client.rate_limit.can_make_request.return_value = True
        client.rate_limit.max_requests = 3000
        client.rate_limit.window_seconds = 3
        client.rate_limit.current_requests = 0
        client.rate_limit.time_until_reset.return_value = 2.5
        client.rate_limit.window_start = None
        return client
    
    @pytest.fixture
    def auth_manager(self, auth_config):
        """Create AuthenticationManager instance."""
        return AuthenticationManager(auth_config)
    
    def test_initialization(self, auth_manager, auth_config):
        """Test manager initialization."""
        assert auth_manager.config == auth_config
        assert auth_manager.metrics.total_requests == 0
        assert auth_manager._connection_status == ConnectionStatus.DISCONNECTED
        assert auth_manager._client is None
        assert auth_manager._last_health_check is None
    
    @patch('utils.authentication_manager.CustomerIOClient')
    def test_connect_success(self, mock_client_class, auth_manager, mock_client):
        """Test successful connection."""
        mock_client_class.return_value = mock_client
        mock_client.get_region.return_value = {"region": "us"}
        
        client = auth_manager.connect()
        
        assert client == mock_client
        assert auth_manager._connection_status == ConnectionStatus.CONNECTED
        assert auth_manager.metrics.connection_established is not None
        mock_client_class.assert_called_once()
    
    @patch('utils.authentication_manager.CustomerIOClient')
    def test_connect_failure(self, mock_client_class, auth_manager):
        """Test connection failure."""
        mock_client_class.side_effect = CustomerIOError("Connection failed")
        
        with pytest.raises(CustomerIOError):
            auth_manager.connect()
        
        assert auth_manager._connection_status == ConnectionStatus.ERROR
    
    def test_health_check_disconnected(self, auth_manager):
        """Test health check when disconnected."""
        result = auth_manager.health_check()
        
        assert result.status == ConnectionStatus.DISCONNECTED
        assert result.is_healthy is False
        assert result.error_message == "Client not initialized"
    
    def test_health_check_connected(self, auth_manager, mock_client):
        """Test health check when connected."""
        auth_manager._client = mock_client
        mock_client.get_region.return_value = {"region": "us"}
        
        result = auth_manager.health_check()
        
        assert result.is_healthy is True
        assert result.status == ConnectionStatus.CONNECTED
        assert result.api_reachable is True
        assert result.auth_valid is True
        assert result.rate_limit_ok is True
        assert auth_manager.metrics.successful_requests == 1
    
    def test_health_check_auth_failure(self, auth_manager, mock_client):
        """Test health check with authentication failure."""
        auth_manager._client = mock_client
        error = CustomerIOError("Unauthorized")
        error.status_code = 401
        mock_client.get_region.side_effect = error
        
        result = auth_manager.health_check()
        
        assert result.is_healthy is False
        assert result.status == ConnectionStatus.ERROR
        assert result.auth_valid is False
        assert result.error_message == "Authentication failed"
        assert auth_manager.metrics.failed_requests == 1
    
    def test_health_check_rate_limited(self, auth_manager, mock_client):
        """Test health check when rate limited."""
        auth_manager._client = mock_client
        error = CustomerIOError("Rate limited")
        error.status_code = 429
        mock_client.get_region.side_effect = error
        mock_client.rate_limit.can_make_request.return_value = False
        
        result = auth_manager.health_check()
        
        assert result.is_healthy is False
        assert result.status == ConnectionStatus.RATE_LIMITED
        assert result.rate_limit_ok is False
        assert auth_manager._connection_status == ConnectionStatus.RATE_LIMITED
    
    def test_validate_authentication(self, auth_manager, mock_client):
        """Test authentication validation."""
        auth_manager._client = mock_client
        mock_client.get_region.return_value = {"region": "us"}
        
        is_valid = auth_manager.validate_authentication()
        
        assert is_valid is True
    
    def test_get_client_not_initialized(self, auth_manager):
        """Test getting client when not initialized."""
        with pytest.raises(CustomerIOError) as exc_info:
            auth_manager.get_client()
        assert "Client not initialized" in str(exc_info.value)
    
    def test_get_client_connected(self, auth_manager, mock_client):
        """Test getting client when connected."""
        auth_manager._client = mock_client
        auth_manager._connection_status = ConnectionStatus.CONNECTED
        
        client = auth_manager.get_client()
        
        assert client == mock_client
    
    def test_get_client_disconnected(self, auth_manager, mock_client):
        """Test getting client when disconnected."""
        auth_manager._client = mock_client
        auth_manager._connection_status = ConnectionStatus.DISCONNECTED
        
        with pytest.raises(CustomerIOError) as exc_info:
            auth_manager.get_client()
        assert "Client not connected" in str(exc_info.value)
    
    def test_disconnect(self, auth_manager, mock_client):
        """Test disconnecting."""
        auth_manager._client = mock_client
        auth_manager._connection_status = ConnectionStatus.CONNECTED
        
        auth_manager.disconnect()
        
        mock_client.close.assert_called_once()
        assert auth_manager._client is None
        assert auth_manager._connection_status == ConnectionStatus.DISCONNECTED
    
    def test_get_rate_limit_status_no_client(self, auth_manager):
        """Test getting rate limit status without client."""
        status = auth_manager.get_rate_limit_status()
        
        assert status["status"] == "unknown"
        assert status["message"] == "Client not initialized"
    
    def test_get_rate_limit_status_with_client(self, auth_manager, mock_client):
        """Test getting rate limit status with client."""
        auth_manager._client = mock_client
        
        status = auth_manager.get_rate_limit_status()
        
        assert status["can_make_request"] is True
        assert status["current_requests"] == 0
        assert status["max_requests"] == 3000
        assert status["window_seconds"] == 3
        assert status["time_until_reset"] == 2.5
    
    def test_update_metrics(self, auth_manager):
        """Test updating metrics."""
        # Update multiple times
        auth_manager.update_metrics("identify", True, 100.0)
        auth_manager.update_metrics("track", True, 150.0)
        auth_manager.update_metrics("identify", False, 200.0)
        
        metrics = auth_manager.metrics
        assert metrics.total_requests == 3
        assert metrics.successful_requests == 2
        assert metrics.failed_requests == 1
        assert metrics.average_response_time == 150.0  # (100 + 150 + 200) / 3
        assert metrics.last_request_time is not None
    
    def test_get_metrics(self, auth_manager):
        """Test getting comprehensive metrics."""
        # Set up some metrics
        auth_manager.metrics.total_requests = 100
        auth_manager.metrics.successful_requests = 95
        auth_manager.metrics.failed_requests = 5
        auth_manager.metrics.average_response_time = 125.5
        auth_manager._connection_status = ConnectionStatus.CONNECTED
        
        metrics = auth_manager.get_metrics()
        
        assert metrics["total_requests"] == 100
        assert metrics["successful_requests"] == 95
        assert metrics["failed_requests"] == 5
        assert metrics["success_rate"] == 95.0
        assert metrics["failure_rate"] == 5.0
        assert metrics["average_response_time"] == 125.5
        assert metrics["connection_status"] == "connected"
        assert "rate_limit_status" in metrics
    
    def test_context_manager(self, auth_manager, mock_client):
        """Test context manager functionality."""
        with patch.object(auth_manager, 'connect', return_value=mock_client) as mock_connect:
            with patch.object(auth_manager, 'disconnect') as mock_disconnect:
                with auth_manager as manager:
                    assert manager == auth_manager
                    mock_connect.assert_called_once()
                
                mock_disconnect.assert_called_once()
    
    def test_context_manager_with_error(self, auth_manager):
        """Test context manager with error."""
        with patch.object(auth_manager, 'connect', side_effect=CustomerIOError("Failed")):
            with patch.object(auth_manager, 'disconnect') as mock_disconnect:
                with pytest.raises(CustomerIOError):
                    with auth_manager:
                        pass
                
                # Disconnect should not be called due to error in connect
                mock_disconnect.assert_not_called()


class TestIntegration:
    """Integration tests for AuthenticationManager."""
    
    def test_full_connection_lifecycle(self):
        """Test complete connection lifecycle."""
        config = AuthenticationConfig(
            api_key="test_key_integration_test",
            region="us",
            environment="test"
        )
        
        manager = AuthenticationManager(config)
        
        # Mock the client
        mock_client = Mock(spec=CustomerIOClient)
        mock_client.rate_limit = Mock()
        mock_client.rate_limit.can_make_request.return_value = True
        mock_client.rate_limit.max_requests = 3000
        mock_client.rate_limit.window_seconds = 3
        mock_client.get_region.return_value = {"region": "us"}
        
        with patch('utils.authentication_manager.CustomerIOClient', return_value=mock_client):
            # Connect
            client = manager.connect()
            assert manager._connection_status == ConnectionStatus.CONNECTED
            
            # Health check
            health = manager.health_check()
            assert health.is_healthy is True
            
            # Update some metrics
            manager.update_metrics("identify", True, 50.0)
            manager.update_metrics("track", True, 75.0)
            
            # Get metrics
            metrics = manager.get_metrics()
            assert metrics["total_requests"] == 3  # 1 from connect, 1 from health check, 1 manual
            assert metrics["success_rate"] == 100.0
            
            # Disconnect
            manager.disconnect()
            assert manager._connection_status == ConnectionStatus.DISCONNECTED