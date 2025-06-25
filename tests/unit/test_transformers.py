"""
Comprehensive tests for Customer.IO data transformers.

Tests cover:
- CustomerTransformer (Spark/Pandas to identify requests, trait normalization)
- EventTransformer (Spark to track requests, ecommerce/mobile event creation)
- GroupTransformer (Spark to group requests)
- BatchTransformer (batch creation, size estimation, optimization)
- ContextTransformer (web/mobile context creation)
- Utility functions (request ID, timestamp, validation)
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import pandas as pd

from utils.transformers import (
    CustomerTransformer,
    EventTransformer,
    GroupTransformer,
    BatchTransformer,
    ContextTransformer,
    add_request_id,
    add_timestamp,
    validate_request_structure
)


class TestCustomerTransformer:
    """Test CustomerTransformer class."""
    
    def test_pandas_to_identify_requests_basic(self, sample_customer_data):
        """Test basic pandas to identify requests transformation."""
        df = pd.DataFrame(sample_customer_data)
        
        requests = CustomerTransformer.pandas_to_identify_requests(
            df=df,
            user_id_col="user_id",
            email_col="email",
            traits_cols=["first_name", "last_name", "plan"]
        )
        
        assert len(requests) == 2
        
        # Check first request
        first_request = requests[0]
        assert first_request["userId"] == "user_001"
        assert first_request["traits"]["email"] == "test1@example.com"
        assert first_request["traits"]["first_name"] == "John"
        assert first_request["traits"]["last_name"] == "Doe"
        assert first_request["traits"]["plan"] == "premium"
    
    def test_pandas_to_identify_requests_with_timestamp(self, sample_customer_data):
        """Test pandas transformation with timestamp."""
        df = pd.DataFrame(sample_customer_data)
        
        requests = CustomerTransformer.pandas_to_identify_requests(
            df=df,
            timestamp_col="created_at"
        )
        
        assert len(requests) == 2
        assert "timestamp" in requests[0]
        assert requests[0]["timestamp"].startswith("2024-01-15")
    
    def test_pandas_to_identify_requests_missing_columns(self):
        """Test pandas transformation with missing columns."""
        df = pd.DataFrame([{"some_col": "value"}])
        
        requests = CustomerTransformer.pandas_to_identify_requests(
            df=df,
            user_id_col="missing_user_id",
            email_col="missing_email"
        )
        
        assert len(requests) == 1
        assert requests[0]["userId"] is None
        assert requests[0]["traits"] == {}
    
    def test_pandas_to_identify_requests_with_na_values(self):
        """Test pandas transformation with NaN values."""
        df = pd.DataFrame([
            {"user_id": "user_1", "email": "test@example.com", "name": "John"},
            {"user_id": "user_2", "email": None, "name": "Jane"}
        ])
        
        requests = CustomerTransformer.pandas_to_identify_requests(
            df=df,
            traits_cols=["name", "email"]
        )
        
        assert len(requests) == 2
        assert "email" in requests[0]["traits"]
        assert "email" not in requests[1]["traits"]  # NaN should be excluded
        assert requests[1]["traits"]["name"] == "Jane"
    
    def test_spark_to_identify_requests_basic(self, mock_spark_session, sample_customer_data):
        """Test basic spark to identify requests transformation."""
        # Mock Spark DataFrame
        mock_df = Mock()
        mock_rows = []
        
        for customer in sample_customer_data:
            mock_row = Mock()
            mock_row.asDict.return_value = {
                "user_id": customer["user_id"],
                "email": customer["email"],
                "traits": customer["traits"],
                "created_at": customer["created_at"]
            }
            # Set up attribute access
            for key, value in mock_row.asDict().items():
                setattr(mock_row, key, value)
            mock_rows.append(mock_row)
        
        mock_df.collect.return_value = mock_rows
        
        requests = CustomerTransformer.spark_to_identify_requests(
            df=mock_df,
            user_id_col="user_id",
            email_col="email",
            traits_cols=["first_name", "last_name"],
            timestamp_col="created_at"
        )
        
        assert len(requests) == 2
        assert requests[0]["userId"] == "user_001"
        assert requests[0]["traits"]["email"] == "test1@example.com"
    
    def test_spark_to_identify_requests_missing_columns(self, mock_spark_session):
        """Test spark transformation with missing columns."""
        # Mock Spark DataFrame with missing columns
        mock_df = Mock()
        mock_row = Mock()
        mock_row.asDict.return_value = {"some_col": "value"}
        mock_df.collect.return_value = [mock_row]
        
        requests = CustomerTransformer.spark_to_identify_requests(
            df=mock_df,
            user_id_col="missing_user_id",
            email_col="missing_email"
        )
        
        assert len(requests) == 1
        assert requests[0]["userId"] is None
        assert requests[0]["traits"] == {}
    
    def test_normalize_traits_basic(self):
        """Test basic trait normalization."""
        traits = {
            "string_val": "test",
            "int_val": 123,
            "float_val": 45.67,
            "bool_val": True,
            "none_val": None
        }
        
        normalized = CustomerTransformer.normalize_traits(traits)
        
        assert normalized["string_val"] == "test"
        assert normalized["int_val"] == "123"
        assert normalized["float_val"] == "45.67"
        assert normalized["bool_val"] == "True"
        assert "none_val" not in normalized  # None values should be excluded
    
    def test_normalize_traits_datetime(self):
        """Test trait normalization with datetime."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        traits = {"created_at": timestamp}
        
        normalized = CustomerTransformer.normalize_traits(traits)
        
        assert normalized["created_at"] == "2024-01-15T12:30:00+00:00"
    
    def test_normalize_traits_complex_types(self):
        """Test trait normalization with complex types."""
        traits = {
            "list_val": ["item1", "item2"],
            "dict_val": {"key": "value"},
            "custom_obj": object()
        }
        
        normalized = CustomerTransformer.normalize_traits(traits)
        
        assert normalized["list_val"] == '["item1", "item2"]'
        assert normalized["dict_val"] == '{"key": "value"}'
        assert "custom_obj" in normalized  # Should be converted to string


