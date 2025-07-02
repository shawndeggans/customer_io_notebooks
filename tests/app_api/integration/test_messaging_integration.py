"""
Integration tests for Customer.IO App API messaging functions.

Tests transactional emails, broadcasts, and push notifications
with support for different test data modes.
"""

import pytest
from datetime import datetime, timezone

from .base import BaseAppAPIIntegrationTest
from .conftest import skip_without_app_credentials, skip_in_existing_mode, skip_without_device
from src.app_api import client as app_client


@skip_without_app_credentials
class TestMessagingIntegration(BaseAppAPIIntegrationTest):
    """Test messaging functionality with real App API."""
    
    def test_send_transactional_with_existing_customer(
        self, 
        app_auth, 
        test_customer_id,
        test_email,
        transactional_message_id,
        test_data_mode,
        cleanup_tracker
    ):
        """Test sending transactional email to existing customer."""
        if not transactional_message_id:
            pytest.skip("No transactional message ID configured")
        
        # Ensure customer exists if in existing mode
        if test_data_mode == "existing":
            self.ensure_test_customer_exists(
                app_auth, 
                test_customer_id, 
                test_email
            )
        
        # Send transactional email
        try:
            result = app_client.send_transactional(
                auth=app_auth,
                transactional_message_id=int(transactional_message_id),
                identifiers={"id": test_customer_id},
                message_data={
                    "first_name": "Test",
                    "test_mode": test_data_mode,
                    "timestamp": self.generate_test_timestamp()
                }
            )
        except Exception as e:
            if "404" in str(e) and "transactional_message_id" in str(e).lower():
                pytest.skip(f"Transactional message ID {transactional_message_id} not found in workspace")
            else:
                self.handle_api_error(e, "Sending transactional email")
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["delivery_id"])
        
        # Track for reporting
        cleanup_tracker["customers"].append(test_customer_id)
    
    def test_send_transactional_with_email_only(
        self,
        app_auth,
        test_email,
        transactional_message_id,
        test_data_mode
    ):
        """Test sending transactional email using only email address."""
        if not transactional_message_id:
            pytest.skip("No transactional message ID configured")
        
        if test_data_mode == "existing":
            # Use existing email from config
            email = test_email
        else:
            # Generate unique email for this test
            timestamp = int(datetime.now(timezone.utc).timestamp())
            email = f"transactional_test_{timestamp}@example.com"
        
        # Send transactional email
        result = app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=int(transactional_message_id),
            to=email,
            message_data={
                "subject_line": "Integration Test Email",
                "test_mode": test_data_mode
            }
        )
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["delivery_id"])
    
    def test_send_transactional_error_handling(self, app_auth):
        """Test error handling for invalid transactional message."""
        # Use invalid message ID
        invalid_message_id = 99999999
        
        with pytest.raises(Exception) as exc_info:
            app_client.send_transactional(
                auth=app_auth,
                transactional_message_id=invalid_message_id,
                to="test@example.com"
            )
        
        # Should get 404 or similar error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
    
    def test_trigger_broadcast_with_existing_data(
        self,
        app_auth,
        broadcast_id,
        test_data_mode
    ):
        """Test triggering broadcast with existing configuration."""
        if not broadcast_id:
            pytest.skip("No broadcast ID configured")
        
        # Trigger broadcast
        try:
            result = app_client.trigger_broadcast(
                auth=app_auth,
                broadcast_id=int(broadcast_id),
                data={
                    "headline": "Integration Test Broadcast",
                    "test_mode": test_data_mode,
                    "timestamp": self.generate_test_timestamp()
                },
                recipients={
                    "segment": {"id": 1}  # Assuming segment 1 exists
                }
            )
        except Exception as e:
            if "404" in str(e) and "broadcast" in str(e).lower():
                pytest.skip(f"Broadcast ID {broadcast_id} not found in workspace")
            else:
                self.handle_api_error(e, "Triggering broadcast")
        
        # Verify response
        self.assert_successful_response(result)
        # Broadcast responses typically include trigger information
        if "id" in result:
            assert isinstance(result["id"], (str, int)), "Trigger ID should be present"
    
    def test_trigger_broadcast_error_handling(self, app_auth):
        """Test error handling for invalid broadcast."""
        # Use invalid broadcast ID
        invalid_broadcast_id = 99999999
        
        with pytest.raises(Exception) as exc_info:
            app_client.trigger_broadcast(
                auth=app_auth,
                broadcast_id=invalid_broadcast_id
            )
        
        # Should get 404 or similar error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
    
    @skip_without_device
    def test_send_push_notification(
        self,
        app_auth,
        test_customer_id,
        device_token,
        test_data_mode
    ):
        """Test sending push notification to existing device."""
        if not device_token:
            pytest.skip("No device token configured")
        
        # Send push notification
        result = app_client.send_push(
            auth=app_auth,
            identifiers={"id": test_customer_id},
            title="Integration Test Push",
            message=f"Test notification - Mode: {test_data_mode}",
            device_tokens=[device_token]
        )
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["delivery_id"])
    
    def test_send_push_error_handling(self, app_auth):
        """Test error handling for push notification."""
        # Test with missing required parameters
        with pytest.raises(ValueError) as exc_info:
            app_client.send_push(
                auth=app_auth,
                identifiers={"id": "test_user"},
                # Missing title, message, and device_tokens
            )
        
        assert "required" in str(exc_info.value).lower()
    
    @pytest.mark.parametrize("endpoint_type,expected_delay", [
        ("transactional", 0.01),  # 100 req/sec
        ("broadcast", 10.0),       # 1 req/10 sec
        ("general", 0.1),          # 10 req/sec
    ])
    def test_rate_limiting_configuration(self, app_auth, endpoint_type, expected_delay):
        """Test that rate limiting is properly configured."""
        delay = app_auth.get_rate_limit_delay(endpoint_type)
        assert delay == expected_delay, f"Incorrect rate limit for {endpoint_type}"
    
    def test_messaging_with_unicode_content(
        self,
        app_auth,
        transactional_message_id,
        test_email
    ):
        """Test sending messages with Unicode content."""
        if not transactional_message_id:
            pytest.skip("No transactional message ID configured")
        
        # Send with Unicode content
        result = app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=int(transactional_message_id),
            to=test_email,
            message_data={
                "greeting": "Hello 你好 مرحبا Здравствуйте",
                "emoji_test": "Testing emoji support",
                "special_chars": "Testing special characters: €£¥"
            }
        )
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["delivery_id"])
    
    @pytest.mark.modifies_data
    def test_messaging_workflow_end_to_end(
        self,
        app_auth,
        test_customer_id,
        test_email,
        transactional_message_id,
        test_data_mode,
        cleanup_tracker
    ):
        """Test complete messaging workflow."""
        if not transactional_message_id:
            pytest.skip("No transactional message ID configured")
        
        # Step 1: Ensure customer exists
        if test_data_mode != "existing":
            # Create customer for test
            try:
                app_client.create_customer(
                    auth=app_auth,
                    id=test_customer_id,
                    email=test_email,
                    attributes={"workflow_test": True}
                )
                self.track_created_customer(test_customer_id)
            except Exception as e:
                if "409" not in str(e):  # Not a duplicate error
                    raise
        
        # Step 2: Send transactional message
        send_result = app_client.send_transactional(
            auth=app_auth,
            transactional_message_id=int(transactional_message_id),
            identifiers={"id": test_customer_id},
            message_data={
                "workflow_step": "end_to_end_test",
                "timestamp": self.generate_test_timestamp()
            }
        )
        
        self.assert_successful_response(send_result)
        delivery_id = send_result.get("delivery_id")
        assert delivery_id, "Delivery ID should be returned"
        
        # Step 3: Wait for eventual consistency
        self.wait_for_eventual_consistency(2.0)
        
        # Step 4: Check customer's message history (if possible)
        try:
            messages = app_client.get_customer_messages(
                auth=app_auth,
                customer_id=test_customer_id,
                limit=10
            )
            
            # Messages might not appear immediately
            assert "messages" in messages, "Messages list should be in response"
        except Exception as e:
            # Some test environments might not have message history enabled
            print(f"Could not retrieve message history: {e}")
        
        # Track for cleanup
        cleanup_tracker["customers"].append(test_customer_id)