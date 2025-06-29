"""
Unit tests for Customer.IO alias/profile merging functions.
"""

from unittest.mock import Mock, patch
import pytest
from datetime import datetime, timezone

from utils.alias_manager import (
    create_alias,
    merge_profiles
)
from utils.exceptions import ValidationError, CustomerIOError
from utils.api_client import CustomerIOClient


class TestCreateAlias:
    """Test alias creation functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_create_alias_success(self, mock_client):
        """Test successful alias creation."""
        result = create_alias(
            client=mock_client,
            user_id="user123",
            previous_id="old_user_456"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/alias",
            {
                "userId": "user123",
                "previousId": "old_user_456"
            }
        )
        assert result == {"status": "success"}
    
    def test_create_alias_with_timestamp(self, mock_client):
        """Test alias creation with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = create_alias(
            client=mock_client,
            user_id="user123",
            previous_id="old_user_456",
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/alias",
            {
                "userId": "user123",
                "previousId": "old_user_456",
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_create_alias_with_context(self, mock_client):
        """Test alias creation with context information."""
        context = {
            "ip": "192.168.1.1",
            "userAgent": "Mozilla/5.0 (Test Browser)",
            "library": {
                "name": "customer-io-python",
                "version": "1.0.0"
            }
        }
        
        result = create_alias(
            client=mock_client,
            user_id="user123",
            previous_id="old_user_456",
            context=context
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/alias",
            {
                "userId": "user123",
                "previousId": "old_user_456",
                "context": context
            }
        )
        assert result == {"status": "success"}
    
    def test_create_alias_invalid_user_id(self, mock_client):
        """Test alias creation with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            create_alias(
                client=mock_client,
                user_id="",
                previous_id="old_user_456"
            )
    
    def test_create_alias_none_user_id(self, mock_client):
        """Test alias creation with None user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            create_alias(
                client=mock_client,
                user_id=None,
                previous_id="old_user_456"
            )
    
    def test_create_alias_invalid_previous_id(self, mock_client):
        """Test alias creation with invalid previous ID."""
        with pytest.raises(ValidationError, match="Previous ID must be a non-empty string"):
            create_alias(
                client=mock_client,
                user_id="user123",
                previous_id=""
            )
    
    def test_create_alias_none_previous_id(self, mock_client):
        """Test alias creation with None previous ID."""
        with pytest.raises(ValidationError, match="Previous ID must be a non-empty string"):
            create_alias(
                client=mock_client,
                user_id="user123",
                previous_id=None
            )
    
    def test_create_alias_same_ids(self, mock_client):
        """Test alias creation with identical user and previous IDs."""
        with pytest.raises(ValidationError, match="User ID and previous ID cannot be the same"):
            create_alias(
                client=mock_client,
                user_id="user123",
                previous_id="user123"
            )
    
    def test_create_alias_invalid_context(self, mock_client):
        """Test alias creation with invalid context."""
        with pytest.raises(ValidationError, match="Context must be a dictionary"):
            create_alias(
                client=mock_client,
                user_id="user123",
                previous_id="old_user_456",
                context="invalid"
            )
    
    def test_create_alias_api_error(self, mock_client):
        """Test alias creation when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            create_alias(
                client=mock_client,
                user_id="user123",
                previous_id="old_user_456"
            )


class TestMergeProfiles:
    """Test profile merging functionality (alias)."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_merge_profiles_success(self, mock_client):
        """Test successful profile merging."""
        result = merge_profiles(
            client=mock_client,
            primary_user_id="user123",
            secondary_user_id="old_user_456"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/alias",
            {
                "userId": "user123",
                "previousId": "old_user_456"
            }
        )
        assert result == {"status": "success"}
    
    def test_merge_profiles_with_reason(self, mock_client):
        """Test profile merging with merge reason."""
        result = merge_profiles(
            client=mock_client,
            primary_user_id="user123",
            secondary_user_id="old_user_456",
            merge_reason="email_identified"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/alias",
            {
                "userId": "user123",
                "previousId": "old_user_456",
                "context": {
                    "merge_reason": "email_identified"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_merge_profiles_with_metadata(self, mock_client):
        """Test profile merging with additional metadata."""
        result = merge_profiles(
            client=mock_client,
            primary_user_id="user123",
            secondary_user_id="old_user_456",
            merge_reason="login_detected",
            merge_source="web_app",
            confidence_score=0.95
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/alias",
            {
                "userId": "user123",
                "previousId": "old_user_456",
                "context": {
                    "merge_reason": "login_detected",
                    "merge_source": "web_app",
                    "confidence_score": 0.95
                }
            }
        )
        assert result == {"status": "success"}


class TestAliasManagerIntegration:
    """Test integration scenarios for alias operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_user_identity_consolidation_workflow(self, mock_client):
        """Test complete user identity consolidation workflow."""
        # Scenario: Anonymous user signs up, then logs in with existing account
        
        anonymous_id = "anon_789"
        temp_user_id = "temp_user_456"
        final_user_id = "user123"
        
        # First alias: Link anonymous ID to temporary user ID (signup)
        signup_result = create_alias(
            client=mock_client,
            user_id=temp_user_id,
            previous_id=anonymous_id
        )
        assert signup_result == {"status": "success"}
        
        # Second alias: Merge temporary user with existing account (login)
        login_result = merge_profiles(
            client=mock_client,
            primary_user_id=final_user_id,
            secondary_user_id=temp_user_id,
            merge_reason="login_with_existing_account"
        )
        assert login_result == {"status": "success"}
        
        # Verify both calls were made
        assert mock_client.make_request.call_count == 2
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        
        # First call (anonymous to temp)
        assert calls[0][0][2]["userId"] == temp_user_id
        assert calls[0][0][2]["previousId"] == anonymous_id
        
        # Second call (temp to final)
        assert calls[1][0][2]["userId"] == final_user_id
        assert calls[1][0][2]["previousId"] == temp_user_id
        assert calls[1][0][2]["context"]["merge_reason"] == "login_with_existing_account"
    
    def test_multiple_device_consolidation(self, mock_client):
        """Test consolidating users from multiple devices."""
        primary_user = "user123"
        device_users = [
            {"id": "mobile_user_456", "device": "mobile", "platform": "ios"},
            {"id": "tablet_user_789", "device": "tablet", "platform": "android"},
            {"id": "web_user_101", "device": "web", "platform": "desktop"}
        ]
        
        # Merge all device users into primary user
        for device_user in device_users:
            result = merge_profiles(
                client=mock_client,
                primary_user_id=primary_user,
                secondary_user_id=device_user["id"],
                merge_reason="device_consolidation",
                source_device=device_user["device"],
                source_platform=device_user["platform"]
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/alias"
            assert args[2]["userId"] == primary_user
            assert args[2]["previousId"] == device_users[i]["id"]
            assert args[2]["context"]["merge_reason"] == "device_consolidation"
            assert args[2]["context"]["source_device"] == device_users[i]["device"]
            assert args[2]["context"]["source_platform"] == device_users[i]["platform"]
    
    def test_email_verification_merge(self, mock_client):
        """Test merging profiles after email verification."""
        verified_user = "user123"
        unverified_user = "unverified_456"
        
        result = merge_profiles(
            client=mock_client,
            primary_user_id=verified_user,
            secondary_user_id=unverified_user,
            merge_reason="email_verification",
            verification_method="email_link",
            verified_at="2024-01-15T12:30:00Z"
        )
        
        assert result == {"status": "success"}
        
        # Verify call details
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/alias",
            {
                "userId": verified_user,
                "previousId": unverified_user,
                "context": {
                    "merge_reason": "email_verification",
                    "verification_method": "email_link",
                    "verified_at": "2024-01-15T12:30:00Z"
                }
            }
        )
    
    def test_social_login_merge(self, mock_client):
        """Test merging profiles during social login."""
        existing_user = "user123"
        social_user = "google_user_789"
        
        result = merge_profiles(
            client=mock_client,
            primary_user_id=existing_user,
            secondary_user_id=social_user,
            merge_reason="social_login",
            provider="google",
            provider_user_id="google_789",
            email_match=True
        )
        
        assert result == {"status": "success"}
        
        # Verify call details
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/alias",
            {
                "userId": existing_user,
                "previousId": social_user,
                "context": {
                    "merge_reason": "social_login",
                    "provider": "google",
                    "provider_user_id": "google_789",
                    "email_match": True
                }
            }
        )
    
    def test_data_migration_aliases(self, mock_client):
        """Test creating aliases during data migration."""
        migration_pairs = [
            {"old": "legacy_1", "new": "user_1"},
            {"old": "legacy_2", "new": "user_2"},
            {"old": "legacy_3", "new": "user_3"}
        ]
        
        # Create aliases for all migrated users
        for pair in migration_pairs:
            result = create_alias(
                client=mock_client,
                user_id=pair["new"],
                previous_id=pair["old"]
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/alias"
            assert args[2]["userId"] == migration_pairs[i]["new"]
            assert args[2]["previousId"] == migration_pairs[i]["old"]