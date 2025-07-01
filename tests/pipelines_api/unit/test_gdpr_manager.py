"""
Unit tests for Customer.IO GDPR and data operations semantic events.
"""

from unittest.mock import Mock
import pytest
from datetime import datetime, timezone

from src.pipelines_api.gdpr_manager import (
    track_user_deleted,
    track_user_suppressed,
    track_user_unsuppressed,
    track_device_deleted,
    track_object_deleted,
    track_relationship_deleted,
    track_report_delivery_event
)
from src.pipelines_api.exceptions import ValidationError, CustomerIOError
from src.pipelines_api.api_client import CustomerIOClient


class TestTrackUserDeleted:
    """Test User Deleted semantic event."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_user_deleted_success(self, mock_client):
        """Test successful User Deleted event tracking."""
        result = track_user_deleted(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "User Deleted"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_user_deleted_with_properties(self, mock_client):
        """Test User Deleted event with additional properties."""
        properties = {
            "reason": "subscription_cancelled",
            "retention_days": 30,
            "deletion_source": "user_request"
        }
        
        result = track_user_deleted(
            client=mock_client,
            user_id="user123",
            properties=properties
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "User Deleted",
                "properties": properties
            }
        )
        assert result == {"status": "success"}
    
    def test_track_user_deleted_with_timestamp(self, mock_client):
        """Test User Deleted event with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = track_user_deleted(
            client=mock_client,
            user_id="user123",
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "User Deleted",
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_user_deleted_invalid_user_id(self, mock_client):
        """Test User Deleted event with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_user_deleted(
                client=mock_client,
                user_id=""
            )
    
    def test_track_user_deleted_none_user_id(self, mock_client):
        """Test User Deleted event with None user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_user_deleted(
                client=mock_client,
                user_id=None
            )
    
    def test_track_user_deleted_invalid_properties(self, mock_client):
        """Test User Deleted event with invalid properties."""
        with pytest.raises(ValidationError, match="Properties must be a dictionary"):
            track_user_deleted(
                client=mock_client,
                user_id="user123",
                properties="invalid"
            )
    
    def test_track_user_deleted_api_error(self, mock_client):
        """Test User Deleted event when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            track_user_deleted(
                client=mock_client,
                user_id="user123"
            )


class TestTrackUserSuppressed:
    """Test User Suppressed semantic event."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_user_suppressed_success(self, mock_client):
        """Test successful User Suppressed event tracking."""
        result = track_user_suppressed(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "User Suppressed"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_user_suppressed_with_gdpr_properties(self, mock_client):
        """Test User Suppressed event with GDPR compliance properties."""
        properties = {
            "gdpr_request_type": "right_to_be_forgotten",
            "request_source": "email",
            "compliance_officer": "legal@company.com",
            "retention_override": False
        }
        
        result = track_user_suppressed(
            client=mock_client,
            user_id="user123",
            properties=properties
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "User Suppressed",
                "properties": properties
            }
        )
        assert result == {"status": "success"}
    
    def test_track_user_suppressed_invalid_user_id(self, mock_client):
        """Test User Suppressed event with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_user_suppressed(
                client=mock_client,
                user_id=""
            )


class TestTrackUserUnsuppressed:
    """Test User Unsuppressed semantic event."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_user_unsuppressed_success(self, mock_client):
        """Test successful User Unsuppressed event tracking."""
        result = track_user_unsuppressed(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "User Unsuppressed"
            }
        )
        assert result == {"status": "success"}
    
    def test_track_user_unsuppressed_with_properties(self, mock_client):
        """Test User Unsuppressed event with restoration properties."""
        properties = {
            "restoration_reason": "false_positive",
            "approved_by": "privacy_officer",
            "original_suppression_date": "2024-01-01T00:00:00Z"
        }
        
        result = track_user_unsuppressed(
            client=mock_client,
            user_id="user123",
            properties=properties
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "User Unsuppressed",
                "properties": properties
            }
        )
        assert result == {"status": "success"}


