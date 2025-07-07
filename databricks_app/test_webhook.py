"""Test script for Customer.io webhook endpoint."""
import requests
import json
import hmac
import hashlib
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_webhook_signature(payload: str, timestamp: str, secret: str) -> str:
    """Generate Customer.io webhook signature."""
    # Create signature string: v0:timestamp:body
    signature_string = f"v0:{timestamp}:{payload}"
    
    # Calculate signature
    signature = hmac.new(
        secret.encode('utf-8'),
        signature_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"v0={signature}"


def test_webhook_endpoint(webhook_url: str, signing_key: str):
    """Test the webhook endpoint with sample data."""
    
    # Sample email opened event (from OpenAPI spec)
    test_payload = {
        "event_id": "01E4C4CT6YDC7Y5M7FE1GWWPQJ",
        "object_type": "email",
        "metric": "opened",
        "timestamp": int(time.time()),
        "data": {
            "customer_id": "12345",
            "delivery_id": "RPILAgUBcRhIBqSfeiIwdIYJKxTY",
            "campaign_id": 123,
            "action_id": 456,
            "subject": "Test Email Subject",
            "recipient": "test@example.com",
            "identifiers": {
                "id": "12345",
                "email": "test@example.com",
                "cio_id": "cio_03000001"
            }
        }
    }
    
    payload_json = json.dumps(test_payload)
    timestamp = str(int(time.time()))
    
    # Generate signature
    signature = generate_webhook_signature(payload_json, timestamp, signing_key)
    
    headers = {
        'Content-Type': 'application/json',
        'X-CIO-Signature': signature,
        'X-CIO-Timestamp': timestamp
    }
    
    print(f"Testing webhook endpoint: {webhook_url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.post(webhook_url, data=payload_json, headers=headers)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Webhook test successful!")
        else:
            print("\n❌ Webhook test failed!")
            
    except Exception as e:
        print(f"\n❌ Error testing webhook: {e}")


def test_health_endpoint(base_url: str):
    """Test the health check endpoint."""
    health_url = f"{base_url}/health"
    print(f"\nTesting health endpoint: {health_url}")
    
    try:
        response = requests.get(health_url)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Health check successful!")
        else:
            print("\n❌ Health check failed!")
            
    except Exception as e:
        print(f"\n❌ Error testing health endpoint: {e}")


def test_various_events(webhook_url: str, signing_key: str):
    """Test various event types."""
    
    # Test customer subscription event
    customer_event = {
        "event_id": "01E4C4CT6YDC7Y5M7FE1GWWPQJ",
        "object_type": "customer",
        "metric": "subscribed",
        "timestamp": int(time.time()),
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
    
    # Test SMS clicked event
    sms_event = {
        "event_id": "01E4C4CT6YDC7Y5M7FE1GWWPQJ",
        "object_type": "sms",
        "metric": "clicked",
        "timestamp": int(time.time()),
        "data": {
            "customer_id": "12345",
            "delivery_id": "SMS123",
            "recipient": "+1234567890",
            "link_id": "link_123",
            "href": "https://example.com/promo",
            "identifiers": {
                "id": "12345"
            }
        }
    }
    
    events = [
        ("Customer Subscribed", customer_event),
        ("SMS Clicked", sms_event)
    ]
    
    for event_name, event_data in events:
        print(f"\n\nTesting {event_name} event...")
        
        payload_json = json.dumps(event_data)
        timestamp = str(int(time.time()))
        signature = generate_webhook_signature(payload_json, timestamp, signing_key)
        
        headers = {
            'Content-Type': 'application/json',
            'X-CIO-Signature': signature,
            'X-CIO-Timestamp': timestamp
        }
        
        try:
            response = requests.post(webhook_url, data=payload_json, headers=headers)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {event_name} test successful!")
            else:
                print(f"❌ {event_name} test failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {event_name}: {e}")


if __name__ == "__main__":
    # Configuration
    base_url = os.environ.get('WEBHOOK_BASE_URL', 'http://localhost:5000')
    webhook_url = f"{base_url}/webhook/customerio"
    signing_key = os.environ.get('CUSTOMERIO_WEBHOOK_SECRET', 'test_webhook_secret')
    
    print("Customer.io Webhook Test Script")
    print("================================")
    
    # Test health endpoint
    test_health_endpoint(base_url)
    
    # Test webhook endpoint
    test_webhook_endpoint(webhook_url, signing_key)
    
    # Test various event types
    test_various_events(webhook_url, signing_key)