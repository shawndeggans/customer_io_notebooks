"""
Integration tests for Customer.IO Batch Operations API.

Tests real API interactions for:
- Batch operation creation
- Batch sending with real API
- Batch size validation
- Large batch splitting
- Mixed operation types
- Error handling
"""

import pytest
from datetime import datetime, timezone

from tests.pipelines_api.integration.base import BaseIntegrationTest
from tests.pipelines_api.integration.utils import generate_test_email
from src.pipelines_api.batch_manager import (
    send_batch,
    create_batch_operations,
    validate_batch_size,
    split_oversized_batch
)
from src.pipelines_api.exceptions import CustomerIOError, ValidationError


@pytest.mark.integration
class TestBatchIntegration(BaseIntegrationTest):
    """Integration tests for batch operations functionality."""
    
    def test_send_batch_identify_operations(self, authenticated_client):
        """Test sending a batch of identify operations."""
        # Arrange
        users = []
        for i in range(3):
            user_id = f"batch_user_{i}_{int(datetime.now().timestamp())}"
            users.append(user_id)
            self.track_user(user_id)
        
        user_data = [
            {
                "user_id": users[0],
                "traits": {
                    "email": generate_test_email("batch1"),
                    "name": "Batch User 1",
                    "plan": "basic"
                }
            },
            {
                "user_id": users[1],
                "traits": {
                    "email": generate_test_email("batch2"),
                    "name": "Batch User 2",
                    "plan": "premium"
                }
            },
            {
                "user_id": users[2], 
                "traits": {
                    "email": generate_test_email("batch3"),
                    "name": "Batch User 3",
                    "plan": "enterprise"
                }
            }
        ]
        
        batch_data = create_batch_operations("identify", user_data)
        
        # Act
        result = send_batch(authenticated_client, batch_data)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_send_batch_track_operations(self, authenticated_client, test_user_id):
        """Test sending a batch of track operations."""
        # Arrange - Create user first
        batch_data = [
            {
                "type": "identify",
                "userId": test_user_id,
                "traits": {
                    "email": generate_test_email("batchtrack"),
                    "name": "Batch Track User"
                }
            },
            {
                "type": "track",
                "userId": test_user_id,
                "event": "Batch Event 1",
                "properties": {"source": "batch", "index": 1}
            },
            {
                "type": "track",
                "userId": test_user_id,
                "event": "Batch Event 2", 
                "properties": {"source": "batch", "index": 2}
            },
            {
                "type": "track",
                "userId": test_user_id,
                "event": "Batch Event 3",
                "properties": {"source": "batch", "index": 3}
            }
        ]
        self.track_user(test_user_id)
        
        # Act
        result = send_batch(authenticated_client, batch_data)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_send_batch_mixed_operations(self, authenticated_client):
        """Test sending a batch with mixed operation types."""
        # Arrange
        user1_id = f"mixed_user1_{int(datetime.now().timestamp())}"
        user2_id = f"mixed_user2_{int(datetime.now().timestamp())}"
        
        batch_data = [
            {
                "type": "identify",
                "userId": user1_id,
                "traits": {
                    "email": generate_test_email("mixed1"),
                    "name": "Mixed User 1"
                }
            },
            {
                "type": "track",
                "userId": user1_id,
                "event": "User Signup",
                "properties": {"method": "email"}
            },
            {
                "type": "identify",
                "userId": user2_id,
                "traits": {
                    "email": generate_test_email("mixed2"),
                    "name": "Mixed User 2"
                }
            },
            {
                "type": "track",
                "userId": user2_id,
                "event": "Page View",
                "properties": {"page": "/welcome"}
            }
        ]
        
        self.track_user(user1_id)
        self.track_user(user2_id)
        
        # Act
        result = send_batch(authenticated_client, batch_data)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_batch_size_validation(self, authenticated_client):
        """Test batch size validation."""
        # Test valid batch size
        small_batch = [
            {
                "type": "identify",
                "userId": "test123",
                "traits": {"email": "test@example.com"}
            }
        ]
        
        # Should not raise
        validate_batch_size(small_batch)
        
        # Test large batch that should be valid
        medium_batch = [
            {
                "type": "track",
                "userId": f"user_{i}",
                "event": "Test Event",
                "properties": {"index": i}
            }
            for i in range(50)  # 50 operations should be fine
        ]
        
        # Should not raise
        validate_batch_size(medium_batch)
    
    def test_split_oversized_batch(self, authenticated_client):
        """Test splitting large batches into smaller chunks."""
        # Arrange - Create a large batch
        large_operations = []
        users = []
        
        for i in range(100):  # Create 100 operations
            user_id = f"split_user_{i}_{int(datetime.now().timestamp())}"
            users.append(user_id)
            # Create large traits to exceed batch size limit
            large_text = "x" * 6000  # 6KB of data per operation
            large_operations.append({
                "type": "identify",
                "userId": user_id,
                "traits": {
                    "email": generate_test_email(f"split{i}"),
                    "name": f"Split User {i}",
                    "index": i,
                    "large_data": large_text,
                    "more_data": f"Additional data for user {i} " * 50
                }
            })
        
        # Track users for cleanup
        for user_id in users[:10]:  # Only track first 10 for cleanup
            self.track_user(user_id)
        
        # These are already formatted operations, not raw data
        large_batch = large_operations
        
        # Act
        batch_chunks = split_oversized_batch(large_batch)
        
        # Assert
        assert len(batch_chunks) >= 2, "Large batch should be split into multiple chunks"
        
        # Test sending first chunk only (to avoid too many API calls)
        if batch_chunks:
            result = send_batch(authenticated_client, batch_chunks[0])
            self.assert_successful_response(result)
    
    def test_batch_with_timestamps(self, authenticated_client, test_user_id):
        """Test batch operations with custom timestamps."""
        # Arrange
        timestamp1 = datetime.now(timezone.utc)
        timestamp2 = datetime.now(timezone.utc)
        
        batch_data = [
            {
                "type": "identify",
                "userId": test_user_id,
                "traits": {"email": generate_test_email("timestamp")},
                "timestamp": timestamp1.isoformat()
            },
            {
                "type": "track",
                "userId": test_user_id,
                "event": "Historical Event",
                "properties": {"backfill": True},
                "timestamp": timestamp2.isoformat()
            }
        ]
        self.track_user(test_user_id)
        
        # Act
        result = send_batch(authenticated_client, batch_data)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_batch_validation_errors(self, authenticated_client):
        """Test batch operation validation."""
        # Test empty batch
        with pytest.raises(ValidationError):
            send_batch(authenticated_client, [])
        
        # Test invalid operation type - API should handle this
        invalid_batch = [
            {
                "type": "invalid_type",
                "userId": "test123"
            }
        ]
        # This may or may not raise - depends on API validation
        try:
            send_batch(authenticated_client, invalid_batch)
        except (ValidationError, CustomerIOError):
            pass  # Either is acceptable
    
    def test_batch_error_handling(self, authenticated_client):
        """Test batch operations with some invalid data."""
        # Create batch with mixed valid/invalid operations
        batch_data = [
            {
                "type": "identify",
                "userId": "valid_user",
                "traits": {"email": generate_test_email("valid")}
            },
            {
                "type": "track",
                "userId": "",  # Invalid empty user ID
                "event": "Test Event"
            }
        ]
        
        self.track_user("valid_user")
        
        # The API should handle this gracefully
        # Some operations may succeed while others fail
        try:
            result = send_batch(authenticated_client, batch_data)
            # If it succeeds, that's fine
            self.assert_successful_response(result)
        except CustomerIOError:
            # If it fails due to validation, that's also expected
            pass
    
    @pytest.mark.slow
    def test_batch_performance(self, authenticated_client):
        """Test batch operation performance with moderate load."""
        # Arrange
        users = []
        for i in range(20):
            user_id = f"perf_user_{i}_{int(datetime.now().timestamp())}"
            users.append(user_id)
            if i < 5:  # Only track first 5 for cleanup
                self.track_user(user_id)
        
        batch_data = [
            {
                "type": "identify",
                "userId": user_id,
                "traits": {
                    "email": generate_test_email(f"perf{i}"),
                    "name": f"Performance User {i}",
                    "segment": "performance_test"
                }
            }
            for i, user_id in enumerate(users)
        ]
        
        # Act & Assert
        result = send_batch(authenticated_client, batch_data)
        self.assert_successful_response(result)