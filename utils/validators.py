"""
Customer.IO API Request Validators

Pydantic models for validating Customer.IO API requests and responses.
These models ensure data integrity and provide clear error messages.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import re

from pydantic import BaseModel, Field, validator, root_validator


class IdentifyRequest(BaseModel):
    """Validation model for /identify API requests."""
    
    userId: Optional[str] = Field(None, description="Unique user identifier")
    anonymousId: Optional[str] = Field(None, description="Anonymous user identifier")
    traits: Optional[Dict[str, Any]] = Field(None, description="User traits and attributes")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    
    @root_validator
    def validate_user_identification(cls, values):
        """Ensure either userId or anonymousId is provided."""
        user_id = values.get('userId')
        anonymous_id = values.get('anonymousId')
        
        if not user_id and not anonymous_id:
            raise ValueError('Either userId or anonymousId must be provided')
        
        return values
    
    @validator('userId')
    def validate_user_id(cls, v):
        """Validate user ID format."""
        if v is not None:
            if len(v) == 0:
                raise ValueError('userId cannot be empty')
            if len(v) > 255:
                raise ValueError('userId cannot exceed 255 characters')
        return v
    
    @validator('anonymousId')
    def validate_anonymous_id(cls, v):
        """Validate anonymous ID format."""
        if v is not None:
            if len(v) == 0:
                raise ValueError('anonymousId cannot be empty')
            if len(v) > 255:
                raise ValueError('anonymousId cannot exceed 255 characters')
        return v
    
    @validator('traits')
    def validate_traits(cls, v):
        """Validate traits object."""
        if v is not None:
            # Check for common email validation if email is provided
            if 'email' in v and v['email']:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, v['email']):
                    raise ValueError('Invalid email format in traits')
        return v


class TrackRequest(BaseModel):
    """Validation model for /track API requests."""
    
    userId: Optional[str] = Field(None, description="Unique user identifier")
    anonymousId: Optional[str] = Field(None, description="Anonymous user identifier")
    event: str = Field(..., description="Event name")
    properties: Optional[Dict[str, Any]] = Field(None, description="Event properties")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    
    @root_validator
    def validate_user_identification(cls, values):
        """Ensure either userId or anonymousId is provided."""
        user_id = values.get('userId')
        anonymous_id = values.get('anonymousId')
        
        if not user_id and not anonymous_id:
            raise ValueError('Either userId or anonymousId must be provided')
        
        return values
    
    @validator('event')
    def validate_event_name(cls, v):
        """Validate event name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Event name cannot be empty')
        if len(v) > 255:
            raise ValueError('Event name cannot exceed 255 characters')
        return v.strip()


