"""
Integration tests for Customer.IO GDPR Compliance API.

Tests real API interactions for:
- User data deletion and suppression
- Privacy compliance tracking
- GDPR-related semantic events
- Data retention and cleanup
"""

import pytest
from datetime import datetime, timezone

from tests.pipelines_api.integration.base import BaseIntegrationTest
from tests.pipelines_api.integration.utils import generate_test_email
from src.pipelines_api.gdpr_manager import (
    track_user_deleted,
    track_user_suppressed,
    track_user_unsuppressed,
    track_device_deleted,
    track_object_deleted,
    track_relationship_deleted,
    track_report_delivery_event
)
from src.pipelines_api.people_manager import identify_user
from src.pipelines_api.exceptions import CustomerIOError, ValidationError


@pytest.mark.integration
class TestGdprIntegration(BaseIntegrationTest):
    """Integration tests for GDPR compliance functionality."""
    
    def test_track_user_deleted(self, authenticated_client, test_user_id):
        """Test tracking user deletion for GDPR compliance."""
        # Arrange - Create user first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("gdpr_delete"),
            "name": "GDPR Delete Test User"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_user_deleted(
            authenticated_client,
            test_user_id,
            {
                "deletion_reason": "user_request",
                "deletion_method": "right_to_be_forgotten",
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "processed_by": "privacy_team"
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_user_suppression_cycle(self, authenticated_client, test_user_id):
        """Test user suppression and unsuppression cycle."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("suppress"),
            "name": "Suppression Test User"
        })
        self.track_user(test_user_id)
        
        # Act & Assert - Suppress user
        suppress_result = track_user_suppressed(
            authenticated_client,
            test_user_id,
            {
                "suppression_reason": "user_request",
                "suppression_type": "marketing_communications",
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "effective_date": datetime.now(timezone.utc).isoformat()
            }
        )
        self.assert_successful_response(suppress_result)
        
        # Unsuppress user
        unsuppress_result = track_user_unsuppressed(
            authenticated_client,
            test_user_id,
            {
                "unsuppression_reason": "user_consent_renewed",
                "unsuppression_type": "marketing_communications",
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "effective_date": datetime.now(timezone.utc).isoformat()
            }
        )
        self.assert_successful_response(unsuppress_result)
    
    def test_track_device_deleted(self, authenticated_client, test_user_id):
        """Test tracking device deletion for privacy compliance."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("device_del"),
            "name": "Device Delete Test"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_device_deleted(
            authenticated_client,
            test_user_id,
            "DEVICE_TO_DELETE_123",
            device_type="ios"
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_object_deleted(self, authenticated_client, test_user_id):
        """Test tracking object deletion for compliance."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("obj_del"),
            "name": "Object Delete Test"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_object_deleted(
            authenticated_client,
            test_user_id,
            {
                "object_id": "OBJECT_TO_DELETE_123",
                "object_type": "user_generated_content",
                "deletion_reason": "gdpr_compliance",
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_relationship_deleted(self, authenticated_client, test_user_id):
        """Test tracking relationship deletion for privacy."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("rel_del"),
            "name": "Relationship Delete Test"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_relationship_deleted(
            authenticated_client,
            test_user_id,
            "REL_TO_DELETE_123"
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_report_delivery_event(self, authenticated_client, test_user_id):
        """Test tracking GDPR report delivery events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("report"),
            "name": "Report Delivery Test"
        })
        self.track_user(test_user_id)
        
        # Act
        report_id = f"GDPR_REPORT_{int(datetime.now().timestamp())}"
        result = track_report_delivery_event(
            authenticated_client,
            report_id,
            "delivered",
            properties={
                "report_type": "data_export",
                "delivery_method": "email",
                "file_format": "json",
                "file_size_bytes": 15420,
                "user_id": test_user_id
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_gdpr_with_timestamps(self, authenticated_client, test_user_id):
        """Test GDPR events with custom timestamps."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("timestamp"),
            "name": "Timestamp Test User"
        })
        self.track_user(test_user_id)
        
        custom_timestamp = datetime.now(timezone.utc)
        
        # Act
        result = track_user_suppressed(
            authenticated_client,
            test_user_id,
            {
                "suppression_reason": "historical_compliance",
                "is_historical": True
            },
            timestamp=custom_timestamp
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_gdpr_validation_errors(self, authenticated_client):
        """Test GDPR event validation."""
        # Test empty user ID
        with pytest.raises(ValidationError):
            track_user_deleted(authenticated_client, "", {"deletion_reason": "test"})
    
    def test_comprehensive_gdpr_compliance_scenario(self, authenticated_client, test_user_id):
        """Test a comprehensive GDPR compliance scenario."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("comprehensive"),
            "name": "Comprehensive GDPR Test"
        })
        self.track_user(test_user_id)
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Scenario: User requests data export, then deletion
        compliance_events = [
            ("report_request", lambda: track_report_delivery_event(
                authenticated_client, f"DATA_EXPORT_{int(datetime.now().timestamp())}", "processing",
                properties={"report_type": "data_export", "user_id": test_user_id}
            )),
            ("report_delivery", lambda: track_report_delivery_event(
                authenticated_client, f"DATA_EXPORT_{int(datetime.now().timestamp())}", "delivered",
                properties={"report_type": "data_export", "delivery_method": "secure_download", "user_id": test_user_id}
            )),
            ("device_deletion", lambda: track_device_deleted(
                authenticated_client, test_user_id, "COMPLIANCE_DEVICE_123"
            )),
            ("object_deletion", lambda: track_object_deleted(
                authenticated_client, "COMPLIANCE_OBJECT_123"
            )),
            ("user_deletion", lambda: track_user_deleted(
                authenticated_client, test_user_id,
                {
                    "deletion_reason": "gdpr_right_to_be_forgotten",
                    "deletion_method": "automated_compliance_system",
                    "processed_at": timestamp,
                    "confirmation_id": f"GDPR_CONF_{int(datetime.now().timestamp())}"
                }
            ))
        ]
        
        # Execute compliance workflow with delays
        for event_name, event_func in compliance_events:
            result = event_func()
            self.assert_successful_response(result)
            self.wait_for_eventual_consistency(0.2)
    
    def test_bulk_privacy_operations(self, authenticated_client):
        """Test bulk privacy operations for compliance."""
        # Arrange - Create multiple test users
        user_ids = []
        for i in range(5):
            user_id = f"bulk_privacy_user_{i}_{int(datetime.now().timestamp())}"
            user_ids.append(user_id)
            
            identify_user(authenticated_client, user_id, {
                "email": generate_test_email(f"bulk{i}"),
                "name": f"Bulk Privacy User {i}"
            })
            
            if i < 3:  # Only track first 3 for cleanup
                self.track_user(user_id)
        
        # Act - Suppress all users in bulk
        for i, user_id in enumerate(user_ids):
            result = track_user_suppressed(
                authenticated_client,
                user_id,
                {
                    "suppression_reason": "bulk_privacy_operation",
                    "batch_id": f"BULK_SUPPRESS_{int(datetime.now().timestamp())}",
                    "user_index": i
                }
            )
            self.assert_successful_response(result)
            
            # Rate limiting
            if i % 2 == 0:
                self.wait_for_eventual_consistency(0.15)
    
    @pytest.mark.slow
    def test_high_volume_gdpr_events(self, authenticated_client, test_user_id):
        """Test tracking multiple GDPR events for compliance load testing."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("volume"),
            "name": "Volume GDPR Test User"
        })
        self.track_user(test_user_id)
        
        # Act - Track 10 different GDPR events with rate limiting
        gdpr_events = [
            lambda i: track_user_suppressed(authenticated_client, test_user_id, {
                "suppression_reason": f"volume_test_{i}",
                "suppression_type": "marketing"
            }),
            lambda i: track_user_unsuppressed(authenticated_client, test_user_id, {
                "unsuppression_reason": f"volume_test_{i}",
                "unsuppression_type": "marketing"
            }),
            lambda i: track_device_deleted(authenticated_client, test_user_id, f"VOLUME_DEVICE_{i}"),
            lambda i: track_object_deleted(authenticated_client, f"VOLUME_OBJECT_{i}"),
            lambda i: track_report_delivery_event(authenticated_client, f"VOLUME_REPORT_{i}", "delivered", properties={"report_type": "data_export", "user_id": test_user_id})
        ]
        
        for i in range(10):
            event_func = gdpr_events[i % len(gdpr_events)]
            result = event_func(i)
            self.assert_successful_response(result)
            
            # Rate limiting
            if i % 3 == 0:
                self.wait_for_eventual_consistency(0.2)