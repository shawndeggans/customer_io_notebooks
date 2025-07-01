"""
Integration tests for Customer.IO Device Management API.

Tests real API interactions for:
- Device registration and updates
- Device deletion
- Device metadata management
- Error handling
"""

import pytest
from datetime import datetime, timezone

from tests.integration.base import BaseIntegrationTest
from tests.integration.utils import generate_test_email
from utils.device_manager import (
    register_device,
    update_device,
    delete_device
)
from utils.people_manager import identify_user
from utils.exceptions import CustomerIOError, ValidationError


@pytest.mark.integration
class TestDeviceIntegration(BaseIntegrationTest):
    """Integration tests for device management functionality."""
    
    def test_register_device_basic(self, authenticated_client, test_user_id, test_device_id):
        """Test registering a basic device."""
        # Arrange - Create user first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("devicebasic"),
            "name": "Device Test User"
        })
        self.track_user(test_user_id)
        
        # Act
        result = register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios"
        )
        self.track_device(test_device_id)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_register_device_with_metadata(self, authenticated_client, test_user_id, test_device_id):
        """Test registering device with metadata."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("devicemeta"),
            "name": "Device Metadata Test"
        })
        self.track_user(test_user_id)
        
        metadata = {
            "app_version": "2.1.0",
            "os_version": "16.0.1",
            "model": "iPhone14,2",
            "timezone": "America/New_York",
            "language": "en-US"
        }
        
        # Act
        result = register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios",
            metadata
        )
        self.track_device(test_device_id)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_register_android_device(self, authenticated_client, test_user_id, test_device_id):
        """Test registering an Android device."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("android"),
            "name": "Android Test User"
        })
        self.track_user(test_user_id)
        
        metadata = {
            "app_version": "1.5.2",
            "os_version": "13",
            "model": "SM-G991B",
            "brand": "Samsung"
        }
        
        # Act
        result = register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "android",
            metadata
        )
        self.track_device(test_device_id)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_update_device(self, authenticated_client, test_user_id, test_device_id):
        """Test updating an existing device."""
        # Arrange - Create user and register device first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("deviceupdate"),
            "name": "Device Update Test"
        })
        self.track_user(test_user_id)
        
        # Register device first
        register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios",
            {"app_version": "1.0.0"}
        )
        self.track_device(test_device_id)
        
        # Act - Update with new metadata
        result = update_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios",
            {
                "app_version": "2.0.0",
                "os_version": "16.1.0",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_delete_device(self, authenticated_client, test_user_id, test_device_id):
        """Test deleting a device."""
        # Arrange - Create user and register device first
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("devicedelete"),
            "name": "Device Delete Test"
        })
        self.track_user(test_user_id)
        
        register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios"
        )
        self.track_device(test_device_id)
        
        # Act
        result = delete_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios"
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_device_with_custom_timestamp(self, authenticated_client, test_user_id, test_device_id):
        """Test device operations with custom timestamps."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("devicetime"),
            "name": "Device Timestamp Test"
        })
        self.track_user(test_user_id)
        
        custom_timestamp = datetime.now(timezone.utc)
        
        # Act
        result = register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios",
            {"historical": True},
            timestamp=custom_timestamp
        )
        self.track_device(test_device_id)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_device_without_type(self, authenticated_client, test_user_id, test_device_id):
        """Test registering device without specifying type."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("devicenotype"),
            "name": "No Type Test"
        })
        self.track_user(test_user_id)
        
        # Act
        result = register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            metadata={"custom_type": "web_browser"}
        )
        self.track_device(test_device_id)
        
        # Assert
        self.assert_successful_response(result)
    
    def test_multiple_devices_per_user(self, authenticated_client, test_user_id):
        """Test registering multiple devices for one user."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("multidev"),
            "name": "Multi Device User"
        })
        self.track_user(test_user_id)
        
        device_ids = []
        for i in range(3):
            device_id = f"multi_device_{i}_{int(datetime.now().timestamp())}"
            device_ids.append(device_id)
            self.track_device(device_id)
        
        # Act - Register multiple devices
        for i, device_id in enumerate(device_ids):
            device_type = "ios" if i % 2 == 0 else "android"
            result = register_device(
                authenticated_client,
                test_user_id,
                device_id,
                device_type,
                {"device_index": i}
            )
            self.assert_successful_response(result)
            # Small delay for rate limiting
            self.wait_for_eventual_consistency(0.1)
    
    def test_device_lifecycle(self, authenticated_client, test_user_id, test_device_id):
        """Test complete device lifecycle: register, update, delete."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("devicelife"),
            "name": "Device Lifecycle Test"
        })
        self.track_user(test_user_id)
        
        # Register
        register_result = register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios",
            {"status": "active", "version": 1}
        )
        self.track_device(test_device_id)
        self.assert_successful_response(register_result)
        
        # Update
        update_result = update_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios",
            {"status": "updated", "version": 2}
        )
        self.assert_successful_response(update_result)
        
        # Delete
        delete_result = delete_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios"
        )
        self.assert_successful_response(delete_result)
    
    def test_device_validation_errors(self, authenticated_client):
        """Test device validation errors."""
        # Test empty device token
        with pytest.raises(ValidationError):
            register_device(authenticated_client, "user123", "", "ios")
        
        # Test invalid device type
        with pytest.raises(ValidationError):
            register_device(authenticated_client, "user123", "token123", "windows")
        
        # Test empty user ID
        with pytest.raises(ValidationError):
            register_device(authenticated_client, "", "token123", "ios")
    
    def test_device_complex_metadata(self, authenticated_client, test_user_id, test_device_id):
        """Test device with complex nested metadata."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("complex"),
            "name": "Complex Device Test"
        })
        self.track_user(test_user_id)
        
        complex_metadata = {
            "hardware": {
                "model": "iPhone14,2",
                "storage": "256GB",
                "memory": "6GB",
                "cpu": "A15 Bionic"
            },
            "software": {
                "os": "iOS",
                "version": "16.0.1",
                "build": "20A371"
            },
            "app": {
                "version": "2.1.0",
                "build": "210001",
                "environment": "production"
            },
            "capabilities": ["push", "location", "camera", "microphone"],
            "settings": {
                "notifications_enabled": True,
                "location_permission": "always",
                "tracking_consent": True
            }
        }
        
        # Act
        result = register_device(
            authenticated_client,
            test_user_id,
            test_device_id,
            "ios",
            complex_metadata
        )
        self.track_device(test_device_id)
        
        # Assert
        self.assert_successful_response(result)
    
    @pytest.mark.slow
    def test_bulk_device_registration(self, authenticated_client):
        """Test registering multiple devices for performance testing."""
        # Arrange
        user_devices = []
        
        for i in range(10):
            user_id = f"bulk_dev_user_{i}_{int(datetime.now().timestamp())}"
            device_id = f"bulk_device_{i}_{int(datetime.now().timestamp())}"
            user_devices.append((user_id, device_id))
            
            if i < 3:  # Only track first 3 for cleanup
                self.track_user(user_id)
                self.track_device(device_id)
        
        # Create users and register devices
        for i, (user_id, device_id) in enumerate(user_devices):
            # Create user
            identify_user(authenticated_client, user_id, {
                "email": generate_test_email(f"bulk{i}"),
                "name": f"Bulk Device User {i}"
            })
            
            # Register device
            result = register_device(
                authenticated_client,
                user_id,
                device_id,
                "ios",
                {"bulk_test": True, "index": i}
            )
            self.assert_successful_response(result)
            
            # Rate limiting
            if i % 3 == 0:
                self.wait_for_eventual_consistency(0.1)