class GroupRequest(BaseModel):
    """Validation model for /group API requests."""
    
    userId: Optional[str] = Field(None, description="Unique user identifier")
    anonymousId: Optional[str] = Field(None, description="Anonymous user identifier")
    groupId: str = Field(..., description="Group/company identifier")
    traits: Optional[Dict[str, Any]] = Field(None, description="Group traits and attributes")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    
    @root_validator
    def validate_user_identification(cls, values):
        """Ensure either userId or anonymousId is provided."""
        user_id = values.get('userId')
        anonymous_id = values.get('anonymousId')
        
        if not user_id and not anonymous_id:
            raise ValueError('Either userId or anonymousId must be provided')
        
        return values
    
    @validator('groupId')
    def validate_group_id(cls, v):
        """Validate group ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Group ID cannot be empty')
        if len(v) > 255:
            raise ValueError('Group ID cannot exceed 255 characters')
        return v.strip()


class PageRequest(BaseModel):
    """Validation model for /page API requests."""
    
    userId: Optional[str] = Field(None, description="Unique user identifier")
    anonymousId: Optional[str] = Field(None, description="Anonymous user identifier")
    name: Optional[str] = Field(None, description="Page name")
    properties: Optional[Dict[str, Any]] = Field(None, description="Page properties")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    
    @root_validator
    def validate_user_identification(cls, values):
        """Ensure either userId or anonymousId is provided."""
        user_id = values.get('userId')
        anonymous_id = values.get('anonymousId')
        
        if not user_id and not anonymous_id:
            raise ValueError('Either userId or anonymousId must be provided')
        
        return values


class ScreenRequest(BaseModel):
    """Validation model for /screen API requests."""
    
    userId: Optional[str] = Field(None, description="Unique user identifier")
    anonymousId: Optional[str] = Field(None, description="Anonymous user identifier")
    name: Optional[str] = Field(None, description="Screen name")
    properties: Optional[Dict[str, Any]] = Field(None, description="Screen properties")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    
    @root_validator
    def validate_user_identification(cls, values):
        """Ensure either userId or anonymousId is provided."""
        user_id = values.get('userId')
        anonymous_id = values.get('anonymousId')
        
        if not user_id and not anonymous_id:
            raise ValueError('Either userId or anonymousId must be provided')
        
        return values


class DeviceRequest(BaseModel):
    """Validation model for device creation/update requests."""
    
    device: Dict[str, str] = Field(..., description="Device information")
    
    @validator('device')
    def validate_device(cls, v):
        """Validate device object structure."""
        if not v:
            raise ValueError('Device information is required')
        
        if 'token' not in v:
            raise ValueError('Device token is required')
        
        if 'type' not in v:
            raise ValueError('Device type is required')
        
        valid_types = ['ios', 'android', 'web']
        if v['type'] not in valid_types:
            raise ValueError(f'Device type must be one of: {valid_types}')
        
        if not v['token'] or len(v['token'].strip()) == 0:
            raise ValueError('Device token cannot be empty')
        
        return v


class BatchRequest(BaseModel):
    """Validation model for /batch API requests."""
    
    batch: List[Dict[str, Any]] = Field(..., description="List of batch requests")
    
    @validator('batch')
    def validate_batch(cls, v):
        """Validate batch request structure."""
        if not v:
            raise ValueError('Batch cannot be empty')
        
        if len(v) > 100:  # Reasonable limit for batch size
            raise ValueError('Batch cannot contain more than 100 requests')
        
        # Validate each request in the batch has a type
        valid_types = ['identify', 'track', 'group', 'page', 'screen']
        for i, request in enumerate(v):
            if 'type' not in request:
                raise ValueError(f'Request {i} is missing type field')
            
            if request['type'] not in valid_types:
                raise ValueError(f'Request {i} has invalid type: {request["type"]}')
        
        return v


# Semantic Event Validators

class EcommerceEventProperties(BaseModel):
    """Base properties for ecommerce semantic events."""
    
    product_id: Optional[str] = Field(None, description="Product identifier")
    sku: Optional[str] = Field(None, description="Product SKU")
    name: Optional[str] = Field(None, description="Product name")
    category: Optional[str] = Field(None, description="Product category")
    brand: Optional[str] = Field(None, description="Product brand")
    price: Optional[Union[float, int]] = Field(None, description="Product price")
    quantity: Optional[int] = Field(None, description="Product quantity")
    currency: Optional[str] = Field("USD", description="Currency code")
    
    @validator('price')
    def validate_price(cls, v):
        """Validate price is positive."""
        if v is not None and v < 0:
            raise ValueError('Price cannot be negative')
        return v
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive."""
        if v is not None and v < 0:
            raise ValueError('Quantity cannot be negative')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        """Validate currency code format."""
        if v is not None:
            if len(v) != 3:
                raise ValueError('Currency code must be 3 characters')
            if not v.isupper():
                raise ValueError('Currency code must be uppercase')
        return v


class OrderCompletedProperties(EcommerceEventProperties):
    """Properties for Order Completed semantic event."""
    
    order_id: str = Field(..., description="Order identifier")
    total: Union[float, int] = Field(..., description="Order total")
    products: Optional[List[Dict[str, Any]]] = Field(None, description="List of products")
    
    @validator('order_id')
    def validate_order_id(cls, v):
        """Validate order ID is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Order ID cannot be empty')
        return v.strip()
    
    @validator('total')
    def validate_total(cls, v):
        """Validate total is positive."""
        if v < 0:
            raise ValueError('Order total cannot be negative')
        return v


class ProductViewedProperties(EcommerceEventProperties):
    """Properties for Product Viewed semantic event."""
    
    product_id: str = Field(..., description="Product identifier")
    
    @validator('product_id')
    def validate_product_id_required(cls, v):
        """Validate product ID is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Product ID cannot be empty')
        return v.strip()


class EmailEventProperties(BaseModel):
    """Base properties for email semantic events."""
    
    email_id: Optional[str] = Field(None, description="Email identifier")
    email_subject: Optional[str] = Field(None, description="Email subject")
    email_address: Optional[str] = Field(None, description="Recipient email address")
    campaign_id: Optional[str] = Field(None, description="Campaign identifier")
    campaign_name: Optional[str] = Field(None, description="Campaign name")
    
    @validator('email_address')
    def validate_email_format(cls, v):
        """Validate email address format."""
        if v is not None:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email address format')
        return v


class MobileAppEventProperties(BaseModel):
    """Base properties for mobile app semantic events."""
    
    app_version: Optional[str] = Field(None, description="Application version")
    app_build: Optional[str] = Field(None, description="Application build number")
    os_version: Optional[str] = Field(None, description="Operating system version")
    device_model: Optional[str] = Field(None, description="Device model")
    platform: Optional[str] = Field(None, description="Platform (iOS/Android)")
    
    @validator('platform')
    def validate_platform(cls, v):
        """Validate platform value."""
        if v is not None:
            valid_platforms = ['iOS', 'Android', 'Web']
            if v not in valid_platforms:
                raise ValueError(f'Platform must be one of: {valid_platforms}')
        return v


