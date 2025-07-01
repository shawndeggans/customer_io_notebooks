"""
Unit tests for Customer.IO comprehensive ecommerce semantic events.
"""

from unittest.mock import Mock
import pytest

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
    track_product_reviewed
)
from src.pipelines_api.exceptions import ValidationError, CustomerIOError
from src.pipelines_api.api_client import CustomerIOClient


class TestProductDiscoveryEvents:
    """Test product discovery and search semantic events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_products_searched_success(self, mock_client):
        """Test successful Products Searched event tracking."""
        result = track_products_searched(
            client=mock_client,
            user_id="user123",
            properties={
                "query": "wireless headphones",
                "results_count": 25,
                "category": "electronics",
                "filters_applied": ["brand:sony", "price:100-200"]
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Products Searched",
                "properties": {
                    "query": "wireless headphones",
                    "results_count": 25,
                    "category": "electronics",
                    "filters_applied": ["brand:sony", "price:100-200"]
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_product_list_viewed_success(self, mock_client):
        """Test successful Product List Viewed event tracking."""
        result = track_product_list_viewed(
            client=mock_client,
            user_id="user123",
            properties={
                "list_id": "featured_products",
                "list_name": "Featured Products",
                "category": "electronics",
                "products": [
                    {"product_id": "prod_1", "name": "Wireless Earbuds", "price": 99.99},
                    {"product_id": "prod_2", "name": "Bluetooth Speaker", "price": 149.99}
                ]
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Product List Viewed",
                "properties": {
                    "list_id": "featured_products",
                    "list_name": "Featured Products",
                    "category": "electronics",
                    "products": [
                        {"product_id": "prod_1", "name": "Wireless Earbuds", "price": 99.99},
                        {"product_id": "prod_2", "name": "Bluetooth Speaker", "price": 149.99}
                    ]
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_product_list_filtered_success(self, mock_client):
        """Test successful Product List Filtered event tracking."""
        result = track_product_list_filtered(
            client=mock_client,
            user_id="user123",
            properties={
                "list_id": "search_results",
                "filters": {
                    "brand": ["Sony", "Apple"],
                    "price_range": {"min": 50, "max": 300},
                    "rating": "4_stars_and_up"
                },
                "results_count": 12
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Product List Filtered",
                "properties": {
                    "list_id": "search_results",
                    "filters": {
                        "brand": ["Sony", "Apple"],
                        "price_range": {"min": 50, "max": 300},
                        "rating": "4_stars_and_up"
                    },
                    "results_count": 12
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_product_clicked_success(self, mock_client):
        """Test successful Product Clicked event tracking."""
        result = track_product_clicked(
            client=mock_client,
            user_id="user123",
            properties={
                "product_id": "prod_123",
                "product_name": "Wireless Headphones",
                "category": "electronics",
                "price": 199.99,
                "position": 3,
                "list_id": "search_results"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Product Clicked",
                "properties": {
                    "product_id": "prod_123",
                    "product_name": "Wireless Headphones",
                    "category": "electronics",
                    "price": 199.99,
                    "position": 3,
                    "list_id": "search_results"
                }
            }
        )
        assert result == {"status": "success"}


class TestCheckoutFunnelEvents:
    """Test checkout funnel semantic events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_checkout_step_viewed_success(self, mock_client):
        """Test successful Checkout Step Viewed event tracking."""
        result = track_checkout_step_viewed(
            client=mock_client,
            user_id="user123",
            properties={
                "checkout_id": "checkout_456",
                "step": 2,
                "step_name": "shipping_info",
                "cart_value": 299.97,
                "items_count": 3
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Checkout Step Viewed",
                "properties": {
                    "checkout_id": "checkout_456",
                    "step": 2,
                    "step_name": "shipping_info",
                    "cart_value": 299.97,
                    "items_count": 3
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_checkout_step_completed_success(self, mock_client):
        """Test successful Checkout Step Completed event tracking."""
        result = track_checkout_step_completed(
            client=mock_client,
            user_id="user123",
            properties={
                "checkout_id": "checkout_456",
                "step": 2,
                "step_name": "shipping_info",
                "shipping_method": "standard",
                "estimated_delivery": "3-5 business days"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Checkout Step Completed",
                "properties": {
                    "checkout_id": "checkout_456",
                    "step": 2,
                    "step_name": "shipping_info",
                    "shipping_method": "standard",
                    "estimated_delivery": "3-5 business days"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_payment_info_entered_success(self, mock_client):
        """Test successful Payment Info Entered event tracking."""
        result = track_payment_info_entered(
            client=mock_client,
            user_id="user123",
            properties={
                "checkout_id": "checkout_456",
                "payment_method": "credit_card",
                "card_type": "visa",
                "cart_value": 299.97
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Payment Info Entered",
                "properties": {
                    "checkout_id": "checkout_456",
                    "payment_method": "credit_card",
                    "card_type": "visa",
                    "cart_value": 299.97
                }
            }
        )
        assert result == {"status": "success"}


class TestPromotionEvents:
    """Test promotion and marketing semantic events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_promotion_viewed_success(self, mock_client):
        """Test successful Promotion Viewed event tracking."""
        result = track_promotion_viewed(
            client=mock_client,
            user_id="user123",
            properties={
                "promotion_id": "summer_sale_2024",
                "promotion_name": "Summer Sale 20% Off",
                "discount_type": "percentage",
                "discount_value": 20,
                "position": "hero_banner"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Promotion Viewed",
                "properties": {
                    "promotion_id": "summer_sale_2024",
                    "promotion_name": "Summer Sale 20% Off",
                    "discount_type": "percentage",
                    "discount_value": 20,
                    "position": "hero_banner"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_promotion_clicked_success(self, mock_client):
        """Test successful Promotion Clicked event tracking."""
        result = track_promotion_clicked(
            client=mock_client,
            user_id="user123",
            properties={
                "promotion_id": "summer_sale_2024",
                "promotion_name": "Summer Sale 20% Off",
                "cta_text": "Shop Now",
                "destination_url": "/summer-sale"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Promotion Clicked",
                "properties": {
                    "promotion_id": "summer_sale_2024",
                    "promotion_name": "Summer Sale 20% Off",
                    "cta_text": "Shop Now",
                    "destination_url": "/summer-sale"
                }
            }
        )
        assert result == {"status": "success"}


class TestCouponEvents:
    """Test coupon management semantic events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_coupon_entered_success(self, mock_client):
        """Test successful Coupon Entered event tracking."""
        result = track_coupon_entered(
            client=mock_client,
            user_id="user123",
            properties={
                "coupon_code": "SAVE20",
                "cart_value": 150.00,
                "checkout_id": "checkout_789"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Coupon Entered",
                "properties": {
                    "coupon_code": "SAVE20",
                    "cart_value": 150.00,
                    "checkout_id": "checkout_789"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_coupon_applied_success(self, mock_client):
        """Test successful Coupon Applied event tracking."""
        result = track_coupon_applied(
            client=mock_client,
            user_id="user123",
            properties={
                "coupon_code": "SAVE20",
                "discount_amount": 30.00,
                "discount_type": "fixed_amount",
                "cart_value_before": 150.00,
                "cart_value_after": 120.00
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Coupon Applied",
                "properties": {
                    "coupon_code": "SAVE20",
                    "discount_amount": 30.00,
                    "discount_type": "fixed_amount",
                    "cart_value_before": 150.00,
                    "cart_value_after": 120.00
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_coupon_denied_success(self, mock_client):
        """Test successful Coupon Denied event tracking."""
        result = track_coupon_denied(
            client=mock_client,
            user_id="user123",
            properties={
                "coupon_code": "EXPIRED20",
                "denial_reason": "expired",
                "cart_value": 150.00,
                "error_message": "This coupon has expired"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Coupon Denied",
                "properties": {
                    "coupon_code": "EXPIRED20",
                    "denial_reason": "expired",
                    "cart_value": 150.00,
                    "error_message": "This coupon has expired"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_coupon_removed_success(self, mock_client):
        """Test successful Coupon Removed event tracking."""
        result = track_coupon_removed(
            client=mock_client,
            user_id="user123",
            properties={
                "coupon_code": "SAVE20",
                "discount_amount_lost": 30.00,
                "cart_value_before": 120.00,
                "cart_value_after": 150.00,
                "removal_reason": "user_action"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Coupon Removed",
                "properties": {
                    "coupon_code": "SAVE20",
                    "discount_amount_lost": 30.00,
                    "cart_value_before": 120.00,
                    "cart_value_after": 150.00,
                    "removal_reason": "user_action"
                }
            }
        )
        assert result == {"status": "success"}


class TestWishlistEvents:
    """Test wishlist management semantic events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_product_added_to_wishlist_success(self, mock_client):
        """Test successful Product Added to Wishlist event tracking."""
        result = track_product_added_to_wishlist(
            client=mock_client,
            user_id="user123",
            properties={
                "product_id": "prod_456",
                "product_name": "Designer Headphones",
                "category": "electronics",
                "price": 299.99,
                "wishlist_id": "default",
                "wishlist_name": "My Wishlist"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Product Added to Wishlist",
                "properties": {
                    "product_id": "prod_456",
                    "product_name": "Designer Headphones",
                    "category": "electronics",
                    "price": 299.99,
                    "wishlist_id": "default",
                    "wishlist_name": "My Wishlist"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_product_removed_from_wishlist_success(self, mock_client):
        """Test successful Product Removed from Wishlist event tracking."""
        result = track_product_removed_from_wishlist(
            client=mock_client,
            user_id="user123",
            properties={
                "product_id": "prod_456",
                "product_name": "Designer Headphones",
                "wishlist_id": "default",
                "removal_reason": "purchased"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Product Removed from Wishlist",
                "properties": {
                    "product_id": "prod_456",
                    "product_name": "Designer Headphones",
                    "wishlist_id": "default",
                    "removal_reason": "purchased"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_wishlist_product_added_to_cart_success(self, mock_client):
        """Test successful Wishlist Product Added to Cart event tracking."""
        result = track_wishlist_product_added_to_cart(
            client=mock_client,
            user_id="user123",
            properties={
                "product_id": "prod_456",
                "product_name": "Designer Headphones",
                "price": 299.99,
                "quantity": 1,
                "wishlist_id": "default",
                "cart_id": "cart_789"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Wishlist Product Added to Cart",
                "properties": {
                    "product_id": "prod_456",
                    "product_name": "Designer Headphones",
                    "price": 299.99,
                    "quantity": 1,
                    "wishlist_id": "default",
                    "cart_id": "cart_789"
                }
            }
        )
        assert result == {"status": "success"}


class TestSocialCommerceEvents:
    """Test social commerce semantic events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_track_product_shared_success(self, mock_client):
        """Test successful Product Shared event tracking."""
        result = track_product_shared(
            client=mock_client,
            user_id="user123",
            properties={
                "product_id": "prod_789",
                "product_name": "Smart Watch",
                "share_method": "social_media",
                "platform": "twitter",
                "share_url": "https://example.com/product/789"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Product Shared",
                "properties": {
                    "product_id": "prod_789",
                    "product_name": "Smart Watch",
                    "share_method": "social_media",
                    "platform": "twitter",
                    "share_url": "https://example.com/product/789"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_cart_shared_success(self, mock_client):
        """Test successful Cart Shared event tracking."""
        result = track_cart_shared(
            client=mock_client,
            user_id="user123",
            properties={
                "cart_id": "cart_456",
                "cart_value": 599.98,
                "items_count": 4,
                "share_method": "email",
                "recipient_type": "friend"
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Cart Shared",
                "properties": {
                    "cart_id": "cart_456",
                    "cart_value": 599.98,
                    "items_count": 4,
                    "share_method": "email",
                    "recipient_type": "friend"
                }
            }
        )
        assert result == {"status": "success"}
    
    def test_track_product_reviewed_success(self, mock_client):
        """Test successful Product Reviewed event tracking."""
        result = track_product_reviewed(
            client=mock_client,
            user_id="user123",
            properties={
                "product_id": "prod_789",
                "product_name": "Smart Watch",
                "rating": 5,
                "review_title": "Excellent product!",
                "review_length": 250,
                "verified_purchase": True
            }
        )
        
        mock_client.make_request.assert_called_once_with(
            "POST",
            "/track",
            {
                "userId": "user123",
                "event": "Product Reviewed",
                "properties": {
                    "product_id": "prod_789",
                    "product_name": "Smart Watch",
                    "rating": 5,
                    "review_title": "Excellent product!",
                    "review_length": 250,
                    "verified_purchase": True
                }
            }
        )
        assert result == {"status": "success"}


class TestEcommerceManagerValidation:
    """Test validation scenarios for ecommerce events."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_invalid_user_id(self, mock_client):
        """Test ecommerce event with invalid user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_products_searched(
                client=mock_client,
                user_id=""
            )
    
    def test_none_user_id(self, mock_client):
        """Test ecommerce event with None user ID."""
        with pytest.raises(ValidationError, match="User ID must be a non-empty string"):
            track_product_list_viewed(
                client=mock_client,
                user_id=None
            )
    
    def test_invalid_properties(self, mock_client):
        """Test ecommerce event with invalid properties."""
        with pytest.raises(ValidationError, match="Properties must be a dictionary"):
            track_checkout_step_viewed(
                client=mock_client,
                user_id="user123",
                properties="invalid"
            )
    
    def test_api_error(self, mock_client):
        """Test ecommerce event when API returns error."""
        mock_client.make_request.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            track_payment_info_entered(
                client=mock_client,
                user_id="user123"
            )


class TestEcommerceManagerIntegration:
    """Test integration scenarios for comprehensive ecommerce analytics."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Customer.IO client."""
        client = Mock(spec=CustomerIOClient)
        client.make_request.return_value = {"status": "success"}
        return client
    
    def test_complete_purchase_funnel_workflow(self, mock_client):
        """Test complete purchase funnel workflow."""
        user_id = "user123"
        
        # Search for products
        search_result = track_products_searched(
            client=mock_client,
            user_id=user_id,
            properties={"query": "running shoes", "results_count": 50}
        )
        assert search_result == {"status": "success"}
        
        # View product list
        list_result = track_product_list_viewed(
            client=mock_client,
            user_id=user_id,
            properties={"list_id": "search_results", "category": "footwear"}
        )
        assert list_result == {"status": "success"}
        
        # Filter results
        filter_result = track_product_list_filtered(
            client=mock_client,
            user_id=user_id,
            properties={"filters": {"size": ["10", "10.5"], "brand": ["Nike"]}}
        )
        assert filter_result == {"status": "success"}
        
        # Click on product
        click_result = track_product_clicked(
            client=mock_client,
            user_id=user_id,
            properties={"product_id": "shoe_123", "position": 1}
        )
        assert click_result == {"status": "success"}
        
        # Start checkout
        checkout_start = track_checkout_step_viewed(
            client=mock_client,
            user_id=user_id,
            properties={"step": 1, "step_name": "cart_review"}
        )
        assert checkout_start == {"status": "success"}
        
        # Complete checkout steps
        checkout_complete = track_checkout_step_completed(
            client=mock_client,
            user_id=user_id,
            properties={"step": 2, "step_name": "shipping_info"}
        )
        assert checkout_complete == {"status": "success"}
        
        # Enter payment info
        payment_result = track_payment_info_entered(
            client=mock_client,
            user_id=user_id,
            properties={"payment_method": "credit_card"}
        )
        assert payment_result == {"status": "success"}
        
        # Verify all funnel events were tracked
        assert mock_client.make_request.call_count == 7
    
    def test_promotion_and_coupon_workflow(self, mock_client):
        """Test promotion viewing and coupon usage workflow."""
        user_id = "user123"
        
        # View promotion
        promotion_view = track_promotion_viewed(
            client=mock_client,
            user_id=user_id,
            properties={"promotion_id": "flash_sale", "discount_value": 25}
        )
        assert promotion_view == {"status": "success"}
        
        # Click promotion
        promotion_click = track_promotion_clicked(
            client=mock_client,
            user_id=user_id,
            properties={"promotion_id": "flash_sale", "cta_text": "Shop Sale"}
        )
        assert promotion_click == {"status": "success"}
        
        # Enter coupon
        coupon_enter = track_coupon_entered(
            client=mock_client,
            user_id=user_id,
            properties={"coupon_code": "FLASH25", "cart_value": 200.00}
        )
        assert coupon_enter == {"status": "success"}
        
        # Apply coupon successfully
        coupon_apply = track_coupon_applied(
            client=mock_client,
            user_id=user_id,
            properties={
                "coupon_code": "FLASH25",
                "discount_amount": 50.00,
                "cart_value_after": 150.00
            }
        )
        assert coupon_apply == {"status": "success"}
        
        # Verify all promotion events were tracked
        assert mock_client.make_request.call_count == 4
    
    def test_wishlist_management_workflow(self, mock_client):
        """Test wishlist management workflow."""
        user_id = "user123"
        product_id = "prod_789"
        
        # Add product to wishlist
        add_wishlist = track_product_added_to_wishlist(
            client=mock_client,
            user_id=user_id,
            properties={
                "product_id": product_id,
                "product_name": "Premium Headphones",
                "price": 399.99
            }
        )
        assert add_wishlist == {"status": "success"}
        
        # Later: Add wishlist item to cart
        add_to_cart = track_wishlist_product_added_to_cart(
            client=mock_client,
            user_id=user_id,
            properties={
                "product_id": product_id,
                "price": 399.99,
                "quantity": 1
            }
        )
        assert add_to_cart == {"status": "success"}
        
        # Remove from wishlist after purchase
        remove_wishlist = track_product_removed_from_wishlist(
            client=mock_client,
            user_id=user_id,
            properties={
                "product_id": product_id,
                "removal_reason": "purchased"
            }
        )
        assert remove_wishlist == {"status": "success"}
        
        # Verify all wishlist events were tracked
        assert mock_client.make_request.call_count == 3
    
    def test_social_commerce_workflow(self, mock_client):
        """Test social commerce engagement workflow."""
        user_id = "user123"
        
        # Share product with friends
        share_product = track_product_shared(
            client=mock_client,
            user_id=user_id,
            properties={
                "product_id": "prod_123",
                "share_method": "social_media",
                "platform": "instagram"
            }
        )
        assert share_product == {"status": "success"}
        
        # Share entire cart
        share_cart = track_cart_shared(
            client=mock_client,
            user_id=user_id,
            properties={
                "cart_value": 750.00,
                "items_count": 5,
                "share_method": "email"
            }
        )
        assert share_cart == {"status": "success"}
        
        # Write product review after purchase
        review_product = track_product_reviewed(
            client=mock_client,
            user_id=user_id,
            properties={
                "product_id": "prod_123",
                "rating": 4,
                "verified_purchase": True
            }
        )
        assert review_product == {"status": "success"}
        
        # Verify all social commerce events were tracked
        assert mock_client.make_request.call_count == 3
    
    def test_coupon_failure_workflow(self, mock_client):
        """Test coupon failure and recovery workflow."""
        user_id = "user123"
        
        # Enter invalid coupon
        coupon_enter = track_coupon_entered(
            client=mock_client,
            user_id=user_id,
            properties={"coupon_code": "INVALID20", "cart_value": 100.00}
        )
        assert coupon_enter == {"status": "success"}
        
        # Coupon denied
        coupon_deny = track_coupon_denied(
            client=mock_client,
            user_id=user_id,
            properties={
                "coupon_code": "INVALID20",
                "denial_reason": "not_found",
                "error_message": "Coupon code not found"
            }
        )
        assert coupon_deny == {"status": "success"}
        
        # Enter valid coupon
        valid_coupon = track_coupon_entered(
            client=mock_client,
            user_id=user_id,
            properties={"coupon_code": "VALID10", "cart_value": 100.00}
        )
        assert valid_coupon == {"status": "success"}
        
        # Apply valid coupon
        coupon_apply = track_coupon_applied(
            client=mock_client,
            user_id=user_id,
            properties={
                "coupon_code": "VALID10",
                "discount_amount": 10.00,
                "cart_value_after": 90.00
            }
        )
        assert coupon_apply == {"status": "success"}
        
        # User removes coupon to try another
        coupon_remove = track_coupon_removed(
            client=mock_client,
            user_id=user_id,
            properties={
                "coupon_code": "VALID10",
                "removal_reason": "user_action",
                "cart_value_after": 100.00
            }
        )
        assert coupon_remove == {"status": "success"}
        
        # Verify all coupon events were tracked
        assert mock_client.make_request.call_count == 5