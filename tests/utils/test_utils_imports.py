"""
Test that utils modules can be imported correctly.
Following TDD Red-Green-Refactor methodology.
"""

import pytest


class TestUtilsImports:
    """Test that utils modules import correctly."""
    
    def test_utils_api_client_import(self):
        """Test that utils.api_client imports correctly."""
        from utils.api_client import CustomerIOClient
        assert CustomerIOClient is not None
    
    def test_utils_people_manager_import(self):
        """Test that utils.people_manager imports correctly."""
        from utils.people_manager import identify_user, delete_user, suppress_user, unsuppress_user
        assert identify_user is not None
        assert delete_user is not None
        assert suppress_user is not None
        assert unsuppress_user is not None
    
    def test_utils_event_manager_import(self):
        """Test that utils.event_manager imports correctly."""
        from utils.event_manager import track_event, track_page_view, track_screen_view
        assert track_event is not None
        assert track_page_view is not None
        assert track_screen_view is not None
    
    def test_utils_video_manager_import(self):
        """Test that utils.video_manager imports correctly."""
        from utils.video_manager import (
            track_video_playback_started,
            track_video_playback_completed
        )
        assert track_video_playback_started is not None
        assert track_video_playback_completed is not None
    
    def test_utils_mobile_manager_import(self):
        """Test that utils.mobile_manager imports correctly."""
        from utils.mobile_manager import (
            track_application_installed,
            track_application_opened
        )
        assert track_application_installed is not None
        assert track_application_opened is not None
    
    def test_utils_ecommerce_manager_import(self):
        """Test that utils.ecommerce_manager imports correctly."""
        from utils.ecommerce_manager import (
            track_product_clicked,
            track_checkout_step_completed,
            track_product_added_to_wishlist
        )
        assert track_product_clicked is not None
        assert track_checkout_step_completed is not None
        assert track_product_added_to_wishlist is not None
    
    def test_utils_device_manager_import(self):
        """Test that utils.device_manager imports correctly."""
        from utils.device_manager import register_device, update_device, delete_device
        assert register_device is not None
        assert update_device is not None
        assert delete_device is not None
    
    def test_utils_object_manager_import(self):
        """Test that utils.object_manager imports correctly."""
        from utils.object_manager import (
            create_object,
            update_object,
            delete_object,
            create_relationship,
            delete_relationship
        )
        assert create_object is not None
        assert update_object is not None
        assert delete_object is not None
        assert create_relationship is not None
        assert delete_relationship is not None
    
    def test_utils_batch_manager_import(self):
        """Test that utils.batch_manager imports correctly."""
        from utils.batch_manager import (
            send_batch,
            create_batch_operations,
            validate_batch_size,
            split_oversized_batch
        )
        assert send_batch is not None
        assert create_batch_operations is not None
        assert validate_batch_size is not None
        assert split_oversized_batch is not None
    
    def test_utils_validators_import(self):
        """Test that utils.validators imports correctly."""
        from utils.validators import (
            validate_email,
            validate_user_id,
            validate_event_name,
            validate_batch_size,
            validate_region
        )
        assert validate_email is not None
        assert validate_user_id is not None
        assert validate_event_name is not None
        assert validate_batch_size is not None
        assert validate_region is not None
    
    def test_utils_exceptions_import(self):
        """Test that utils.exceptions imports correctly."""
        from utils.exceptions import (
            CustomerIOError,
            AuthenticationError,
            RateLimitError,
            ValidationError,
            NetworkError
        )
        assert CustomerIOError is not None
        assert AuthenticationError is not None
        assert RateLimitError is not None
        assert ValidationError is not None
        assert NetworkError is not None


class TestAppUtilsImports:
    """Test that app_utils modules import correctly."""
    
    def test_app_utils_auth_import(self):
        """Test that app_utils.auth imports correctly."""
        from app_utils.auth import AppAPIAuth
        assert AppAPIAuth is not None
    
    def test_app_utils_client_import(self):
        """Test that app_utils.client imports correctly."""
        from app_utils.client import (
            send_transactional,
            trigger_broadcast,
            send_push
        )
        assert send_transactional is not None
        assert trigger_broadcast is not None
        assert send_push is not None


class TestWebhookUtilsImports:
    """Test that webhook_utils modules import correctly."""
    
    def test_webhook_utils_processor_import(self):
        """Test that webhook_utils.processor imports correctly."""
        from webhook_utils.processor import (
            verify_signature,
            parse_event,
            get_event_type
        )
        assert verify_signature is not None
        assert parse_event is not None
        assert get_event_type is not None
    
    def test_webhook_utils_event_handlers_import(self):
        """Test that webhook_utils.event_handlers imports correctly."""
        from webhook_utils.event_handlers import get_event_handler
        assert get_event_handler is not None
    
    def test_webhook_utils_config_manager_import(self):
        """Test that webhook_utils.config_manager imports correctly."""
        from webhook_utils.config_manager import (
            CustomerIOWebhookManager,
            setup_databricks_webhook
        )
        assert CustomerIOWebhookManager is not None
        assert setup_databricks_webhook is not None


class TestUtilsFunctionality:
    """Test that imported functions work correctly."""
    
    def test_utils_api_client_functionality(self):
        """Test that utils.api_client functions work correctly."""
        from utils.api_client import CustomerIOClient
        from utils.people_manager import identify_user
        
        # Test that imported functions work
        client = CustomerIOClient(api_key="test", region="us")
        assert client.api_key == "test"
        assert hasattr(identify_user, '__call__')
    
    def test_app_utils_functionality(self):
        """Test that app_utils functions work correctly."""
        from app_utils.auth import AppAPIAuth
        from app_utils.client import send_transactional
        
        # Test that imported functions work
        auth = AppAPIAuth(api_token="test", region="us")
        assert auth.api_token == "test"
        assert hasattr(send_transactional, '__call__')
    
    def test_webhook_utils_functionality(self):
        """Test that webhook_utils functions work correctly."""
        from webhook_utils.processor import verify_signature
        
        # Test that imported functions work
        assert hasattr(verify_signature, '__call__')