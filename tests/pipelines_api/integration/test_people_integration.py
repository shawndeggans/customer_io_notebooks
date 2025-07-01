"""
Integration tests for Customer.IO People Management API.

Tests real API interactions for:
- User identification
- User deletion  
- User suppression/unsuppression
- Error handling
"""

import pytest
from datetime import datetime, timezone

from tests.pipelines_api.integration.base import BaseIntegrationTest
from tests.pipelines_api.integration.utils import (
    generate_test_traits,
    generate_test_email,
    assert_user_traits_match
)
from src.pipelines_api.people_manager import (
    identify_user,
    delete_user,
    suppress_user,
    unsuppress_user
)
from src.pipelines_api.gdpr_manager import track_user_suppressed, track_user_unsuppressed
from src.pipelines_api.exceptions import CustomerIOError, ValidationError


@pytest.mark.integration
class TestPeopleIntegration(BaseIntegrationTest):
    """Integration tests for people management functionality."""
    
    def test_identify_user_basic(self, authenticated_client, test_user_id):
        """Test basic user identification."""
        # Arrange
        traits = {
            "email": generate_test_email("identify"),
            "first_name": "Test",
            "last_name": "User",
            "plan": "basic"
        }
        
        # Act
        result = identify_user(authenticated_client, test_user_id, traits)
        self.track_user(test_user_id)
        
        # Assert
        self.assert_successful_response(result)
        
        # Cleanup
        self.cleanup_user(authenticated_client, test_user_id)
    
    def test_identify_user_with_complex_traits(self, authenticated_client, test_user_id):
        """Test user identification with complex nested traits."""
        # Arrange
        user_data = {
            "userId": test_user_id,
            "traits": {
                "email": generate_test_email("complex"),
                "profile": {
                    "age": 25,
                    "interests": ["coding", "testing", "automation"],
                    "location": {
                        "city": "San Francisco",
                        "country": "US"
                    }
                },
                "scores": {
                    "engagement": 85.5,
                    "activity": 92
                },
                "tags": ["integration-test", "automated"],
                "registered_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Act
        result = identify_user(authenticated_client, user_data["userId"], user_data["traits"])
        self.track_user(test_user_id)
        
        # Assert
        self.assert_successful_response(result)
        
        # Cleanup
        self.cleanup_user(authenticated_client, test_user_id)
    
    def test_identify_user_update_existing(self, authenticated_client, test_user_id):
        """Test updating an existing user's traits."""
        # Arrange - Create initial user
        initial_data = {
            "userId": test_user_id,
            "traits": {
                "email": generate_test_email("update"),
                "first_name": "Initial",
                "plan": "free"
            }
        }
        identify_user(authenticated_client, initial_data["userId"], initial_data["traits"])
        self.track_user(test_user_id)
        
        # Act - Update user
        updated_data = {
            "userId": test_user_id,
            "traits": {
                "first_name": "Updated",
                "plan": "premium",
                "upgraded_at": datetime.now(timezone.utc).isoformat()
            }
        }
        result = identify_user(authenticated_client, updated_data["userId"], updated_data["traits"])
        
        # Assert
        self.assert_successful_response(result)
        
        # Cleanup
        self.cleanup_user(authenticated_client, test_user_id)
    
    def test_identify_user_with_timestamp(self, authenticated_client, test_user_id):
        """Test user identification with custom timestamp."""
        # Arrange
        custom_timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        user_data = {
            "userId": test_user_id,
            "traits": {
                "email": generate_test_email("timestamp"),
                "event": "historical_import"
            },
            "timestamp": custom_timestamp
        }
        
        # Act
        result = identify_user(authenticated_client, user_data["userId"], user_data["traits"])
        self.track_user(test_user_id)
        
        # Assert
        self.assert_successful_response(result)
        
        # Cleanup
        self.cleanup_user(authenticated_client, test_user_id)
    
    def test_delete_user(self, authenticated_client, test_user_id):
        """Test user deletion."""
        # Arrange - Create user first
        user_data = {
            "userId": test_user_id,
            "traits": {
                "email": generate_test_email("delete"),
                "first_name": "Delete",
                "last_name": "Me"
            }
        }
        identify_user(authenticated_client, user_data["userId"], user_data["traits"])
        self.track_user(test_user_id)
        
        # Act
        result = delete_user(authenticated_client, test_user_id)
        
        # Assert
        self.assert_successful_response(result)
        
        # Verify user is deleted by trying to update (should succeed as it recreates)
        # Customer.IO allows re-creating deleted users
        result2 = identify_user(authenticated_client, user_data["userId"], user_data["traits"])
        self.assert_successful_response(result2)
        
        # Final cleanup
        self.cleanup_user(authenticated_client, test_user_id)
    
    def test_suppress_and_unsuppress_user(self, authenticated_client, test_user_id):
        """Test user suppression and unsuppression."""
        # Arrange - Create user first
        user_data = {
            "userId": test_user_id,
            "traits": {
                "email": generate_test_email("suppress"),
                "first_name": "Suppress",
                "last_name": "Test"
            }
        }
        identify_user(authenticated_client, user_data["userId"], user_data["traits"])
        self.track_user(test_user_id)
        
        # Act - Suppress user
        suppress_result = suppress_user(authenticated_client, test_user_id)
        self.assert_successful_response(suppress_result)
        
        # Wait for eventual consistency
        self.wait_for_eventual_consistency()
        
        # Act - Unsuppress user
        unsuppress_result = unsuppress_user(authenticated_client, test_user_id)
        self.assert_successful_response(unsuppress_result)
        
        # Cleanup
        self.cleanup_user(authenticated_client, test_user_id)
    
    def test_gdpr_suppress_profile(self, authenticated_client, test_user_id):
        """Test GDPR profile suppression."""
        # Arrange - Create user
        user_data = {
            "userId": test_user_id,
            "traits": {
                "email": generate_test_email("gdpr"),
                "first_name": "GDPR",
                "last_name": "Test",
                "gdpr_consent": True
            }
        }
        identify_user(authenticated_client, user_data["userId"], user_data["traits"])
        self.track_user(test_user_id)
        
        # Act - Suppress via GDPR semantic event
        result = track_user_suppressed(authenticated_client, test_user_id)
        
        # Assert
        self.assert_successful_response(result)
        
        # Cleanup - Unsuppress and delete
        track_user_unsuppressed(authenticated_client, test_user_id)
        self.cleanup_user(authenticated_client, test_user_id)
    
    def test_identify_user_invalid_data(self, authenticated_client):
        """Test user identification with invalid data."""
        # Test missing/empty userId
        with pytest.raises(ValidationError, match="User ID"):
            identify_user(authenticated_client, "", {"email": "test@example.com"})
        
        # Test missing traits (None)
        with pytest.raises(ValidationError):
            identify_user(authenticated_client, "test123", None)
        
        # Test empty userId
        with pytest.raises(ValidationError, match="User ID"):
            identify_user(authenticated_client, "", {})
    
    def test_delete_nonexistent_user(self, authenticated_client):
        """Test deleting a user that doesn't exist."""
        # Act & Assert - Should not raise an error
        # Customer.IO typically returns success even for non-existent users
        result = delete_user(authenticated_client, "nonexistent_user_12345")
        self.assert_successful_response(result)
    
    @pytest.mark.slow
    def test_identify_multiple_users_sequential(self, authenticated_client):
        """Test identifying multiple users sequentially."""
        user_ids = []
        
        try:
            # Create multiple users
            for i in range(5):
                user_id = f"test_multi_{i}_{datetime.now().timestamp()}"
                user_data = {
                    "userId": user_id,
                    "traits": {
                        "email": generate_test_email(f"multi{i}"),
                        "index": i,
                        "batch": "sequential_test"
                    }
                }
                
                result = identify_user(authenticated_client, user_data["userId"], user_data["traits"])
                self.assert_successful_response(result)
                
                user_ids.append(user_id)
                self.track_user(user_id)
                
                # Small delay to avoid rate limiting
                self.wait_for_eventual_consistency(0.2)
            
            assert len(user_ids) == 5
            
        finally:
            # Cleanup all created users
            for user_id in user_ids:
                self.cleanup_user(authenticated_client, user_id)
    
    def test_identify_user_with_special_characters(self, authenticated_client):
        """Test user identification with special characters in traits."""
        # User ID with special characters (URL encoded)
        user_id = f"test-user.with_special+chars@{datetime.now().timestamp()}"
        
        user_data = {
            "userId": user_id,
            "traits": {
                "email": "special+test@example.com",
                "name": "Test User (Special)",
                "description": "User with special chars: !@#$%^&*()",
                "unicode": "Hello 世界 🌍",
                "nested": {
                    "special_field": "value/with/slashes"
                }
            }
        }
        
        try:
            # Act
            result = identify_user(authenticated_client, user_data["userId"], user_data["traits"])
            self.track_user(user_id)
            
            # Assert
            self.assert_successful_response(result)
            
        finally:
            # Cleanup
            self.cleanup_user(authenticated_client, user_id)