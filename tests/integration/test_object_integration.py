"""
Integration tests for Customer.IO Object Management API.

Tests real API interactions for:
- Object creation and updates
- Object deletion
- Relationship management
- Complex object hierarchies
- Error handling
"""

import pytest
from datetime import datetime, timezone

from tests.integration.base import BaseIntegrationTest
from tests.integration.utils import generate_test_email
from utils.object_manager import (
    create_object,
    update_object,
    delete_object,
    create_relationship,
    delete_relationship
)
from utils.people_manager import identify_user
from utils.exceptions import CustomerIOError, ValidationError


@pytest.mark.integration
class TestObjectIntegration(BaseIntegrationTest):
    """Integration tests for object management functionality."""
    
    def test_create_object_basic(self, authenticated_client, test_user_id, test_object_id):
        """Test creating a basic object."""
        # Arrange - Create user first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("objbasic"),
            "name": "Object Test User"
        })
        self.track_user(test_user_id)
        
        # Act
        result = create_object(
            authenticated_client,
            test_user_id,
            test_object_id,
            {
                "name": "Test Product",
                "category": "electronics",
                "price": 299.99,
                "in_stock": True
            }
        )
        self.track_object("product", test_object_id)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_update_object(self, authenticated_client, test_user_id, test_object_id):
        """Test updating an existing object."""
        # Arrange - Create user and object first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("objupdate"),
            "name": "Update Test User"
        })
        self.track_user(test_user_id)
        
        create_object(
            authenticated_client,
            test_user_id,
            test_object_id,
            {
                "name": "Original Product",
                "price": 199.99,
                "status": "draft"
            }
        )
        self.track_object("product", test_object_id)
        
        # Act - Update the object
        result = update_object(
            authenticated_client,
            test_user_id,
            test_object_id,
            {
                "name": "Updated Product",
                "price": 249.99,
                "status": "published",
                "last_modified": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_delete_object(self, authenticated_client, test_user_id, test_object_id):
        """Test deleting an object."""
        # Arrange - Create user and object first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("objdelete"),
            "name": "Delete Test User"
        })
        self.track_user(test_user_id)
        
        create_object(
            authenticated_client,
            test_user_id,
            test_object_id,
            {
                "name": "Temporary Product",
                "temporary": True
            }
        )
        self.track_object("product", test_object_id)
        
        # Act
        result = delete_object(authenticated_client, test_object_id)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_create_relationship(self, authenticated_client, test_user_id, test_object_id):
        """Test creating a relationship between user and object."""
        # Arrange - Create user and object
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("relationship"),
            "name": "Relationship Test User"
        })
        self.track_user(test_user_id)
        
        create_object(authenticated_client, test_user_id, test_object_id, {
            "name": "Relationship Product",
            "type": "product"
        })
        self.track_object("product", test_object_id)
        
        # Act
        result = create_relationship(
            authenticated_client,
            test_user_id,
            test_object_id
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_delete_relationship(self, authenticated_client, test_user_id, test_object_id):
        """Test deleting a relationship."""
        # Arrange - Create user, object, and relationship
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("delrel"),
            "name": "Delete Relationship User"
        })
        self.track_user(test_user_id)
        
        create_object(authenticated_client, test_user_id, test_object_id, {
            "name": "Temporary Relationship Product"
        })
        self.track_object("product", test_object_id)
        
        create_relationship(
            authenticated_client,
            test_user_id,
            test_object_id
        )
        
        # Act
        result = delete_relationship(
            authenticated_client,
            test_user_id,
            test_object_id
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_complex_object_with_nested_data(self, authenticated_client, test_user_id, test_object_id):
        """Test creating object with complex nested data."""
        # Arrange - Create user first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("complex"),
            "name": "Complex Test User"
        })
        self.track_user(test_user_id)
        
        # Act
        result = create_object(
            authenticated_client,
            test_user_id,
            test_object_id,
            {
                "name": "Complex Product",
                "specifications": {
                    "dimensions": {
                        "width": 10.5,
                        "height": 8.2,
                        "depth": 3.1
                    },
                    "features": ["waterproof", "wireless", "portable"],
                    "compatibility": {
                        "ios": True,
                        "android": True,
                        "windows": False
                    }
                },
                "inventory": {
                    "warehouse_a": 150,
                    "warehouse_b": 75,
                    "total": 225
                },
                "tags": ["electronics", "mobile", "accessory"]
            }
        )
        self.track_object("product", test_object_id)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_multiple_relationships(self, authenticated_client):
        """Test creating multiple relationships for one user."""
        # Arrange
        user_id = f"multi_rel_user_{int(datetime.now().timestamp())}"
        object_ids = []
        
        for i in range(3):
            object_id = f"multi_rel_obj_{i}_{int(datetime.now().timestamp())}"
            object_ids.append(object_id)
            self.track_object("product", object_id)
        
        self.track_user(user_id)
        
        # Create user
        identify_user(authenticated_client, user_id, {
            "email": generate_test_email("multirel"),
            "name": "Multi Relationship User"
        })
        
        # Create objects
        for i, object_id in enumerate(object_ids):
            create_object(authenticated_client, user_id, object_id, {
                "name": f"Product {i+1}",
                "category": "test",
                "index": i
            })
        
        # Act - Create relationships
        for i, object_id in enumerate(object_ids):
            result = create_relationship(
                authenticated_client,
                user_id,
                object_id
            )
            self.assert_successful_response(result)
            # Small delay for rate limiting
            self.wait_for_eventual_consistency(0.1)
    
    def test_object_lifecycle(self, authenticated_client, test_user_id, test_object_id):
        """Test complete object lifecycle: create, update, delete."""
        # Arrange - Create user first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("lifecycle"),
            "name": "Lifecycle Test User"
        })
        self.track_user(test_user_id)
        
        # Create
        create_result = create_object(
            authenticated_client,
            test_user_id,
            test_object_id,
            {
                "name": "Lifecycle Product",
                "status": "draft",
                "version": 1
            }
        )
        self.track_object("product", test_object_id)
        self.assert_successful_response(create_result)
        
        # Update
        update_result = update_object(
            authenticated_client,
            test_user_id,
            test_object_id,
            {
                "status": "published",
                "version": 2,
                "published_at": datetime.now(timezone.utc).isoformat()
            }
        )
        self.assert_successful_response(update_result)
        
        # Delete
        delete_result = delete_object(authenticated_client, test_object_id)
        self.assert_successful_response(delete_result)
    
    def test_object_validation_errors(self, authenticated_client):
        """Test object validation errors."""
        # Test empty object ID
        with pytest.raises(ValidationError):
            create_object(authenticated_client, "user123", "", {"name": "Test"})
        
        # Test empty object data
        with pytest.raises(ValidationError):
            create_object(authenticated_client, "user123", "test_obj", {})
    
    def test_relationship_validation_errors(self, authenticated_client):
        """Test relationship validation errors."""
        # Test empty user ID
        with pytest.raises(ValidationError):
            create_relationship(authenticated_client, "", "obj123", {})
        
        # Test empty object ID
        with pytest.raises(ValidationError):
            create_relationship(authenticated_client, "user123", "", {})
    
    def test_object_with_timestamps(self, authenticated_client, test_user_id, test_object_id):
        """Test creating objects with custom timestamps."""
        # Arrange - Create user first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("timestamp"),
            "name": "Timestamp Test User"
        })
        self.track_user(test_user_id)
        
        custom_timestamp = datetime.now(timezone.utc)
        
        # Act
        result = create_object(
            authenticated_client,
            test_user_id,
            test_object_id,
            {
                "name": "Timestamped Product",
                "created_at": custom_timestamp.isoformat(),
                "is_historical": True
            },
            timestamp=custom_timestamp
        )
        self.track_object("product", test_object_id)
        
        # Assert
        self.assert_successful_response(result)
    
    @pytest.mark.slow
    def test_bulk_object_operations(self, authenticated_client):
        """Test creating multiple objects for performance testing."""
        object_ids = []
        
        # Create multiple objects
        for i in range(10):
            object_id = f"bulk_obj_{i}_{int(datetime.now().timestamp())}"
            object_ids.append(object_id)
            
            if i < 3:  # Only track first 3 for cleanup
                self.track_object("product", object_id)
            
            # Create a test user for this object
            user_id = f"bulk_user_{i}_{int(datetime.now().timestamp())}"
            identify_user(authenticated_client, user_id, {
                "email": generate_test_email(f"bulk{i}"),
                "name": f"Bulk User {i}"
            })
            if i < 3:  # Only track first 3 users for cleanup
                self.track_user(user_id)
            
            result = create_object(
                authenticated_client,
                user_id,
                object_id,
                {
                    "name": f"Bulk Product {i}",
                    "index": i,
                    "bulk_test": True,
                    "created_in_batch": True
                }
            )
            self.assert_successful_response(result)
            
            # Rate limiting
            if i % 3 == 0:
                self.wait_for_eventual_consistency(0.1)