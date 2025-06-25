"""
Customer.IO Device Management Module

Type-safe device management operations for Customer.IO API including:
- Multi-platform device registration (iOS/APNS, Android/FCM, Web Push, Desktop)
- Device lifecycle management (registration, status updates, token refresh, removal)
- Cross-platform user tracking and analytics
- Device health monitoring and diagnostics
- Batch device operations with optimization
- Device attribute management and validation
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set, Union
from enum import Enum
import structlog
from pydantic import BaseModel, Field, validator
import json
import re

from .api_client import CustomerIOClient
from .validators import DeviceRequest, validate_request_size
from .transformers import BatchTransformer
from .error_handlers import retry_on_error, ErrorContext


class DeviceType(str, Enum):
    """Enumeration for device types."""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    DESKTOP = "desktop"
    IOT = "iot"


class PushProvider(str, Enum):
    """Enumeration for push notification providers."""
    APNS = "apns"  # Apple Push Notification Service
    FCM = "fcm"    # Firebase Cloud Messaging
    WEB_PUSH = "web_push"  # Web Push API
    DESKTOP = "desktop"    # Desktop notifications
    CUSTOM = "custom"      # Custom push provider


class DeviceStatus(str, Enum):
    """Enumeration for device status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNINSTALLED = "uninstalled"
    OPT_OUT = "opt_out"
    INVALID_TOKEN = "invalid_token"


