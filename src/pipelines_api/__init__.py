"""
Customer.IO Data Pipelines API Utilities

This module provides utility classes and functions for working with
Customer.IO's Data Pipelines API.
"""

from .api_client import CustomerIOClient
from .exceptions import (
    CustomerIOError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NetworkError
)
from .validators import (
    validate_email,
    validate_user_id,
    validate_event_name,
    validate_batch_size,
    validate_region
)
from .people_manager import (
    identify_user,
    delete_user,
    suppress_user,
    unsuppress_user
)
from .event_manager import (
    track_event,
    track_page_view,
    track_screen_view,
    track_ecommerce_event,
    track_email_event,
    track_mobile_event,
    track_video_event
)
from .device_manager import (
    register_device,
    update_device,
    delete_device
)
from .object_manager import (
    create_object,
    update_object,
    delete_object,
    create_relationship,
    delete_relationship
)
from .batch_manager import (
    send_batch,
    create_batch_operations,
    validate_batch_size,
    split_oversized_batch
)
from .page_manager import (
    track_page,
    track_pageview
)
from .screen_manager import (
    track_screen,
    track_screenview
)
from .alias_manager import (
    create_alias,
    merge_profiles
)
from .gdpr_manager import (
    track_user_deleted,
    track_user_suppressed,
    track_user_unsuppressed,
    track_device_deleted,
    track_object_deleted,
    track_relationship_deleted,
    track_report_delivery_event
)
from .video_manager import (
    track_video_playback_started,
    track_video_playback_paused,
    track_video_playback_interrupted,
    track_video_playback_buffer_started,
    track_video_playback_buffer_completed,
    track_video_playback_seek_started,
    track_video_playback_seek_completed,
    track_video_playback_resumed,
    track_video_playback_completed,
    track_video_playback_exited,
    track_video_content_started,
    track_video_content_playing,
    track_video_content_completed,
    track_video_ad_started,
    track_video_ad_playing,
    track_video_ad_completed
)
from .mobile_manager import (
    track_application_installed,
    track_application_opened,
    track_application_backgrounded,
    track_application_foregrounded,
    track_application_updated,
    track_application_uninstalled,
    track_application_crashed,
    track_push_notification_received,
    track_push_notification_tapped
)
from .ecommerce_manager import (
    track_products_searched,
    track_product_list_viewed,
    track_product_list_filtered,
    track_product_clicked,
    track_checkout_step_viewed,
    track_checkout_step_completed,
    track_payment_info_entered,
    track_promotion_viewed,
    track_promotion_clicked,
    track_coupon_entered,
    track_coupon_applied,
    track_coupon_denied,
    track_coupon_removed,
    track_product_added_to_wishlist,
    track_product_removed_from_wishlist,
    track_wishlist_product_added_to_cart,
    track_product_shared,
    track_cart_shared,
    track_product_reviewed
)

__version__ = "1.0.0"
__all__ = [
    "CustomerIOClient",
    "CustomerIOError",
    "AuthenticationError", 
    "RateLimitError",
    "ValidationError",
    "NetworkError",
    "validate_email",
    "validate_user_id",
    "validate_event_name",
    "validate_batch_size",
    "validate_region",
    "identify_user",
    "delete_user",
    "suppress_user",
    "unsuppress_user",
    "track_event",
    "track_page_view",
    "track_screen_view",
    "track_ecommerce_event",
    "track_email_event",
    "track_mobile_event",
    "track_video_event",
    "register_device",
    "update_device",
    "delete_device",
    "create_object",
    "update_object",
    "delete_object",
    "create_relationship",
    "delete_relationship",
    "send_batch",
    "create_batch_operations",
    "validate_batch_size",
    "split_oversized_batch",
    "track_page",
    "track_pageview",
    "track_screen",
    "track_screenview",
    "create_alias",
    "merge_profiles",
    "track_user_deleted",
    "track_user_suppressed",
    "track_user_unsuppressed",
    "track_device_deleted",
    "track_object_deleted",
    "track_relationship_deleted",
    "track_report_delivery_event",
    "track_video_playback_started",
    "track_video_playback_paused",
    "track_video_playback_interrupted",
    "track_video_playback_buffer_started",
    "track_video_playback_buffer_completed",
    "track_video_playback_seek_started",
    "track_video_playback_seek_completed",
    "track_video_playback_resumed",
    "track_video_playback_completed",
    "track_video_playback_exited",
    "track_video_content_started",
    "track_video_content_playing",
    "track_video_content_completed",
    "track_video_ad_started",
    "track_video_ad_playing",
    "track_video_ad_completed",
    "track_application_installed",
    "track_application_opened",
    "track_application_backgrounded",
    "track_application_foregrounded",
    "track_application_updated",
    "track_application_uninstalled",
    "track_application_crashed",
    "track_push_notification_received",
    "track_push_notification_tapped"
]