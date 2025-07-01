"""Tests for webhook processing functions."""
import pytest
import json
import hmac
import hashlib
from src.webhooks.processor import verify_signature, parse_event, get_event_type


class TestWebhookProcessor:
    """Test webhook processing functionality."""
    
    def test_verify_signature_valid(self):
        """Test webhook signature verification with valid signature."""
        payload = '{"event": "email_delivered", "data": {"customer_id": "123"}}'
        secret = "webhook_secret_key"
        
        # Generate valid signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        result = verify_signature(payload, f"sha256={signature}", secret)
        assert result is True
    
    def test_verify_signature_invalid(self):
        """Test webhook signature verification with invalid signature."""
        payload = '{"event": "email_delivered", "data": {"customer_id": "123"}}'
        secret = "webhook_secret_key"
        invalid_signature = "sha256=invalid_signature_hash"
        
        result = verify_signature(payload, invalid_signature, secret)
        assert result is False
    
    def test_verify_signature_missing_prefix(self):
        """Test webhook signature verification with missing sha256 prefix."""
        payload = '{"event": "email_delivered"}'
        secret = "webhook_secret_key"
        signature_without_prefix = "abcdef123456"
        
        result = verify_signature(payload, signature_without_prefix, secret)
        assert result is False
    
    def test_verify_signature_empty_payload(self):
        """Test webhook signature verification with empty payload."""
        result = verify_signature("", "sha256=test", "secret")
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
            "event_type": "email_delivered",
            "data": {"customer_id": "123"}
        }
        
        event_type = get_event_type(event)
        assert event_type == "email_delivered"
    
    def test_get_event_type_customer_subscribed(self):
        """Test getting event type from customer subscription event."""
        event = {
            "event_type": "customer_subscribed",
            "data": {"customer_id": "123"}
        }
        
        event_type = get_event_type(event)
        assert event_type == "customer_subscribed"
    
    def test_get_event_type_missing_field(self):
        """Test getting event type when field is missing."""
        event = {
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
            "event_type": "email_opened",
            "timestamp": 1640995200,
            "data": {
                "customer_id": "cust_789",
                "delivery_id": "del_xyz",
                "link_url": "https://example.com"
            }
        }
        
        payload = json.dumps(payload_data)
        secret = "test_webhook_secret"
        
        # Generate signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Test workflow
        # 1. Verify signature
        is_valid = verify_signature(payload, f"sha256={signature}", secret)
        assert is_valid is True
        
        # 2. Parse event
        event = parse_event(payload)
        assert event["event_id"] == "evt_abc123"
        
        # 3. Get event type
        event_type = get_event_type(event)
        assert event_type == "email_opened"