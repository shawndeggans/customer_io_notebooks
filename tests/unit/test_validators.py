"""
Comprehensive tests for Customer.IO API request validators.

Tests cover:
- All request model validation (identify, track, group, page, screen, device, batch)
- Semantic event property models (ecommerce, email, mobile, video)
- Response model validation
- Utility functions for size validation and context creation
- Edge cases and error handling
"""

import pytest
import json
from datetime import datetime, timezone
from pydantic import ValidationError

from utils.validators import (
    # Request Models
    IdentifyRequest,
    TrackRequest,
    GroupRequest,
    PageRequest,
    ScreenRequest,
    DeviceRequest,
    BatchRequest,
    
    # Semantic Event Properties
    EcommerceEventProperties,
    OrderCompletedProperties,
    ProductViewedProperties,
    EmailEventProperties,
    MobileAppEventProperties,
    VideoEventProperties,
    
    # Response Models
    CustomerIOResponse,
    IdentifyResponse,
    TrackResponse,
    BatchResponse,
    RegionResponse,
    
    # Utility Functions
    validate_request_size,
    validate_batch_size,
    create_context
)


class TestIdentifyRequest:
    """Test IdentifyRequest validation model."""
    
    def test_valid_identify_with_user_id(self):
        """Test valid identify request with user ID."""
        data = {
            "userId": "user_123",
            "traits": {"email": "test@example.com", "name": "Test User"}
        }
        
        request = IdentifyRequest(**data)
        
        assert request.userId == "user_123"
        assert request.traits["email"] == "test@example.com"
        assert request.anonymousId is None
    
    def test_valid_identify_with_anonymous_id(self):
        """Test valid identify request with anonymous ID."""
        data = {
            "anonymousId": "anon_456",
            "traits": {"plan": "premium"}
        }
        
        request = IdentifyRequest(**data)
        
        assert request.anonymousId == "anon_456"
        assert request.userId is None
        assert request.traits["plan"] == "premium"
    
    def test_valid_identify_with_both_ids(self):
        """Test valid identify request with both user and anonymous IDs."""
        data = {
            "userId": "user_123",
            "anonymousId": "anon_456",
            "traits": {"email": "test@example.com"}
        }
        
        request = IdentifyRequest(**data)
        
        assert request.userId == "user_123"
        assert request.anonymousId == "anon_456"
    
    def test_identify_requires_user_identification(self):
        """Test identify fails without user identification."""
        data = {"traits": {"email": "test@example.com"}}
        
        with pytest.raises(ValidationError, match="Either userId or anonymousId must be provided"):
            IdentifyRequest(**data)
    
    def test_identify_empty_user_id_validation(self):
        """Test identify fails with empty user ID."""
        data = {"userId": "", "traits": {"email": "test@example.com"}}
        
        with pytest.raises(ValidationError, match="userId cannot be empty"):
            IdentifyRequest(**data)
    
    def test_identify_long_user_id_validation(self):
        """Test identify fails with user ID over 255 characters."""
        data = {"userId": "x" * 256, "traits": {"email": "test@example.com"}}
        
        with pytest.raises(ValidationError, match="userId cannot exceed 255 characters"):
            IdentifyRequest(**data)
    
    def test_identify_empty_anonymous_id_validation(self):
        """Test identify fails with empty anonymous ID."""
        data = {"anonymousId": "", "traits": {"email": "test@example.com"}}
        
        with pytest.raises(ValidationError, match="anonymousId cannot be empty"):
            IdentifyRequest(**data)
    
    def test_identify_long_anonymous_id_validation(self):
        """Test identify fails with anonymous ID over 255 characters."""
        data = {"anonymousId": "x" * 256, "traits": {"email": "test@example.com"}}
        
        with pytest.raises(ValidationError, match="anonymousId cannot exceed 255 characters"):
            IdentifyRequest(**data)
    
    def test_identify_invalid_email_in_traits(self):
        """Test identify fails with invalid email in traits."""
        data = {
            "userId": "user_123",
            "traits": {"email": "invalid-email"}
        }
        
        with pytest.raises(ValidationError, match="Invalid email format in traits"):
            IdentifyRequest(**data)
    
    def test_identify_valid_email_in_traits(self):
        """Test identify succeeds with valid email in traits."""
        data = {
            "userId": "user_123",
            "traits": {"email": "valid@example.com"}
        }
        
        request = IdentifyRequest(**data)
        assert request.traits["email"] == "valid@example.com"
    
    def test_identify_with_timestamp(self):
        """Test identify with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        data = {
            "userId": "user_123",
            "traits": {"email": "test@example.com"},
            "timestamp": timestamp
        }
        
        request = IdentifyRequest(**data)
        assert request.timestamp == timestamp


class TestTrackRequest:
    """Test TrackRequest validation model."""
    
    def test_valid_track_with_user_id(self):
        """Test valid track request with user ID."""
        data = {
            "userId": "user_123",
            "event": "Product Viewed",
            "properties": {"product_id": "prod_456"}
        }
        
        request = TrackRequest(**data)
        
        assert request.userId == "user_123"
        assert request.event == "Product Viewed"
        assert request.properties["product_id"] == "prod_456"
    
    def test_valid_track_with_anonymous_id(self):
        """Test valid track request with anonymous ID."""
        data = {
            "anonymousId": "anon_456",
            "event": "Page Viewed",
            "properties": {"page": "Home"}
        }
        
        request = TrackRequest(**data)
        
        assert request.anonymousId == "anon_456"
        assert request.event == "Page Viewed"
    
    def test_track_requires_user_identification(self):
        """Test track fails without user identification."""
        data = {"event": "Test Event"}
        
        with pytest.raises(ValidationError, match="Either userId or anonymousId must be provided"):
            TrackRequest(**data)
    
    def test_track_requires_event_name(self):
        """Test track fails without event name."""
        data = {"userId": "user_123"}
        
        with pytest.raises(ValidationError, match="Field required"):
            TrackRequest(**data)
    
    def test_track_empty_event_name(self):
        """Test track fails with empty event name."""
        data = {"userId": "user_123", "event": ""}
        
        with pytest.raises(ValidationError, match="Event name cannot be empty"):
            TrackRequest(**data)
    
    def test_track_whitespace_event_name(self):
        """Test track fails with whitespace-only event name."""
        data = {"userId": "user_123", "event": "   "}
        
        with pytest.raises(ValidationError, match="Event name cannot be empty"):
            TrackRequest(**data)
    
    def test_track_long_event_name(self):
        """Test track fails with event name over 255 characters."""
        data = {"userId": "user_123", "event": "x" * 256}
        
        with pytest.raises(ValidationError, match="Event name cannot exceed 255 characters"):
            TrackRequest(**data)
    
    def test_track_strips_event_name(self):
        """Test track strips whitespace from event name."""
        data = {"userId": "user_123", "event": "  Product Viewed  "}
        
        request = TrackRequest(**data)
        assert request.event == "Product Viewed"


class TestGroupRequest:
    """Test GroupRequest validation model."""
    
    def test_valid_group_request(self):
        """Test valid group request."""
        data = {
            "userId": "user_123",
            "groupId": "company_456",
            "traits": {"name": "Acme Corp"}
        }
        
        request = GroupRequest(**data)
        
        assert request.userId == "user_123"
        assert request.groupId == "company_456"
        assert request.traits["name"] == "Acme Corp"
    
    def test_group_requires_user_identification(self):
        """Test group fails without user identification."""
        data = {"groupId": "company_456"}
        
        with pytest.raises(ValidationError, match="Either userId or anonymousId must be provided"):
            GroupRequest(**data)
    
    def test_group_requires_group_id(self):
        """Test group fails without group ID."""
        data = {"userId": "user_123"}
        
        with pytest.raises(ValidationError, match="Field required"):
            GroupRequest(**data)
    
    def test_group_empty_group_id(self):
        """Test group fails with empty group ID."""
        data = {"userId": "user_123", "groupId": ""}
        
        with pytest.raises(ValidationError, match="Group ID cannot be empty"):
            GroupRequest(**data)
    
    def test_group_whitespace_group_id(self):
        """Test group fails with whitespace-only group ID."""
        data = {"userId": "user_123", "groupId": "   "}
        
        with pytest.raises(ValidationError, match="Group ID cannot be empty"):
            GroupRequest(**data)
    
    def test_group_long_group_id(self):
        """Test group fails with group ID over 255 characters."""
        data = {"userId": "user_123", "groupId": "x" * 256}
        
        with pytest.raises(ValidationError, match="Group ID cannot exceed 255 characters"):
            GroupRequest(**data)
    
    def test_group_strips_group_id(self):
        """Test group strips whitespace from group ID."""
        data = {"userId": "user_123", "groupId": "  company_456  "}
        
        request = GroupRequest(**data)
        assert request.groupId == "company_456"


class TestPageRequest:
    """Test PageRequest validation model."""
    
    def test_valid_page_request(self):
        """Test valid page request."""
        data = {
            "userId": "user_123",
            "name": "Home Page",
            "properties": {"url": "https://example.com"}
        }
        
        request = PageRequest(**data)
        
        assert request.userId == "user_123"
        assert request.name == "Home Page"
        assert request.properties["url"] == "https://example.com"
    
    def test_page_requires_user_identification(self):
        """Test page fails without user identification."""
        data = {"name": "Home Page"}
        
        with pytest.raises(ValidationError, match="Either userId or anonymousId must be provided"):
            PageRequest(**data)
    
    def test_page_optional_name(self):
        """Test page request with optional name."""
        data = {"userId": "user_123"}
        
        request = PageRequest(**data)
        assert request.name is None


class TestScreenRequest:
    """Test ScreenRequest validation model."""
    
    def test_valid_screen_request(self):
        """Test valid screen request."""
        data = {
            "userId": "user_123",
            "name": "Product Details",
            "properties": {"product_id": "prod_456"}
        }
        
        request = ScreenRequest(**data)
        
        assert request.userId == "user_123"
        assert request.name == "Product Details"
        assert request.properties["product_id"] == "prod_456"
    
    def test_screen_requires_user_identification(self):
        """Test screen fails without user identification."""
        data = {"name": "Product Details"}
        
        with pytest.raises(ValidationError, match="Either userId or anonymousId must be provided"):
            ScreenRequest(**data)


class TestDeviceRequest:
    """Test DeviceRequest validation model."""
    
    def test_valid_device_request(self):
        """Test valid device request."""
        data = {
            "device": {
                "token": "device_token_123",
                "type": "ios"
            }
        }
        
        request = DeviceRequest(**data)
        
        assert request.device["token"] == "device_token_123"
        assert request.device["type"] == "ios"
    
    def test_device_requires_device_info(self):
        """Test device fails without device info."""
        with pytest.raises(ValidationError, match="Field required"):
            DeviceRequest()
    
    def test_device_empty_device_info(self):
        """Test device fails with empty device info."""
        data = {"device": {}}
        
        with pytest.raises(ValidationError, match="Device information is required"):
            DeviceRequest(**data)
    
    def test_device_missing_token(self):
        """Test device fails without token."""
        data = {"device": {"type": "ios"}}
        
        with pytest.raises(ValidationError, match="Device token is required"):
            DeviceRequest(**data)
    
    def test_device_missing_type(self):
        """Test device fails without type."""
        data = {"device": {"token": "device_token_123"}}
        
        with pytest.raises(ValidationError, match="Device type is required"):
            DeviceRequest(**data)
    
    def test_device_invalid_type(self):
        """Test device fails with invalid type."""
        data = {"device": {"token": "device_token_123", "type": "invalid"}}
        
        with pytest.raises(ValidationError, match="Device type must be one of"):
            DeviceRequest(**data)
    
    def test_device_empty_token(self):
        """Test device fails with empty token."""
        data = {"device": {"token": "", "type": "ios"}}
        
        with pytest.raises(ValidationError, match="Device token cannot be empty"):
            DeviceRequest(**data)
    
    def test_device_whitespace_token(self):
        """Test device fails with whitespace-only token."""
        data = {"device": {"token": "   ", "type": "ios"}}
        
        with pytest.raises(ValidationError, match="Device token cannot be empty"):
            DeviceRequest(**data)
    
    def test_device_valid_types(self):
        """Test device accepts all valid types."""
        valid_types = ["ios", "android", "web"]
        
        for device_type in valid_types:
            data = {"device": {"token": "token_123", "type": device_type}}
            request = DeviceRequest(**data)
            assert request.device["type"] == device_type


class TestBatchRequest:
    """Test BatchRequest validation model."""
    
    def test_valid_batch_request(self):
        """Test valid batch request."""
        data = {
            "batch": [
                {"type": "identify", "userId": "user_1"},
                {"type": "track", "userId": "user_2", "event": "Test Event"}
            ]
        }
        
        request = BatchRequest(**data)
        
        assert len(request.batch) == 2
        assert request.batch[0]["type"] == "identify"
        assert request.batch[1]["type"] == "track"
    
    def test_batch_requires_batch_data(self):
        """Test batch fails without batch data."""
        with pytest.raises(ValidationError, match="Field required"):
            BatchRequest()
    
    def test_batch_empty_batch_data(self):
        """Test batch fails with empty batch data."""
        data = {"batch": []}
        
        with pytest.raises(ValidationError, match="Batch cannot be empty"):
            BatchRequest(**data)
    
    def test_batch_too_many_requests(self):
        """Test batch fails with too many requests."""
        data = {"batch": [{"type": "identify", "userId": f"user_{i}"} for i in range(101)]}
        
        with pytest.raises(ValidationError, match="Batch cannot contain more than 100 requests"):
            BatchRequest(**data)
    
    def test_batch_missing_type(self):
        """Test batch fails when request is missing type."""
        data = {"batch": [{"userId": "user_1"}]}
        
        with pytest.raises(ValidationError, match="Request 0 is missing type field"):
            BatchRequest(**data)
    
    def test_batch_invalid_type(self):
        """Test batch fails with invalid request type."""
        data = {"batch": [{"type": "invalid", "userId": "user_1"}]}
        
        with pytest.raises(ValidationError, match="Request 0 has invalid type"):
            BatchRequest(**data)
    
    def test_batch_valid_types(self):
        """Test batch accepts all valid request types."""
        valid_types = ["identify", "track", "group", "page", "screen"]
        
        for request_type in valid_types:
            data = {"batch": [{"type": request_type, "userId": "user_1"}]}
            request = BatchRequest(**data)
            assert request.batch[0]["type"] == request_type


class TestEcommerceEventProperties:
    """Test EcommerceEventProperties validation model."""
    
    def test_valid_ecommerce_properties(self):
        """Test valid ecommerce event properties."""
        data = {
            "product_id": "prod_123",
            "name": "Test Product",
            "price": 29.99,
            "quantity": 2,
            "currency": "USD"
        }
        
        props = EcommerceEventProperties(**data)
        
        assert props.product_id == "prod_123"
        assert props.price == 29.99
        assert props.quantity == 2
        assert props.currency == "USD"
    
    def test_ecommerce_negative_price(self):
        """Test ecommerce fails with negative price."""
        data = {"price": -10.0}
        
        with pytest.raises(ValidationError, match="Price cannot be negative"):
            EcommerceEventProperties(**data)
    
    def test_ecommerce_negative_quantity(self):
        """Test ecommerce fails with negative quantity."""
        data = {"quantity": -1}
        
        with pytest.raises(ValidationError, match="Quantity cannot be negative"):
            EcommerceEventProperties(**data)
    
    def test_ecommerce_invalid_currency_length(self):
        """Test ecommerce fails with invalid currency length."""
        data = {"currency": "US"}
        
        with pytest.raises(ValidationError, match="Currency code must be 3 characters"):
            EcommerceEventProperties(**data)
    
    def test_ecommerce_lowercase_currency(self):
        """Test ecommerce fails with lowercase currency."""
        data = {"currency": "usd"}
        
        with pytest.raises(ValidationError, match="Currency code must be uppercase"):
            EcommerceEventProperties(**data)
    
    def test_ecommerce_default_currency(self):
        """Test ecommerce uses default currency."""
        data = {"product_id": "prod_123"}
        
        props = EcommerceEventProperties(**data)
        assert props.currency == "USD"


class TestOrderCompletedProperties:
    """Test OrderCompletedProperties validation model."""
    
    def test_valid_order_completed(self):
        """Test valid order completed properties."""
        data = {
            "order_id": "order_123",
            "total": 99.99,
            "products": [{"product_id": "prod_1"}]
        }
        
        props = OrderCompletedProperties(**data)
        
        assert props.order_id == "order_123"
        assert props.total == 99.99
        assert len(props.products) == 1
    
    def test_order_completed_requires_order_id(self):
        """Test order completed fails without order ID."""
        data = {"total": 99.99}
        
        with pytest.raises(ValidationError, match="Field required"):
            OrderCompletedProperties(**data)
    
    def test_order_completed_requires_total(self):
        """Test order completed fails without total."""
        data = {"order_id": "order_123"}
        
        with pytest.raises(ValidationError, match="Field required"):
            OrderCompletedProperties(**data)
    
    def test_order_completed_empty_order_id(self):
        """Test order completed fails with empty order ID."""
        data = {"order_id": "", "total": 99.99}
        
        with pytest.raises(ValidationError, match="Order ID cannot be empty"):
            OrderCompletedProperties(**data)
    
    def test_order_completed_strips_order_id(self):
        """Test order completed strips whitespace from order ID."""
        data = {"order_id": "  order_123  ", "total": 99.99}
        
        props = OrderCompletedProperties(**data)
        assert props.order_id == "order_123"
    
    def test_order_completed_negative_total(self):
        """Test order completed fails with negative total."""
        data = {"order_id": "order_123", "total": -10.0}
        
        with pytest.raises(ValidationError, match="Order total cannot be negative"):
            OrderCompletedProperties(**data)


class TestProductViewedProperties:
    """Test ProductViewedProperties validation model."""
    
    def test_valid_product_viewed(self):
        """Test valid product viewed properties."""
        data = {"product_id": "prod_123", "price": 29.99}
        
        props = ProductViewedProperties(**data)
        
        assert props.product_id == "prod_123"
        assert props.price == 29.99
    
    def test_product_viewed_requires_product_id(self):
        """Test product viewed fails without product ID."""
        with pytest.raises(ValidationError, match="Field required"):
            ProductViewedProperties()
    
    def test_product_viewed_empty_product_id(self):
        """Test product viewed fails with empty product ID."""
        data = {"product_id": ""}
        
        with pytest.raises(ValidationError, match="Product ID cannot be empty"):
            ProductViewedProperties(**data)
    
    def test_product_viewed_strips_product_id(self):
        """Test product viewed strips whitespace from product ID."""
        data = {"product_id": "  prod_123  "}
        
        props = ProductViewedProperties(**data)
        assert props.product_id == "prod_123"


class TestEmailEventProperties:
    """Test EmailEventProperties validation model."""
    
    def test_valid_email_properties(self):
        """Test valid email event properties."""
        data = {
            "email_id": "email_123",
            "email_address": "test@example.com",
            "campaign_id": "campaign_456"
        }
        
        props = EmailEventProperties(**data)
        
        assert props.email_id == "email_123"
        assert props.email_address == "test@example.com"
        assert props.campaign_id == "campaign_456"
    
    def test_email_invalid_email_address(self):
        """Test email fails with invalid email address."""
        data = {"email_address": "invalid-email"}
        
        with pytest.raises(ValidationError, match="Invalid email address format"):
            EmailEventProperties(**data)
    
    def test_email_valid_email_formats(self):
        """Test email accepts various valid email formats."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "123@example.com"
        ]
        
        for email in valid_emails:
            data = {"email_address": email}
            props = EmailEventProperties(**data)
            assert props.email_address == email


