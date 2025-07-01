"""
Integration tests for Customer.IO E-commerce Semantic Events API.

Tests real API interactions for:
- Product discovery events (search, click, list view)
- Promotional events (coupon, promotion interactions)
- Checkout and payment events
"""

import pytest
from datetime import datetime, timezone

from tests.integration.base import BaseIntegrationTest
from tests.integration.utils import generate_test_email
from utils.ecommerce_manager import (
    track_products_searched,
    track_product_clicked,
    track_product_list_viewed,
    track_checkout_step_viewed,
    track_checkout_step_completed,
    track_payment_info_entered,
    track_coupon_entered,
    track_coupon_applied,
    track_coupon_denied,
    track_promotion_viewed,
    track_promotion_clicked,
    track_product_added_to_wishlist,
    track_product_shared,
    track_product_reviewed
)
from utils.people_manager import identify_user
from utils.exceptions import CustomerIOError, ValidationError


@pytest.mark.integration
class TestEcommerceIntegration(BaseIntegrationTest):
    """Integration tests for e-commerce semantic events."""
    
    def test_track_products_searched(self, authenticated_client, test_user_id):
        """Test tracking product search events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("search"),
            "name": "Search Test User"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_products_searched(
            authenticated_client,
            test_user_id,
            {
                "query": "wireless headphones",
                "results_count": 24,
                "category": "electronics",
                "filters_applied": ["brand:sony", "price:under-200"],
                "sort_by": "price_low_to_high"
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_product_clicked(self, authenticated_client, test_user_id):
        """Test tracking product click events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("prodclick"),
            "name": "Product Click Test"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_product_clicked(
            authenticated_client,
            test_user_id,
            {
                "product_id": "PROD123",
                "sku": "WH-1000XM4",
                "name": "Sony WH-1000XM4 Headphones",
                "category": "Electronics > Audio > Headphones",
                "brand": "Sony",
                "price": 349.99,
                "currency": "USD",
                "position": 1
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_product_list_viewed(self, authenticated_client, test_user_id):
        """Test tracking product list view events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("listview"),
            "name": "List View Test"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_product_list_viewed(
            authenticated_client,
            test_user_id,
            {
                "list_id": "category_electronics",
                "category": "Electronics",
                "products": [
                    {
                        "product_id": "PROD123",
                        "name": "Sony Headphones",
                        "price": 349.99,
                        "position": 1
                    },
                    {
                        "product_id": "PROD456", 
                        "name": "Apple AirPods",
                        "price": 179.99,
                        "position": 2
                    }
                ],
                "sort_by": "popularity"
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_checkout_events(self, authenticated_client, test_user_id):
        """Test checkout event sequence."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("checkout"),
            "name": "Checkout Test User"
        })
        self.track_user(test_user_id)
        
        checkout_id = f"CHECKOUT_{int(datetime.now().timestamp())}"
        
        # Act & Assert - View checkout step
        view_result = track_checkout_step_viewed(
            authenticated_client,
            test_user_id,
            {
                "step": 1,
                "checkout_id": checkout_id,
                "step_name": "shipping_info"
            }
        )
        self.assert_successful_response(view_result)
        
        # Complete checkout step
        complete_result = track_checkout_step_completed(
            authenticated_client,
            test_user_id,
            {
                "step": 1,
                "checkout_id": checkout_id,
                "step_name": "shipping_info"
            }
        )
        self.assert_successful_response(complete_result)
        
        # Enter payment info
        payment_result = track_payment_info_entered(
            authenticated_client,
            test_user_id,
            {
                "checkout_id": checkout_id,
                "payment_method": "credit_card"
            }
        )
        self.assert_successful_response(payment_result)
    
    def test_track_coupon_events(self, authenticated_client, test_user_id):
        """Test coupon interaction events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("coupon"),
            "name": "Coupon Test User"
        })
        self.track_user(test_user_id)
        
        coupon_data = {
            "coupon_id": "SAVE20",
            "coupon_name": "20% Off Everything",
            "discount_type": "percentage",
            "discount_value": 20.0
        }
        
        # Act & Assert - Enter coupon
        enter_result = track_coupon_entered(
            authenticated_client,
            test_user_id,
            coupon_data
        )
        self.assert_successful_response(enter_result)
        
        # Apply coupon
        apply_result = track_coupon_applied(
            authenticated_client,
            test_user_id,
            {
                **coupon_data,
                "order_total": 100.00,
                "discount_amount": 20.00
            }
        )
        self.assert_successful_response(apply_result)
        
        # Test denied coupon
        deny_result = track_coupon_denied(
            authenticated_client,
            test_user_id,
            {
                "coupon_id": "EXPIRED10",
                "reason": "expired"
            }
        )
        self.assert_successful_response(deny_result)
    
    def test_track_promotion_events(self, authenticated_client, test_user_id):
        """Test promotion interaction events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("promo"),
            "name": "Promotion Test User"
        })
        self.track_user(test_user_id)
        
        promotion_data = {
            "promotion_id": "SUMMER2024",
            "promotion_name": "Summer Sale 2024",
            "creative": "banner_top",
            "position": "header"
        }
        
        # Act & Assert - View promotion
        view_result = track_promotion_viewed(
            authenticated_client,
            test_user_id,
            promotion_data
        )
        self.assert_successful_response(view_result)
        
        # Click promotion
        click_result = track_promotion_clicked(
            authenticated_client,
            test_user_id,
            promotion_data
        )
        self.assert_successful_response(click_result)
    
    def test_track_wishlist_events(self, authenticated_client, test_user_id):
        """Test wishlist interaction events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("wishlist"),
            "name": "Wishlist Test User"
        })
        self.track_user(test_user_id)
        
        # Act
        result = track_product_added_to_wishlist(
            authenticated_client,
            test_user_id,
            {
                "product_id": "WISH_PROD_123",
                "name": "Wishlist Product",
                "price": 299.99,
                "category": "Electronics"
            }
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_track_product_social_events(self, authenticated_client, test_user_id):
        """Test product social interaction events."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("social"),
            "name": "Social Test User"
        })
        self.track_user(test_user_id)
        
        # Act & Assert - Share product
        share_result = track_product_shared(
            authenticated_client,
            test_user_id,
            {
                "product_id": "SOCIAL_PROD_123",
                "name": "Shared Product",
                "share_via": "facebook",
                "share_message": "Check out this awesome product!"
            }
        )
        self.assert_successful_response(share_result)
        
        # Review product
        review_result = track_product_reviewed(
            authenticated_client,
            test_user_id,
            {
                "product_id": "SOCIAL_PROD_123",
                "review_id": f"REVIEW_{int(datetime.now().timestamp())}",
                "rating": 5,
                "review_body": "Great product, highly recommended!"
            }
        )
        self.assert_successful_response(review_result)
    
    def test_ecommerce_with_timestamps(self, authenticated_client, test_user_id):
        """Test e-commerce events with custom timestamps."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("timestamp"),
            "name": "Timestamp Test User"
        })
        self.track_user(test_user_id)
        
        custom_timestamp = datetime.now(timezone.utc)
        
        # Act
        result = track_product_clicked(
            authenticated_client,
            test_user_id,
            {
                "product_id": "HIST_PROD_123",
                "name": "Historical Product Click",
                "price": 199.99
            },
            timestamp=custom_timestamp
        )
        
        # Assert
        self.assert_successful_response(result)
    
    def test_ecommerce_validation_errors(self, authenticated_client):
        """Test e-commerce event validation."""
        # Test empty user ID
        with pytest.raises(ValidationError):
            track_product_clicked(authenticated_client, "", {"product_id": "test"})
    
    def test_complex_ecommerce_journey(self, authenticated_client, test_user_id):
        """Test a complex e-commerce user journey."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("journey"),
            "name": "Journey Test User"
        })
        self.track_user(test_user_id)
        
        # Journey: Search -> List -> Click -> Wishlist -> Checkout
        journey_events = [
            ("search", lambda: track_products_searched(
                authenticated_client, test_user_id, 
                {"query": "laptop", "results_count": 15}
            )),
            ("list_view", lambda: track_product_list_viewed(
                authenticated_client, test_user_id,
                {
                    "list_id": "search_results",
                    "category": "Computers",
                    "products": [{"product_id": "LAPTOP_001", "position": 1}]
                }
            )),
            ("click_product", lambda: track_product_clicked(
                authenticated_client, test_user_id,
                {
                    "product_id": "LAPTOP_001",
                    "name": "Professional Laptop",
                    "price": 1299.99,
                    "position": 1
                }
            )),
            ("add_to_wishlist", lambda: track_product_added_to_wishlist(
                authenticated_client, test_user_id,
                {
                    "product_id": "LAPTOP_001",
                    "name": "Professional Laptop", 
                    "price": 1299.99
                }
            )),
            ("view_checkout", lambda: track_checkout_step_viewed(
                authenticated_client, test_user_id,
                {
                    "step": 1,
                    "checkout_id": f"JOURNEY_{int(datetime.now().timestamp())}",
                    "step_name": "review"
                }
            ))
        ]
        
        # Execute journey with delays for rate limiting
        for step_name, event_func in journey_events:
            result = event_func()
            self.assert_successful_response(result)
            self.wait_for_eventual_consistency(0.2)
    
    @pytest.mark.slow
    def test_high_volume_ecommerce_events(self, authenticated_client, test_user_id):
        """Test tracking multiple e-commerce events for load testing."""
        # Arrange
        identify_user(authenticated_client, test_user_id, {
            "email": generate_test_email("volume"),
            "name": "Volume Test User"
        })
        self.track_user(test_user_id)
        
        # Act - Track 15 product clicks with rate limiting
        for i in range(15):
            result = track_product_clicked(
                authenticated_client,
                test_user_id,
                {
                    "product_id": f"VOLUME_PROD_{i}",
                    "name": f"Volume Test Product {i}",
                    "price": 99.99 + i,
                    "position": i + 1
                }
            )
            self.assert_successful_response(result)
            
            # Rate limiting
            if i % 5 == 0:
                self.wait_for_eventual_consistency(0.2)