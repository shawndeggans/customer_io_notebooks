"""
Integration tests for Customer.IO Profile Aliasing API.

Tests real API interactions for:
- Creating aliases between user IDs
- Merging anonymous users with known users
- Complex aliasing scenarios
"""

import pytest
from datetime import datetime, timezone

from tests.pipelines_api.integration.base import BaseIntegrationTest
from tests.pipelines_api.integration.utils import generate_test_email, generate_test_traits
from src.pipelines_api.alias_manager import create_alias, merge_profiles
from src.pipelines_api.people_manager import identify_user
from src.pipelines_api.event_manager import track_event
from src.pipelines_api.exceptions import ValidationError


@pytest.mark.integration
class TestAliasIntegration(BaseIntegrationTest):
    """Integration tests for profile aliasing functionality."""
    
    def test_create_alias_basic(self, authenticated_client):
        """Test creating a basic alias between two user IDs."""
        # Arrange
        timestamp = int(datetime.now().timestamp())
        primary_id = f"test_primary_{timestamp}"
        secondary_id = f"test_secondary_{timestamp}"
        
        # Create primary user
        primary_data = {
            "userId": primary_id,
            "traits": {
                "email": generate_test_email("primary"),
                "name": "Primary User"
            }
        }
        identify_user(authenticated_client, primary_data["userId"], primary_data["traits"])
        self.track_user(primary_id)
        
        # Create secondary user
        secondary_data = {
            "userId": secondary_id,
            "traits": {
                "email": generate_test_email("secondary"),
                "name": "Secondary User"
            }
        }
        identify_user(authenticated_client, secondary_data["userId"], secondary_data["traits"])
        self.track_user(secondary_id)
        
        # Act - Create alias
        result = create_alias(authenticated_client, primary_id, secondary_id)
        self.track_alias(primary_id, secondary_id)
        
        # Assert
        self.assert_successful_response(result)
        
        # Cleanup
        self.cleanup_user(authenticated_client, primary_id)
        self.cleanup_user(authenticated_client, secondary_id)
    
    def test_merge_anonymous_to_known_user(self, authenticated_client, test_user_id, test_anonymous_id):
        """Test merging anonymous user data to known user."""
        # Arrange - Create anonymous events first
        anon_event = {
            "anonymousId": test_anonymous_id,
            "event": "Anonymous Browse",
            "properties": {
                "page": "product_page",
                "product_id": "test_123"
            }
        }
        track_event(authenticated_client, anon_event["anonymousId"], anon_event["event"], anon_event["properties"])
        
        # Create known user
        user_traits = {
            "email": generate_test_email("merge"),
            "name": "Known User"
        }
        identify_user(authenticated_client, test_user_id, user_traits)
        self.track_user(test_user_id)
        
        # Act - Merge profiles
        result = merge_profiles(authenticated_client, test_user_id, test_anonymous_id)
        self.track_alias(test_user_id, test_anonymous_id)
        
        # Assert
        self.assert_successful_response(result)
        
        # Cleanup
        self.cleanup_user(authenticated_client, test_user_id)
    
    def test_alias_chain(self, authenticated_client):
        """Test creating a chain of aliases."""
        # Arrange
        timestamp = int(datetime.now().timestamp())
        user_ids = [f"test_alias_chain_{i}_{timestamp}" for i in range(4)]
        
        try:
            # Create all users
            for i, user_id in enumerate(user_ids):
                user_traits = {
                    "email": generate_test_email(f"chain_{i}"),
                    "index": i
                }
                identify_user(authenticated_client, user_id, user_traits)
                self.track_user(user_id)
                self.wait_for_eventual_consistency(0.1)
            
            # Create chain of aliases: id3 -> id2 -> id1 -> id0
            for i in range(len(user_ids) - 1, 0, -1):
                result = create_alias(authenticated_client, user_ids[i-1], user_ids[i])
                self.assert_successful_response(result)
                self.track_alias(user_ids[i-1], user_ids[i])
                self.wait_for_eventual_consistency(0.2)
            
        finally:
            # Cleanup all users
            for user_id in user_ids:
                self.cleanup_user(authenticated_client, user_id)
    
    def test_alias_with_events(self, authenticated_client):
        """Test aliasing users who have existing events."""
        # Arrange
        timestamp = int(datetime.now().timestamp())
        old_id = f"test_old_user_{timestamp}"
        new_id = f"test_new_user_{timestamp}"
        
        try:
            # Create old user with events
            old_user_traits = {
                "email": generate_test_email("old"),
                "signup_date": "2023-01-01"
            }
            identify_user(authenticated_client, old_id, old_user_traits)
            self.track_user(old_id)
            
            # Track events for old user
            for i in range(3):
                event_data = {
                    "userId": old_id,
                    "event": f"Old User Event {i}",
                    "properties": {"index": i}
                }
                track_event(authenticated_client, event_data["userId"], event_data["event"], event_data["properties"])
                self.wait_for_eventual_consistency(0.1)
            
            # Create new user
            new_user_traits = {
                "email": generate_test_email("new"),
                "signup_date": "2024-01-01"
            }
            identify_user(authenticated_client, new_id, new_user_traits)
            self.track_user(new_id)
            
            # Act - Create alias
            result = create_alias(authenticated_client, new_id, old_id)
            self.track_alias(new_id, old_id)
            
            # Assert
            self.assert_successful_response(result)
            
            # Track event with new ID to verify alias works
            new_event = {
                "userId": new_id,
                "event": "Post-Alias Event",
                "properties": {"after_alias": True}
            }
            event_result = track_event(authenticated_client, new_event["userId"], new_event["event"], new_event["properties"])
            self.assert_successful_response(event_result)
            
        finally:
            # Cleanup
            self.cleanup_user(authenticated_client, new_id)
            self.cleanup_user(authenticated_client, old_id)
    
    def test_alias_with_timestamp(self, authenticated_client):
        """Test creating alias with custom timestamp."""
        # Arrange
        timestamp = int(datetime.now().timestamp())
        user1_id = f"test_timestamp_user1_{timestamp}"
        user2_id = f"test_timestamp_user2_{timestamp}"
        
        # Create users
        for user_id in [user1_id, user2_id]:
            user_traits = {"email": generate_test_email(user_id)}
            identify_user(authenticated_client, user_id, user_traits)
            self.track_user(user_id)
        
        try:
            # Act - Create alias with past timestamp
            past_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            result = create_alias(authenticated_client, user1_id, user2_id, timestamp=past_time)
            self.track_alias(user1_id, user2_id)
            
            # Assert
            self.assert_successful_response(result)
            
        finally:
            # Cleanup
            self.cleanup_user(authenticated_client, user1_id)
            self.cleanup_user(authenticated_client, user2_id)
    
    def test_alias_invalid_data(self, authenticated_client):
        """Test alias operations with invalid data."""
        # None userId
        with pytest.raises(ValidationError):
            create_alias(authenticated_client, None, "test_id")
        
        # Missing previousId (empty string)
        with pytest.raises(ValidationError):
            create_alias(authenticated_client, "test_id", "")
        
        # Empty userId
        with pytest.raises(ValidationError):
            create_alias(authenticated_client, "", "test_id")
        
        # Same ID for both
        with pytest.raises(ValidationError):
            create_alias(authenticated_client, "same_id", "same_id")
    
    def test_multiple_aliases_to_single_user(self, authenticated_client):
        """Test multiple users aliased to a single primary user."""
        # Arrange
        timestamp = int(datetime.now().timestamp())
        primary_id = f"test_primary_multi_{timestamp}"
        secondary_ids = [f"test_secondary_{i}_{timestamp}" for i in range(3)]
        
        try:
            # Create primary user
            primary_data = {
                "userId": primary_id,
                "traits": {
                    "email": generate_test_email("primary_multi"),
                    "role": "primary"
                }
            }
            identify_user(authenticated_client, primary_data["userId"], primary_data["traits"])
            self.track_user(primary_id)
            
            # Create and alias secondary users
            for i, secondary_id in enumerate(secondary_ids):
                # Create secondary user
                secondary_data = {
                    "userId": secondary_id,
                    "traits": {
                        "email": generate_test_email(f"secondary_{i}"),
                        "role": "secondary",
                        "index": i
                    }
                }
                identify_user(authenticated_client, secondary_data["userId"], secondary_data["traits"])
                self.track_user(secondary_id)
                
                # Create alias
                result = create_alias(authenticated_client, primary_id, secondary_id)
                self.assert_successful_response(result)
                self.track_alias(primary_id, secondary_id)
                
                # Small delay between aliases
                self.wait_for_eventual_consistency(0.2)
            
        finally:
            # Cleanup
            self.cleanup_user(authenticated_client, primary_id)
            for secondary_id in secondary_ids:
                self.cleanup_user(authenticated_client, secondary_id)
    
    def test_alias_special_characters(self, authenticated_client):
        """Test aliasing with special characters in IDs."""
        # Arrange
        timestamp = int(datetime.now().timestamp())
        user1_id = f"test-user.with_special+chars@{timestamp}"
        user2_id = f"test-user.another_special+id@{timestamp}"
        
        try:
            # Create users
            for user_id in [user1_id, user2_id]:
                user_traits = {
                    "email": generate_test_email("special"),
                    "special_id": True
                }
                identify_user(authenticated_client, user_id, user_traits)
                self.track_user(user_id)
            
            # Act - Create alias
            result = create_alias(authenticated_client, user1_id, user2_id)
            self.track_alias(user1_id, user2_id)
            
            # Assert
            self.assert_successful_response(result)
            
        finally:
            # Cleanup
            self.cleanup_user(authenticated_client, user1_id)
            self.cleanup_user(authenticated_client, user2_id)