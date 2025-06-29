"""
Unit tests for Customer.IO batch operations functions.
"""

from unittest.mock import Mock, patch
import pytest
from datetime import datetime, timezone
from typing import List, Dict, Any

from utils.batch_manager import (
    send_batch,
    create_batch_operations,
    validate_batch_size,
    split_oversized_batch
)
from utils.exceptions import ValidationError, CustomerIOError
from utils.api_client import CustomerIOClient


class TestSendBatch:
    """Test batch sending functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {}
        return client
    
    def test_send_batch_success(self, mock_client):
        """Test successful batch sending."""
        operations = [
            {
                "type": "identify",
                "userId": "user123",
                "traits": {"email": "user@example.com", "name": "John Doe"}
            },
            {
                "type": "track",
                "userId": "user123",
                "event": "Product Viewed",
                "properties": {"product_id": "prod_123", "price": 29.99}
            }
        ]
        
        result = send_batch(
            client=mock_client,
            operations=operations
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/batch",
            {
                "batch": operations
            }
        )
        assert result == {}
    
    def test_send_batch_with_context(self, mock_client):
        """Test batch sending with context."""
        operations = [
            {
                "type": "identify",
                "userId": "user123",
                "traits": {"email": "user@example.com"}
            }
        ]
        
        context = {
            "ip": "192.168.1.1",
            "userAgent": "Mozilla/5.0 (Test Browser)"
        }
        
        result = send_batch(
            client=mock_client,
            operations=operations,
            context=context
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/batch",
            {
                "batch": operations,
                "context": context
            }
        )
        assert result == {}
    
    def test_send_batch_with_integrations(self, mock_client):
        """Test batch sending with integrations config."""
        operations = [
            {
                "type": "track",
                "userId": "user123",
                "event": "Purchase",
                "properties": {"amount": 99.99}
            }
        ]
        
        integrations = {
            "All": True,
            "Salesforce": False
        }
        
        result = send_batch(
            client=mock_client,
            operations=operations,
            integrations=integrations
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/batch",
            {
                "batch": operations,
                "integrations": integrations
            }
        )
        assert result == {}
    
    def test_send_batch_empty_operations(self, mock_client):
        """Test batch sending with empty operations."""
        with pytest.raises(ValidationError, match="Operations list cannot be empty"):
            send_batch(
                client=mock_client,
                operations=[]
            )
    
    def test_send_batch_invalid_operations(self, mock_client):
        """Test batch sending with invalid operations."""
        with pytest.raises(ValidationError, match="Operations must be a list"):
            send_batch(
                client=mock_client,
                operations="invalid"
            )
    
    def test_send_batch_api_error(self, mock_client):
        """Test batch sending when API returns error."""
        operations = [
            {
                "type": "identify",
                "userId": "user123",
                "traits": {"email": "user@example.com"}
            }
        ]
        
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            send_batch(
                client=mock_client,
                operations=operations
            )


class TestCreateBatchOperations:
    """Test batch operations creation functionality."""
    
    def test_create_identify_operations(self):
        """Test creating identify operations for batch."""
        users = [
            {"user_id": "user1", "traits": {"email": "user1@example.com", "name": "User One"}},
            {"user_id": "user2", "traits": {"email": "user2@example.com", "name": "User Two"}}
        ]
        
        operations = create_batch_operations("identify", users)
        
        expected = [
            {
                "type": "identify",
                "userId": "user1",
                "traits": {"email": "user1@example.com", "name": "User One"}
            },
            {
                "type": "identify", 
                "userId": "user2",
                "traits": {"email": "user2@example.com", "name": "User Two"}
            }
        ]
        
        assert operations == expected
    
    def test_create_track_operations(self):
        """Test creating track operations for batch."""
        events = [
            {"user_id": "user1", "event": "Product Viewed", "properties": {"product_id": "prod_1"}},
            {"user_id": "user2", "event": "Add to Cart", "properties": {"product_id": "prod_2", "quantity": 2}}
        ]
        
        operations = create_batch_operations("track", events)
        
        expected = [
            {
                "type": "track",
                "userId": "user1",
                "event": "Product Viewed",
                "properties": {"product_id": "prod_1"}
            },
            {
                "type": "track",
                "userId": "user2", 
                "event": "Add to Cart",
                "properties": {"product_id": "prod_2", "quantity": 2}
            }
        ]
        
        assert operations == expected
    
    def test_create_group_operations(self):
        """Test creating group operations for batch."""
        groups = [
            {"user_id": "user1", "group_id": "company_1", "traits": {"name": "Company One", "plan": "pro"}},
            {"user_id": "user2", "group_id": "company_2", "traits": {"name": "Company Two", "plan": "enterprise"}}
        ]
        
        operations = create_batch_operations("group", groups)
        
        expected = [
            {
                "type": "group",
                "userId": "user1",
                "groupId": "company_1",
                "traits": {"name": "Company One", "plan": "pro"}
            },
            {
                "type": "group",
                "userId": "user2",
                "groupId": "company_2", 
                "traits": {"name": "Company Two", "plan": "enterprise"}
            }
        ]
        
        assert operations == expected
    
    def test_create_page_operations(self):
        """Test creating page operations for batch."""
        pages = [
            {"user_id": "user1", "name": "Home Page", "properties": {"url": "https://example.com"}},
            {"user_id": "user2", "name": "Product Page", "properties": {"url": "https://example.com/product/123"}}
        ]
        
        operations = create_batch_operations("page", pages)
        
        expected = [
            {
                "type": "page",
                "userId": "user1",
                "name": "Home Page",
                "properties": {"url": "https://example.com"}
            },
            {
                "type": "page",
                "userId": "user2",
                "name": "Product Page", 
                "properties": {"url": "https://example.com/product/123"}
            }
        ]
        
        assert operations == expected
    
    def test_create_screen_operations(self):
        """Test creating screen operations for batch."""
        screens = [
            {"user_id": "user1", "name": "Dashboard", "properties": {"screen_class": "DashboardViewController"}},
            {"user_id": "user2", "name": "Settings", "properties": {"screen_class": "SettingsViewController"}}
        ]
        
        operations = create_batch_operations("screen", screens)
        
        expected = [
            {
                "type": "screen",
                "userId": "user1",
                "name": "Dashboard",
                "properties": {"screen_class": "DashboardViewController"}
            },
            {
                "type": "screen",
                "userId": "user2",
                "name": "Settings",
                "properties": {"screen_class": "SettingsViewController"}
            }
        ]
        
        assert operations == expected
    
    def test_create_operations_invalid_type(self):
        """Test creating operations with invalid type."""
        with pytest.raises(ValidationError, match="Invalid operation type"):
            create_batch_operations("invalid", [])
    
    def test_create_operations_empty_data(self):
        """Test creating operations with empty data."""
        with pytest.raises(ValidationError, match="Data list cannot be empty"):
            create_batch_operations("identify", [])


class TestValidateBatchSize:
    """Test batch size validation functionality."""
    
    def test_validate_batch_size_success(self):
        """Test successful batch size validation."""
        operations = [
            {
                "type": "identify",
                "userId": "user123",
                "traits": {"email": "user@example.com"}
            }
        ]
        
        # Should not raise any exception
        validate_batch_size(operations)
    
    def test_validate_batch_size_too_large(self):
        """Test batch size validation with oversized batch."""
        # Create operations that exceed 500KB
        large_traits = {"description": "x" * 100000}  # ~100KB string
        operations = []
        
        for i in range(6):  # 6 * 100KB = ~600KB > 500KB limit
            operations.append({
                "type": "identify",
                "userId": f"user{i}",
                "traits": large_traits
            })
        
        with pytest.raises(ValidationError, match="Batch size .* exceeds maximum allowed size"):
            validate_batch_size(operations)
    
    def test_validate_batch_size_single_operation_too_large(self):
        """Test batch size validation with single oversized operation."""
        # Create single operation that exceeds 32KB
        large_traits = {"description": "x" * 33000}  # ~33KB > 32KB limit
        operations = [
            {
                "type": "identify",
                "userId": "user123",
                "traits": large_traits
            }
        ]
        
        with pytest.raises(ValidationError, match="Operation .* exceeds maximum size"):
            validate_batch_size(operations)
    
    def test_validate_batch_size_empty_operations(self):
        """Test batch size validation with empty operations."""
        with pytest.raises(ValidationError, match="Operations list cannot be empty"):
            validate_batch_size([])


class TestSplitOversizedBatch:
    """Test oversized batch splitting functionality."""
    
    def test_split_oversized_batch_success(self):
        """Test splitting an oversized batch."""
        # Create operations that exceed 500KB but stay under 32KB each
        large_traits = {"description": "x" * 25000}  # ~25KB string (under 32KB limit)
        operations = []
        
        for i in range(25):  # 25 * 25KB = ~625KB > 500KB limit
            operations.append({
                "type": "identify",
                "userId": f"user{i}",
                "traits": large_traits
            })
        
        batches = split_oversized_batch(operations)
        
        # Should be split into multiple batches
        assert len(batches) > 1
        
        # Each batch should be under size limit
        for batch in batches:
            validate_batch_size(batch)  # Should not raise exception
    
    def test_split_oversized_batch_single_batch(self):
        """Test splitting a batch that's already under size limit."""
        operations = [
            {
                "type": "identify",
                "userId": "user123",
                "traits": {"email": "user@example.com"}
            }
        ]
        
        batches = split_oversized_batch(operations)
        
        # Should return single batch
        assert len(batches) == 1
        assert batches[0] == operations
    
    def test_split_oversized_batch_individual_operation_too_large(self):
        """Test splitting batch with individual operation too large."""
        # Create single operation that exceeds 32KB
        large_traits = {"description": "x" * 33000}  # ~33KB > 32KB limit
        operations = [
            {
                "type": "identify",
                "userId": "user123",
                "traits": large_traits
            }
        ]
        
        with pytest.raises(ValidationError, match="Individual operation exceeds maximum size"):
            split_oversized_batch(operations)


