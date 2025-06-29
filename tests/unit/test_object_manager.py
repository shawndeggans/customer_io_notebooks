"""
Unit tests for Customer.IO object management functions.
"""

from unittest.mock import Mock, patch
import pytest
from datetime import datetime, timezone

from utils.object_manager import (
    create_object,
    update_object,
    delete_object,
    create_relationship,
    delete_relationship
)
from utils.exceptions import ValidationError, CustomerIOError
from utils.api_client import CustomerIOClient


class TestCreateObject:
    """Test object creation functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_create_object_success(self, mock_client):
        """Test successful object creation."""
        result = create_object(
            client=mock_client,
            user_id="user123",
            object_id="company_acme",
            traits={"name": "Acme Corporation", "industry": "Technology"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/group",
            {
                "userId": "user123",
                "type": "group",
                "groupId": "company_acme",
                "objectTypeId": "1",
                "traits": {"name": "Acme Corporation", "industry": "Technology"}
            }
        )
        assert result == {"status": "success"}
    
    def test_create_object_with_type_id(self, mock_client):
        """Test object creation with specific object type ID."""
        result = create_object(
            client=mock_client,
            user_id="user123",
            object_id="course_python",
            traits={"name": "Python Basics", "instructor": "John Doe"},
            object_type_id="3"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/group",
            {
                "userId": "user123",
                "type": "group",
                "groupId": "course_python",
                "objectTypeId": "3",
                "traits": {"name": "Python Basics", "instructor": "John Doe"}
            }
        )
        assert result == {"status": "success"}
    
    def test_create_object_with_timestamp(self, mock_client):
        """Test object creation with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = create_object(
            client=mock_client,
            user_id="user123",
            object_id="account_pro",
            traits={"plan": "pro", "billing_status": "active"},
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/group",
            {
                "userId": "user123",
                "type": "group",
                "groupId": "account_pro",
                "objectTypeId": "1",
                "traits": {"plan": "pro", "billing_status": "active"},
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_create_object_invalid_user_id(self, mock_client):
        """Test object creation with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            create_object(
                client=mock_client,
                user_id="",
                object_id="company_acme",
                traits={"name": "Acme Corporation"}
            )
    
    def test_create_object_invalid_object_id(self, mock_client):
        """Test object creation with invalid object ID."""
        with pytest.raises(ValidationError, match="Object ID must be a non-empty string"):
            create_object(
                client=mock_client,
                user_id="user123",
                object_id="",
                traits={"name": "Acme Corporation"}
            )
    
    def test_create_object_invalid_traits(self, mock_client):
        """Test object creation with invalid traits."""
        with pytest.raises(ValidationError, match="Traits must be a dictionary"):
            create_object(
                client=mock_client,
                user_id="user123",
                object_id="company_acme",
                traits="invalid"
            )
    
    def test_create_object_empty_traits(self, mock_client):
        """Test object creation with empty traits."""
        with pytest.raises(ValidationError, match="Traits cannot be empty"):
            create_object(
                client=mock_client,
                user_id="user123",
                object_id="company_acme",
                traits={}
            )
    
    def test_create_object_invalid_object_type_id(self, mock_client):
        """Test object creation with invalid object type ID."""
        with pytest.raises(ValidationError, match="Object type ID must be a positive integer string"):
            create_object(
                client=mock_client,
                user_id="user123",
                object_id="company_acme",
                traits={"name": "Acme Corporation"},
                object_type_id="invalid"
            )
    
    def test_create_object_api_error(self, mock_client):
        """Test object creation when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            create_object(
                client=mock_client,
                user_id="user123",
                object_id="company_acme",
                traits={"name": "Acme Corporation"}
            )


class TestUpdateObject:
    """Test object update functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_update_object_success(self, mock_client):
        """Test successful object update."""
        result = update_object(
            client=mock_client,
            user_id="user123",
            object_id="company_acme",
            traits={"employee_count": 600, "plan": "enterprise"}
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/group",
            {
                "userId": "user123",
                "type": "group",
                "groupId": "company_acme",
                "objectTypeId": "1",
                "traits": {"employee_count": 600, "plan": "enterprise"}
            }
        )
        assert result == {"status": "success"}
    
    def test_update_object_with_type_id(self, mock_client):
        """Test object update with specific object type ID."""
        result = update_object(
            client=mock_client,
            user_id="user123",
            object_id="course_python",
            traits={"duration": "8 weeks", "difficulty": "beginner"},
            object_type_id="3"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/group",
            {
                "userId": "user123",
                "type": "group",
                "groupId": "course_python",
                "objectTypeId": "3",
                "traits": {"duration": "8 weeks", "difficulty": "beginner"}
            }
        )
        assert result == {"status": "success"}


class TestDeleteObject:
    """Test object deletion functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_delete_object_success(self, mock_client):
        """Test successful object deletion."""
        result = delete_object(
            client=mock_client,
            object_id="company_acme"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "event": "Object Deleted",
                "anonymousId": "system",
                "properties": {
                    "objectId": "company_acme",
                    "objectTypeId": "1"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_object_with_type_id(self, mock_client):
        """Test object deletion with specific object type ID."""
        result = delete_object(
            client=mock_client,
            object_id="course_python",
            object_type_id="3"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "event": "Object Deleted",
                "anonymousId": "system",
                "properties": {
                    "objectId": "course_python",
                    "objectTypeId": "3"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_object_with_timestamp(self, mock_client):
        """Test object deletion with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = delete_object(
            client=mock_client,
            object_id="company_acme",
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "event": "Object Deleted",
                "anonymousId": "system",
                "properties": {
                    "objectId": "company_acme",
                    "objectTypeId": "1"
                },
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_object_invalid_object_id(self, mock_client):
        """Test object deletion with invalid object ID."""
        with pytest.raises(ValidationError, match="Object ID must be a non-empty string"):
            delete_object(
                client=mock_client,
                object_id=""
            )
    
    def test_delete_object_api_error(self, mock_client):
        """Test object deletion when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            delete_object(
                client=mock_client,
                object_id="company_acme"
            )


class TestCreateRelationship:
    """Test relationship creation functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_create_relationship_success(self, mock_client):
        """Test successful relationship creation."""
        result = create_relationship(
            client=mock_client,
            user_id="user123",
            object_id="company_acme"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/group",
            {
                "userId": "user123",
                "type": "group",
                "groupId": "company_acme",
                "objectTypeId": "1",
                "traits": {}
            }
        )
        assert result == {"status": "success"}
    
    def test_create_relationship_with_type_id(self, mock_client):
        """Test relationship creation with specific object type ID."""
        result = create_relationship(
            client=mock_client,
            user_id="user123",
            object_id="course_python",
            object_type_id="3"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/group",
            {
                "userId": "user123",
                "type": "group",
                "groupId": "course_python",
                "objectTypeId": "3",
                "traits": {}
            }
        )
        assert result == {"status": "success"}
    
    def test_create_relationship_invalid_user_id(self, mock_client):
        """Test relationship creation with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            create_relationship(
                client=mock_client,
                user_id="",
                object_id="company_acme"
            )


class TestDeleteRelationship:
    """Test relationship deletion functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_delete_relationship_success(self, mock_client):
        """Test successful relationship deletion."""
        result = delete_relationship(
            client=mock_client,
            user_id="user123",
            object_id="company_acme"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "event": "Relationship Deleted",
                "userId": "user123",
                "properties": {
                    "objectId": "company_acme",
                    "objectTypeId": "1"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_relationship_with_type_id(self, mock_client):
        """Test relationship deletion with specific object type ID."""
        result = delete_relationship(
            client=mock_client,
            user_id="user123",
            object_id="course_python",
            object_type_id="3"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "event": "Relationship Deleted",
                "userId": "user123",
                "properties": {
                    "objectId": "course_python",
                    "objectTypeId": "3"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_relationship_with_timestamp(self, mock_client):
        """Test relationship deletion with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = delete_relationship(
            client=mock_client,
            user_id="user123",
            object_id="company_acme",
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "event": "Relationship Deleted",
                "userId": "user123",
                "properties": {
                    "objectId": "company_acme",
                    "objectTypeId": "1"
                },
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_relationship_invalid_user_id(self, mock_client):
        """Test relationship deletion with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            delete_relationship(
                client=mock_client,
                user_id="",
                object_id="company_acme"
            )
    
    def test_delete_relationship_invalid_object_id(self, mock_client):
        """Test relationship deletion with invalid object ID."""
        with pytest.raises(ValidationError, match="Object ID must be a non-empty string"):
            delete_relationship(
                client=mock_client,
                user_id="user123",
                object_id=""
            )


class TestObjectManagerIntegration:
    """Test integration scenarios for object and relationship management."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_object_lifecycle_workflow(self, mock_client):
        """Test complete object lifecycle workflow."""
        object_id = "company_acme"
        user_id = "user123"
        
        # Create object with user relationship
        create_result = create_object(
            client=mock_client,
            user_id=user_id,
            object_id=object_id,
            traits={"name": "Acme Corporation", "industry": "Technology"}
        )
        assert create_result == {"status": "success"}
        
        # Update object
        update_result = update_object(
            client=mock_client,
            user_id=user_id,
            object_id=object_id,
            traits={"employee_count": 500, "plan": "enterprise"}
        )
        assert update_result == {"status": "success"}
        
        # Delete relationship
        delete_rel_result = delete_relationship(
            client=mock_client,
            user_id=user_id,
            object_id=object_id
        )
        assert delete_rel_result == {"status": "success"}
        
        # Delete object
        delete_obj_result = delete_object(
            client=mock_client,
            object_id=object_id
        )
        assert delete_obj_result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 4
    
    def test_multiple_user_relationships(self, mock_client):
        """Test object with multiple user relationships."""
        object_id = "company_acme"
        users = ["user1", "user2", "user3"]
        
        # Create object and relationships for multiple users
        for user_id in users:
            result = create_relationship(
                client=mock_client,
                user_id=user_id,
                object_id=object_id
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/group"
            assert args[2]["userId"] == users[i]
            assert args[2]["groupId"] == object_id
    
    def test_batch_object_operations(self, mock_client):
        """Test batch operations on multiple objects."""
        objects = [
            {"id": "company_1", "traits": {"name": "Company 1", "industry": "Tech"}},
            {"id": "company_2", "traits": {"name": "Company 2", "industry": "Finance"}},
            {"id": "company_3", "traits": {"name": "Company 3", "industry": "Healthcare"}}
        ]
        user_id = "user123"
        
        # Create all objects
        for obj in objects:
            result = create_object(
                client=mock_client,
                user_id=user_id,
                object_id=obj["id"],
                traits=obj["traits"]
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/group"
            assert args[2]["userId"] == user_id
            assert args[2]["groupId"] == objects[i]["id"]
            assert args[2]["traits"] == objects[i]["traits"]