class TestMobileAppEventProperties:
    """Test MobileAppEventProperties validation model."""
    
    def test_valid_mobile_app_properties(self):
        """Test valid mobile app event properties."""
        data = {
            "app_version": "1.2.3",
            "platform": "iOS",
            "device_model": "iPhone 12"
        }
        
        props = MobileAppEventProperties(**data)
        
        assert props.app_version == "1.2.3"
        assert props.platform == "iOS"
        assert props.device_model == "iPhone 12"
    
    def test_mobile_app_invalid_platform(self):
        """Test mobile app fails with invalid platform."""
        data = {"platform": "Windows"}
        
        with pytest.raises(ValidationError, match="Platform must be one of"):
            MobileAppEventProperties(**data)
    
    def test_mobile_app_valid_platforms(self):
        """Test mobile app accepts all valid platforms."""
        valid_platforms = ["iOS", "Android", "Web"]
        
        for platform in valid_platforms:
            data = {"platform": platform}
            props = MobileAppEventProperties(**data)
            assert props.platform == platform


class TestVideoEventProperties:
    """Test VideoEventProperties validation model."""
    
    def test_valid_video_properties(self):
        """Test valid video event properties."""
        data = {
            "video_id": "video_123",
            "video_length": 300,
            "position": 150,
            "quality": "720p"
        }
        
        props = VideoEventProperties(**data)
        
        assert props.video_id == "video_123"
        assert props.video_length == 300
        assert props.position == 150
        assert props.quality == "720p"
    
    def test_video_negative_length(self):
        """Test video fails with negative length."""
        data = {"video_length": -100}
        
        with pytest.raises(ValidationError, match="Video length cannot be negative"):
            VideoEventProperties(**data)
    
    def test_video_negative_position(self):
        """Test video fails with negative position."""
        data = {"position": -10}
        
        with pytest.raises(ValidationError, match="Video position cannot be negative"):
            VideoEventProperties(**data)


