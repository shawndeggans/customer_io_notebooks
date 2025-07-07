"""Tests for webhook event handlers."""
import pytest
import json
from datetime import datetime
from src.webhooks.event_handlers import (
    EmailEventHandler,
    CustomerEventHandler,
    SMSEventHandler,
    PushEventHandler,
    InAppEventHandler,
    SlackEventHandler,
    WebhookEventHandler,
    get_event_handler
)


class TestEmailEventHandler:
    """Test EmailEventHandler functionality."""
    
    def test_handle_email_opened_event(self):
        """Test handling email opened event."""
        handler = EmailEventHandler()
        
        event_data = {
            "event_id": "01E4C4CT6YDC7Y5M7FE1GWWPQJ",
            "object_type": "email",
            "metric": "opened",
            "timestamp": 1613063089,
            "data": {
                "customer_id": "12345",
                "delivery_id": "RPILAgUBcRhIBqSfeiIwdIYJKxTY",
                "campaign_id": 123,
                "action_id": 456,
                "subject": "Test Email",
                "recipient": "test@example.com",
                "identifiers": {
                    "id": "12345",
                    "email": "test@example.com",
                    "cio_id": "cio_03000001"
                },
                "proxied": False,
                "prefetched": False
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["event_id"] == "01E4C4CT6YDC7Y5M7FE1GWWPQJ"
        assert result["object_type"] == "email"
        assert result["metric"] == "opened"
        assert result["customer_id"] == "12345"
        assert result["email_address"] == "test@example.com"
        assert result["proxied"] is False
        assert result["prefetched"] is False
    
    def test_handle_email_clicked_event(self):
        """Test handling email clicked event."""
        handler = EmailEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "email",
            "metric": "clicked",
            "timestamp": 1613063089,
            "data": {
                "customer_id": "12345",
                "delivery_id": "del_123",
                "recipient": "test@example.com",
                "subject": "Test",
                "href": "https://example.com/promo",
                "link_id": "link_123",
                "machine": False,
                "identifiers": {"id": "12345", "email": "test@example.com"}
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["metric"] == "clicked"
        assert result["href"] == "https://example.com/promo"
        assert result["link_id"] == "link_123"
        assert result["machine_click"] is False
    
    def test_handle_email_bounced_event(self):
        """Test handling email bounced event."""
        handler = EmailEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "email",
            "metric": "bounced",
            "timestamp": 1613063089,
            "data": {
                "customer_id": "12345",
                "delivery_id": "del_123",
                "recipient": "test@example.com",
                "subject": "Test",
                "failure_message": "550 5.1.1 User unknown",
                "identifiers": {"id": "12345"}
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["metric"] == "bounced"
        assert result["failure_message"] == "550 5.1.1 User unknown"
    
    def test_handle_email_invalid_object_type(self):
        """Test handling event with wrong object type."""
        handler = EmailEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "sms",  # Wrong type
            "metric": "delivered",
            "timestamp": 1613063089,
            "data": {}
        }
        
        with pytest.raises(ValueError, match="Invalid object_type"):
            handler.handle_event(event_data)


class TestCustomerEventHandler:
    """Test CustomerEventHandler functionality."""
    
    def test_handle_customer_subscribed_event(self):
        """Test handling customer subscribed event."""
        handler = CustomerEventHandler()
        
        event_data = {
            "event_id": "01E4C4CT6YDC7Y5M7FE1GWWPQJ",
            "object_type": "customer",
            "metric": "subscribed",
            "timestamp": 1613063089,
            "data": {
                "customer_id": "12345",
                "email_address": "test@example.com",
                "identifiers": {
                    "id": "12345",
                    "email": "test@example.com",
                    "cio_id": "cio_03000001"
                }
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["event_id"] == "01E4C4CT6YDC7Y5M7FE1GWWPQJ"
        assert result["object_type"] == "customer"
        assert result["metric"] == "subscribed"
        assert result["customer_id"] == "12345"
        assert result["email_address"] == "test@example.com"
    
    def test_handle_subscription_preferences_changed(self):
        """Test handling subscription preferences changed event."""
        handler = CustomerEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "customer",
            "metric": "cio_subscription_preferences_changed",
            "timestamp": 1613063089,
            "delivery_type": "email",
            "data": {
                "customer_id": "12345",
                "email_address": "test@example.com",
                "identifiers": {"id": "12345"},
                "content": '{"marketing": true, "newsletter": false}'
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["metric"] == "cio_subscription_preferences_changed"
        assert result["content"] == '{"marketing": true, "newsletter": false}'
        assert result["delivery_type"] == "email"
    
    def test_handle_customer_invalid_metric(self):
        """Test handling customer event with invalid metric."""
        handler = CustomerEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "customer",
            "metric": "invalid_metric",
            "timestamp": 1613063089,
            "data": {}
        }
        
        with pytest.raises(ValueError, match="Invalid metric"):
            handler.handle_event(event_data)


class TestSMSEventHandler:
    """Test SMSEventHandler functionality."""
    
    def test_handle_sms_sent_event(self):
        """Test handling SMS sent event."""
        handler = SMSEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "sms",
            "metric": "sent",
            "timestamp": 1613063089,
            "data": {
                "customer_id": "12345",
                "delivery_id": "sms_123",
                "recipient": "+1234567890",
                "content": "Your order is ready!",
                "identifiers": {"id": "12345"}
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["object_type"] == "sms"
        assert result["metric"] == "sent"
        assert result["recipient"] == "+1234567890"
        assert result["content"] == "Your order is ready!"
    
    def test_handle_sms_clicked_event(self):
        """Test handling SMS clicked event."""
        handler = SMSEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "sms",
            "metric": "clicked",
            "timestamp": 1613063089,
            "data": {
                "customer_id": "12345",
                "delivery_id": "sms_123",
                "recipient": "+1234567890",
                "href": "https://example.com/track",
                "link_id": "link_456",
                "identifiers": {"id": "12345"}
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["metric"] == "clicked"
        assert result["href"] == "https://example.com/track"
        assert result["link_id"] == "link_456"


class TestPushEventHandler:
    """Test PushEventHandler functionality."""
    
    def test_handle_push_sent_event(self):
        """Test handling push sent event."""
        handler = PushEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "push",
            "metric": "sent",
            "timestamp": 1613063089,
            "data": {
                "customer_id": "12345",
                "delivery_id": "push_123",
                "recipients": [
                    {"device_id": "device_abc", "device_platform": "ios"},
                    {"device_id": "device_xyz", "device_platform": "android"}
                ],
                "content": "New message!",
                "identifiers": {"id": "12345"}
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["object_type"] == "push"
        assert result["metric"] == "sent"
        assert result["primary_device_id"] == "device_abc"
        assert "recipients" in result  # Stored as JSON string
    
    def test_handle_push_bounced_event(self):
        """Test handling push bounced event."""
        handler = PushEventHandler()
        
        event_data = {
            "event_id": "123",
            "object_type": "push",
            "metric": "bounced",
            "timestamp": 1613063089,
            "data": {
                "customer_id": "12345",
                "delivery_id": "push_123",
                "recipients": [
                    {
                        "device_id": "device_abc",
                        "device_platform": "ios",
                        "failure_message": "Invalid token"
                    }
                ],
                "failure_message": "Push notification failed",
                "identifiers": {"id": "12345"}
            }
        }
        
        result = handler.handle_event(event_data)
        
        assert result["metric"] == "bounced"
        assert result["failure_message"] == "Push notification failed"


class TestEventHandlerFactory:
    """Test get_event_handler factory function."""
    
    def test_get_email_handler(self):
        """Test getting email event handler."""
        handler = get_event_handler("email")
        assert isinstance(handler, EmailEventHandler)
    
    def test_get_customer_handler(self):
        """Test getting customer event handler."""
        handler = get_event_handler("customer")
        assert isinstance(handler, CustomerEventHandler)
    
    def test_get_sms_handler(self):
        """Test getting SMS event handler."""
        handler = get_event_handler("sms")
        assert isinstance(handler, SMSEventHandler)
    
    def test_get_push_handler(self):
        """Test getting push event handler."""
        handler = get_event_handler("push")
        assert isinstance(handler, PushEventHandler)
    
    def test_get_in_app_handler(self):
        """Test getting in-app event handler."""
        handler = get_event_handler("in_app")
        assert isinstance(handler, InAppEventHandler)
    
    def test_get_slack_handler(self):
        """Test getting Slack event handler."""
        handler = get_event_handler("slack")
        assert isinstance(handler, SlackEventHandler)
    
    def test_get_webhook_handler(self):
        """Test getting webhook event handler."""
        handler = get_event_handler("webhook")
        assert isinstance(handler, WebhookEventHandler)
    
    def test_get_invalid_handler(self):
        """Test getting handler for invalid object type."""
        with pytest.raises(ValueError, match="No handler available"):
            get_event_handler("invalid_type")