class TestBatchManagerIntegration:
    """Test integration scenarios for batch operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {}
        return client
    
    def test_complete_batch_workflow(self, mock_client):
        """Test complete batch processing workflow."""
        # Create mixed operations
        identify_data = [
            {"user_id": "user1", "traits": {"email": "user1@example.com", "name": "User One"}},
            {"user_id": "user2", "traits": {"email": "user2@example.com", "name": "User Two"}}
        ]
        
        track_data = [
            {"user_id": "user1", "event": "Login", "properties": {"source": "web"}},
            {"user_id": "user2", "event": "Purchase", "properties": {"amount": 99.99}}
        ]
        
        # Create operations
        identify_ops = create_batch_operations("identify", identify_data)
        track_ops = create_batch_operations("track", track_data)
        
        # Combine operations
        all_operations = identify_ops + track_ops
        
        # Validate size
        validate_batch_size(all_operations)
        
        # Send batch
        result = send_batch(
            client=mock_client,
            operations=all_operations
        )
        
        # Verify
        assert result == {}
        mock_client.make_request.assert_called_once()
        args, kwargs = mock_client.make_request.call_args
        assert args[0] == "POST"
        assert args[1] == "/batch"
        assert len(args[2]["batch"]) == 4
    
    def test_batch_size_management_workflow(self, mock_client):
        """Test batch size management and splitting."""
        # Create operations that will exceed size limits but stay under individual limit
        large_traits = {"description": "x" * 20000}  # ~20KB string (under 32KB limit)
        users = []
        
        for i in range(30):  # 30 * 20KB = ~600KB > 500KB limit
            users.append({
                "user_id": f"user{i}",
                "traits": large_traits
            })
        
        # Create operations
        operations = create_batch_operations("identify", users)
        
        # Split oversized batch
        batches = split_oversized_batch(operations)
        
        # Send each batch
        results = []
        for batch in batches:
            result = send_batch(client=mock_client, operations=batch)
            results.append(result)
        
        # Verify
        assert len(batches) > 1  # Should be split
        assert len(results) == len(batches)
        assert all(result == {} for result in results)
        assert mock_client.make_request.call_count == len(batches)
    
    def test_batch_with_context_and_integrations(self, mock_client):
        """Test batch with context and integrations."""
        operations = create_batch_operations("track", [
            {"user_id": "user1", "event": "Purchase", "properties": {"amount": 50.00}},
            {"user_id": "user2", "event": "Signup", "properties": {"source": "referral"}}
        ])
        
        context = {
            "ip": "192.168.1.100",
            "userAgent": "Test Suite",
            "library": {"name": "customer-io-python", "version": "1.0.0"}
        }
        
        integrations = {
            "All": True,
            "Salesforce": False,
            "Webhook": True
        }
        
        result = send_batch(
            client=mock_client,
            operations=operations,
            context=context,
            integrations=integrations
        )
        
        # Verify
        assert result == {}
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/batch",
            {
                "batch": operations,
                "context": context,
                "integrations": integrations
            }
        )