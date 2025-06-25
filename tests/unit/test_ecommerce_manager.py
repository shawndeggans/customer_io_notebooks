"""
Comprehensive tests for Customer.IO Ecommerce Manager.

Tests cover:
- Product categories, order statuses, payment methods, and customer segments enumerations
- Data model validation (Product, CartItem, ShoppingCart, Order)
- Product event tracking (views, searches)
- Shopping cart management (add items, abandonment)
- Order processing (checkout, completion)
- Customer lifetime value calculation and segmentation
- Ecommerce analytics and performance metrics
- Event batch processing and error handling
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
from pydantic import ValidationError

from utils.ecommerce_manager import (
    ProductCategory,
    OrderStatus,
    PaymentMethod,
    PromotionType,
    CustomerSegment,
    Product,
    CartItem,
    ShoppingCart,
    Order,
    EcommerceManager
)
from utils.event_manager import EventManager
from utils.error_handlers import CustomerIOError


class TestProductCategory:
    """Test ProductCategory enum."""
    
    def test_product_category_values(self):
        """Test all product category values."""
        assert ProductCategory.ELECTRONICS == "electronics"
        assert ProductCategory.CLOTHING == "clothing"
        assert ProductCategory.HOME_GARDEN == "home_garden"
        assert ProductCategory.HEALTH_BEAUTY == "health_beauty"
        assert ProductCategory.SPORTS_OUTDOORS == "sports_outdoors"
        assert ProductCategory.BOOKS_MEDIA == "books_media"
        assert ProductCategory.AUTOMOTIVE == "automotive"
        assert ProductCategory.FOOD_BEVERAGE == "food_beverage"
        assert ProductCategory.TOYS_GAMES == "toys_games"
        assert ProductCategory.CUSTOM == "custom"
    
    def test_product_category_membership(self):
        """Test product category membership."""
        valid_categories = [category.value for category in ProductCategory]
        assert "electronics" in valid_categories
        assert "invalid_category" not in valid_categories


class TestOrderStatus:
    """Test OrderStatus enum."""
    
    def test_order_status_values(self):
        """Test all order status values."""
        assert OrderStatus.PENDING == "pending"
        assert OrderStatus.CONFIRMED == "confirmed"
        assert OrderStatus.PROCESSING == "processing"
        assert OrderStatus.SHIPPED == "shipped"
        assert OrderStatus.DELIVERED == "delivered"
        assert OrderStatus.COMPLETED == "completed"
        assert OrderStatus.CANCELLED == "cancelled"
        assert OrderStatus.REFUNDED == "refunded"
        assert OrderStatus.RETURNED == "returned"
    
    def test_order_status_membership(self):
        """Test order status membership."""
        valid_statuses = [status.value for status in OrderStatus]
        assert "pending" in valid_statuses
        assert "invalid_status" not in valid_statuses


class TestPaymentMethod:
    """Test PaymentMethod enum."""
    
    def test_payment_method_values(self):
        """Test all payment method values."""
        assert PaymentMethod.CREDIT_CARD == "credit_card"
        assert PaymentMethod.DEBIT_CARD == "debit_card"
        assert PaymentMethod.PAYPAL == "paypal"
        assert PaymentMethod.APPLE_PAY == "apple_pay"
        assert PaymentMethod.GOOGLE_PAY == "google_pay"
        assert PaymentMethod.BANK_TRANSFER == "bank_transfer"
        assert PaymentMethod.CASH_ON_DELIVERY == "cash_on_delivery"
        assert PaymentMethod.CRYPTOCURRENCY == "cryptocurrency"
        assert PaymentMethod.GIFT_CARD == "gift_card"
        assert PaymentMethod.STORE_CREDIT == "store_credit"


class TestCustomerSegment:
    """Test CustomerSegment enum."""
    
    def test_customer_segment_values(self):
        """Test all customer segment values."""
        assert CustomerSegment.NEW_CUSTOMER == "new_customer"
        assert CustomerSegment.RETURNING_CUSTOMER == "returning_customer"
        assert CustomerSegment.VIP_CUSTOMER == "vip_customer"
        assert CustomerSegment.HIGH_VALUE == "high_value"
        assert CustomerSegment.FREQUENT_BUYER == "frequent_buyer"
        assert CustomerSegment.DORMANT == "dormant"
        assert CustomerSegment.AT_RISK == "at_risk"
        assert CustomerSegment.LOYAL == "loyal"


class TestProduct:
    """Test Product data model."""
    
    def test_valid_product(self):
        """Test valid product creation."""
        product = Product(
            product_id="prod_123",
            name="Wireless Headphones",
            category=ProductCategory.ELECTRONICS,
            subcategory="Audio",
            brand="TechBrand",
            price=Decimal("199.99"),
            currency="USD",
            sku="TB-WH-001",
            description="Premium wireless headphones",
            stock_quantity=50,
            rating=4.5,
            reviews_count=128,
            tags=["wireless", "bluetooth", "premium"]
        )
        
        assert product.product_id == "prod_123"
        assert product.name == "Wireless Headphones"
        assert product.category == ProductCategory.ELECTRONICS
        assert product.price == Decimal("199.99")
        assert product.currency == "USD"
        assert product.rating == 4.5
        assert "wireless" in product.tags
    
    def test_product_id_validation(self):
        """Test product ID validation."""
        with pytest.raises(ValidationError):
            Product(
                product_id="",
                name="Test Product",
                category=ProductCategory.ELECTRONICS,
                price=Decimal("99.99")
            )
        
        with pytest.raises(ValidationError):
            Product(
                product_id="   ",
                name="Test Product",
                category=ProductCategory.ELECTRONICS,
                price=Decimal("99.99")
            )
    
    def test_currency_validation(self):
        """Test currency format validation."""
        with pytest.raises(ValidationError):
            Product(
                product_id="prod_123",
                name="Test Product",
                category=ProductCategory.ELECTRONICS,
                price=Decimal("99.99"),
                currency="usd"  # Should be uppercase
            )
        
        with pytest.raises(ValidationError):
            Product(
                product_id="prod_123",
                name="Test Product",
                category=ProductCategory.ELECTRONICS,
                price=Decimal("99.99"),
                currency="DOLLAR"  # Should be 3 letters
            )
    
    def test_price_validation(self):
        """Test price validation."""
        with pytest.raises(ValidationError):
            Product(
                product_id="prod_123",
                name="Test Product",
                category=ProductCategory.ELECTRONICS,
                price=Decimal("0")  # Must be greater than 0
            )
        
        with pytest.raises(ValidationError):
            Product(
                product_id="prod_123",
                name="Test Product",
                category=ProductCategory.ELECTRONICS,
                price=Decimal("-10.99")  # Must be positive
            )


class TestCartItem:
    """Test CartItem data model."""
    
    def test_valid_cart_item(self):
        """Test valid cart item creation."""
        item = CartItem(
            product_id="prod_123",
            variant_id="var_456",
            quantity=2,
            unit_price=Decimal("199.99"),
            total_price=Decimal("399.98"),
            currency="USD"
        )
        
        assert item.product_id == "prod_123"
        assert item.variant_id == "var_456"
        assert item.quantity == 2
        assert item.total_price == Decimal("399.98")
    
    def test_cart_item_total_validation(self):
        """Test cart item total price validation."""
        with pytest.raises(ValidationError):
            CartItem(
                product_id="prod_123",
                quantity=2,
                unit_price=Decimal("199.99"),
                total_price=Decimal("300.00")  # Incorrect total
            )
    
    def test_cart_item_with_discount(self):
        """Test cart item with discount applied."""
        item = CartItem(
            product_id="prod_123",
            quantity=2,
            unit_price=Decimal("199.99"),
            total_price=Decimal("379.98"),  # 399.98 - 20.00 discount
            discount_amount=Decimal("20.00")
        )
        
        assert item.total_price == Decimal("379.98")
        assert item.discount_amount == Decimal("20.00")


class TestShoppingCart:
    """Test ShoppingCart data model."""
    
    def test_valid_shopping_cart(self):
        """Test valid shopping cart creation."""
        cart = ShoppingCart(
            cart_id="cart_123",
            user_id="user_456",
            session_id="session_789"
        )
        
        assert cart.cart_id == "cart_123"
        assert cart.user_id == "user_456"
        assert cart.session_id == "session_789"
        assert len(cart.items) == 0
        assert cart.total_amount == Decimal("0")
    
    def test_cart_id_validation(self):
        """Test cart ID validation."""
        with pytest.raises(ValidationError):
            ShoppingCart(
                cart_id="",
                user_id="user_456"
            )
    
    def test_add_item_to_cart(self):
        """Test adding item to cart."""
        cart = ShoppingCart(
            cart_id="cart_123",
            user_id="user_456"
        )
        
        item = CartItem(
            product_id="prod_123",
            quantity=1,
            unit_price=Decimal("199.99"),
            total_price=Decimal("199.99")
        )
        
        cart.add_item(item)
        
        assert len(cart.items) == 1
        assert cart.get_item_count() == 1
        assert cart.subtotal == Decimal("199.99")
    
    def test_add_existing_item_to_cart(self):
        """Test adding existing item to cart (should update quantity)."""
        cart = ShoppingCart(
            cart_id="cart_123",
            user_id="user_456"
        )
        
        item1 = CartItem(
            product_id="prod_123",
            quantity=1,
            unit_price=Decimal("199.99"),
            total_price=Decimal("199.99")
        )
        
        item2 = CartItem(
            product_id="prod_123",
            quantity=2,
            unit_price=Decimal("199.99"),
            total_price=Decimal("399.98")
        )
        
        cart.add_item(item1)
        cart.add_item(item2)
        
        assert len(cart.items) == 1  # Should still be 1 item
        assert cart.items[0].quantity == 3  # Quantities should be combined
        assert cart.get_item_count() == 3
    
    def test_remove_item_from_cart(self):
        """Test removing item from cart."""
        cart = ShoppingCart(
            cart_id="cart_123",
            user_id="user_456"
        )
        
        item = CartItem(
            product_id="prod_123",
            quantity=1,
            unit_price=Decimal("199.99"),
            total_price=Decimal("199.99")
        )
        
        cart.add_item(item)
        assert len(cart.items) == 1
        
        removed = cart.remove_item("prod_123")
        assert removed is True
        assert len(cart.items) == 0
        assert cart.total_amount == Decimal("0")
    
    def test_calculate_totals(self):
        """Test cart totals calculation."""
        cart = ShoppingCart(
            cart_id="cart_123",
            user_id="user_456",
            tax_amount=Decimal("16.00"),
            shipping_amount=Decimal("9.99"),
            discount_amount=Decimal("10.00")
        )
        
        item = CartItem(
            product_id="prod_123",
            quantity=1,
            unit_price=Decimal("199.99"),
            total_price=Decimal("199.99")
        )
        
        cart.add_item(item)
        
        # Should be: 199.99 + 16.00 + 9.99 - 10.00 = 215.98
        assert cart.total_amount == Decimal("215.98")


class TestOrder:
    """Test Order data model."""
    
    def test_valid_order(self):
        """Test valid order creation."""
        item = CartItem(
            product_id="prod_123",
            quantity=1,
            unit_price=Decimal("199.99"),
            total_price=Decimal("199.99")
        )
        
        order = Order(
            order_id="order_123",
            customer_id="customer_456",
            items=[item],
            subtotal=Decimal("199.99"),
            tax_amount=Decimal("16.00"),
            shipping_amount=Decimal("9.99"),
            total_amount=Decimal("225.98"),
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        assert order.order_id == "order_123"
        assert order.customer_id == "customer_456"
        assert len(order.items) == 1
        assert order.total_amount == Decimal("225.98")
        assert order.payment_method == PaymentMethod.CREDIT_CARD
    
    def test_order_without_items(self):
        """Test order validation without items."""
        with pytest.raises(ValidationError):
            Order(
                order_id="order_123",
                customer_id="customer_456",
                items=[],  # Empty items list
                subtotal=Decimal("0"),
                total_amount=Decimal("0"),
                payment_method=PaymentMethod.CREDIT_CARD
            )
    
    def test_order_total_validation(self):
        """Test order total amount validation."""
        item = CartItem(
            product_id="prod_123",
            quantity=1,
            unit_price=Decimal("199.99"),
            total_price=Decimal("199.99")
        )
        
        with pytest.raises(ValidationError):
            Order(
                order_id="order_123",
                customer_id="customer_456",
                items=[item],
                subtotal=Decimal("199.99"),
                tax_amount=Decimal("16.00"),
                shipping_amount=Decimal("9.99"),
                total_amount=Decimal("200.00")  # Incorrect total
            )


class TestEcommerceManager:
    """Test EcommerceManager operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        client = Mock()
        client.batch.return_value = {"success": True}
        return client
    
    @pytest.fixture
    def mock_event_manager(self, mock_client):
        """Create mock event manager."""
        return Mock(spec=EventManager)
    
    @pytest.fixture
    def ecommerce_manager(self, mock_client, mock_event_manager):
        """Create EcommerceManager instance."""
        return EcommerceManager(mock_client, mock_event_manager)
    
    @pytest.fixture
    def sample_product(self):
        """Create sample product."""
        return Product(
            product_id="prod_test_001",
            name="Test Wireless Headphones",
            category=ProductCategory.ELECTRONICS,
            subcategory="Audio",
            brand="TestBrand",
            price=Decimal("299.99"),
            currency="USD",
            sku="TB-WH-001",
            rating=4.5,
            reviews_count=100,
            tags=["wireless", "premium"]
        )
    
    @pytest.fixture
    def sample_cart(self):
        """Create sample shopping cart."""
        return ShoppingCart(
            cart_id="cart_test_001",
            user_id="user_test_001",
            session_id="session_test_001"
        )
    
    def test_track_product_view(self, ecommerce_manager, sample_product):
        """Test product view tracking."""
        event = ecommerce_manager.track_product_view(
            user_id="user_test_001",
            product=sample_product,
            context={"source": "search_results", "position": 3}
        )
        
        assert event["userId"] == "user_test_001"
        assert event["event"] == "Product Viewed"
        assert event["properties"]["product_id"] == "prod_test_001"
        assert event["properties"]["product_name"] == "Test Wireless Headphones"
        assert event["properties"]["category"] == "electronics"
        assert event["properties"]["price"] == 299.99
        assert event["context"]["source"] == "search_results"
    
    def test_track_product_search(self, ecommerce_manager):
        """Test product search tracking."""
        event = ecommerce_manager.track_product_search(
            user_id="user_test_001",
            search_query="wireless headphones",
            results_count=25,
            filters={"category": "electronics", "price_range": "200-500"},
            sort_by="price_low_to_high"
        )
        
        assert event["userId"] == "user_test_001"
        assert event["event"] == "Products Searched"
        assert event["properties"]["search_query"] == "wireless headphones"
        assert event["properties"]["results_count"] == 25
        assert event["properties"]["has_results"] is True
        assert event["properties"]["filters_applied"]["category"] == "electronics"
    
    def test_track_add_to_cart(self, ecommerce_manager, sample_product, sample_cart):
        """Test add to cart tracking."""
        event, updated_cart = ecommerce_manager.track_add_to_cart(
            user_id="user_test_001",
            cart=sample_cart,
            product=sample_product,
            quantity=2
        )
        
        assert event["userId"] == "user_test_001"
        assert event["event"] == "Product Added to Cart"
        assert event["properties"]["product_id"] == "prod_test_001"
        assert event["properties"]["quantity"] == 2
        assert event["properties"]["unit_price"] == 299.99
        assert event["properties"]["cart_total_items"] == 2
        
        # Check cart state
        assert len(updated_cart.items) == 1
        assert updated_cart.items[0].quantity == 2
        assert updated_cart.get_item_count() == 2
    
    def test_track_cart_abandonment(self, ecommerce_manager, sample_cart):
        """Test cart abandonment tracking."""
        # Add item to cart first
        item = CartItem(
            product_id="prod_test_001",
            quantity=1,
            unit_price=Decimal("299.99"),
            total_price=Decimal("299.99")
        )
        sample_cart.add_item(item)
        
        event = ecommerce_manager.track_cart_abandonment(
            user_id="user_test_001",
            cart=sample_cart,
            abandonment_reason="session_timeout"
        )
        
        assert event["userId"] == "user_test_001"
        assert event["event"] == "Cart Abandoned"
        assert event["properties"]["cart_id"] == "cart_test_001"
        assert event["properties"]["total_items"] == 1
        assert event["properties"]["abandonment_reason"] == "session_timeout"
        assert sample_cart.abandoned_at is not None
    
    def test_track_checkout_started(self, ecommerce_manager, sample_cart):
        """Test checkout started tracking."""
        # Add item to cart
        item = CartItem(
            product_id="prod_test_001",
            quantity=1,
            unit_price=Decimal("299.99"),
            total_price=Decimal("299.99")
        )
        sample_cart.add_item(item)
        sample_cart.tax_amount = Decimal("24.00")
        sample_cart.shipping_amount = Decimal("9.99")
        sample_cart.calculate_totals()
        
        event = ecommerce_manager.track_checkout_started(
            user_id="user_test_001",
            cart=sample_cart,
            checkout_step="payment_info"
        )
        
        assert event["userId"] == "user_test_001"
        assert event["event"] == "Checkout Started"
        assert event["properties"]["checkout_step"] == "payment_info"
        assert event["properties"]["total_items"] == 1
        assert event["properties"]["total_amount"] == 333.98  # 299.99 + 24.00 + 9.99
    
    def test_track_order_completed(self, ecommerce_manager):
        """Test order completion tracking."""
        item = CartItem(
            product_id="prod_test_001",
            quantity=1,
            unit_price=Decimal("299.99"),
            total_price=Decimal("299.99")
        )
        
        order = Order(
            order_id="order_test_001",
            customer_id="customer_test_001",
            items=[item],
            subtotal=Decimal("299.99"),
            tax_amount=Decimal("24.00"),
            shipping_amount=Decimal("9.99"),
            total_amount=Decimal("333.98"),
            payment_method=PaymentMethod.CREDIT_CARD,
            payment_status="completed"
        )
        
        event = ecommerce_manager.track_order_completed(order)
        
        assert event["userId"] == "customer_test_001"
        assert event["event"] == "Order Completed"
        assert event["properties"]["order_id"] == "order_test_001"
        assert event["properties"]["total_amount"] == 333.98
        assert event["properties"]["payment_method"] == "credit_card"
        assert order.status == OrderStatus.COMPLETED
        assert order.completed_at is not None
    
    def test_calculate_customer_lifetime_value_new_customer(self, ecommerce_manager):
        """Test CLV calculation for new customer."""
        clv = ecommerce_manager.calculate_customer_lifetime_value(
            customer_id="customer_new_001",
            orders=[],
            lookback_days=365
        )
        
        assert clv["customer_id"] == "customer_new_001"
        assert clv["total_orders"] == 0
        assert clv["total_revenue"] == 0.0
        assert clv["customer_segment"] == CustomerSegment.NEW_CUSTOMER
    
    def test_calculate_customer_lifetime_value_existing_customer(self, ecommerce_manager):
        """Test CLV calculation for existing customer."""
        # Create sample orders
        item1 = CartItem(
            product_id="prod_001",
            quantity=1,
            unit_price=Decimal("299.99"),
            total_price=Decimal("299.99")
        )
        
        item2 = CartItem(
            product_id="prod_002",
            quantity=2,
            unit_price=Decimal("150.00"),
            total_price=Decimal("300.00")
        )
        
        order1 = Order(
            order_id="order_001",
            customer_id="customer_existing_001",
            items=[item1],
            subtotal=Decimal("299.99"),
            total_amount=Decimal("299.99"),
            payment_method=PaymentMethod.CREDIT_CARD,
            status=OrderStatus.COMPLETED,
            created_at=datetime.now(timezone.utc) - timedelta(days=30)
        )
        
        order2 = Order(
            order_id="order_002",
            customer_id="customer_existing_001",
            items=[item2],
            subtotal=Decimal("300.00"),
            total_amount=Decimal("300.00"),
            payment_method=PaymentMethod.PAYPAL,
            status=OrderStatus.COMPLETED,
            created_at=datetime.now(timezone.utc) - timedelta(days=15)
        )
        
        clv = ecommerce_manager.calculate_customer_lifetime_value(
            customer_id="customer_existing_001",
            orders=[order1, order2],
            lookback_days=365
        )
        
        assert clv["customer_id"] == "customer_existing_001"
        assert clv["total_orders"] == 2
        assert clv["total_revenue"] == 599.99
        assert clv["average_order_value"] == 299.995
        assert clv["unique_products_purchased"] == 2
        assert clv["customer_segment"] == CustomerSegment.RETURNING_CUSTOMER
    
    def test_track_customer_segment_change(self, ecommerce_manager):
        """Test customer segment change tracking."""
        clv_data = {
            "total_orders": 3,
            "total_revenue": 899.97,
            "average_order_value": 299.99
        }
        
        event = ecommerce_manager.track_customer_segment_change(
            customer_id="customer_test_001",
            old_segment=CustomerSegment.RETURNING_CUSTOMER,
            new_segment=CustomerSegment.HIGH_VALUE,
            trigger_event="order_completed",
            clv_data=clv_data
        )
        
        assert event["userId"] == "customer_test_001"
        assert event["event"] == "Customer Segment Changed"
        assert event["properties"]["previous_segment"] == CustomerSegment.RETURNING_CUSTOMER
        assert event["properties"]["new_segment"] == CustomerSegment.HIGH_VALUE
        assert event["properties"]["trigger_event"] == "order_completed"
        assert event["properties"]["total_orders"] == 3
    
    def test_calculate_ecommerce_metrics(self, ecommerce_manager):
        """Test ecommerce metrics calculation."""
        # Create sample events
        now = datetime.now(timezone.utc)
        events = [
            {
                "event": "Product Viewed",
                "properties": {"product_id": "prod_001"},
                "timestamp": now - timedelta(hours=1)
            },
            {
                "event": "Product Viewed",
                "properties": {"product_id": "prod_002"},
                "timestamp": now - timedelta(hours=2)
            },
            {
                "event": "Product Added to Cart",
                "properties": {"product_id": "prod_001"},
                "timestamp": now - timedelta(hours=1)
            },
            {
                "event": "Checkout Started",
                "properties": {"product_id": "prod_001"},
                "timestamp": now - timedelta(minutes=30)
            },
            {
                "event": "Order Completed",
                "properties": {"product_id": "prod_001", "price": 299.99, "quantity": 1},
                "timestamp": now - timedelta(minutes=15)
            }
        ]
        
        metrics = ecommerce_manager.calculate_ecommerce_metrics(
            events=events,
            time_period_days=1
        )
        
        assert metrics["total_events"] == 5
        assert metrics["funnel_metrics"]["product_views"] == 2
        assert metrics["funnel_metrics"]["add_to_carts"] == 1
        assert metrics["funnel_metrics"]["checkouts_started"] == 1
        assert metrics["funnel_metrics"]["orders_completed"] == 1
        assert metrics["conversion_rates"]["view_to_cart_rate"] == 50.0  # 1/2 * 100
        assert metrics["conversion_rates"]["overall_conversion_rate"] == 50.0  # 1/2 * 100
        assert metrics["revenue_metrics"]["total_revenue"] == 299.99
        assert metrics["revenue_metrics"]["total_orders"] == 1
    
    def test_send_ecommerce_events_test_mode(self, ecommerce_manager):
        """Test sending ecommerce events in test mode."""
        events = [
            {
                "userId": "user_001",
                "event": "Product Viewed",
                "properties": {"product_id": "prod_001"},
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "userId": "user_001",
                "event": "Product Added to Cart",
                "properties": {"product_id": "prod_001"},
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        results = ecommerce_manager.send_ecommerce_events(
            events=events,
            test_mode=True
        )
        
        assert len(results) == 1  # Should be 1 batch
        assert results[0]["status"] == "test_success"
        assert results[0]["count"] == 2
    
    @patch('utils.ecommerce_manager.BatchTransformer.optimize_batch_sizes')
    def test_send_ecommerce_events_production_mode(self, mock_optimize, ecommerce_manager, mock_client):
        """Test sending ecommerce events in production mode."""
        mock_optimize.return_value = [[{"type": "track", "userId": "user_001", "event": "test"}]]
        mock_client.batch.return_value = {"success": True}
        
        events = [
            {
                "userId": "user_001",
                "event": "Product Viewed",
                "properties": {"product_id": "prod_001"},
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        results = ecommerce_manager.send_ecommerce_events(
            events=events,
            test_mode=False
        )
        
        assert len(results) == 1
        assert results[0]["status"] == "success"
        mock_client.batch.assert_called_once()
    
    def test_send_ecommerce_events_batch_failure(self, ecommerce_manager, mock_client):
        """Test handling of batch failures."""
        mock_client.batch.side_effect = Exception("API Error")
        
        events = [
            {
                "userId": "user_001",
                "event": "Product Viewed",
                "properties": {"product_id": "prod_001"},
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        results = ecommerce_manager.send_ecommerce_events(
            events=events,
            test_mode=False
        )
        
        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "API Error" in results[0]["error"]
    
    def test_get_metrics(self, ecommerce_manager, mock_client, mock_event_manager):
        """Test metrics retrieval."""
        mock_client.base_url = "https://track.customer.io"
        mock_client.region = "us"
        mock_client.timeout = 30
        mock_client.max_retries = 3
        mock_event_manager.templates = {"template1": {}, "template2": {}}
        
        metrics = ecommerce_manager.get_metrics()
        
        assert metrics["client"]["base_url"] == "https://track.customer.io"
        assert metrics["client"]["region"] == "us"
        assert metrics["event_manager"]["templates_registered"] == 2
        assert "product_categories" in metrics["supported_features"]
        assert "order_statuses" in metrics["supported_features"]
        assert "payment_methods" in metrics["supported_features"]
        assert "customer_segments" in metrics["supported_features"]
        assert "avg_product_view_time_ms" in metrics["performance"]


class TestEcommerceManagerIntegration:
    """Integration tests for EcommerceManager."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        client = Mock()
        client.batch.return_value = {"success": True}
        return client
    
    @pytest.fixture
    def ecommerce_manager(self, mock_client):
        """Create EcommerceManager instance."""
        return EcommerceManager(mock_client)
    
    def test_complete_ecommerce_flow(self, ecommerce_manager):
        """Test complete ecommerce flow from product view to order completion."""
        user_id = "user_integration_001"
        
        # 1. Create product
        product = Product(
            product_id="prod_integration_001",
            name="Integration Test Product",
            category=ProductCategory.ELECTRONICS,
            price=Decimal("199.99"),
            currency="USD"
        )
        
        # 2. Track product view
        view_event = ecommerce_manager.track_product_view(
            user_id=user_id,
            product=product
        )
        assert view_event["event"] == "Product Viewed"
        
        # 3. Create cart and add product
        cart = ShoppingCart(
            cart_id="cart_integration_001",
            user_id=user_id
        )
        
        add_event, updated_cart = ecommerce_manager.track_add_to_cart(
            user_id=user_id,
            cart=cart,
            product=product,
            quantity=1
        )
        assert add_event["event"] == "Product Added to Cart"
        assert len(updated_cart.items) == 1
        
        # 4. Start checkout
        checkout_event = ecommerce_manager.track_checkout_started(
            user_id=user_id,
            cart=updated_cart
        )
        assert checkout_event["event"] == "Checkout Started"
        
        # 5. Complete order
        order = Order(
            order_id="order_integration_001",
            customer_id=user_id,
            items=updated_cart.items,
            subtotal=updated_cart.subtotal,
            total_amount=updated_cart.total_amount,
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        completion_event = ecommerce_manager.track_order_completed(order)
        assert completion_event["event"] == "Order Completed"
        assert order.status == OrderStatus.COMPLETED
        
        # 6. Calculate CLV
        clv = ecommerce_manager.calculate_customer_lifetime_value(
            customer_id=user_id,
            orders=[order]
        )
        assert clv["total_orders"] == 1
        assert clv["customer_segment"] == CustomerSegment.NEW_CUSTOMER
        
        # 7. Calculate metrics
        all_events = [view_event, add_event, checkout_event, completion_event]
        metrics = ecommerce_manager.calculate_ecommerce_metrics(all_events)
        assert metrics["funnel_metrics"]["product_views"] == 1
        assert metrics["funnel_metrics"]["orders_completed"] == 1
        assert metrics["conversion_rates"]["overall_conversion_rate"] == 100.0
    
    def test_cart_abandonment_flow(self, ecommerce_manager):
        """Test cart abandonment flow."""
        user_id = "user_abandonment_001"
        
        # Create product and cart
        product = Product(
            product_id="prod_abandonment_001",
            name="Abandonment Test Product",
            category=ProductCategory.ELECTRONICS,
            price=Decimal("299.99"),
            currency="USD"
        )
        
        cart = ShoppingCart(
            cart_id="cart_abandonment_001",
            user_id=user_id
        )
        
        # Add product to cart
        add_event, updated_cart = ecommerce_manager.track_add_to_cart(
            user_id=user_id,
            cart=cart,
            product=product
        )
        
        # Track abandonment
        abandonment_event = ecommerce_manager.track_cart_abandonment(
            user_id=user_id,
            cart=updated_cart,
            abandonment_reason="price_sensitivity"
        )
        
        assert abandonment_event["event"] == "Cart Abandoned"
        assert abandonment_event["properties"]["abandonment_reason"] == "price_sensitivity"
        assert updated_cart.abandoned_at is not None
    
    def test_customer_segmentation_progression(self, ecommerce_manager):
        """Test customer segment progression through multiple orders."""
        customer_id = "customer_progression_001"
        
        # Create multiple orders over time
        orders = []
        for i in range(6):  # Create 6 orders to trigger frequent buyer segment
            item = CartItem(
                product_id=f"prod_{i}",
                quantity=1,
                unit_price=Decimal("150.00"),
                total_price=Decimal("150.00")
            )
            
            order = Order(
                order_id=f"order_{i}",
                customer_id=customer_id,
                items=[item],
                subtotal=Decimal("150.00"),
                total_amount=Decimal("150.00"),
                payment_method=PaymentMethod.CREDIT_CARD,
                status=OrderStatus.COMPLETED,
                created_at=datetime.now(timezone.utc) - timedelta(days=30-i*5)
            )
            orders.append(order)
        
        # Calculate CLV
        clv = ecommerce_manager.calculate_customer_lifetime_value(
            customer_id=customer_id,
            orders=orders
        )
        
        assert clv["total_orders"] == 6
        assert clv["total_revenue"] == 900.0  # 6 * 150
        assert clv["customer_segment"] == CustomerSegment.FREQUENT_BUYER
        assert clv["unique_products_purchased"] == 6
        
        # Track segment change
        segment_event = ecommerce_manager.track_customer_segment_change(
            customer_id=customer_id,
            old_segment=CustomerSegment.RETURNING_CUSTOMER,
            new_segment=CustomerSegment.FREQUENT_BUYER,
            trigger_event="order_completed",
            clv_data=clv
        )
        
        assert segment_event["event"] == "Customer Segment Changed"
        assert segment_event["properties"]["new_segment"] == CustomerSegment.FREQUENT_BUYER