class VideoEventProperties(BaseModel):
    """Base properties for video semantic events."""
    
    video_id: Optional[str] = Field(None, description="Video identifier")
    video_title: Optional[str] = Field(None, description="Video title")
    video_length: Optional[int] = Field(None, description="Video length in seconds")
    position: Optional[int] = Field(None, description="Current position in seconds")
    quality: Optional[str] = Field(None, description="Video quality")
    
    @validator('video_length')
    def validate_video_length(cls, v):
        """Validate video length is positive."""
        if v is not None and v < 0:
            raise ValueError('Video length cannot be negative')
        return v
    
    @validator('position')
    def validate_position(cls, v):
        """Validate position is non-negative."""
        if v is not None and v < 0:
            raise ValueError('Video position cannot be negative')
        return v


# Response Models

class CustomerIOResponse(BaseModel):
    """Base response model for Customer.IO API responses."""
    
    status: str = Field(..., description="Response status")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: Optional[datetime] = Field(None, description="Response timestamp")


class IdentifyResponse(CustomerIOResponse):
    """Response model for /identify API responses."""
    
    userId: Optional[str] = Field(None, description="User identifier")
    traits: Optional[Dict[str, Any]] = Field(None, description="Updated traits")


class TrackResponse(CustomerIOResponse):
    """Response model for /track API responses."""
    
    event: Optional[str] = Field(None, description="Event name")
    userId: Optional[str] = Field(None, description="User identifier")


class BatchResponse(CustomerIOResponse):
    """Response model for /batch API responses."""
    
    processed: Optional[int] = Field(None, description="Number of processed requests")
    failed: Optional[int] = Field(None, description="Number of failed requests")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of errors")


class RegionResponse(BaseModel):
    """Response model for /region API endpoint."""
    
    region: str = Field(..., description="Account region")
    data_center: Optional[str] = Field(None, description="Data center location")


# Utility Functions

def validate_request_size(data: Dict[str, Any]) -> bool:
    """
    Validate that request size is within limits.
    
    Args:
        data: Request data to validate
        
    Returns:
        True if size is valid, False otherwise
    """
    import json
    
    try:
        serialized = json.dumps(data)
        size_bytes = len(serialized.encode('utf-8'))
        return size_bytes <= 32 * 1024  # 32KB limit
    except (TypeError, ValueError):
        return False


def validate_batch_size(batch_data: List[Dict[str, Any]]) -> bool:
    """
    Validate that batch size is within limits.
    
    Args:
        batch_data: Batch request data to validate
        
    Returns:
        True if size is valid, False otherwise
    """
    import json
    
    try:
        serialized = json.dumps({"batch": batch_data})
        size_bytes = len(serialized.encode('utf-8'))
        return size_bytes <= 500 * 1024  # 500KB limit
    except (TypeError, ValueError):
        return False


def create_context(
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    locale: Optional[str] = None,
    timezone: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a context object for API requests.
    
    Args:
        ip: IP address
        user_agent: User agent string
        locale: User locale
        timezone: User timezone
        **kwargs: Additional context fields
        
    Returns:
        Context dictionary
    """
    context = {}
    
    if ip:
        context['ip'] = ip
    if user_agent:
        context['userAgent'] = user_agent
    if locale:
        context['locale'] = locale
    if timezone:
        context['timezone'] = timezone
    
    # Add any additional context fields
    context.update(kwargs)
    
    return context


# Configuration Models

class CustomerIOConfig(BaseModel):
    """Type-safe configuration class for Customer.IO API settings."""
    
    api_key: str = Field(..., description="Customer.IO API key")
    region: str = Field(default="us", description="API region")
    
    # Rate limiting configuration (class variables)
    RATE_LIMIT_REQUESTS: int = 3000
    RATE_LIMIT_WINDOW: int = 3  # seconds
    
    # Request size limits
    MAX_REQUEST_SIZE: int = 32 * 1024  # 32KB
    MAX_BATCH_SIZE: int = 500 * 1024   # 500KB
    
    # Retry configuration
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    
    @validator('api_key')
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("API key cannot be empty")
        if len(v) < 10:  # Reasonable minimum length
            raise ValueError("API key appears to be too short")
        return v.strip()
    
    @validator('region')
    def validate_region(cls, v: str) -> str:
        """Validate and normalize region."""
        normalized = v.lower()
        if normalized not in ["us", "eu"]:
            raise ValueError("Region must be 'us' or 'eu'")
        return normalized
    
    @property
    def base_url(self) -> str:
        """Get base URL based on region."""
        if self.region == "eu":
            return "https://cdp-eu.customer.io/v1"
        else:
            return "https://cdp.customer.io/v1"
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        import base64
        
        # Customer.IO uses Basic Auth with API key as username, empty password
        auth_string = base64.b64encode(f"{self.api_key}:".encode()).decode()
        
        return {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json",
            "User-Agent": "CustomerIO-Databricks-Notebooks/1.0.0",
            "Accept": "application/json"
        }
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
        extra = "forbid"