class TestEventTransformer:
    """Test EventTransformer class."""
    
    def test_spark_to_track_requests_basic(self, mock_spark_session, sample_event_data):
        """Test basic spark to track requests transformation."""
        # Mock Spark DataFrame
        mock_df = Mock()
        mock_rows = []
        
        for event in sample_event_data:
            mock_row = Mock()
            mock_row.asDict.return_value = {
                "user_id": event["user_id"],
                "event_name": event["event_name"],
                "timestamp": event["timestamp"],
                "product_id": event["properties"].get("product_id"),
                "category": event["properties"].get("category")
            }
            # Set up attribute access
            for key, value in mock_row.asDict().items():
                setattr(mock_row, key, value)
            mock_rows.append(mock_row)
        
        mock_df.collect.return_value = mock_rows
        
        requests = EventTransformer.spark_to_track_requests(
            df=mock_df,
            user_id_col="user_id",
            event_name_col="event_name",
            properties_cols=["product_id", "category"],
            timestamp_col="timestamp"
        )
        
        assert len(requests) == 2
        assert requests[0]["userId"] == "user_001"
        assert requests[0]["event"] == "Product Viewed"
        assert requests[0]["properties"]["product_id"] == "prod_123"
        assert requests[0]["properties"]["category"] == "electronics"
    
    def test_spark_to_track_requests_missing_event_name(self, mock_spark_session):
        """Test spark transformation with missing event name."""
        mock_df = Mock()
        mock_row = Mock()
        mock_row.asDict.return_value = {"user_id": "user_1"}
        setattr(mock_row, "user_id", "user_1")
        mock_df.collect.return_value = [mock_row]
        
        requests = EventTransformer.spark_to_track_requests(
            df=mock_df,
            event_name_col="missing_event"
        )
        
        assert len(requests) == 1
        assert requests[0]["event"] == "Unknown Event"
    
    def test_create_ecommerce_event_product_viewed(self):
        """Test creating a product viewed ecommerce event."""
        with patch('utils.transformers.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            event = EventTransformer.create_ecommerce_event(
                event_name="Product Viewed",
                user_id="user_123",
                product_id="prod_456",
                price=29.99,
                category="electronics"
            )
            
            assert event["event"] == "Product Viewed"
            assert event["userId"] == "user_123"
            assert event["properties"]["product_id"] == "prod_456"
            assert event["properties"]["price"] == 29.99
            assert event["properties"]["currency"] == "USD"
            assert event["properties"]["category"] == "electronics"
    
    def test_create_ecommerce_event_order_completed(self):
        """Test creating an order completed ecommerce event."""
        event = EventTransformer.create_ecommerce_event(
            event_name="Order Completed",
            user_id="user_123",
            order_id="order_789",
            price=99.99,
            quantity=2,
            currency="EUR"
        )
        
        assert event["event"] == "Order Completed"
        assert event["properties"]["order_id"] == "order_789"
        assert event["properties"]["price"] == 99.99
        assert event["properties"]["quantity"] == 2
        assert event["properties"]["currency"] == "EUR"
    
    def test_create_ecommerce_event_with_anonymous_id(self):
        """Test creating ecommerce event with anonymous ID."""
        event = EventTransformer.create_ecommerce_event(
            event_name="Product Viewed",
            anonymous_id="anon_456",
            product_id="prod_123"
        )
        
        assert event["anonymousId"] == "anon_456"
        assert "userId" not in event
    
    def test_create_mobile_app_event_basic(self):
        """Test creating a basic mobile app event."""
        with patch('utils.transformers.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            event = EventTransformer.create_mobile_app_event(
                event_name="App Opened",
                user_id="user_123",
                app_version="1.2.3",
                os_version="iOS 15.0",
                device_model="iPhone 12"
            )
            
            assert event["event"] == "App Opened"
            assert event["userId"] == "user_123"
            assert event["properties"]["app_version"] == "1.2.3"
            assert event["properties"]["os_version"] == "iOS 15.0"
            assert event["properties"]["device_model"] == "iPhone 12"
    
    def test_create_mobile_app_event_minimal(self):
        """Test creating mobile app event with minimal parameters."""
        event = EventTransformer.create_mobile_app_event(
            event_name="Screen Viewed",
            anonymous_id="anon_789"
        )
        
        assert event["event"] == "Screen Viewed"
        assert event["anonymousId"] == "anon_789"
        assert "userId" not in event
        assert isinstance(event["properties"], dict)


