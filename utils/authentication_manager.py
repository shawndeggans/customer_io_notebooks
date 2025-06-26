"""
Customer.IO Authentication and Connection Manager

Comprehensive authentication management for Customer.IO API including:
- API client initialization and configuration
- Connection health checks and monitoring
- Rate limit tracking and management
- Authentication validation and error handling
- Metrics collection and reporting
"""

import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import structlog
from pydantic import BaseModel, Field, validator

from .api_client import CustomerIOClient
from .error_handlers import retry_on_error, ErrorContext, CustomerIOError, NetworkError, RateLimitError


class AuthenticationMethod(str, Enum):
    """Supported authentication methods."""
    API_KEY = "api_key"
    OAUTH = "oauth"  # Future support
    SERVICE_ACCOUNT = "service_account"  # Future support


class ConnectionStatus(str, Enum):
    """Connection status values."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


class AuthenticationConfig(BaseModel):
    """Type-safe authentication configuration."""
    
    api_key: str = Field(..., description="Customer.IO API key")
    region: str = Field(default="us", description="API region (us/eu)")
    method: AuthenticationMethod = Field(default=AuthenticationMethod.API_KEY)
    environment: str = Field(default="production", description="Environment name")
    
    # Connection settings
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(default=2.0, description="Backoff multiplier")
    
    # Feature flags
    enable_logging: bool = Field(default=True, description="Enable structured logging")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    validate_ssl: bool = Field(default=True, description="Validate SSL certificates")
    
    @validator('api_key')
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("API key cannot be empty")
        if len(v) < 10:
            raise ValueError("API key appears to be invalid")
        return v.strip()
    
    @validator('region')
    def validate_region(cls, v: str) -> str:
        """Validate region selection."""
        valid_regions = ["us", "eu"]
        if v.lower() not in valid_regions:
            raise ValueError(f"Region must be one of: {valid_regions}")
        return v.lower()
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
        extra = "forbid"


class ConnectionMetrics(BaseModel):
    """Connection metrics and statistics."""
    
    total_requests: int = Field(default=0, description="Total API requests made")
    successful_requests: int = Field(default=0, description="Successful requests")
    failed_requests: int = Field(default=0, description="Failed requests")
    rate_limited_requests: int = Field(default=0, description="Rate limited requests")
    
    total_retries: int = Field(default=0, description="Total retry attempts")
    average_response_time: float = Field(default=0.0, description="Average response time in ms")
    
    last_request_time: Optional[datetime] = Field(None, description="Last request timestamp")
    last_error_time: Optional[datetime] = Field(None, description="Last error timestamp")
    last_error_message: Optional[str] = Field(None, description="Last error message")
    
    connection_established: Optional[datetime] = Field(None, description="Connection established time")
    uptime_seconds: float = Field(default=0.0, description="Connection uptime in seconds")
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True


class HealthCheckResult(BaseModel):
    """Health check result model."""
    
    status: ConnectionStatus = Field(..., description="Overall connection status")
    is_healthy: bool = Field(..., description="Whether connection is healthy")
    region: str = Field(..., description="Connected region")
    
    api_reachable: bool = Field(default=False, description="API endpoint reachable")
    auth_valid: bool = Field(default=False, description="Authentication valid")
    rate_limit_ok: bool = Field(default=True, description="Within rate limits")
    
    response_time_ms: Optional[float] = Field(None, description="Health check response time")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True


class AuthenticationManager:
    """
    Comprehensive authentication and connection management for Customer.IO API.
    
    Features:
    - Secure API client initialization
    - Connection health monitoring
    - Rate limit tracking
    - Authentication validation
    - Metrics collection and reporting
    - Automatic retry and error handling
    """
    
    def __init__(self, config: AuthenticationConfig, spark_session=None):
        """
        Initialize authentication manager.
        
        Args:
            config: Authentication configuration
            spark_session: Optional Spark session for logging
        """
        self.config = config
        self.spark = spark_session
        self.logger = structlog.get_logger("authentication_manager")
        
        # Initialize metrics
        self.metrics = ConnectionMetrics()
        self._metrics_lock = threading.Lock()
        
        # Connection state
        self._client: Optional[CustomerIOClient] = None
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._last_health_check: Optional[HealthCheckResult] = None
        
        self.logger.info("AuthenticationManager initialized",
                        region=config.region,
                        environment=config.environment,
                        method=config.method.value)
    
    def connect(self) -> CustomerIOClient:
        """
        Establish connection to Customer.IO API.
        
        Returns:
            Initialized CustomerIOClient
            
        Raises:
            CustomerIOError: If connection fails
        """
        try:
            self.logger.info("Establishing Customer.IO API connection",
                           region=self.config.region)
            
            # Create client
            self._client = CustomerIOClient(
                api_key=self.config.api_key,
                region=self.config.region,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
                retry_backoff_factor=self.config.retry_backoff_factor,
                enable_logging=self.config.enable_logging,
                spark_session=self.spark
            )
            
            # Test connection
            health_result = self.health_check()
            
            if health_result.is_healthy:
                self._connection_status = ConnectionStatus.CONNECTED
                self.metrics.connection_established = datetime.now(timezone.utc)
                self.logger.info("Customer.IO API connection established",
                               status=health_result.status.value,
                               region=health_result.region)
            else:
                self._connection_status = ConnectionStatus.ERROR
                raise CustomerIOError(f"Connection unhealthy: {health_result.error_message}")
            
            return self._client
            
        except Exception as e:
            self._connection_status = ConnectionStatus.ERROR
            self.logger.error("Failed to establish connection", error=str(e))
            raise
    
    @retry_on_error(max_retries=2, backoff_factor=1.5)
    def health_check(self) -> HealthCheckResult:
        """
        Perform comprehensive health check.
        
        Returns:
            HealthCheckResult with connection status
        """
        start_time = time.time()
        
        try:
            if not self._client:
                return HealthCheckResult(
                    status=ConnectionStatus.DISCONNECTED,
                    is_healthy=False,
                    region=self.config.region,
                    error_message="Client not initialized"
                )
            
            # Check API reachability
            api_reachable = False
            auth_valid = False
            
            try:
                # Make a lightweight API call
                response = self._client.get_region()
                api_reachable = True
                auth_valid = True
                
                # Update metrics
                with self._metrics_lock:
                    self.metrics.successful_requests += 1
                    
            except CustomerIOError as e:
                if hasattr(e, 'status_code'):
                    if e.status_code == 401:
                        auth_valid = False
                    elif e.status_code == 429:
                        self._connection_status = ConnectionStatus.RATE_LIMITED
                
                with self._metrics_lock:
                    self.metrics.failed_requests += 1
                    self.metrics.last_error_time = datetime.now(timezone.utc)
                    self.metrics.last_error_message = str(e)
            
            # Check rate limits
            rate_limit_ok = self._client.rate_limit.can_make_request()
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Determine overall status
            is_healthy = api_reachable and auth_valid and rate_limit_ok
            
            if is_healthy:
                status = ConnectionStatus.CONNECTED
                error_message = None
            elif not auth_valid:
                status = ConnectionStatus.ERROR
                error_message = "Authentication failed"
            elif not rate_limit_ok:
                status = ConnectionStatus.RATE_LIMITED
                error_message = "Rate limit exceeded"
            else:
                status = ConnectionStatus.ERROR
                error_message = "API unreachable"
            
            # Create result
            result = HealthCheckResult(
                status=status,
                is_healthy=is_healthy,
                region=self.config.region,
                api_reachable=api_reachable,
                auth_valid=auth_valid,
                rate_limit_ok=rate_limit_ok,
                response_time_ms=response_time_ms,
                error_message=error_message
            )
            
            self._last_health_check = result
            self._connection_status = status
            
            return result
            
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            
            return HealthCheckResult(
                status=ConnectionStatus.ERROR,
                is_healthy=False,
                region=self.config.region,
                error_message=f"Health check error: {str(e)}"
            )
    
    def validate_authentication(self) -> bool:
        """
        Validate current authentication credentials.
        
        Returns:
            True if authentication is valid
        """
        health = self.health_check()
        return health.auth_valid
    
    def get_client(self) -> CustomerIOClient:
        """
        Get authenticated API client.
        
        Returns:
            CustomerIOClient instance
            
        Raises:
            CustomerIOError: If client not connected
        """
        if not self._client:
            raise CustomerIOError("Client not initialized. Call connect() first.")
        
        if self._connection_status != ConnectionStatus.CONNECTED:
            raise CustomerIOError(f"Client not connected. Status: {self._connection_status.value}")
        
        return self._client
    
    def disconnect(self):
        """Disconnect and cleanup resources."""
        if self._client:
            self._client.close()
            self._client = None
            
        self._connection_status = ConnectionStatus.DISCONNECTED
        self.logger.info("Disconnected from Customer.IO API")
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.
        
        Returns:
            Rate limit information
        """
        if not self._client:
            return {
                "status": "unknown",
                "message": "Client not initialized"
            }
        
        rate_limit = self._client.rate_limit
        
        return {
            "can_make_request": rate_limit.can_make_request(),
            "current_requests": rate_limit.current_requests,
            "max_requests": rate_limit.max_requests,
            "window_seconds": rate_limit.window_seconds,
            "time_until_reset": rate_limit.time_until_reset(),
            "window_start": rate_limit.window_start.isoformat() if rate_limit.window_start else None
        }
    
    def update_metrics(self, request_type: str, success: bool, response_time_ms: float):
        """
        Update connection metrics.
        
        Args:
            request_type: Type of request made
            success: Whether request succeeded
            response_time_ms: Response time in milliseconds
        """
        with self._metrics_lock:
            self.metrics.total_requests += 1
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
            
            # Update average response time
            total_time = self.metrics.average_response_time * (self.metrics.total_requests - 1)
            self.metrics.average_response_time = (total_time + response_time_ms) / self.metrics.total_requests
            
            self.metrics.last_request_time = datetime.now(timezone.utc)
            
            # Update uptime
            if self.metrics.connection_established:
                self.metrics.uptime_seconds = (
                    datetime.now(timezone.utc) - self.metrics.connection_established
                ).total_seconds()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get authentication manager metrics.
        
        Returns:
            Comprehensive metrics dictionary
        """
        metrics_dict = self.metrics.dict()
        
        # Add calculated metrics
        if self.metrics.total_requests > 0:
            metrics_dict["success_rate"] = (
                self.metrics.successful_requests / self.metrics.total_requests
            ) * 100
            metrics_dict["failure_rate"] = (
                self.metrics.failed_requests / self.metrics.total_requests
            ) * 100
        else:
            metrics_dict["success_rate"] = 0.0
            metrics_dict["failure_rate"] = 0.0
        
        # Add current status
        metrics_dict["connection_status"] = self._connection_status.value
        metrics_dict["last_health_check"] = (
            self._last_health_check.dict() if self._last_health_check else None
        )
        
        # Add rate limit status
        metrics_dict["rate_limit_status"] = self.get_rate_limit_status()
        
        return metrics_dict
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False