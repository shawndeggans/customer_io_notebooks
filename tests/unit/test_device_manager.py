"""
Comprehensive tests for Customer.IO Device Manager.

Tests cover:
- Device type and status enumerations
- Data model validation (DeviceInfo, DeviceAttributes, DeviceRegistration)
- Device registration and lifecycle management
- Multi-platform device support (iOS/APNS, Android/FCM, Web Push, Desktop)
- Device status updates and token refresh
- Cross-platform user tracking
- Batch device operations
- Device analytics and health monitoring
- Metrics and reporting
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from pydantic import ValidationError

from utils.device_manager import (
    DeviceType,
    PushProvider,
    DeviceStatus,
    DeviceInfo,
    DeviceAttributes,
    DeviceRegistration,
    DeviceManager
)
from utils.error_handlers import CustomerIOError


class TestDeviceType:
    """Test DeviceType enum."""
    
    def test_device_type_values(self):
        """Test all device type values."""
        assert DeviceType.IOS == "ios"
        assert DeviceType.ANDROID == "android"
        assert DeviceType.WEB == "web"
        assert DeviceType.DESKTOP == "desktop"
        assert DeviceType.IOT == "iot"
    
    def test_device_type_membership(self):
        """Test device type membership."""
        valid_types = [device_type.value for device_type in DeviceType]
        assert "ios" in valid_types
        assert "invalid_type" not in valid_types


class TestPushProvider:
    """Test PushProvider enum."""
    
    def test_push_provider_values(self):
        """Test all push provider values."""
        assert PushProvider.APNS == "apns"
        assert PushProvider.FCM == "fcm"
        assert PushProvider.WEB_PUSH == "web_push"
        assert PushProvider.DESKTOP == "desktop"
        assert PushProvider.CUSTOM == "custom"
    
    def test_push_provider_membership(self):
        """Test push provider membership."""
        valid_providers = [provider.value for provider in PushProvider]
        assert "apns" in valid_providers
        assert "invalid_provider" not in valid_providers


class TestDeviceStatus:
    """Test DeviceStatus enum."""
    
    def test_device_status_values(self):
        """Test all device status values."""
        assert DeviceStatus.ACTIVE == "active"
        assert DeviceStatus.INACTIVE == "inactive"
        assert DeviceStatus.UNINSTALLED == "uninstalled"
        assert DeviceStatus.OPT_OUT == "opt_out"
        assert DeviceStatus.INVALID_TOKEN == "invalid_token"
    
    def test_device_status_membership(self):
        """Test device status membership."""
        valid_statuses = [status.value for status in DeviceStatus]
        assert "active" in valid_statuses
        assert "invalid_status" not in valid_statuses


class TestDeviceInfo:
    """Test DeviceInfo data model."""
    
    def test_valid_device_info(self):
        """Test valid device info creation."""
        device_info = DeviceInfo(
            token="a1b2c3d4e5f6789012345678901234567890123456789012345678901234abcd",
            type=DeviceType.IOS,
            device_id="iPhone14,2",
            device_model="iPhone 15 Pro",
            os_version="17.2",
            app_version="2.1.0",
            push_provider=PushProvider.APNS
        )
        
        assert device_info.token == "a1b2c3d4e5f6789012345678901234567890123456789012345678901234abcd"
        assert device_info.type == "ios"  # Should be converted to string
        assert device_info.device_id == "iPhone14,2"
        assert device_info.device_model == "iPhone 15 Pro"
        assert device_info.os_version == "17.2"
        assert device_info.app_version == "2.1.0"
        assert device_info.push_provider == "apns"
    
    def test_required_token_field(self):
        """Test that token field is required."""
        with pytest.raises(ValidationError, match="field required"):
            DeviceInfo(type=DeviceType.IOS)
    
    def test_required_type_field(self):
        """Test that type field is required."""
        with pytest.raises(ValidationError, match="field required"):
            DeviceInfo(token="valid_token_123456789")
    
    def test_empty_token_validation(self):
        """Test validation of empty token."""
        with pytest.raises(ValidationError, match="Push token cannot be empty"):
            DeviceInfo(
                token="",
                type=DeviceType.IOS
            )
    
    def test_short_token_validation(self):
        """Test validation of short token."""
        with pytest.raises(ValidationError, match="Push token appears to be too short"):
            DeviceInfo(
                token="short",
                type=DeviceType.IOS
            )
    
    def test_token_whitespace_normalization(self):
        """Test token whitespace normalization."""
        device_info = DeviceInfo(
            token="  valid_token_123456789  ",
            type=DeviceType.IOS
        )
        
        assert device_info.token == "valid_token_123456789"
    
    def test_optional_fields(self):
        """Test that optional fields can be None."""
        device_info = DeviceInfo(
            token="valid_token_123456789",
            type=DeviceType.IOS
        )
        
        assert device_info.device_id is None
        assert device_info.device_model is None
        assert device_info.os_version is None
        assert device_info.app_version is None
        assert device_info.push_provider is None


class TestDeviceAttributes:
    """Test DeviceAttributes data model."""
    
    def test_valid_device_attributes(self):
        """Test valid device attributes creation."""
        attributes = DeviceAttributes(
            push_enabled=True,
            timezone="America/New_York",
            locale="en-US",
            battery_level=0.85,
            network_type="wifi",
            carrier="Verizon",
            screen_width=1179,
            screen_height=2556,
            last_seen=datetime.now(timezone.utc)
        )
        
        assert attributes.push_enabled is True
        assert attributes.timezone == "America/New_York"
        assert attributes.locale == "en-US"
        assert attributes.battery_level == 0.85
        assert attributes.network_type == "wifi"
        assert attributes.carrier == "Verizon"
        assert attributes.screen_width == 1179
        assert attributes.screen_height == 2556
        assert isinstance(attributes.last_seen, datetime)
    
    def test_default_push_enabled(self):
        """Test that push_enabled defaults to True."""
        attributes = DeviceAttributes()
        assert attributes.push_enabled is True
    
    def test_battery_level_validation_high(self):
        """Test validation of battery level too high."""
        with pytest.raises(ValidationError, match="ensure this value is less than or equal to 1"):
            DeviceAttributes(battery_level=1.5)
    
    def test_battery_level_validation_low(self):
        """Test validation of battery level too low."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            DeviceAttributes(battery_level=-0.1)
    
    def test_screen_dimension_validation(self):
        """Test validation of negative screen dimensions."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            DeviceAttributes(screen_width=-100)
        
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            DeviceAttributes(screen_height=-100)
    
    def test_timezone_validation_invalid(self):
        """Test validation of invalid timezone format."""
        with pytest.raises(ValidationError, match="Timezone should be in region/city format"):
            DeviceAttributes(timezone="EST")
    
    def test_timezone_validation_valid(self):
        """Test validation of valid timezone format."""
        attributes = DeviceAttributes(timezone="America/New_York")
        assert attributes.timezone == "America/New_York"
    
    def test_locale_validation_invalid(self):
        """Test validation of invalid locale format."""
        with pytest.raises(ValidationError, match="Locale should be in format 'en' or 'en-US'"):
            DeviceAttributes(locale="invalid_locale")
    
    def test_locale_validation_valid_short(self):
        """Test validation of valid short locale format."""
        attributes = DeviceAttributes(locale="en")
        assert attributes.locale == "en"
    
    def test_locale_validation_valid_long(self):
        """Test validation of valid long locale format."""
        attributes = DeviceAttributes(locale="en-US")
        assert attributes.locale == "en-US"
    
    def test_optional_fields_default_none(self):
        """Test that optional fields default to None."""
        attributes = DeviceAttributes()
        
        assert attributes.timezone is None
        assert attributes.locale is None
        assert attributes.battery_level is None
        assert attributes.network_type is None
        assert attributes.carrier is None
        assert attributes.screen_width is None
        assert attributes.screen_height is None
        assert attributes.last_seen is None


class TestDeviceRegistration:
    """Test DeviceRegistration data model."""
    
    def test_valid_device_registration(self):
        """Test valid device registration creation."""
        device_info = DeviceInfo(
            token="valid_token_123456789",
            type=DeviceType.IOS,
            device_model="iPhone 15 Pro"
        )
        
        attributes = DeviceAttributes(
            push_enabled=True,
            timezone="America/New_York"
        )
        
        registration = DeviceRegistration(
            user_id="user_123",
            device_info=device_info,
            attributes=attributes,
            status=DeviceStatus.ACTIVE
        )
        
        assert registration.user_id == "user_123"
        assert registration.device_info == device_info
        assert registration.attributes == attributes
        assert registration.status == "active"
        assert isinstance(registration.registered_at, datetime)
    
    def test_required_user_id_field(self):
        """Test that user_id field is required."""
        device_info = DeviceInfo(token="valid_token_123456789", type=DeviceType.IOS)
        
        with pytest.raises(ValidationError, match="field required"):
            DeviceRegistration(device_info=device_info)
    
    def test_required_device_info_field(self):
        """Test that device_info field is required."""
        with pytest.raises(ValidationError, match="field required"):
            DeviceRegistration(user_id="user_123")
    
    def test_empty_user_id_validation(self):
        """Test validation of empty user ID."""
        device_info = DeviceInfo(token="valid_token_123456789", type=DeviceType.IOS)
        
        with pytest.raises(ValidationError, match="User ID cannot be empty"):
            DeviceRegistration(
                user_id="",
                device_info=device_info
            )
    
    def test_user_id_whitespace_normalization(self):
        """Test user ID whitespace normalization."""
        device_info = DeviceInfo(token="valid_token_123456789", type=DeviceType.IOS)
        
        registration = DeviceRegistration(
            user_id="  user_123  ",
            device_info=device_info
        )
        
        assert registration.user_id == "user_123"
    
    def test_default_attributes(self):
        """Test that attributes defaults to empty DeviceAttributes."""
        device_info = DeviceInfo(token="valid_token_123456789", type=DeviceType.IOS)
        
        registration = DeviceRegistration(
            user_id="user_123",
            device_info=device_info
        )
        
        assert isinstance(registration.attributes, DeviceAttributes)
        assert registration.attributes.push_enabled is True
    
    def test_default_status(self):
        """Test that status defaults to ACTIVE."""
        device_info = DeviceInfo(token="valid_token_123456789", type=DeviceType.IOS)
        
        registration = DeviceRegistration(
            user_id="user_123",
            device_info=device_info
        )
        
        assert registration.status == "active"
    
    def test_default_registered_at(self):
        """Test that registered_at is automatically set."""
        device_info = DeviceInfo(token="valid_token_123456789", type=DeviceType.IOS)
        
        registration = DeviceRegistration(
            user_id="user_123",
            device_info=device_info
        )
        
        assert isinstance(registration.registered_at, datetime)
        assert registration.registered_at.tzinfo is not None


class TestDeviceManager:
    """Test DeviceManager class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock CustomerIOClient."""
        return Mock()
    
    @pytest.fixture
    def device_manager(self, mock_client):
        """Create DeviceManager with mock client."""
        return DeviceManager(mock_client)
    
    @pytest.fixture
    def sample_device_info(self):
        """Create sample device info."""
        return DeviceInfo(
            token="a1b2c3d4e5f6789012345678901234567890123456789012345678901234abcd",
            type=DeviceType.IOS,
            device_id="iPhone14,2",
            device_model="iPhone 15 Pro",
            os_version="17.2",
            app_version="2.1.0",
            push_provider=PushProvider.APNS
        )
    
    @pytest.fixture
    def sample_attributes(self):
        """Create sample device attributes."""
        return DeviceAttributes(
            push_enabled=True,
            timezone="America/New_York",
            locale="en-US",
            battery_level=0.85,
            network_type="wifi"
        )
    
    @pytest.fixture
    def sample_registration(self, sample_device_info, sample_attributes):
        """Create sample device registration."""
        return DeviceRegistration(
            user_id="user_123",
            device_info=sample_device_info,
            attributes=sample_attributes,
            status=DeviceStatus.ACTIVE
        )
    
    def test_device_manager_initialization(self, mock_client):
        """Test DeviceManager initialization."""
        manager = DeviceManager(mock_client)
        
        assert manager.client == mock_client
        assert manager.logger is not None
    
    @patch('utils.device_manager.validate_request_size', return_value=True)
    def test_register_device_success(self, mock_validate, device_manager, sample_registration):
        """Test successful device registration."""
        device_manager.client.add_device.return_value = {"status": "success"}
        
        result = device_manager.register_device(sample_registration)
        
        assert result == {"status": "success"}
        device_manager.client.add_device.assert_called_once()
        
        # Check call arguments
        call_args = device_manager.client.add_device.call_args
        assert call_args[1]["user_id"] == "user_123"
        assert "device" in call_args[1]
    
    @patch('utils.device_manager.validate_request_size', return_value=False)
    def test_register_device_size_validation_failure(self, mock_validate, device_manager, sample_registration):
        """Test device registration with size validation failure."""
        with pytest.raises(ValueError, match="Device data exceeds 32KB limit"):
            device_manager.register_device(sample_registration)
    
    def test_register_device_api_error(self, device_manager, sample_registration):
        """Test device registration with API error."""
        device_manager.client.add_device.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            device_manager.register_device(sample_registration)
    
    def test_register_device_with_context(self, device_manager, sample_registration):
        """Test device registration with context."""
        device_manager.client.add_device.return_value = {"status": "success"}
        context = {"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        
        result = device_manager.register_device(sample_registration, context=context)
        
        assert result == {"status": "success"}
        # Context should be included in the device data
        call_args = device_manager.client.add_device.call_args[1]
        assert "context" in call_args
    
    def test_update_device_status_success(self, device_manager):
        """Test successful device status update."""
        device_manager.client.track.return_value = {"status": "success"}
        
        result = device_manager.update_device_status(
            user_id="user_123",
            device_token="valid_token_123456789",
            new_status=DeviceStatus.INACTIVE,
            reason="User disabled notifications"
        )
        
        assert result == {"status": "success"}
        device_manager.client.track.assert_called_once()
        
        # Check event structure
        call_args = device_manager.client.track.call_args[1]
        assert call_args["userId"] == "user_123"
        assert call_args["event"] == "Device Status Updated"
        assert call_args["properties"]["new_status"] == "inactive"
        assert call_args["properties"]["reason"] == "User disabled notifications"
    
    def test_refresh_device_token(self, device_manager):
        """Test device token refresh."""
        old_token = "old_token_123456789"
        new_token = "new_token_987654321"
        
        result = device_manager.refresh_device_token(
            user_id="user_123",
            old_token=old_token,
            new_token=new_token,
            device_type=DeviceType.IOS
        )
        
        assert result["userId"] == "user_123"
        assert result["event"] == "Device Token Refreshed"
        assert result["properties"]["device_type"] == "ios"
        assert old_token[:20] in result["properties"]["old_token"]
        assert new_token[:20] in result["properties"]["new_token"]
    
    def test_remove_device(self, device_manager):
        """Test device removal."""
        result = device_manager.remove_device(
            user_id="user_123",
            device_token="token_to_remove_123456789",
            device_type=DeviceType.ANDROID,
            reason="app_uninstalled"
        )
        
        assert result["userId"] == "user_123"
        assert result["event"] == "Device Removed"
        assert result["properties"]["device_type"] == "android"
        assert result["properties"]["reason"] == "app_uninstalled"
    
    def test_batch_register_devices_success(self, device_manager, sample_registration):
        """Test successful batch device registration."""
        registrations = [sample_registration] * 3
        device_manager.client.batch.return_value = {"status": "success"}
        
        results = device_manager.batch_register_devices(registrations)
        
        assert len(results) >= 1
        assert results[0]["status"] == "success"
        assert results[0]["count"] == 3
        device_manager.client.batch.assert_called()
    
    def test_batch_register_devices_partial_failure(self, device_manager, sample_registration):
        """Test batch device registration with partial failures."""
        registrations = [sample_registration] * 2
        
        # Force multiple batches and simulate failure
        with patch('utils.device_manager.BatchTransformer.optimize_batch_sizes') as mock_optimize:
            mock_optimize.return_value = [
                [{"type": "track", "userId": "user_123", "event": "Device Registered"}],
                [{"type": "track", "userId": "user_123", "event": "Device Registered"}]
            ]
            
            device_manager.client.batch.side_effect = [
                {"status": "success"},
                CustomerIOError("API error")
            ]
            
            results = device_manager.batch_register_devices(registrations)
        
        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert results[1]["status"] == "failed"
        assert "error" in results[1]
    
    def test_create_cross_platform_user(self, device_manager):
        """Test cross-platform user creation."""
        # Create devices for different platforms
        ios_info = DeviceInfo(token="ios_token_123456789", type=DeviceType.IOS)
        android_info = DeviceInfo(token="android_token_123456789", type=DeviceType.ANDROID)
        web_info = DeviceInfo(token="web_token_123456789", type=DeviceType.WEB)
        
        devices = [
            DeviceRegistration(user_id="user_123", device_info=ios_info),
            DeviceRegistration(user_id="user_123", device_info=android_info),
            DeviceRegistration(user_id="user_123", device_info=web_info)
        ]
        
        result = device_manager.create_cross_platform_user(
            user_id="user_123",
            devices=devices
        )
        
        assert result["userId"] == "user_123"
        assert result["event"] == "Multi-Device User Profile"
        assert result["properties"]["total_devices"] == 3
        assert result["properties"]["cross_platform"] is True
        assert len(result["properties"]["platforms"]) == 3
        assert "ios" in result["properties"]["platforms"]
        assert "android" in result["properties"]["platforms"]
        assert "web" in result["properties"]["platforms"]
    
    def test_analyze_device_preferences(self, device_manager):
        """Test device preference analysis."""
        # Create diverse device set
        devices = [
            DeviceRegistration(
                user_id="user_1",
                device_info=DeviceInfo(token="token1", type=DeviceType.IOS),
                attributes=DeviceAttributes(timezone="America/New_York", locale="en-US")
            ),
            DeviceRegistration(
                user_id="user_2",
                device_info=DeviceInfo(token="token2", type=DeviceType.IOS),
                attributes=DeviceAttributes(timezone="America/Los_Angeles", locale="en-US")
            ),
            DeviceRegistration(
                user_id="user_3",
                device_info=DeviceInfo(token="token3", type=DeviceType.ANDROID),
                attributes=DeviceAttributes(timezone="America/New_York", locale="es-US")
            )
        ]
        
        analysis = device_manager.analyze_device_preferences(devices)
        
        assert analysis["total_devices"] == 3
        assert "ios" in analysis["device_types"]
        assert "android" in analysis["device_types"]
        assert analysis["type_distribution"]["ios"] == 2
        assert analysis["type_distribution"]["android"] == 1
        assert analysis["push_enabled_count"] == 3  # All default to enabled
        assert analysis["active_devices"] == 3  # All default to active
        assert analysis["unique_timezones"] == 2
        assert analysis["unique_locales"] == 2
        assert "most_recent_device" in analysis
    
    def test_calculate_device_metrics(self, device_manager):
        """Test device metrics calculation."""
        devices = [
            DeviceRegistration(
                user_id="user_1",
                device_info=DeviceInfo(token="token1", type=DeviceType.IOS, push_provider=PushProvider.APNS),
                attributes=DeviceAttributes(push_enabled=True, timezone="America/New_York"),
                status=DeviceStatus.ACTIVE
            ),
            DeviceRegistration(
                user_id="user_2",
                device_info=DeviceInfo(token="token2", type=DeviceType.ANDROID, push_provider=PushProvider.FCM),
                attributes=DeviceAttributes(push_enabled=False, timezone="America/Los_Angeles"),
                status=DeviceStatus.INACTIVE
            )
        ]
        
        metrics = device_manager.calculate_device_metrics(devices)
        
        assert metrics["total_devices"] == 2
        assert metrics["active_devices"] == 1
        assert metrics["inactive_devices"] == 1
        assert metrics["push_enabled_devices"] == 1
        assert metrics["push_opt_out_devices"] == 1
        assert metrics["platform_distribution"]["ios"] == 1
        assert metrics["platform_distribution"]["android"] == 1
        assert metrics["push_provider_distribution"]["apns"] == 1
        assert metrics["push_provider_distribution"]["fcm"] == 1
        assert metrics["unique_timezones"] == 2
        assert metrics["unique_locales"] == 0  # No locales set
        assert metrics["push_adoption_rate"] == 0.5
        assert metrics["active_device_rate"] == 0.5
    
    def test_calculate_device_metrics_empty(self, device_manager):
        """Test device metrics calculation with empty list."""
        metrics = device_manager.calculate_device_metrics([])
        
        assert metrics == {"total_devices": 0}
    
    def test_monitor_device_health(self, device_manager):
        """Test device health monitoring."""
        old_date = datetime.now(timezone.utc) - timedelta(days=100)
        
        devices = [
            DeviceRegistration(
                user_id="user_healthy",
                device_info=DeviceInfo(token="healthy_token_123456789", type=DeviceType.IOS),
                attributes=DeviceAttributes(push_enabled=True, timezone="America/New_York", locale="en-US"),
                status=DeviceStatus.ACTIVE
            ),
            DeviceRegistration(
                user_id="user_issues",
                device_info=DeviceInfo(token="short", type=DeviceType.ANDROID),  # Short token
                attributes=DeviceAttributes(push_enabled=False),  # Push disabled, missing timezone/locale
                status=DeviceStatus.INACTIVE,  # Inactive status
                registered_at=old_date  # Old registration
            )
        ]
        
        health_report = device_manager.monitor_device_health(devices)
        
        assert health_report["total_devices"] == 2
        assert health_report["healthy_devices"] == 1
        assert len(health_report["issues_found"]) == 1
        
        # Check issues for problematic device
        issues = health_report["issues_found"][0]
        assert issues["user_id"] == "user_issues"
        assert "Device status: inactive" in issues["issues"]
        assert "Push notifications disabled" in issues["issues"]
        assert "Suspicious token length" in issues["issues"]
        assert "Missing timezone information" in issues["issues"]
        assert "Missing locale information" in issues["issues"]
        assert any("Device registration is" in issue and "days old" in issue for issue in issues["issues"])
        
        assert len(health_report["recommendations"]) > 0
        assert health_report["health_score"] == 0.5
    
    def test_monitor_device_health_all_healthy(self, device_manager):
        """Test device health monitoring with all healthy devices."""
        devices = [
            DeviceRegistration(
                user_id="user_1",
                device_info=DeviceInfo(token="healthy_token_123456789", type=DeviceType.IOS),
                attributes=DeviceAttributes(push_enabled=True, timezone="America/New_York", locale="en-US"),
                status=DeviceStatus.ACTIVE
            )
        ]
        
        health_report = device_manager.monitor_device_health(devices)
        
        assert health_report["total_devices"] == 1
        assert health_report["healthy_devices"] == 1
        assert len(health_report["issues_found"]) == 0
        assert len(health_report["recommendations"]) == 0
        assert health_report["health_score"] == 1.0
    
    def test_get_metrics(self, device_manager):
        """Test getting device manager metrics."""
        metrics = device_manager.get_metrics()
        
        assert "client" in metrics
        assert "supported_platforms" in metrics
        assert "validation" in metrics
        
        # Check client metrics
        assert "base_url" in metrics["client"]
        assert "rate_limit" in metrics["client"]
        
        # Check supported platforms
        assert "device_types" in metrics["supported_platforms"]
        assert "push_providers" in metrics["supported_platforms"]
        assert "device_statuses" in metrics["supported_platforms"]
        assert "ios" in metrics["supported_platforms"]["device_types"]
        assert "apns" in metrics["supported_platforms"]["push_providers"]
        assert "active" in metrics["supported_platforms"]["device_statuses"]
        
        # Check validation rules
        assert "min_token_length" in metrics["validation"]
        assert "max_request_size_bytes" in metrics["validation"]
        assert metrics["validation"]["min_token_length"] == 10
        assert metrics["validation"]["max_request_size_bytes"] == 32 * 1024