class TestGroupTransformer:
    """Test GroupTransformer class."""
    
    def test_spark_to_group_requests_basic(self, mock_spark_session):
        """Test basic spark to group requests transformation."""
        # Mock Spark DataFrame
        mock_df = Mock()
        mock_row = Mock()
        mock_row.asDict.return_value = {
            "user_id": "user_123",
            "group_id": "company_456",
            "company_name": "Acme Corp",
            "created_at": datetime(2024, 1, 15, tzinfo=timezone.utc)
        }
        # Set up attribute access
        for key, value in mock_row.asDict().items():
            setattr(mock_row, key, value)
        mock_df.collect.return_value = [mock_row]
        
        requests = GroupTransformer.spark_to_group_requests(
            df=mock_df,
            user_id_col="user_id",
            group_id_col="group_id",
            traits_cols=["company_name"],
            timestamp_col="created_at"
        )
        
        assert len(requests) == 1
        assert requests[0]["userId"] == "user_123"
        assert requests[0]["groupId"] == "company_456"
        assert requests[0]["traits"]["company_name"] == "Acme Corp"
        assert "timestamp" in requests[0]
    
    def test_spark_to_group_requests_missing_columns(self, mock_spark_session):
        """Test spark group transformation with missing columns."""
        mock_df = Mock()
        mock_row = Mock()
        mock_row.asDict.return_value = {"some_col": "value"}
        mock_df.collect.return_value = [mock_row]
        
        requests = GroupTransformer.spark_to_group_requests(
            df=mock_df,
            user_id_col="missing_user_id",
            group_id_col="missing_group_id"
        )
        
        assert len(requests) == 1
        assert requests[0]["userId"] is None
        assert requests[0]["groupId"] is None
        assert requests[0]["traits"] == {}