class DeviceInfo(BaseModel):
    """Type-safe device information model."""
    token: str = Field(..., description="Push notification token")
    type: DeviceType = Field(..., description="Device type")
    device_id: Optional[str] = Field(None, description="Unique device identifier")
    device_model: Optional[str] = Field(None, description="Device model name")
    os_version: Optional[str] = Field(None, description="Operating system version")
    app_version: Optional[str] = Field(None, description="Application version")
    push_provider: Optional[PushProvider] = Field(None, description="Push provider")
    
    @validator('token')
    def validate_token(cls, v: str) -> str:
        """Validate push token format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Push token cannot be empty")
        if len(v) < 10:  # Minimum reasonable token length
            raise ValueError("Push token appears to be too short")
        return v.strip()
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class DeviceAttributes(BaseModel):
    """Type-safe device attributes model."""
    push_enabled: bool = Field(default=True, description="Push notifications enabled")
    timezone: Optional[str] = Field(None, description="Device timezone")
    locale: Optional[str] = Field(None, description="Device locale")
    battery_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Battery level (0.0-1.0)")
    network_type: Optional[str] = Field(None, description="Network connection type")
    carrier: Optional[str] = Field(None, description="Mobile carrier")
    screen_width: Optional[int] = Field(None, ge=0, description="Screen width in pixels")
    screen_height: Optional[int] = Field(None, ge=0, description="Screen height in pixels")
    last_seen: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    @validator('timezone')
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        """Validate timezone format."""
        if v and '/' not in v:
            # Simple validation - proper timezone should have region/city format
            raise ValueError("Timezone should be in region/city format (e.g., America/New_York)")
        return v
    
    @validator('locale')
    def validate_locale(cls, v: Optional[str]) -> Optional[str]:
        """Validate locale format."""
        if v and not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', v):
            raise ValueError("Locale should be in format 'en' or 'en-US'")
        return v


class DeviceRegistration(BaseModel):
    """Type-safe device registration model."""
    user_id: str = Field(..., description="User identifier")
    device_info: DeviceInfo = Field(..., description="Device information")
    attributes: DeviceAttributes = Field(default_factory=DeviceAttributes, description="Device attributes")
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE, description="Device status")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('user_id')
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("User ID cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class DeviceManager:
    """Type-safe device management operations."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("device_manager")
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def register_device(
        self,
        device_registration: DeviceRegistration,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a device with Customer.IO with comprehensive validation.
        
        Args:
            device_registration: DeviceRegistration object with device data
            context: Optional context data
            
        Returns:
            API response dictionary
            
        Raises:
            ValidationError: If device validation fails
            CustomerIOError: If API call fails
        """
        
        try:
            # Create device request
            device_data = {
                "device": {
                    "token": device_registration.device_info.token,
                    "type": device_registration.device_info.type,
                    **device_registration.device_info.dict(exclude={'token', 'type'}, exclude_none=True)
                }
            }
            
            # Add device attributes
            if device_registration.attributes:
                device_data["device"].update(
                    device_registration.attributes.dict(exclude_none=True)
                )
            
            if context:
                device_data["context"] = context
            
            # Validate request size
            if not validate_request_size(device_data):
                raise ValueError("Device data exceeds 32KB limit")
            
            # Validate with DeviceRequest model
            device_request = DeviceRequest(**device_data)
            
            # Send to Customer.IO
            response = self.client.add_device(
                user_id=device_registration.user_id,
                **device_request.dict()
            )
            
            self.logger.info(
                "Device registered successfully",
                user_id=device_registration.user_id,
                device_type=device_registration.device_info.type,
                device_model=device_registration.device_info.device_model
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to register device",
                user_id=device_registration.user_id,
                device_type=device_registration.device_info.type,
                error=str(e)
            )
            raise
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def update_device_status(
        self,
        user_id: str,
        device_token: str,
        new_status: DeviceStatus,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update device status with tracking event.
        
        Args:
            user_id: User identifier
            device_token: Device push token
            new_status: New device status
            reason: Reason for status change
            
        Returns:
            API response dictionary
        """
        
        try:
            event_data = {
                "userId": user_id,
                "event": "Device Status Updated",
                "properties": {
                    "device_token": device_token[:20] + "...",  # Truncate for privacy
                    "new_status": new_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "timestamp": datetime.now(timezone.utc)
            }
            
            if reason:
                event_data["properties"]["reason"] = reason
            
            # Send tracking event
            response = self.client.track(**event_data)
            
            self.logger.info(
                "Device status updated",
                user_id=user_id,
                new_status=new_status,
                reason=reason
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to update device status",
                user_id=user_id,
                new_status=new_status,
                error=str(e)
            )
            raise
    
    def refresh_device_token(
        self,
        user_id: str,
        old_token: str,
        new_token: str,
        device_type: DeviceType
    ) -> Dict[str, Any]:
        """
        Handle device token refresh with proper tracking.
        
        Args:
            user_id: User identifier
            old_token: Previous device token
            new_token: New device token
            device_type: Type of device
            
        Returns:
            Event data dictionary
        """
        
        event_data = {
            "userId": user_id,
            "event": "Device Token Refreshed",
            "properties": {
                "old_token": old_token[:20] + "...",  # Truncate for privacy
                "new_token": new_token[:20] + "...",  # Truncate for privacy
                "device_type": device_type,
                "refreshed_at": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.logger.info(
            "Device token refreshed",
            user_id=user_id,
            device_type=device_type
        )
        
        return event_data
    
    def remove_device(
        self,
        user_id: str,
        device_token: str,
        device_type: DeviceType,
        reason: str = "user_request"
    ) -> Dict[str, Any]:
        """
        Remove device registration with tracking.
        
        Args:
            user_id: User identifier
            device_token: Device push token
            device_type: Type of device
            reason: Reason for removal
            
        Returns:
            Event data dictionary
        """
        
        event_data = {
            "userId": user_id,
            "event": "Device Removed",
            "properties": {
                "device_token": device_token[:20] + "...",  # Truncate for privacy
                "device_type": device_type,
                "reason": reason,
                "removed_at": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.logger.info(
            "Device removed",
            user_id=user_id,
            device_type=device_type,
            reason=reason
        )
        
        return event_data
    
    def batch_register_devices(
        self,
        registrations: List[DeviceRegistration]
    ) -> List[Dict[str, Any]]:
        """
        Register multiple devices in batch with optimization.
        
        Args:
            registrations: List of DeviceRegistration objects
            
        Returns:
            List of batch result dictionaries
            
        Raises:
            CustomerIOError: If batch processing fails
        """
        
        results = []
        
        try:
            # Convert to batch requests
            batch_requests = []
            
            for registration in registrations:
                # Create device registration event
                event_data = {
                    "userId": registration.user_id,
                    "event": "Device Registered",
                    "properties": {
                        "device_type": registration.device_info.type,
                        "device_model": registration.device_info.device_model,
                        "os_version": registration.device_info.os_version,
                        "app_version": registration.device_info.app_version,
                        "push_provider": registration.device_info.push_provider,
                        "push_enabled": registration.attributes.push_enabled,
                        "timezone": registration.attributes.timezone,
                        "locale": registration.attributes.locale,
                        "registered_at": registration.registered_at.isoformat()
                    },
                    "timestamp": datetime.now(timezone.utc)
                }
                
                batch_request = {
                    "type": "track",
                    **event_data
                }
                batch_requests.append(batch_request)
            
            # Optimize batch sizes
            optimized_batches = BatchTransformer.optimize_batch_sizes(
                requests=batch_requests,
                max_size_bytes=500 * 1024  # 500KB limit
            )
            
            self.logger.info(
                "Processing batch device registrations",
                total_devices=len(registrations),
                num_batches=len(optimized_batches)
            )
            
            # Process each batch
            for i, batch_requests in enumerate(optimized_batches):
                try:
                    response = self.client.batch(batch_requests)
                    results.append({
                        "batch_id": i,
                        "status": "success",
                        "count": len(batch_requests),
                        "response": response
                    })
                except Exception as e:
                    results.append({
                        "batch_id": i,
                        "status": "failed",
                        "count": len(batch_requests),
                        "error": str(e)
                    })
                    self.logger.error(
                        "Batch device registration failed",
                        batch_id=i,
                        error=str(e)
                    )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "Batch device processing failed",
                total_devices=len(registrations),
                error=str(e)
            )
            raise
    
    def create_cross_platform_user(
        self,
        user_id: str,
        devices: List[DeviceRegistration]
    ) -> Dict[str, Any]:
        """
        Create tracking for user with multiple devices.
        
        Args:
            user_id: User identifier
            devices: List of user's device registrations
            
        Returns:
            Cross-platform event data
        """
        
        # Analyze device portfolio
        device_types = [device.device_info.type for device in devices]
        platforms = list(set(device_types))
        
        # Create cross-platform event
        event_data = {
            "userId": user_id,
            "event": "Multi-Device User Profile",
            "properties": {
                "total_devices": len(devices),
                "platforms": platforms,
                "device_breakdown": {
                    device_type: device_types.count(device_type)
                    for device_type in set(device_types)
                },
                "primary_platform": max(set(device_types), key=device_types.count) if device_types else None,
                "cross_platform": len(platforms) > 1,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.logger.info(
            "Cross-platform user profile created",
            user_id=user_id,
            total_devices=len(devices),
            platforms=platforms
        )
        
        return event_data
    
    def analyze_device_preferences(
        self,
        devices: List[DeviceRegistration]
    ) -> Dict[str, Any]:
        """
        Analyze device usage patterns and preferences.
        
        Args:
            devices: List of device registrations
            
        Returns:
            Device preference analysis
        """
        
        # Group devices by type
        by_type = {}
        for device in devices:
            device_type = device.device_info.type
            if device_type not in by_type:
                by_type[device_type] = []
            by_type[device_type].append(device)
        
        # Analyze preferences
        analysis = {
            "total_devices": len(devices),
            "device_types": list(by_type.keys()),
            "type_distribution": {k: len(v) for k, v in by_type.items()},
            "push_enabled_count": sum(1 for d in devices if d.attributes.push_enabled),
            "active_devices": sum(1 for d in devices if d.status == DeviceStatus.ACTIVE),
            "unique_timezones": len(set(
                d.attributes.timezone for d in devices 
                if d.attributes.timezone
            )),
            "unique_locales": len(set(
                d.attributes.locale for d in devices 
                if d.attributes.locale
            ))
        }
        
        # Find most recent device
        if devices:
            most_recent = max(devices, key=lambda d: d.registered_at)
            analysis["most_recent_device"] = {
                "type": most_recent.device_info.type,
                "model": most_recent.device_info.device_model,
                "registered_at": most_recent.registered_at.isoformat()
            }
        
        return analysis
    
    def calculate_device_metrics(
        self,
        registrations: List[DeviceRegistration]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive device metrics.
        
        Args:
            registrations: List of device registrations
            
        Returns:
            Device metrics dictionary
        """
        
        if not registrations:
            return {"total_devices": 0}
        
        # Basic counts
        total_devices = len(registrations)
        active_devices = sum(1 for d in registrations if d.status == DeviceStatus.ACTIVE)
        push_enabled = sum(1 for d in registrations if d.attributes.push_enabled)
        
        # Platform distribution
        platform_counts = {}
        for device in registrations:
            platform = device.device_info.type
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Push provider distribution
        provider_counts = {}
        for device in registrations:
            provider = device.device_info.push_provider or "unknown"
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        # Timezone and locale analysis
        timezones = [d.attributes.timezone for d in registrations if d.attributes.timezone]
        locales = [d.attributes.locale for d in registrations if d.attributes.locale]
        
        # Registration timeline
        if registrations:
            newest = max(registrations, key=lambda d: d.registered_at)
            oldest = min(registrations, key=lambda d: d.registered_at)
            
            registration_span = (newest.registered_at - oldest.registered_at).days
        else:
            registration_span = 0
        
        metrics = {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "inactive_devices": total_devices - active_devices,
            "push_enabled_devices": push_enabled,
            "push_opt_out_devices": total_devices - push_enabled,
            "platform_distribution": platform_counts,
            "push_provider_distribution": provider_counts,
            "unique_timezones": len(set(timezones)),
            "unique_locales": len(set(locales)),
            "registration_span_days": registration_span,
            "avg_devices_per_day": (
                total_devices / max(registration_span, 1) if registration_span > 0 else total_devices
            ),
            "push_adoption_rate": push_enabled / total_devices if total_devices > 0 else 0,
            "active_device_rate": active_devices / total_devices if total_devices > 0 else 0
        }
        
        return metrics
    
    def monitor_device_health(
        self,
        registrations: List[DeviceRegistration]
    ) -> Dict[str, Any]:
        """
        Monitor device health and identify issues.
        
        Args:
            registrations: List of device registrations
            
        Returns:
            Device health report
        """
        
        health_report = {
            "total_devices": len(registrations),
            "healthy_devices": 0,
            "issues_found": [],
            "recommendations": []
        }
        
        for device in registrations:
            device_issues = []
            
            # Check device status
            if device.status != DeviceStatus.ACTIVE:
                device_issues.append(f"Device status: {device.status}")
            
            # Check push enabled
            if not device.attributes.push_enabled:
                device_issues.append("Push notifications disabled")
            
            # Check token length (basic validation)
            if len(device.device_info.token) < 20:
                device_issues.append("Suspicious token length")
            
            # Check for missing attributes
            if not device.attributes.timezone:
                device_issues.append("Missing timezone information")
            
            if not device.attributes.locale:
                device_issues.append("Missing locale information")
            
            # Check registration age
            age_days = (datetime.now(timezone.utc) - device.registered_at).days
            if age_days > 90:  # Devices older than 90 days might need token refresh
                device_issues.append(f"Device registration is {age_days} days old")
            
            if device_issues:
                health_report["issues_found"].append({
                    "user_id": device.user_id,
                    "device_type": device.device_info.type,
                    "device_model": device.device_info.device_model,
                    "issues": device_issues
                })
            else:
                health_report["healthy_devices"] += 1
        
        # Generate recommendations
        if health_report["issues_found"]:
            health_report["recommendations"].extend([
                "Review devices with disabled push notifications",
                "Update tokens for devices with suspicious token lengths",
                "Collect missing timezone and locale information",
                "Implement periodic token refresh for old registrations"
            ])
        
        health_report["health_score"] = (
            health_report["healthy_devices"] / health_report["total_devices"]
            if health_report["total_devices"] > 0 else 1.0
        )
        
        return health_report
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get DeviceManager metrics and status.
        
        Returns:
            DeviceManager metrics dictionary
        """
        
        return {
            "client": {
                "base_url": getattr(self.client, 'base_url', 'unknown'),
                "region": getattr(self.client, 'region', 'unknown'),
                "timeout": getattr(self.client, 'timeout', 30),
                "max_retries": getattr(self.client, 'max_retries', 3),
                "rate_limit": {
                    "requests_per_window": 3000,
                    "window_seconds": 3
                }
            },
            "supported_platforms": {
                "device_types": [device_type.value for device_type in DeviceType],
                "push_providers": [provider.value for provider in PushProvider],
                "device_statuses": [status.value for status in DeviceStatus]
            },
            "validation": {
                "min_token_length": 10,
                "max_request_size_bytes": 32 * 1024,
                "timezone_format": "Region/City",
                "locale_format": "en or en-US"
            }
        }