class TestTrackDeviceDeleted:
    """Test Device Deleted semantic event."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_device_deleted_success(self, mock_client):
        """Test successful Device Deleted event tracking."""
        result = track_device_deleted(
            client=mock_client,
            user_id="user123",
            device_token="device_token_string"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Device Deleted",
                "context": {
                    "device": {
                        "token": "device_token_string"
                    }
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_device_deleted_with_device_type(self, mock_client):
        """Test Device Deleted event with device type."""
        result = track_device_deleted(
            client=mock_client,
            user_id="user123",
            device_token="device_token_string",
            device_type="ios"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Device Deleted",
                "context": {
                    "device": {
                        "token": "device_token_string",
                        "type": "ios"
                    }
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_device_deleted_invalid_device_token(self, mock_client):
        """Test Device Deleted event with invalid device token."""
        with pytest.raises(ValidationError, match="Device token must be a non-empty string"):
            track_device_deleted(
                client=mock_client,
                user_id="user123",
                device_token=""
            )


class TestTrackObjectDeleted:
    """Test Object Deleted semantic event."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_object_deleted_success(self, mock_client):
        """Test successful Object Deleted event tracking."""
        result = track_object_deleted(
            client=mock_client,
            object_id="company_abc"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "anonymousId": "gdpr_compliance",
                "event": "Object Deleted",
                "properties": {
                    "objectId": "company_abc",
                    "objectTypeId": 1
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_object_deleted_with_type_id(self, mock_client):
        """Test Object Deleted event with custom object type ID."""
        result = track_object_deleted(
            client=mock_client,
            object_id="company_abc",
            object_type_id=5
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "anonymousId": "gdpr_compliance",
                "event": "Object Deleted",
                "properties": {
                    "objectId": "company_abc",
                    "objectTypeId": 5
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_object_deleted_invalid_object_id(self, mock_client):
        """Test Object Deleted event with invalid object ID."""
        with pytest.raises(ValidationError, match="Object ID must be a non-empty string"):
            track_object_deleted(
                client=mock_client,
                object_id=""
            )


class TestTrackRelationshipDeleted:
    """Test Relationship Deleted semantic event."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_relationship_deleted_success(self, mock_client):
        """Test successful Relationship Deleted event tracking."""
        result = track_relationship_deleted(
            client=mock_client,
            user_id="user123",
            object_id="company_abc"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Relationship Deleted",
                "properties": {
                    "objectId": "company_abc",
                    "objectTypeId": 1
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_relationship_deleted_with_type_id(self, mock_client):
        """Test Relationship Deleted event with custom object type ID."""
        result = track_relationship_deleted(
            client=mock_client,
            user_id="user123",
            object_id="company_abc",
            object_type_id=3
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Relationship Deleted",
                "properties": {
                    "objectId": "company_abc",
                    "objectTypeId": 3
                }
            }
        )
        assert result == {"status": "success"}


class TestTrackReportDeliveryEvent:
    """Test Report Delivery Event semantic event."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_report_delivery_event_success(self, mock_client):
        """Test successful Report Delivery Event tracking."""
        result = track_report_delivery_event(
            client=mock_client,
            delivery_id="delivery_123",
            metric="delivered"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "anonymousId": "system_audit",
                "event": "Report Delivery Event",
                "properties": {
                    "deliveryId": "delivery_123",
                    "metric": "delivered"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_report_delivery_event_with_additional_properties(self, mock_client):
        """Test Report Delivery Event with additional audit properties."""
        properties = {
            "campaign_id": "campaign_456",
            "message_type": "email",
            "recipient_count": 1000,
            "compliance_region": "EU"
        }
        
        result = track_report_delivery_event(
            client=mock_client,
            delivery_id="delivery_123",
            metric="opened",
            properties=properties
        )
        
        expected_properties = {
            "deliveryId": "delivery_123",
            "metric": "opened",
            "campaign_id": "campaign_456",
            "message_type": "email",
            "recipient_count": 1000,
            "compliance_region": "EU"
        }
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "anonymousId": "system_audit",
                "event": "Report Delivery Event",
                "properties": expected_properties
            }
        )
        assert result == {"status": "success"}
    
    def test_track_report_delivery_event_invalid_delivery_id(self, mock_client):
        """Test Report Delivery Event with invalid delivery ID."""
        with pytest.raises(ValidationError, match="Delivery ID must be a non-empty string"):
            track_report_delivery_event(
                client=mock_client,
                delivery_id="",
                metric="delivered"
            )
    
    def test_track_report_delivery_event_invalid_metric(self, mock_client):
        """Test Report Delivery Event with invalid metric."""
        with pytest.raises(ValidationError, match="Metric must be a non-empty string"):
            track_report_delivery_event(
                client=mock_client,
                delivery_id="delivery_123",
                metric=""
            )


class TestGDPRManagerIntegration:
    """Test integration scenarios for GDPR compliance operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_complete_gdpr_deletion_workflow(self, mock_client):
        """Test complete GDPR deletion workflow."""
        user_id = "user123"
        
        # Step 1: Suppress user (right to be forgotten)
        suppress_result = track_user_suppressed(
            client=mock_client,
            user_id=user_id,
            properties={
                "gdpr_request_type": "right_to_be_forgotten",
                "request_source": "email",
                "compliance_officer": "legal@company.com"
            }
        )
        assert suppress_result == {"status": "success"}
        
        # Step 2: Delete user devices
        device_result = track_device_deleted(
            client=mock_client,
            user_id=user_id,
            device_token="device_token_123",
            device_type="ios"
        )
        assert device_result == {"status": "success"}
        
        # Step 3: Delete user relationships
        relationship_result = track_relationship_deleted(
            client=mock_client,
            user_id=user_id,
            object_id="company_abc"
        )
        assert relationship_result == {"status": "success"}
        
        # Step 4: Track final user deletion
        deletion_result = track_user_deleted(
            client=mock_client,
            user_id=user_id,
            properties={
                "reason": "gdpr_compliance",
                "deletion_source": "right_to_be_forgotten"
            }
        )
        assert deletion_result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 4
    
    def test_data_retention_cleanup_workflow(self, mock_client):
        """Test data retention policy cleanup workflow."""
        objects_to_delete = [
            {"id": "old_company_1", "type_id": 1},
            {"id": "old_company_2", "type_id": 1},
            {"id": "old_account_1", "type_id": 2}
        ]
        
        # Delete old objects based on retention policy
        for obj in objects_to_delete:
            result = track_object_deleted(
                client=mock_client,
                object_id=obj["id"],
                object_type_id=obj["type_id"]
            )
            assert result == {"status": "success"}
        
        # Verify all objects were deleted
        assert mock_client.make_request.call_count == 3
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/track"
            assert args[2]["event"] == "Object Deleted"
            assert args[2]["properties"]["objectId"] == objects_to_delete[i]["id"]
            assert args[2]["properties"]["objectTypeId"] == objects_to_delete[i]["type_id"]
    
    def test_audit_trail_workflow(self, mock_client):
        """Test audit trail generation for compliance reporting."""
        delivery_events = [
            {"id": "delivery_1", "metric": "delivered"},
            {"id": "delivery_2", "metric": "opened"},
            {"id": "delivery_3", "metric": "clicked"},
            {"id": "delivery_4", "metric": "bounced"}
        ]
        
        # Track delivery events for audit trail
        for event in delivery_events:
            result = track_report_delivery_event(
                client=mock_client,
                delivery_id=event["id"],
                metric=event["metric"],
                properties={
                    "compliance_region": "EU",
                    "audit_timestamp": "2024-01-15T12:30:00Z"
                }
            )
            assert result == {"status": "success"}
        
        # Verify all events were tracked
        assert mock_client.make_request.call_count == 4
    
    def test_user_suppression_and_restoration_workflow(self, mock_client):
        """Test user suppression and restoration workflow."""
        user_id = "user123"
        
        # Suppress user for GDPR compliance
        suppress_result = track_user_suppressed(
            client=mock_client,
            user_id=user_id,
            properties={
                "gdpr_request_type": "right_to_be_forgotten",
                "request_date": "2024-01-01T00:00:00Z"
            }
        )
        assert suppress_result == {"status": "success"}
        
        # Later: Restore user (false positive case)
        unsuppress_result = track_user_unsuppressed(
            client=mock_client,
            user_id=user_id,
            properties={
                "restoration_reason": "false_positive",
                "approved_by": "privacy_officer",
                "original_suppression_date": "2024-01-01T00:00:00Z"
            }
        )
        assert unsuppress_result == {"status": "success"}
        
        # Verify both operations
        assert mock_client.make_request.call_count == 2
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        assert calls[0][0][2]["event"] == "User Suppressed"
        assert calls[1][0][2]["event"] == "User Unsuppressed"