"""
Unit tests for Customer.IO people management functions.
"""

from unittest.mock import Mock, patch
import pytest

from utils.people_manager import (
    identify_user,
    delete_user,
    suppress_user,
    unsuppress_user
)
from utils.exceptions import ValidationError, CustomerIOError
from utils.api_client import CustomerIOClient


class TestIdentifyUser:
    """Test user identification functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_identify_user_success(self, mock_client):
        """Test successful user identification."""
        result = identify_user(
            client=mock_client,
            user_id="user123",
            traits={"email": "test@example.com", "name": "Test User"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/identify",
            {
                "userId": "user123",
                "traits": {"email": "test@example.com", "name": "Test User"}
            }
        )
        assert result == {"status": "success"}
    
    def test_identify_user_with_minimal_traits(self, mock_client):
        """Test user identification with minimal traits."""
        result = identify_user(
            client=mock_client,
            user_id="user123",
            traits={"email": "test@example.com"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/identify",
            {
                "userId": "user123",
                "traits": {"email": "test@example.com"}
            }
        )
        assert result == {"status": "success"}
    
    def test_identify_user_with_timestamp(self, mock_client):
        """Test user identification with timestamp."""
        from datetime import datetime, timezone
        
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = identify_user(
            client=mock_client,
            user_id="user123",
            traits={"email": "test@example.com"},
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/identify",
            {
                "userId": "user123",
                "traits": {"email": "test@example.com"},
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_identify_user_invalid_user_id(self, mock_client):
        """Test identification with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            identify_user(
                client=mock_client,
                user_id="",
                traits={"email": "test@example.com"}
            )
    
    def test_identify_user_none_user_id(self, mock_client):
        """Test identification with None user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            identify_user(
                client=mock_client,
                user_id=None,
                traits={"email": "test@example.com"}
            )
    
    def test_identify_user_long_user_id(self, mock_client):
        """Test identification with user ID that's too long."""
        long_user_id = "x" * 151  # Over 150 character limit
        
        with pytest.raises(ValidationError, match="User ID must be 150 characters or less"):
            identify_user(
                client=mock_client,
                user_id=long_user_id,
                traits={"email": "test@example.com"}
            )
    
    def test_identify_user_invalid_email(self, mock_client):
        """Test identification with invalid email format."""
        with pytest.raises(ValidationError, match="Invalid email format"):
            identify_user(
                client=mock_client,
                user_id="user123",
                traits={"email": "invalid-email"}
            )
    
    def test_identify_user_empty_traits(self, mock_client):
        """Test identification with empty traits."""
        with pytest.raises(ValidationError, match="Traits cannot be empty"):
            identify_user(
                client=mock_client,
                user_id="user123",
                traits={}
            )
    
    def test_identify_user_none_traits(self, mock_client):
        """Test identification with None traits."""
        with pytest.raises(ValidationError, match="Traits must be a dictionary"):
            identify_user(
                client=mock_client,
                user_id="user123",
                traits=None
            )
    
    def test_identify_user_api_error(self, mock_client):
        """Test identification when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            identify_user(
                client=mock_client,
                user_id="user123",
                traits={"email": "test@example.com"}
            )


class TestDeleteUser:
    """Test user deletion functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_delete_user_success(self, mock_client):
        """Test successful user deletion."""
        result = delete_user(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "DELETE",
            "/identify",
            {"userId": "user123"}
        )
        assert result == {"status": "success"}
    
    def test_delete_user_invalid_user_id(self, mock_client):
        """Test deletion with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            delete_user(
                client=mock_client,
                user_id=""
            )
    
    def test_delete_user_none_user_id(self, mock_client):
        """Test deletion with None user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            delete_user(
                client=mock_client,
                user_id=None
            )
    
    def test_delete_user_long_user_id(self, mock_client):
        """Test deletion with user ID that's too long."""
        long_user_id = "x" * 151
        
        with pytest.raises(ValidationError, match="User ID must be 150 characters or less"):
            delete_user(
                client=mock_client,
                user_id=long_user_id
            )
    
    def test_delete_user_api_error(self, mock_client):
        """Test deletion when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            delete_user(
                client=mock_client,
                user_id="user123"
            )


class TestSuppressUser:
    """Test user suppression functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_suppress_user_success(self, mock_client):
        """Test successful user suppression."""
        result = suppress_user(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/identify",
            {
                "userId": "user123",
                "traits": {"unsubscribed": True}
            }
        )
        assert result == {"status": "success"}
    
    def test_suppress_user_invalid_user_id(self, mock_client):
        """Test suppression with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            suppress_user(
                client=mock_client,
                user_id=""
            )
    
    def test_suppress_user_api_error(self, mock_client):
        """Test suppression when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            suppress_user(
                client=mock_client,
                user_id="user123"
            )


class TestUnsuppressUser:
    """Test user unsuppression functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_unsuppress_user_success(self, mock_client):
        """Test successful user unsuppression."""
        result = unsuppress_user(
            client=mock_client,
            user_id="user123"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/identify",
            {
                "userId": "user123",
                "traits": {"unsubscribed": False}
            }
        )
        assert result == {"status": "success"}
    
    def test_unsuppress_user_invalid_user_id(self, mock_client):
        """Test unsuppression with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            unsuppress_user(
                client=mock_client,
                user_id=""
            )
    
    def test_unsuppress_user_api_error(self, mock_client):
        """Test unsuppression when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            unsuppress_user(
                client=mock_client,
                user_id="user123"
            )


class TestPeopleManagerIntegration:
    """Test integration scenarios for people management."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_user_lifecycle_workflow(self, mock_client):
        """Test complete user lifecycle workflow."""
        user_id = "user123"
        
        # Identify user
        identify_result = identify_user(
            client=mock_client,
            user_id=user_id,
            traits={"email": "test@example.com", "name": "Test User"}
        )
        assert identify_result == {"status": "success"}
        
        # Suppress user
        suppress_result = suppress_user(
            client=mock_client,
            user_id=user_id
        )
        assert suppress_result == {"status": "success"}
        
        # Unsuppress user
        unsuppress_result = unsuppress_user(
            client=mock_client,
            user_id=user_id
        )
        assert unsuppress_result == {"status": "success"}
        
        # Delete user
        delete_result = delete_user(
            client=mock_client,
            user_id=user_id
        )
        assert delete_result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 4
    
    def test_batch_user_operations(self, mock_client):
        """Test batch operations on multiple users."""
        users = [
            {"user_id": "user1", "email": "user1@example.com"},
            {"user_id": "user2", "email": "user2@example.com"},
            {"user_id": "user3", "email": "user3@example.com"}
        ]
        
        # Identify all users
        for user in users:
            result = identify_user(
                client=mock_client,
                user_id=user["user_id"],
                traits={"email": user["email"]}
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/identify"
            assert args[2]["userId"] == users[i]["user_id"]
            assert args[2]["traits"]["email"] == users[i]["email"]