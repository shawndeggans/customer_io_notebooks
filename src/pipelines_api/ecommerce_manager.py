"""
Customer.IO comprehensive ecommerce semantic events.

This module provides functions for tracking all ecommerce-related semantic events
as defined in the Customer.IO Data Pipelines API specification, including
product discovery, checkout funnel, promotions, coupons, wishlists, and social commerce.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .api_client import CustomerIOClient
from .validators import validate_user_id
from .exceptions import ValidationError


def track_products_searched(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Products Searched" semantic event.
    
    This event indicates that a user has performed a product search,
    providing insights into search behavior and product discovery patterns.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (query, results_count, category, filters_applied, etc.)
    timestamp : datetime, optional
        When the search was performed
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id or parameters are invalid
    CustomerIOError
        If API request fails
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Products Searched"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_product_list_viewed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Product List Viewed" semantic event.
    
    This event indicates that a user has viewed a list of products,
    providing insights into browsing behavior and category engagement.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (list_id, list_name, category, products, etc.)
    timestamp : datetime, optional
        When the product list was viewed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Product List Viewed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_product_list_filtered(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Product List Filtered" semantic event.
    
    This event indicates that a user has applied filters to a product list,
    providing insights into product discovery preferences and intent.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (list_id, filters, results_count, etc.)
    timestamp : datetime, optional
        When the filters were applied
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Product List Filtered"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_product_clicked(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Product Clicked" semantic event.
    
    This event indicates that a user has clicked on a product from a list,
    providing insights into product interest and click-through rates.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (product_id, product_name, position, list_id, etc.)
    timestamp : datetime, optional
        When the product was clicked
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Product Clicked"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_checkout_step_viewed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Checkout Step Viewed" semantic event.
    
    This event indicates that a user has viewed a specific step in the checkout
    process, providing insights into checkout funnel progression.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (checkout_id, step, step_name, cart_value, etc.)
    timestamp : datetime, optional
        When the checkout step was viewed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Checkout Step Viewed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_checkout_step_completed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Checkout Step Completed" semantic event.
    
    This event indicates that a user has completed a specific step in the checkout
    process, providing insights into checkout funnel conversion rates.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (checkout_id, step, step_name, completion_data, etc.)
    timestamp : datetime, optional
        When the checkout step was completed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Checkout Step Completed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_payment_info_entered(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Payment Info Entered" semantic event.
    
    This event indicates that a user has entered payment information during
    checkout, providing insights into payment funnel conversion.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (checkout_id, payment_method, card_type, etc.)
    timestamp : datetime, optional
        When the payment info was entered
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Payment Info Entered"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_promotion_viewed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Promotion Viewed" semantic event.
    
    This event indicates that a user has viewed a promotional offer,
    providing insights into promotion effectiveness and exposure.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (promotion_id, promotion_name, discount_type, etc.)
    timestamp : datetime, optional
        When the promotion was viewed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Promotion Viewed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_promotion_clicked(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Promotion Clicked" semantic event.
    
    This event indicates that a user has clicked on a promotional offer,
    providing insights into promotion engagement and click-through rates.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (promotion_id, cta_text, destination_url, etc.)
    timestamp : datetime, optional
        When the promotion was clicked
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Promotion Clicked"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_coupon_entered(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Coupon Entered" semantic event.
    
    This event indicates that a user has entered a coupon code,
    providing insights into coupon usage attempts and marketing effectiveness.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (coupon_code, cart_value, checkout_id, etc.)
    timestamp : datetime, optional
        When the coupon was entered
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Coupon Entered"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_coupon_applied(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Coupon Applied" semantic event.
    
    This event indicates that a coupon has been successfully applied,
    providing insights into coupon effectiveness and discount impact.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (coupon_code, discount_amount, cart_value_before/after, etc.)
    timestamp : datetime, optional
        When the coupon was applied
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Coupon Applied"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_coupon_denied(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Coupon Denied" semantic event.
    
    This event indicates that a coupon application was denied,
    providing insights into coupon validation issues and user experience.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (coupon_code, denial_reason, error_message, etc.)
    timestamp : datetime, optional
        When the coupon was denied
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Coupon Denied"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_coupon_removed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Coupon Removed" semantic event.
    
    This event indicates that a previously applied coupon has been removed,
    providing insights into coupon management behavior and cart modifications.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (coupon_code, discount_amount_lost, removal_reason, etc.)
    timestamp : datetime, optional
        When the coupon was removed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Coupon Removed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_product_added_to_wishlist(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Product Added to Wishlist" semantic event.
    
    This event indicates that a user has added a product to their wishlist,
    providing insights into product interest and future purchase intent.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (product_id, product_name, wishlist_id, etc.)
    timestamp : datetime, optional
        When the product was added to wishlist
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Product Added to Wishlist"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_product_removed_from_wishlist(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Product Removed from Wishlist" semantic event.
    
    This event indicates that a user has removed a product from their wishlist,
    providing insights into wishlist management and changing preferences.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (product_id, wishlist_id, removal_reason, etc.)
    timestamp : datetime, optional
        When the product was removed from wishlist
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Product Removed from Wishlist"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_wishlist_product_added_to_cart(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Wishlist Product Added to Cart" semantic event.
    
    This event indicates that a user has moved a product from their wishlist
    to their cart, providing insights into wishlist-to-purchase conversion.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (product_id, wishlist_id, cart_id, quantity, etc.)
    timestamp : datetime, optional
        When the wishlist product was added to cart
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Wishlist Product Added to Cart"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_product_shared(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Product Shared" semantic event.
    
    This event indicates that a user has shared a product with others,
    providing insights into social commerce and word-of-mouth marketing.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (product_id, share_method, platform, share_url, etc.)
    timestamp : datetime, optional
        When the product was shared
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Product Shared"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_cart_shared(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Cart Shared" semantic event.
    
    This event indicates that a user has shared their cart with others,
    providing insights into social commerce and collaborative shopping.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (cart_id, cart_value, items_count, share_method, etc.)
    timestamp : datetime, optional
        When the cart was shared
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Cart Shared"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)


def track_product_reviewed(
    client: CustomerIOClient,
    user_id: str,
    properties: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Track a "Product Reviewed" semantic event.
    
    This event indicates that a user has written a review for a product,
    providing insights into customer satisfaction and engagement with products.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    properties : dict, optional
        Additional properties (product_id, rating, review_title, verified_purchase, etc.)
    timestamp : datetime, optional
        When the product was reviewed
        
    Returns
    -------
    dict
        API response containing operation status
    """
    # Validate inputs
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("User ID must be a non-empty string")
    
    validate_user_id(user_id)
    
    if properties is not None and not isinstance(properties, dict):
        raise ValidationError("Properties must be a dictionary")
    
    # Build request data
    data = {
        "userId": user_id,
        "event": "Product Reviewed"
    }
    
    # Add properties if provided
    if properties:
        data["properties"] = properties
    
    # Add timestamp if provided
    if timestamp:
        data["timestamp"] = timestamp.isoformat()
    
    return client.make_request("POST", "/track", data)