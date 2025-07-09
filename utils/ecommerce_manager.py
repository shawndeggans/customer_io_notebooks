"""
Re-export of src.pipelines_api.ecommerce_manager for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.ecommerce_manager instead of src.pipelines_api.ecommerce_manager.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.ecommerce_manager import (
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
        track_product_reviewed,
    )

from src.pipelines_api.ecommerce_manager import *

__all__ = [
    "track_products_searched",
    "track_product_list_viewed",
    "track_product_list_filtered",
    "track_product_clicked",
    "track_checkout_step_viewed",
    "track_checkout_step_completed",
    "track_payment_info_entered",
    "track_promotion_viewed",
    "track_promotion_clicked",
    "track_coupon_entered",
    "track_coupon_applied",
    "track_coupon_denied",
    "track_coupon_removed",
    "track_product_added_to_wishlist",
    "track_product_removed_from_wishlist",
    "track_wishlist_product_added_to_cart",
    "track_product_shared",
    "track_cart_shared",
    "track_product_reviewed",
]
