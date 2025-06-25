"""
Comprehensive tests for Customer.IO Event Manager.

Tests cover:
- Event template registration and management
- Standard event creation and validation
- Ecommerce event creation with semantic schemas
- Session-based event tracking
- Batch event processing with optimization
- Event context enrichment
- Error handling and fallback mechanisms
- Metrics and monitoring
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from pydantic import ValidationError

from utils.event_manager import (
    EventCategory,
    EventPriority,
    EventTemplate,
    EventSession,
    EventManager
)
from utils.validators import ProductViewedProperties, OrderCompletedProperties
from utils.error_handlers import CustomerIOError


class TestEventCategory:
    """Test EventCategory enum."""
    
    def test_event_category_values(self):
        """Test all event category values."""
        assert EventCategory.NAVIGATION == "navigation"
        assert EventCategory.ECOMMERCE == "ecommerce"
        assert EventCategory.ENGAGEMENT == "engagement"
        assert EventCategory.LIFECYCLE == "lifecycle"
        assert EventCategory.FEATURE_USAGE == "feature_usage"
        assert EventCategory.CUSTOM == "custom"
    
    def test_event_category_membership(self):
        """Test event category membership."""
        valid_categories = [cat.value for cat in EventCategory]
        assert "navigation" in valid_categories
        assert "invalid_category" not in valid_categories


class TestEventPriority:
    """Test EventPriority enum."""
    
    def test_event_priority_values(self):
        """Test all event priority values."""
        assert EventPriority.LOW == "low"
        assert EventPriority.NORMAL == "normal"
        assert EventPriority.HIGH == "high"
        assert EventPriority.CRITICAL == "critical"
    
    def test_event_priority_membership(self):
        """Test event priority membership."""
        valid_priorities = [priority.value for priority in EventPriority]
        assert "normal" in valid_priorities
        assert "invalid_priority" not in valid_priorities


class TestEventTemplate:
    """Test EventTemplate data model."""
    
    def test_valid_event_template(self):
        """Test valid event template creation."""
        template = EventTemplate(
            name="Test Event",
            category=EventCategory.CUSTOM,
            priority=EventPriority.HIGH,
            required_properties=["prop1", "prop2"],
            default_properties={"default_prop": "value"}
        )
        
        assert template.name == "Test Event"
        assert template.category == "custom"  # Should be converted to string
        assert template.priority == "high"
        assert template.required_properties == ["prop1", "prop2"]
        assert template.default_properties == {"default_prop": "value"}
    
    def test_required_name_field(self):
        """Test that name field is required."""
        with pytest.raises(ValidationError, match="field required"):
            EventTemplate(category=EventCategory.CUSTOM)
    
    def test_required_category_field(self):
        """Test that category field is required."""
        with pytest.raises(ValidationError, match="field required"):
            EventTemplate(name="Test Event")
    
    def test_default_priority(self):
        """Test that priority defaults to NORMAL."""
        template = EventTemplate(
            name="Test Event",
            category=EventCategory.CUSTOM
        )
        
        assert template.priority == "normal"
    
    def test_default_empty_lists(self):
        """Test that lists default to empty."""
        template = EventTemplate(
            name="Test Event",
            category=EventCategory.CUSTOM
        )
        
        assert template.required_properties == []
        assert template.default_properties == {}
    
    def test_enum_value_conversion(self):
        """Test that enum values are converted to strings."""
        template = EventTemplate(
            name="Test Event",
            category=EventCategory.ECOMMERCE,
            priority=EventPriority.CRITICAL
        )
        
        assert isinstance(template.category, str)
        assert isinstance(template.priority, str)
        assert template.category == "ecommerce"
        assert template.priority == "critical"


class TestEventSession:
    """Test EventSession data model."""
    
    def test_valid_event_session(self):
        """Test valid event session creation."""
        now = datetime.now(timezone.utc)
        session = EventSession(
            session_id="session_123",
            user_id="user_456",
            platform="web",
            started_at=now,
            last_activity=now,
            events_count=5
        )
        
        assert session.session_id == "session_123"
        assert session.user_id == "user_456"
        assert session.platform == "web"
        assert session.started_at == now
        assert session.last_activity == now
        assert session.events_count == 5
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError, match="field required"):
            EventSession()
    
    def test_session_id_validation_empty(self):
        """Test session ID validation with empty string."""
        now = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError, match="Session ID cannot be empty"):
            EventSession(
                session_id="",
                user_id="user_456",
                platform="web",
                started_at=now,
                last_activity=now
            )
    
    def test_session_id_normalization(self):
        """Test session ID whitespace normalization."""
        now = datetime.now(timezone.utc)
        session = EventSession(
            session_id="  session_123  ",
            user_id="user_456",
            platform="web",
            started_at=now,
            last_activity=now
        )
        
        assert session.session_id == "session_123"
    
    def test_default_events_count(self):
        """Test that events_count defaults to 0."""
        now = datetime.now(timezone.utc)
        session = EventSession(
            session_id="session_123",
            user_id="user_456",
            platform="web",
            started_at=now,
            last_activity=now
        )
        
        assert session.events_count == 0


class TestEventManager:
    """Test EventManager class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock CustomerIOClient."""
        return Mock()
    
    @pytest.fixture
    def event_manager(self, mock_client):
        """Create EventManager with mock client."""
        return EventManager(mock_client)
    
    def test_event_manager_initialization(self, mock_client):
        """Test EventManager initialization."""
        manager = EventManager(mock_client)
        
        assert manager.client == mock_client
        assert manager.logger is not None
        assert len(manager.templates) > 0  # Should have default templates
    
    def test_default_templates_registered(self, event_manager):
        """Test that default templates are registered."""
        expected_templates = [
            "page_viewed", "screen_viewed", "product_viewed", 
            "order_completed", "feature_used", "content_engaged"
        ]
        
        for template_name in expected_templates:
            assert template_name in event_manager.templates
    
    def test_register_custom_template(self, event_manager):
        """Test registering a custom event template."""
        custom_template = EventTemplate(
            name="Custom Event",
            category=EventCategory.CUSTOM,
            priority=EventPriority.HIGH,
            required_properties=["custom_prop"],
            default_properties={"default": "value"}
        )
        
        event_manager.register_template(custom_template)
        
        assert "custom_event" in event_manager.templates
        template = event_manager.templates["custom_event"]
        assert template.name == "Custom Event"
        assert template.category == "custom"
        assert template.priority == "high"
    
    def test_create_event_with_template(self, event_manager):
        """Test creating an event using a template."""
        event = event_manager.create_event(
            user_id="user_123",
            template_name="page_viewed",
            properties={
                "page_name": "Home",
                "url": "https://example.com",
                "load_time": 1.5
            }
        )
        
        assert event["userId"] == "user_123"
        assert event["event"] == "Page Viewed"
        assert event["properties"]["page_name"] == "Home"
        assert event["properties"]["url"] == "https://example.com"
        assert event["properties"]["platform"] == "web"  # Default property
        assert "timestamp" in event
    
    def test_create_event_missing_template(self, event_manager):
        """Test creating event with non-existent template."""
        with pytest.raises(ValueError, match="Event template 'nonexistent' not found"):
            event_manager.create_event(
                user_id="user_123",
                template_name="nonexistent",
                properties={}
            )
    
    def test_create_event_missing_required_properties(self, event_manager):
        """Test creating event with missing required properties."""
        with pytest.raises(ValueError, match="Missing required properties"):
            event_manager.create_event(
                user_id="user_123",
                template_name="page_viewed",
                properties={"page_name": "Home"}  # Missing 'url'
            )
    
    def test_create_event_with_context(self, event_manager):
        """Test creating event with context."""
        context = {"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        
        event = event_manager.create_event(
            user_id="user_123",
            template_name="page_viewed",
            properties={"page_name": "Home", "url": "https://example.com"},
            context=context
        )
        
        assert event["context"] == context
    
    def test_create_event_custom_timestamp(self, event_manager):
        """Test creating event with custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        event = event_manager.create_event(
            user_id="user_123",
            template_name="page_viewed",
            properties={"page_name": "Home", "url": "https://example.com"},
            timestamp=custom_time
        )
        
        assert event["timestamp"] == custom_time
    
    @patch('utils.event_manager.validate_request_size', return_value=True)
    def test_send_event_success(self, mock_validate, event_manager):
        """Test successful event sending."""
        event_data = {
            "userId": "user_123",
            "event": "Test Event",
            "properties": {"test": "value"},
            "timestamp": datetime.now(timezone.utc)
        }
        
        event_manager.client.track.return_value = {"status": "success"}
        
        result = event_manager.send_event(event_data)
        
        assert result == {"status": "success"}
        event_manager.client.track.assert_called_once()
    
    @patch('utils.event_manager.validate_request_size', return_value=False)
    def test_send_event_size_validation_failure(self, mock_validate, event_manager):
        """Test event sending with size validation failure."""
        event_data = {
            "userId": "user_123",
            "event": "Large Event",
            "properties": {"large_data": "x" * 50000},
            "timestamp": datetime.now(timezone.utc)
        }
        
        with pytest.raises(ValueError, match="Event size exceeds 32KB limit"):
            event_manager.send_event(event_data)
    
    def test_send_event_api_error(self, event_manager):
        """Test event sending with API error."""
        event_data = {
            "userId": "user_123",
            "event": "Test Event",
            "properties": {"test": "value"},
            "timestamp": datetime.now(timezone.utc)
        }
        
        event_manager.client.track.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            event_manager.send_event(event_data)
    
    def test_send_events_batch_success(self, event_manager):
        """Test successful batch event sending."""
        events = [
            {
                "userId": "user_123",
                "event": "Event 1",
                "properties": {"test": "value1"},
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "userId": "user_123",
                "event": "Event 2",
                "properties": {"test": "value2"},
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        event_manager.client.batch.return_value = {"status": "success"}
        
        results = event_manager.send_events_batch(events)
        
        assert len(results) == 1  # Should be one batch
        assert results[0]["status"] == "success"
        assert results[0]["count"] == 2
        event_manager.client.batch.assert_called_once()
    
    def test_send_events_batch_partial_failure(self, event_manager):
        """Test batch sending with partial failures."""
        events = [
            {
                "userId": "user_123",
                "event": "Event 1",
                "properties": {"test": "value1"},
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "userId": "user_123",
                "event": "Event 2",
                "properties": {"test": "value2"},
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        # First call succeeds, second fails (would happen with multiple batches)
        event_manager.client.batch.side_effect = [
            {"status": "success"},
            CustomerIOError("API error")
        ]
        
        # Force multiple batches by setting small batch size
        with patch('utils.event_manager.BatchTransformer.optimize_batch_sizes') as mock_optimize:
            mock_optimize.return_value = [
                [{"type": "track", "userId": "user_123", "event": "Event 1"}],
                [{"type": "track", "userId": "user_123", "event": "Event 2"}]
            ]
            
            results = event_manager.send_events_batch(events)
        
        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert results[1]["status"] == "failed"
        assert "error" in results[1]
    
    def test_create_ecommerce_event_product_viewed(self, event_manager):
        """Test creating product viewed ecommerce event."""
        product_data = {
            "product_id": "prod_123",
            "name": "Test Product",
            "price": 29.99,
            "currency": "USD"
        }
        
        event = event_manager.create_ecommerce_event(
            user_id="user_123",
            event_type="product_viewed",
            product_data=product_data,
            category="electronics"
        )
        
        assert event["event"] == "Product Viewed"
        assert event["properties"]["product_id"] == "prod_123"
        assert event["properties"]["price"] == 29.99
        assert event["properties"]["category"] == "electronics"
    
    def test_create_ecommerce_event_order_completed(self, event_manager):
        """Test creating order completed ecommerce event."""
        order_data = {
            "order_id": "order_456",
            "total": 59.99,
            "currency": "USD",
            "products": [{"product_id": "prod_123", "quantity": 2}]
        }
        
        event = event_manager.create_ecommerce_event(
            user_id="user_123",
            event_type="order_completed",
            product_data=order_data,
            payment_method="credit_card"
        )
        
        assert event["event"] == "Order Completed"
        assert event["properties"]["order_id"] == "order_456"
        assert event["properties"]["total"] == 59.99
        assert event["properties"]["payment_method"] == "credit_card"
    
    def test_create_session_events(self, event_manager):
        """Test creating session-based events."""
        session = EventSession(
            session_id="session_123",
            user_id="user_456",
            platform="web",
            started_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc)
        )
        
        events_data = [
            {
                "template_name": "page_viewed",
                "properties": {"page_name": "Home", "url": "/"},
                "time_offset_seconds": 0
            },
            {
                "template_name": "page_viewed",
                "properties": {"page_name": "Products", "url": "/products"},
                "time_offset_seconds": 30
            }
        ]
        
        # Register session_started template for test
        session_template = EventTemplate(
            name="Session Started",
            category=EventCategory.LIFECYCLE,
            required_properties=["session_id", "platform"],
            default_properties={}
        )
        event_manager.register_template(session_template)
        
        session_events = event_manager.create_session_events(session, events_data)
        
        assert len(session_events) == 3  # session_start + 2 page views
        assert session_events[0]["event"] == "Session Started"
        assert all("session_id" in event["properties"] for event in session_events)
        assert session.events_count == 3
    
    def test_create_enriched_event_web(self, event_manager):
        """Test creating enriched web event."""
        with patch('utils.event_manager.ContextTransformer.create_web_context') as mock_context:
            mock_context.return_value = {"platform": "web", "ip": "192.168.1.1"}
            
            event = event_manager.create_enriched_event(
                user_id="user_123",
                template_name="page_viewed",
                properties={"page_name": "Home", "url": "https://example.com"},
                platform="web",
                ip="192.168.1.1"
            )
            
            assert "context" in event
            assert event["context"]["platform"] == "web"
            mock_context.assert_called_once()
    
    def test_create_enriched_event_mobile(self, event_manager):
        """Test creating enriched mobile event."""
        with patch('utils.event_manager.ContextTransformer.create_mobile_context') as mock_context:
            mock_context.return_value = {"platform": "mobile", "app_version": "1.0.0"}
            
            event = event_manager.create_enriched_event(
                user_id="user_123",
                template_name="screen_viewed",
                properties={"screen_name": "Home"},
                platform="mobile",
                app_version="1.0.0"
            )
            
            assert "context" in event
            assert event["context"]["platform"] == "mobile"
            mock_context.assert_called_once()
    
    def test_send_event_with_fallback_success(self, event_manager):
        """Test event sending with fallback - success case."""
        event_data = {
            "userId": "user_123",
            "event": "Test Event",
            "properties": {"test": "value"},
            "timestamp": datetime.now(timezone.utc)
        }
        
        event_manager.client.track.return_value = {"status": "success"}
        
        result = event_manager.send_event_with_fallback(event_data)
        
        assert result["status"] == "success"
    
    def test_send_event_with_fallback_failure(self, event_manager):
        """Test event sending with fallback - failure case."""
        event_data = {
            "userId": "user_123",
            "event": "Test Event",
            "properties": {"test": "value"},
            "timestamp": datetime.now(timezone.utc)
        }
        
        event_manager.client.track.side_effect = CustomerIOError("API error")
        
        result = event_manager.send_event_with_fallback(event_data)
        
        assert result["status"] == "fallback_saved"
        assert "message" in result
    
    def test_get_metrics(self, event_manager):
        """Test getting event manager metrics."""
        metrics = event_manager.get_metrics()
        
        assert "templates" in metrics
        assert "client" in metrics
        assert metrics["templates"]["registered_count"] > 0
        assert len(metrics["templates"]["template_names"]) > 0
        assert "rate_limit" in metrics["client"]
        assert "base_url" in metrics["client"]
        assert "max_retries" in metrics["client"]