class TestBatchTransformer:
    """Test BatchTransformer class."""
    
    def test_create_batch_request_basic(self):
        """Test creating basic batch request."""
        identify_requests = [
            {"userId": "user_1", "traits": {"email": "user1@example.com"}},
            {"userId": "user_2", "traits": {"email": "user2@example.com"}}
        ]
        track_requests = [
            {"userId": "user_1", "event": "Product Viewed"}
        ]
        group_requests = [
            {"userId": "user_1", "groupId": "company_1"}
        ]
        
        batches = BatchTransformer.create_batch_request(
            identify_requests=identify_requests,
            track_requests=track_requests,
            group_requests=group_requests,
            max_batch_size=10
        )
        
        assert len(batches) == 1  # All should fit in one batch
        batch = batches[0]["batch"]
        assert len(batch) == 4  # 2 identify + 1 track + 1 group
        
        # Check types are added correctly
        types = [req["type"] for req in batch]
        assert types.count("identify") == 2
        assert types.count("track") == 1
        assert types.count("group") == 1
    
    def test_create_batch_request_size_limit(self):
        """Test batch creation with size limits."""
        identify_requests = [
            {"userId": f"user_{i}", "traits": {"email": f"user{i}@example.com"}}
            for i in range(5)
        ]
        
        batches = BatchTransformer.create_batch_request(
            identify_requests=identify_requests,
            max_batch_size=2
        )
        
        assert len(batches) == 3  # 5 requests / 2 per batch = 3 batches
        assert len(batches[0]["batch"]) == 2
        assert len(batches[1]["batch"]) == 2
        assert len(batches[2]["batch"]) == 1
    
    def test_create_batch_request_empty_inputs(self):
        """Test batch creation with empty inputs."""
        batches = BatchTransformer.create_batch_request()
        
        assert batches == []
    
    def test_estimate_batch_size(self):
        """Test batch size estimation."""
        requests = [
            {"type": "identify", "userId": "user_1", "traits": {"email": "test@example.com"}},
            {"type": "track", "userId": "user_2", "event": "Product Viewed"}
        ]
        
        size = BatchTransformer.estimate_batch_size(requests)
        
        assert isinstance(size, int)
        assert size > 0
        
        # Verify it matches actual JSON encoding
        expected_size = len(json.dumps({"batch": requests}).encode('utf-8'))
        assert size == expected_size
    
    def test_optimize_batch_sizes_under_limit(self):
        """Test batch optimization when all requests fit in one batch."""
        requests = [
            {"type": "identify", "userId": f"user_{i}"}
            for i in range(5)
        ]
        
        batches = BatchTransformer.optimize_batch_sizes(
            requests=requests,
            max_size_bytes=10 * 1024  # 10KB - should be plenty
        )
        
        assert len(batches) == 1
        assert len(batches[0]) == 5
    
    def test_optimize_batch_sizes_over_limit(self):
        """Test batch optimization when requests exceed size limit."""
        # Create requests with large data to exceed size limit
        requests = [
            {"type": "identify", "userId": f"user_{i}", "large_data": "x" * 1000}
            for i in range(10)
        ]
        
        batches = BatchTransformer.optimize_batch_sizes(
            requests=requests,
            max_size_bytes=2048  # 2KB - small limit
        )
        
        assert len(batches) > 1  # Should be split into multiple batches
        
        # Verify each batch is within size limit
        for batch in batches:
            size = BatchTransformer.estimate_batch_size(batch)
            assert size <= 2048
    
    def test_optimize_batch_sizes_empty_requests(self):
        """Test batch optimization with empty request list."""
        batches = BatchTransformer.optimize_batch_sizes([])
        
        assert batches == []


