"""
Unit tests for Customer.IO device management functions.
"""

from unittest.mock import Mock
import pytest
from datetime import datetime, timezone

from src.pipelines_api.device_manager import (
    register_device,
    update_device,
    delete_device
)
from src.pipelines_api.exceptions import ValidationError, CustomerIOError
from src.pipelines_api.api_client import CustomerIOClient


class TestRegisterDevice:
    """Test device registration functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_register_device_success(self, mock_client):
        """Test successful device registration."""
        result = register_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken",
            device_type="ios"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Created or Updated",
                "userId": "user123",
                "context": {
                    "device": {
                        "token": "abc123devicetoken",
                        "type": "ios"
                    }
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_register_device_minimal_params(self, mock_client):
        """Test device registration with minimal parameters."""
        result = register_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Created or Updated",
                "userId": "user123",
                "context": {
                    "device": {
                        "token": "abc123devicetoken"
                    }
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_register_device_with_metadata(self, mock_client):
        """Test device registration with additional metadata."""
        metadata = {
            "manufacturer": "Apple",
            "model": "iPhone 13",
            "version": "15.0.1"
        }
        
        result = register_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken",
            device_type="ios",
            metadata=metadata
        )
        
        expected_device = {
            "token": "abc123devicetoken",
            "type": "ios",
            "manufacturer": "Apple",
            "model": "iPhone 13",
            "version": "15.0.1"
        }
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Created or Updated",
                "userId": "user123",
                "context": {
                    "device": expected_device
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_register_device_with_timestamp(self, mock_client):
        """Test device registration with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = register_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken",
            device_type="android",
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Created or Updated",
                "userId": "user123",
                "context": {
                    "device": {
                        "token": "abc123devicetoken",
                        "type": "android"
                    }
                },
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_register_device_invalid_user_id(self, mock_client):
        """Test device registration with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            register_device(
                client=mock_client,
                user_id="",
                device_token="abc123devicetoken"
            )
    
    def test_register_device_invalid_device_token(self, mock_client):
        """Test device registration with invalid device token."""
        with pytest.raises(ValidationError, match="Device token must be a non-empty string"):
            register_device(
                client=mock_client,
                user_id="user123",
                device_token=""
            )
    
    def test_register_device_none_device_token(self, mock_client):
        """Test device registration with None device token."""
        with pytest.raises(ValidationError, match="Device token must be a non-empty string"):
            register_device(
                client=mock_client,
                user_id="user123",
                device_token=None
            )
    
    def test_register_device_invalid_device_type(self, mock_client):
        """Test device registration with invalid device type."""
        with pytest.raises(ValidationError, match="Device type must be 'ios' or 'android'"):
            register_device(
                client=mock_client,
                user_id="user123",
                device_token="abc123devicetoken",
                device_type="invalid"
            )
    
    def test_register_device_api_error(self, mock_client):
        """Test device registration when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            register_device(
                client=mock_client,
                user_id="user123",
                device_token="abc123devicetoken"
            )


class TestUpdateDevice:
    """Test device update functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_update_device_success(self, mock_client):
        """Test successful device update."""
        result = update_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken",
            device_type="ios"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Created or Updated",
                "userId": "user123",
                "context": {
                    "device": {
                        "token": "abc123devicetoken",
                        "type": "ios"
                    }
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_update_device_with_new_metadata(self, mock_client):
        """Test device update with new metadata."""
        metadata = {
            "version": "16.0.2",
            "name": "John's iPhone"
        }
        
        result = update_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken",
            metadata=metadata
        )
        
        expected_device = {
            "token": "abc123devicetoken",
            "version": "16.0.2",
            "name": "John's iPhone"
        }
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Created or Updated",
                "userId": "user123",
                "context": {
                    "device": expected_device
                }
            }
        )
        assert result == {"status": "success"}


class TestDeleteDevice:
    """Test device deletion functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_delete_device_success(self, mock_client):
        """Test successful device deletion."""
        result = delete_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Deleted",
                "userId": "user123",
                "context": {
                    "device": {
                        "token": "abc123devicetoken"
                    }
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_device_with_type(self, mock_client):
        """Test device deletion with device type."""
        result = delete_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken",
            device_type="android"
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Deleted",
                "userId": "user123",
                "context": {
                    "device": {
                        "token": "abc123devicetoken",
                        "type": "android"
                    }
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_device_with_timestamp(self, mock_client):
        """Test device deletion with timestamp."""
        timestamp = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        
        result = delete_device(
            client=mock_client,
            user_id="user123",
            device_token="abc123devicetoken",
            timestamp=timestamp
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "type": "track",
                "event": "Device Deleted",
                "userId": "user123",
                "context": {
                    "device": {
                        "token": "abc123devicetoken"
                    }
                },
                "timestamp": "2024-01-15T12:30:00+00:00"
            }
        )
        assert result == {"status": "success"}
    
    def test_delete_device_invalid_user_id(self, mock_client):
        """Test device deletion with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            delete_device(
                client=mock_client,
                user_id="",
                device_token="abc123devicetoken"
            )
    
    def test_delete_device_invalid_device_token(self, mock_client):
        """Test device deletion with invalid device token."""
        with pytest.raises(ValidationError, match="Device token must be a non-empty string"):
            delete_device(
                client=mock_client,
                user_id="user123",
                device_token=""
            )
    
    def test_delete_device_api_error(self, mock_client):
        """Test device deletion when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            delete_device(
                client=mock_client,
                user_id="user123",
                device_token="abc123devicetoken"
            )


class TestDeviceManagerIntegration:
    """Test integration scenarios for device management."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_device_lifecycle_workflow(self, mock_client):
        """Test complete device lifecycle workflow."""
        user_id = "user123"
        device_token = "abc123devicetoken"
        
        # Register device
        register_result = register_device(
            client=mock_client,
            user_id=user_id,
            device_token=device_token,
            device_type="ios"
        )
        assert register_result == {"status": "success"}
        
        # Update device
        update_result = update_device(
            client=mock_client,
            user_id=user_id,
            device_token=device_token,
            metadata={"version": "16.0.1"}
        )
        assert update_result == {"status": "success"}
        
        # Delete device
        delete_result = delete_device(
            client=mock_client,
            user_id=user_id,
            device_token=device_token
        )
        assert delete_result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
    
    def test_batch_device_operations(self, mock_client):
        """Test batch operations on multiple devices."""
        devices = [
            {"user_id": "user1", "token": "token1", "type": "ios"},
            {"user_id": "user2", "token": "token2", "type": "android"},
            {"user_id": "user3", "token": "token3", "type": "ios"}
        ]
        
        # Register all devices
        for device in devices:
            result = register_device(
                client=mock_client,
                user_id=device["user_id"],
                device_token=device["token"],
                device_type=device["type"]
            )
            assert result == {"status": "success"}
        
        # Verify all calls were made
        assert mock_client.make_request.call_count == 3
        
        # Verify call details
        calls = mock_client.make_request.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            assert args[0] == "POST"
            assert args[1] == "/track"
            assert args[2]["userId"] == devices[i]["user_id"]
            assert args[2]["context"]["device"]["token"] == devices[i]["token"]
            assert args[2]["context"]["device"]["type"] == devices[i]["type"]