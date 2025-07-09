"""
Integration tests for Customer.IO App API messaging functions.

Tests transactional emails, broadcasts, and push notifications
with automatic test data creation and cleanup.
"""

import pytest
from datetime import datetime, timezone
import uuid

from .base import assert_api_response, assert_successful_response, handle_api_error, generate_test_timestamp
from src.app_api import client as app_client


@pytest.mark.app_integration
def test_send_transactional_with_email_identifier(app_auth, transactional_message_id):
    """Test sending transactional email using email identifier."""
    # Generate unique email for this test
    email = f"email_id_test_{uuid.uuid4().hex[:8]}@test.example.com"
    
    # Send transactional email using email as identifier
    try:
        result = app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=transactional_message_id,
            identifiers={"email": email},
            message_data={
                "first_name": "Test User",
                "timestamp": generate_test_timestamp()
            }
        )
    except Exception as e:
        if "404" in str(e) and "transactional_message_id" in str(e).lower():
            pytest.skip(f"Transactional message ID {transactional_message_id} not found in workspace")
        else:
            handle_api_error(e, "Sending transactional email")
    
    # Verify response
    assert_successful_response(result)
    assert_api_response(result, expected_keys=["delivery_id"])
    
    # Verify delivery_id is returned
    delivery_id = result.get("delivery_id")
    assert delivery_id, "Delivery ID should be returned"


@pytest.mark.app_integration
def test_send_transactional_with_email_only(app_auth, transactional_message_id):
    """Test sending transactional email using only email address."""
    # Generate unique email for this test
    email = f"transactional_test_{uuid.uuid4().hex[:8]}@test.example.com"
    
    # Send transactional email
    try:
        result = app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=transactional_message_id,
            to=email,
            message_data={
                "subject_line": "Integration Test Email",
                "timestamp": generate_test_timestamp()
            }
        )
    except Exception as e:
        if "404" in str(e) and "transactional_message_id" in str(e).lower():
            pytest.skip(f"Transactional message ID {transactional_message_id} not found in workspace")
        else:
            handle_api_error(e, "Sending transactional email")
    
    # Verify response
    assert_successful_response(result)
    assert_api_response(result, expected_keys=["delivery_id"])


@pytest.mark.app_integration
def test_send_transactional_error_handling(app_auth):
    """Test error handling for invalid transactional message."""
    # Use invalid message ID
    invalid_message_id = 99999999
    
    with pytest.raises(Exception) as exc_info:
        app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=invalid_message_id,
            to="test@example.com"
        )
    
    # Should get 404, 403, or similar business logic error (not 401 auth error)
    error_str = str(exc_info.value).lower()
    assert any(code in error_str for code in ["404", "403", "400", "not found", "forbidden", "bad request"])


@pytest.mark.app_integration  
def test_trigger_broadcast(app_auth, broadcast_id):
    """Test triggering broadcast with configuration."""
    # Trigger broadcast
    try:
        result = app_client.trigger_broadcast(
            auth=app_auth,
            broadcast_id=broadcast_id,
            data={
                "headline": "Integration Test Broadcast",
                "timestamp": generate_test_timestamp()
            },
            recipients={
                "segment": {"id": 1}  # Assuming segment 1 exists
            }
        )
    except Exception as e:
        if "404" in str(e) and "broadcast" in str(e).lower():
            pytest.skip(f"Broadcast ID {broadcast_id} not found in workspace")
        else:
            handle_api_error(e, "Triggering broadcast")
    
    # Verify response
    assert_successful_response(result)
    # Broadcast responses typically include trigger information
    if "id" in result:
        assert isinstance(result["id"], (str, int)), "Trigger ID should be present"


@pytest.mark.app_integration
def test_trigger_broadcast_error_handling(app_auth):
    """Test error handling for invalid broadcast."""
    # Use invalid broadcast ID
    invalid_broadcast_id = 99999999
    
    with pytest.raises(Exception) as exc_info:
        app_client.trigger_broadcast(
            auth=app_auth,
            broadcast_id=invalid_broadcast_id
        )
    
    # Should get 404, 403, or similar business logic error (not 401 auth error)
    error_str = str(exc_info.value).lower()
    assert any(code in error_str for code in ["404", "403", "400", "not found", "forbidden", "bad request"])


