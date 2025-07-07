"""Tests for webhook processing functions."""
import pytest
import json
import hmac
import hashlib
import time
from src.webhooks.processor import (
    verify_signature, 
    parse_event, 
    get_event_type,
    validate_webhook_headers,
    route_webhook_event
)


class TestWebhookProcessor:
    """Test webhook processing functionality."""
    
    def test_verify_signature_valid(self):
        """Test webhook signature verification with valid signature."""
        payload = '{"event": "email_delivered", "data": {"customer_id": "123"}}'
        secret = "webhook_secret_key"
        timestamp = str(int(time.time()))
        
        # Generate valid signature with Customer.io format: v0:timestamp:body
        signature_string = f"v0:{timestamp}:{payload}"
        signature_hash = hmac.new(
            secret.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        signature = f"v0={signature_hash}"
        
        result = verify_signature(payload, signature, timestamp, secret)
        assert result is True
    
    def test_verify_signature_invalid(self):
        """Test webhook signature verification with invalid signature."""
        payload = '{"event": "email_delivered", "data": {"customer_id": "123"}}'
        secret = "webhook_secret_key"
        timestamp = str(int(time.time()))
        invalid_signature = "v0=invalid_signature_hash"
        
        result = verify_signature(payload, invalid_signature, timestamp, secret)
        assert result is False
    
    def test_verify_signature_missing_prefix(self):
        """Test webhook signature verification with missing v0= prefix."""
        payload = '{"event": "email_delivered"}'
        secret = "webhook_secret_key"
        timestamp = str(int(time.time()))
        signature_without_prefix = "abcdef123456"
        
        result = verify_signature(payload, signature_without_prefix, timestamp, secret)
        assert result is False
    
    def test_verify_signature_empty_payload(self):
        """Test webhook signature verification with empty payload."""
        result = verify_signature("", "v0=test", "12345", "secret")
        assert result is False
    
    def test_verify_signature_expired_timestamp(self):
        """Test webhook signature verification with expired timestamp."""
        payload = '{"event": "test"}'
        secret = "secret"
        # Timestamp from 10 minutes ago
        old_timestamp = str(int(time.time()) - 600)
        
        # Generate otherwise valid signature
        signature_string = f"v0:{old_timestamp}:{payload}"
        signature_hash = hmac.new(
            secret.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        signature = f"v0={signature_hash}"
        
        result = verify_signature(payload, signature, old_timestamp, secret)
        assert result is False
    
    def test_parse_event_valid_json(self):
        """Test parsing valid webhook event JSON."""
        payload = {
            "event_id": "evt_123",
            "event_type": "email_delivered",
            "timestamp": 1640995200,
            "data": {
                "customer_id": "cust_123",
                "delivery_id": "del_456"
            }
        }
        
        json_payload = json.dumps(payload)
        result = parse_event(json_payload)
        
        assert result == payload
        assert result["event_type"] == "email_delivered"
        assert result["data"]["customer_id"] == "cust_123"
    
    def test_parse_event_invalid_json(self):
        """Test parsing invalid JSON payload."""
        invalid_json = '{"event": "test", invalid}'
        
        with pytest.raises(ValueError):
            parse_event(invalid_json)
    
    def test_parse_event_empty_payload(self):
        """Test parsing empty payload."""
        with pytest.raises(ValueError):
            parse_event("")
    
    def test_get_event_type_email_delivered(self):
        """Test getting event type from email delivered event."""
        event = {
            "object_type": "email",
            "metric": "delivered",
            "data": {"customer_id": "123"}
        }
        
        object_type, metric = get_event_type(event)
        assert object_type == "email"
        assert metric == "delivered"
    
    def test_get_event_type_customer_subscribed(self):
        """Test getting event type from customer subscription event."""
        event = {
            "object_type": "customer",
            "metric": "subscribed",
            "data": {"customer_id": "123"}
        }
        
        object_type, metric = get_event_type(event)
        assert object_type == "customer"
        assert metric == "subscribed"
    
    def test_get_event_type_missing_field(self):
        """Test getting event type when object_type is missing."""
        event = {
            "metric": "delivered",
            "data": {"customer_id": "123"}
        }
        
        with pytest.raises(KeyError):
            get_event_type(event)
    
    def test_get_event_type_empty_event(self):
        """Test getting event type from empty event."""
        with pytest.raises(KeyError):
            get_event_type({})
    
    def test_webhook_processing_workflow(self):
        """Test complete webhook processing workflow."""
        # Prepare test data
        payload_data = {
            "event_id": "evt_abc123",
            "object_type": "email",
            "metric": "opened",
            "timestamp": int(time.time()),
            "data": {
                "customer_id": "cust_789",
                "delivery_id": "del_xyz",
                "recipient": "test@example.com",
                "subject": "Test Email",
                "identifiers": {
                    "id": "cust_789",
                    "email": "test@example.com"
                }
            }
        }
        
        payload = json.dumps(payload_data)
        secret = "test_webhook_secret"
        timestamp = str(int(time.time()))
        
        # Generate signature with Customer.io format
        signature_string = f"v0:{timestamp}:{payload}"
        signature_hash = hmac.new(
            secret.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        signature = f"v0={signature_hash}"
        
        # Test workflow
        # 1. Verify signature
        is_valid = verify_signature(payload, signature, timestamp, secret)
        assert is_valid is True
        
        # 2. Parse event
        event = parse_event(payload)
        assert event["event_id"] == "evt_abc123"
        
        # 3. Get event type
        object_type, metric = get_event_type(event)
        assert object_type == "email"
        assert metric == "opened"
        
        # 4. Route event
        routed = route_webhook_event(event)
        assert routed["object_type"] == "email"
        assert routed["metric"] == "opened"
    
    def test_validate_webhook_headers_valid(self):
        """Test validating webhook headers with valid headers."""
        headers = {
            "X-CIO-Timestamp": "1234567890",
            "X-CIO-Signature": "v0=abcdef123456"
        }
        
        timestamp, signature = validate_webhook_headers(headers)
        assert timestamp == "1234567890"
        assert signature == "v0=abcdef123456"
    
    def test_validate_webhook_headers_lowercase(self):
        """Test validating webhook headers with lowercase keys."""
        headers = {
            "x-cio-timestamp": "1234567890",
            "x-cio-signature": "v0=abcdef123456"
        }
        
        timestamp, signature = validate_webhook_headers(headers)
        assert timestamp == "1234567890"
        assert signature == "v0=abcdef123456"
    
    def test_validate_webhook_headers_missing(self):
        """Test validating webhook headers with missing headers."""
        headers = {
            "X-CIO-Timestamp": "1234567890"
            # Missing signature
        }
        
        with pytest.raises(ValueError, match="Missing required headers"):
            validate_webhook_headers(headers)
    
    def test_validate_webhook_headers_invalid_timestamp(self):
        """Test validating webhook headers with non-numeric timestamp."""
        headers = {
            "X-CIO-Timestamp": "not-a-number",
            "X-CIO-Signature": "v0=abcdef123456"
        }
        
        with pytest.raises(ValueError, match="must be unix timestamp"):
            validate_webhook_headers(headers)
    
    def test_validate_webhook_headers_invalid_signature_format(self):
        """Test validating webhook headers with wrong signature format."""
        headers = {
            "X-CIO-Timestamp": "1234567890",
            "X-CIO-Signature": "sha256=abcdef123456"  # Wrong prefix
        }
        
        with pytest.raises(ValueError, match="must start with 'v0='"):
            validate_webhook_headers(headers)
    
    def test_route_webhook_event_email(self):
        """Test routing email webhook event."""
        event = {
            "event_id": "123",
            "object_type": "email",
            "metric": "delivered",
            "data": {}
        }
        
        result = route_webhook_event(event)
        assert result["object_type"] == "email"
        assert result["metric"] == "delivered"
        assert result["event"] == event
    
    def test_route_webhook_event_customer(self):
        """Test routing customer webhook event."""
        event = {
            "event_id": "123",
            "object_type": "customer",
            "metric": "subscribed",
            "data": {}
        }
        
        result = route_webhook_event(event)
        assert result["object_type"] == "customer"
        assert result["metric"] == "subscribed"
    
    def test_route_webhook_event_unsupported(self):
        """Test routing unsupported webhook event type."""
        event = {
            "event_id": "123",
            "object_type": "unknown_type",
            "metric": "test",
            "data": {}
        }
        
        with pytest.raises(ValueError, match="Unsupported object_type"):
            route_webhook_event(event)