class TestContextTransformer:
    """Test ContextTransformer class."""
    
    def test_create_web_context_full(self):
        """Test creating full web context."""
        context = ContextTransformer.create_web_context(
            ip="192.168.1.1",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            url="https://example.com/page",
            referrer="https://google.com",
            locale="en-US",
            timezone="America/New_York"
        )
        
        assert context["ip"] == "192.168.1.1"
        assert context["userAgent"] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        assert context["locale"] == "en-US"
        assert context["timezone"] == "America/New_York"
        assert context["page"]["url"] == "https://example.com/page"
        assert context["page"]["referrer"] == "https://google.com"
    
    def test_create_web_context_minimal(self):
        """Test creating minimal web context."""
        context = ContextTransformer.create_web_context(ip="192.168.1.1")
        
        assert context["ip"] == "192.168.1.1"
        assert "page" not in context  # No page info provided
        assert "userAgent" not in context
    
    def test_create_web_context_empty(self):
        """Test creating empty web context."""
        context = ContextTransformer.create_web_context()
        
        assert context == {}
    
    def test_create_mobile_context_full(self):
        """Test creating full mobile context."""
        context = ContextTransformer.create_mobile_context(
            app_name="My App",
            app_version="1.2.3",
            os_name="iOS",
            os_version="15.0",
            device_model="iPhone 12",
            device_id="device_123",
            locale="en-US",
            timezone="America/New_York"
        )
        
        assert context["locale"] == "en-US"
        assert context["timezone"] == "America/New_York"
        assert context["app"]["name"] == "My App"
        assert context["app"]["version"] == "1.2.3"
        assert context["device"]["model"] == "iPhone 12"
        assert context["device"]["id"] == "device_123"
        assert context["os"]["name"] == "iOS"
        assert context["os"]["version"] == "15.0"
    
    def test_create_mobile_context_partial(self):
        """Test creating partial mobile context."""
        context = ContextTransformer.create_mobile_context(
            app_name="My App",
            device_model="iPhone 12"
        )
        
        assert context["app"]["name"] == "My App"
        assert "version" not in context["app"]  # Not provided
        assert context["device"]["model"] == "iPhone 12"
        assert "id" not in context["device"]  # Not provided
        assert "os" not in context  # No OS info provided
    
    def test_create_mobile_context_empty(self):
        """Test creating empty mobile context."""
        context = ContextTransformer.create_mobile_context()
        
        assert context == {}


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_add_request_id_new_context(self):
        """Test adding request ID to request without existing context."""
        request = {"userId": "user_123", "event": "Test Event"}
        
        result = add_request_id(request)
        
        assert "context" in result
        assert "requestId" in result["context"]
        assert len(result["context"]["requestId"]) == 36  # UUID4 length
        assert result["userId"] == "user_123"  # Original data preserved
        assert request == {"userId": "user_123", "event": "Test Event"}  # Original unchanged
    
    def test_add_request_id_existing_context(self):
        """Test adding request ID to request with existing context."""
        request = {
            "userId": "user_123",
            "context": {"existingField": "value"}
        }
        
        result = add_request_id(request)
        
        assert result["context"]["existingField"] == "value"
        assert "requestId" in result["context"]
    
    def test_add_timestamp_no_existing_timestamp(self):
        """Test adding timestamp when none exists."""
        request = {"userId": "user_123", "event": "Test Event"}
        custom_timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = add_timestamp(request, custom_timestamp)
        
        assert result["timestamp"] == "2024-01-15T12:30:00+00:00"
        assert result["userId"] == "user_123"
        assert request == {"userId": "user_123", "event": "Test Event"}  # Original unchanged
    
    def test_add_timestamp_existing_timestamp(self):
        """Test adding timestamp when one already exists."""
        original_timestamp = "2023-01-01T00:00:00+00:00"
        request = {"userId": "user_123", "timestamp": original_timestamp}
        
        result = add_timestamp(request)
        
        assert result["timestamp"] == original_timestamp  # Should not be overridden
    
    def test_add_timestamp_default_now(self):
        """Test adding timestamp with default current time."""
        request = {"userId": "user_123"}
        
        with patch('utils.transformers.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            result = add_timestamp(request)
            
            assert result["timestamp"] == "2024-01-15T12:30:00+00:00"
    
    def test_validate_request_structure_identify_valid(self):
        """Test validating valid identify request structure."""
        request = {
            "userId": "user_123",
            "traits": {"email": "test@example.com"}
        }
        
        assert validate_request_structure(request, "identify") is True
    
    def test_validate_request_structure_identify_anonymous(self):
        """Test validating identify request with anonymous ID."""
        request = {
            "anonymousId": "anon_456",
            "traits": {"plan": "premium"}
        }
        
        assert validate_request_structure(request, "identify") is True
    
    def test_validate_request_structure_track_valid(self):
        """Test validating valid track request structure."""
        request = {
            "userId": "user_123",
            "event": "Product Viewed",
            "properties": {"product_id": "prod_456"}
        }
        
        assert validate_request_structure(request, "track") is True
    
    def test_validate_request_structure_track_missing_event(self):
        """Test validating track request missing event name."""
        request = {"userId": "user_123"}
        
        assert validate_request_structure(request, "track") is False
    
    def test_validate_request_structure_group_valid(self):
        """Test validating valid group request structure."""
        request = {
            "userId": "user_123",
            "groupId": "company_456",
            "traits": {"name": "Acme Corp"}
        }
        
        assert validate_request_structure(request, "group") is True
    
    def test_validate_request_structure_group_missing_group_id(self):
        """Test validating group request missing group ID."""
        request = {"userId": "user_123"}
        
        assert validate_request_structure(request, "group") is False
    
    def test_validate_request_structure_no_user_identification(self):
        """Test validating request without user identification."""
        request = {"event": "Test Event"}
        
        assert validate_request_structure(request, "track") is False
        assert validate_request_structure(request, "identify") is False
        assert validate_request_structure(request, "group") is False
    
    def test_validate_request_structure_unknown_type(self):
        """Test validating request with unknown type."""
        request = {"userId": "user_123"}
        
        assert validate_request_structure(request, "unknown") is False