@pytest.mark.app_integration
def test_send_push_notification(app_auth):
    """Test sending push notification using email identifier."""
    # Generate unique email for this test
    email = f"push_test_{uuid.uuid4().hex[:8]}@test.example.com"
    
    # Send push notification
    try:
        result = app_client.send_push(
            auth=app_auth,
            identifiers={"email": email},
            title="Integration Test Push",
            message="Test notification from integration tests",
            device_tokens=["test_device_token_12345"]  # Test token
        )
        
        # Verify response if successful
        assert_successful_response(result)
        assert_api_response(result, expected_keys=["delivery_id"])
        
    except Exception as e:
        # Push notifications may require special permissions or setup
        if "403" in str(e) or "forbidden" in str(e).lower():
            pytest.skip("Push notifications require special API permissions - skipping test")
        else:
            handle_api_error(e, "Sending push notification")


@pytest.mark.app_integration
def test_send_push_error_handling(app_auth):
    """Test error handling for push notification."""
    # Test with missing required parameters
    with pytest.raises(ValueError) as exc_info:
        app_client.send_push(
            auth=app_auth,
            identifiers={"id": "test_user"},
            # Missing title, message, and device_tokens
        )
    
    assert "required" in str(exc_info.value).lower()


@pytest.mark.app_integration
def test_messaging_with_unicode_content(app_auth, transactional_message_id):
    """Test sending messages with Unicode content."""
    # Generate test email
    email = f"unicode_test_{uuid.uuid4().hex[:8]}@test.example.com"
    
    # Send with Unicode content
    try:
        result = app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=transactional_message_id,
            to=email,
            message_data={
                "greeting": "Hello 你好 مرحبا Здравствуйте",
                "emoji_test": "Testing emoji support with text indicators",
                "special_chars": "Testing special characters: €£¥"
            }
        )
    except Exception as e:
        if "404" in str(e) and "transactional_message_id" in str(e).lower():
            pytest.skip(f"Transactional message ID {transactional_message_id} not found in workspace")
        else:
            handle_api_error(e, "Sending Unicode content message")
    
    # Verify response
    assert_successful_response(result)
    assert_api_response(result, expected_keys=["delivery_id"])


@pytest.mark.app_integration
def test_messaging_workflow_end_to_end(app_auth, transactional_message_id):
    """Test complete messaging workflow using email."""
    # Generate unique email for this test
    email = f"workflow_test_{uuid.uuid4().hex[:8]}@test.example.com"
    
    # Step 1: Send transactional message using email
    try:
        send_result = app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=transactional_message_id,
            to=email,
            message_data={
                "workflow_step": "end_to_end_test",
                "timestamp": generate_test_timestamp(),
                "customer_email": email
            }
        )
    except Exception as e:
        if "404" in str(e) and "transactional_message_id" in str(e).lower():
            pytest.skip(f"Transactional message ID {transactional_message_id} not found in workspace")
        else:
            handle_api_error(e, "Sending workflow message")
    
    assert_successful_response(send_result)
    delivery_id = send_result.get("delivery_id")
    assert delivery_id, "Delivery ID should be returned"
    
    # Step 2: Wait for eventual consistency
    import time
    time.sleep(1.0)
    
    # Note: Message history requires customer ID, which we don't have when using email directly
    # This is expected behavior - email-only sends don't create persistent customers


@pytest.mark.app_integration
def test_transactional_with_custom_data(app_auth, transactional_message_id):
    """Test sending transactional email with custom data fields."""
    # Generate unique email for this test
    email = f"custom_data_test_{uuid.uuid4().hex[:8]}@test.example.com"
    
    custom_data = {
        "product_name": "Integration Test Product",
        "order_total": "$99.99",
        "shipping_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "tracking_number": f"TRK{uuid.uuid4().hex[:8].upper()}",
        "custom_boolean": True,
        "custom_number": 42
    }
    
    try:
        result = app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=transactional_message_id,
            to=email,
            message_data=custom_data
        )
    except Exception as e:
        if "404" in str(e) and "transactional_message_id" in str(e).lower():
            pytest.skip(f"Transactional message ID {transactional_message_id} not found in workspace")
        else:
            handle_api_error(e, "Sending custom data message")
    
    assert_successful_response(result)
    assert_api_response(result, expected_keys=["delivery_id"])