class TestResponseModels:
    """Test response validation models."""
    
    def test_customer_io_response(self):
        """Test base CustomerIOResponse model."""
        data = {"status": "success", "message": "Request processed"}
        
        response = CustomerIOResponse(**data)
        
        assert response.status == "success"
        assert response.message == "Request processed"
    
    def test_identify_response(self):
        """Test IdentifyResponse model."""
        data = {
            "status": "success",
            "userId": "user_123",
            "traits": {"email": "test@example.com"}
        }
        
        response = IdentifyResponse(**data)
        
        assert response.status == "success"
        assert response.userId == "user_123"
        assert response.traits["email"] == "test@example.com"
    
    def test_track_response(self):
        """Test TrackResponse model."""
        data = {
            "status": "success",
            "event": "Product Viewed",
            "userId": "user_123"
        }
        
        response = TrackResponse(**data)
        
        assert response.status == "success"
        assert response.event == "Product Viewed"
        assert response.userId == "user_123"
    
    def test_batch_response(self):
        """Test BatchResponse model."""
        data = {
            "status": "success",
            "processed": 10,
            "failed": 1,
            "errors": [{"index": 5, "error": "Invalid data"}]
        }
        
        response = BatchResponse(**data)
        
        assert response.status == "success"
        assert response.processed == 10
        assert response.failed == 1
        assert len(response.errors) == 1
    
    def test_region_response(self):
        """Test RegionResponse model."""
        data = {
            "region": "us",
            "data_center": "us-east-1"
        }
        
        response = RegionResponse(**data)
        
        assert response.region == "us"
        assert response.data_center == "us-east-1"


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_validate_request_size_valid(self):
        """Test validate_request_size with valid data."""
        data = {"userId": "user_123", "event": "Test Event"}
        
        assert validate_request_size(data) is True
    
    def test_validate_request_size_too_large(self):
        """Test validate_request_size with data exceeding 32KB."""
        # Create data that exceeds 32KB
        large_data = {"data": "x" * (33 * 1024)}
        
        assert validate_request_size(large_data) is False
    
    def test_validate_request_size_invalid_data(self):
        """Test validate_request_size with non-serializable data."""
        # Create non-serializable data
        invalid_data = {"function": lambda x: x}
        
        assert validate_request_size(invalid_data) is False
    
    def test_validate_batch_size_valid(self):
        """Test validate_batch_size with valid batch data."""
        batch_data = [
            {"type": "identify", "userId": "user_1"},
            {"type": "track", "userId": "user_2", "event": "Test"}
        ]
        
        assert validate_batch_size(batch_data) is True
    
    def test_validate_batch_size_too_large(self):
        """Test validate_batch_size with data exceeding 500KB."""
        # Create batch data that exceeds 500KB
        large_batch = [{"data": "x" * (10 * 1024)} for _ in range(60)]
        
        assert validate_batch_size(large_batch) is False
    
    def test_validate_batch_size_invalid_data(self):
        """Test validate_batch_size with non-serializable data."""
        # Create non-serializable batch data
        invalid_batch = [{"function": lambda x: x}]
        
        assert validate_batch_size(invalid_batch) is False
    
    def test_create_context_basic(self):
        """Test create_context with basic parameters."""
        context = create_context(
            ip="192.168.1.1",
            user_agent="Mozilla/5.0",
            locale="en-US",
            timezone="America/New_York"
        )
        
        assert context["ip"] == "192.168.1.1"
        assert context["userAgent"] == "Mozilla/5.0"
        assert context["locale"] == "en-US"
        assert context["timezone"] == "America/New_York"
    
    def test_create_context_empty(self):
        """Test create_context with no parameters."""
        context = create_context()
        
        assert context == {}
    
    def test_create_context_with_kwargs(self):
        """Test create_context with additional keyword arguments."""
        context = create_context(
            ip="192.168.1.1",
            custom_field="custom_value",
            app_version="1.2.3"
        )
        
        assert context["ip"] == "192.168.1.1"
        assert context["custom_field"] == "custom_value"
        assert context["app_version"] == "1.2.3"
    
    def test_create_context_none_values(self):
        """Test create_context skips None values."""
        context = create_context(
            ip=None,
            user_agent="Mozilla/5.0",
            locale=None
        )
        
        assert "ip" not in context
        assert context["userAgent"] == "Mozilla/5.0"
        assert "locale" not in context