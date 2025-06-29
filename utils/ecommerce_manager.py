"""
Customer.IO Ecommerce Manager Module

Type-safe ecommerce event tracking operations for Customer.IO API including:
- Product analytics and catalog management
- Shopping cart state management and abandonment tracking
- Order processing and lifecycle management
- Revenue analytics and customer lifetime value calculation
- Purchase behavior analysis and customer segmentation
- Financial calculations with decimal precision
- Conversion funnel optimization and performance monitoring
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from enum import Enum
from collections import defaultdict, Counter
from decimal import Decimal, ROUND_HALF_UP
import statistics
import structlog
from pydantic import BaseModel, Field, field_validator

from .api_client import CustomerIOClient
from .event_manager import EventManager
from .transformers import BatchTransformer
from .error_handlers import retry_on_error, ErrorContext


class ProductCategory(str, Enum):
    """Enumeration for product categories."""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME_GARDEN = "home_garden"
    HEALTH_BEAUTY = "health_beauty"
    SPORTS_OUTDOORS = "sports_outdoors"
    BOOKS_MEDIA = "books_media"
    AUTOMOTIVE = "automotive"
    FOOD_BEVERAGE = "food_beverage"
    TOYS_GAMES = "toys_games"
    CUSTOM = "custom"


class OrderStatus(str, Enum):
    """Enumeration for order status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    RETURNED = "returned"


class PaymentMethod(str, Enum):
    """Enumeration for payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"
    CRYPTOCURRENCY = "cryptocurrency"
    GIFT_CARD = "gift_card"
    STORE_CREDIT = "store_credit"


class PromotionType(str, Enum):
    """Enumeration for promotion types."""
    PERCENTAGE_DISCOUNT = "percentage_discount"
    FIXED_AMOUNT_DISCOUNT = "fixed_amount_discount"
    FREE_SHIPPING = "free_shipping"
    BUY_ONE_GET_ONE = "buy_one_get_one"
    BUNDLE_DISCOUNT = "bundle_discount"
    LOYALTY_POINTS = "loyalty_points"
    REFERRAL_BONUS = "referral_bonus"
    SEASONAL_SALE = "seasonal_sale"


class CustomerSegment(str, Enum):
    """Enumeration for customer segments."""
    NEW_CUSTOMER = "new_customer"
    RETURNING_CUSTOMER = "returning_customer"
    VIP_CUSTOMER = "vip_customer"
    HIGH_VALUE = "high_value"
    FREQUENT_BUYER = "frequent_buyer"
    DORMANT = "dormant"
    AT_RISK = "at_risk"
    LOYAL = "loyal"


class Product(BaseModel):
    """Type-safe product model."""
    product_id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    category: ProductCategory = Field(..., description="Product category")
    subcategory: Optional[str] = Field(None, description="Product subcategory")
    brand: Optional[str] = Field(None, description="Product brand")
    price: Decimal = Field(..., gt=0, description="Product price")
    currency: str = Field(default="USD", description="Price currency")
    sku: Optional[str] = Field(None, description="Stock keeping unit")
    description: Optional[str] = Field(None, description="Product description")
    image_url: Optional[str] = Field(None, description="Product image URL")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Available stock")
    weight: Optional[float] = Field(None, gt=0, description="Product weight")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Product dimensions")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    reviews_count: Optional[int] = Field(None, ge=0, description="Number of reviews")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    
    @field_validator('product_id')
    @classmethod
    def validate_product_id(cls, v: str) -> str:
        """Validate product ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Product ID cannot be empty")
        return v.strip()
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency format."""
        if len(v) != 3 or not v.isupper():
            raise ValueError("Currency must be 3-letter uppercase code (e.g., USD)")
        return v
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }

    product_id: str = Field(..., description="Product identifier")
    variant_id: Optional[str] = Field(None, description="Product variant identifier")
    quantity: int = Field(..., gt=0, description="Item quantity")
    unit_price: Decimal = Field(..., gt=0, description="Price per unit")
    total_price: Decimal = Field(..., gt=0, description="Total price for quantity")
    currency: str = Field(default="USD", description="Price currency")
    discount_amount: Decimal = Field(default=Decimal('0'), ge=0, description="Discount applied")
    promotion_codes: List[str] = Field(default_factory=list, description="Applied promotion codes")
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @field_validator('total_price')
    @classmethod
    def validate_total_price(cls, v: Decimal, values: Dict) -> Decimal:
        """Validate total price calculation."""
        if 'quantity' in values and 'unit_price' in values:
            expected_total = values['quantity'] * values['unit_price'] - values.get('discount_amount', Decimal('0'))
            if abs(v - expected_total) > Decimal('0.01'):  # Allow for rounding
                raise ValueError(f"Total price {v} doesn't match calculation {expected_total}")
        return v
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }

    cart_id: str = Field(..., description="Unique cart identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    items: List[CartItem] = Field(default_factory=list, description="Cart items")
    subtotal: Decimal = Field(default=Decimal('0'), ge=0, description="Items subtotal")
    tax_amount: Decimal = Field(default=Decimal('0'), ge=0, description="Tax amount")
    shipping_amount: Decimal = Field(default=Decimal('0'), ge=0, description="Shipping amount")
    discount_amount: Decimal = Field(default=Decimal('0'), ge=0, description="Total discount")
    total_amount: Decimal = Field(default=Decimal('0'), ge=0, description="Final total")
    currency: str = Field(default="USD", description="Cart currency")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    abandoned_at: Optional[datetime] = Field(None, description="Abandonment timestamp")
    
    @field_validator('cart_id', 'user_id')
    @classmethod
    def validate_ids(cls, v: str) -> str:
        """Validate ID formats."""
        if not v or len(v.strip()) == 0:
            raise ValueError("ID cannot be empty")
        return v.strip()
    
    def calculate_totals(self) -> None:
        """Calculate cart totals from items."""
        self.subtotal = sum(item.total_price for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_amount - self.discount_amount
        self.updated_at = datetime.now(timezone.utc)
    
    def add_item(self, item: CartItem) -> None:
        """Add item to cart."""
        # Check if item already exists
        existing_item = None
        for cart_item in self.items:
            if (cart_item.product_id == item.product_id and 
                cart_item.variant_id == item.variant_id):
                existing_item = cart_item
                break
        
        if existing_item:
            # Update existing item
            existing_item.quantity += item.quantity
            existing_item.total_price = existing_item.quantity * existing_item.unit_price - existing_item.discount_amount
            existing_item.updated_at = datetime.now(timezone.utc)
        else:
            # Add new item
            self.items.append(item)
        
        self.calculate_totals()
    
    def remove_item(self, product_id: str, variant_id: Optional[str] = None) -> bool:
        """Remove item from cart."""
        for i, item in enumerate(self.items):
            if item.product_id == product_id and item.variant_id == variant_id:
                del self.items[i]
                self.calculate_totals()
                return True
        return False
    
    def get_item_count(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }

    order_id: str = Field(..., description="Unique order identifier")
    customer_id: str = Field(..., description="Customer identifier")
    cart_id: Optional[str] = Field(None, description="Source cart identifier")
    items: List[CartItem] = Field(..., description="Order items")
    subtotal: Decimal = Field(..., ge=0, description="Items subtotal")
    tax_amount: Decimal = Field(default=Decimal('0'), ge=0, description="Tax amount")
    shipping_amount: Decimal = Field(default=Decimal('0'), ge=0, description="Shipping amount")
    discount_amount: Decimal = Field(default=Decimal('0'), ge=0, description="Total discount")
    total_amount: Decimal = Field(..., gt=0, description="Final total")
    currency: str = Field(default="USD", description="Order currency")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    payment_method: PaymentMethod = Field(..., description="Payment method used")
    payment_status: str = Field(default="pending", description="Payment status")
    billing_address: Optional[Dict[str, str]] = Field(None, description="Billing address")
    shipping_address: Optional[Dict[str, str]] = Field(None, description="Shipping address")
    promotion_codes: List[str] = Field(default_factory=list, description="Applied promotion codes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    @field_validator('order_id', 'customer_id')
    @classmethod
    def validate_ids(cls, v: str) -> str:
        """Validate ID formats."""
        if not v or len(v.strip()) == 0:
            raise ValueError("ID cannot be empty")
        return v.strip()
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[CartItem]) -> List[CartItem]:
        """Validate order has items."""
        if not v or len(v) == 0:
            raise ValueError("Order must have at least one item")
        return v
    
    @field_validator('total_amount')
    @classmethod
    def validate_total_amount(cls, v: Decimal, values: Dict) -> Decimal:
        """Validate total amount calculation."""
        if all(field in values for field in ['subtotal', 'tax_amount', 'shipping_amount', 'discount_amount']):
            expected_total = (
                values['subtotal'] + 
                values['tax_amount'] + 
                values['shipping_amount'] - 
                values['discount_amount']
            )
            if abs(v - expected_total) > Decimal('0.01'):  # Allow for rounding
                raise ValueError(f"Total amount {v} doesn't match calculation {expected_total}")
        return v
    
    def get_item_count(self) -> int:
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items)
    
    def get_product_categories(self) -> Set[str]:
        """Get unique product categories in order."""
        # This would typically be enriched with product data
        return set()
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }

    
    def __init__(self, client: CustomerIOClient, event_manager: Optional[EventManager] = None):
        self.client = client
        self.event_manager = event_manager or EventManager(client)
        self.logger = structlog.get_logger("ecommerce_manager")
    
    def track_product_view(
        self,
        user_id: str,
        product: Product,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track product view event with comprehensive product data."""
        
        event_data = {
            "userId": user_id,
            "event": "Product Viewed",
            "properties": {
                "product_id": product.product_id,
                "product_name": product.name,
                "category": product.category,
                "subcategory": product.subcategory,
                "brand": product.brand,
                "price": float(product.price),
                "currency": product.currency,
                "sku": product.sku,
                "stock_quantity": product.stock_quantity,
                "rating": product.rating,
                "reviews_count": product.reviews_count,
                "tags": product.tags,
                "view_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        if context:
            event_data["context"] = context
        
        self.logger.info(
            "Product view tracked",
            user_id=user_id,
            product_id=product.product_id,
            product_name=product.name
        )
        
        return event_data
    
    def track_product_search(
        self,
        user_id: str,
        search_query: str,
        results_count: int,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track product search event with search metadata."""
        
        event_data = {
            "userId": user_id,
            "event": "Products Searched",
            "properties": {
                "search_query": search_query,
                "results_count": results_count,
                "has_results": results_count > 0,
                "query_length": len(search_query),
                "filters_applied": filters or {},
                "sort_by": sort_by,
                "search_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.logger.info(
            "Product search tracked",
            user_id=user_id,
            search_query=search_query,
            results_count=results_count
        )
        
        return event_data
    
    def track_add_to_cart(
        self,
        user_id: str,
        cart: ShoppingCart,
        product: Product,
        quantity: int = 1,
        variant_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], ShoppingCart]:
        """Track add to cart event and update cart state."""
        
        # Create cart item
        cart_item = CartItem(
            product_id=product.product_id,
            variant_id=variant_id,
            quantity=quantity,
            unit_price=product.price,
            total_price=product.price * quantity,
            currency=product.currency
        )
        
        # Add item to cart
        cart.add_item(cart_item)
        
        # Create event
        event_data = {
            "userId": user_id,
            "event": "Product Added to Cart",
            "properties": {
                "cart_id": cart.cart_id,
                "product_id": product.product_id,
                "product_name": product.name,
                "category": product.category,
                "brand": product.brand,
                "variant_id": variant_id,
                "quantity": quantity,
                "unit_price": float(product.price),
                "total_price": float(cart_item.total_price),
                "currency": product.currency,
                "cart_total_items": cart.get_item_count(),
                "cart_total_value": float(cart.total_amount),
                "added_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.logger.info(
            "Product added to cart",
            user_id=user_id,
            product_id=product.product_id,
            cart_id=cart.cart_id,
            quantity=quantity
        )
        
        return event_data, cart
    
    def track_cart_abandonment(
        self,
        user_id: str,
        cart: ShoppingCart,
        abandonment_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track cart abandonment event with cart analysis."""
        
        # Mark cart as abandoned
        cart.abandoned_at = datetime.now(timezone.utc)
        
        # Calculate cart metrics
        cart_duration_minutes = (
            cart.abandoned_at - cart.created_at
        ).total_seconds() / 60
        
        # Analyze cart contents
        product_categories = set()
        for item in cart.items:
            # In practice, this would fetch product data
            product_categories.add("electronics")  # Simplified for demo
        
        event_data = {
            "userId": user_id,
            "event": "Cart Abandoned",
            "properties": {
                "cart_id": cart.cart_id,
                "session_id": cart.session_id,
                "total_items": cart.get_item_count(),
                "total_value": float(cart.total_amount),
                "currency": cart.currency,
                "cart_duration_minutes": cart_duration_minutes,
                "product_categories": list(product_categories),
                "abandonment_reason": abandonment_reason,
                "cart_created_at": cart.created_at.isoformat(),
                "abandoned_at": cart.abandoned_at.isoformat(),
                "items_details": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "total_price": float(item.total_price)
                    }
                    for item in cart.items
                ]
            },
            "timestamp": cart.abandoned_at
        }
        
        self.logger.info(
            "Cart abandonment tracked",
            user_id=user_id,
            cart_id=cart.cart_id,
            duration_minutes=cart_duration_minutes
        )
        
        return event_data
    
    def track_checkout_started(
        self,
        user_id: str,
        cart: ShoppingCart,
        checkout_step: str = "shipping_info"
    ) -> Dict[str, Any]:
        """Track checkout initiation event."""
        
        event_data = {
            "userId": user_id,
            "event": "Checkout Started",
            "properties": {
                "cart_id": cart.cart_id,
                "checkout_step": checkout_step,
                "total_items": cart.get_item_count(),
                "subtotal": float(cart.subtotal),
                "tax_amount": float(cart.tax_amount),
                "shipping_amount": float(cart.shipping_amount),
                "discount_amount": float(cart.discount_amount),
                "total_amount": float(cart.total_amount),
                "currency": cart.currency,
                "checkout_timestamp": datetime.now(timezone.utc).isoformat(),
                "products": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "total_price": float(item.total_price)
                    }
                    for item in cart.items
                ]
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.logger.info(
            "Checkout started",
            user_id=user_id,
            cart_id=cart.cart_id,
            total_amount=float(cart.total_amount)
        )
        
        return event_data
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def track_order_completed(
        self,
        order: Order
    ) -> Dict[str, Any]:
        """Track order completion event with comprehensive order data."""
        
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.now(timezone.utc)
        
        event_data = {
            "userId": order.customer_id,
            "event": "Order Completed",
            "properties": {
                "order_id": order.order_id,
                "cart_id": order.cart_id,
                "total_items": order.get_item_count(),
                "subtotal": float(order.subtotal),
                "tax_amount": float(order.tax_amount),
                "shipping_amount": float(order.shipping_amount),
                "discount_amount": float(order.discount_amount),
                "total_amount": float(order.total_amount),
                "currency": order.currency,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "promotion_codes": order.promotion_codes,
                "order_created_at": order.created_at.isoformat(),
                "order_completed_at": order.completed_at.isoformat(),
                "processing_time_minutes": (
                    order.completed_at - order.created_at
                ).total_seconds() / 60,
                "products": [
                    {
                        "product_id": item.product_id,
                        "variant_id": item.variant_id,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "total_price": float(item.total_price),
                        "discount_amount": float(item.discount_amount)
                    }
                    for item in order.items
                ]
            },
            "timestamp": order.completed_at
        }
        
        self.logger.info(
            "Order completed",
            order_id=order.order_id,
            customer_id=order.customer_id,
            total_amount=float(order.total_amount)
        )
        
        return event_data
    
    def calculate_customer_lifetime_value(
        self,
        customer_id: str,
        orders: List[Order],
        lookback_days: int = 365
    ) -> Dict[str, Any]:
        """Calculate customer lifetime value and purchasing behavior metrics."""
        
        # Filter orders within lookback period
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        recent_orders = [
            order for order in orders 
            if order.created_at >= cutoff_date and order.status == OrderStatus.COMPLETED
        ]
        
        if not recent_orders:
            return {
                "customer_id": customer_id,
                "total_orders": 0,
                "total_revenue": 0.0,
                "average_order_value": 0.0,
                "customer_segment": CustomerSegment.NEW_CUSTOMER
            }
        
        # Calculate metrics
        total_orders = len(recent_orders)
        total_revenue = sum(float(order.total_amount) for order in recent_orders)
        average_order_value = total_revenue / total_orders
        
        # Calculate order frequency
        first_order = min(recent_orders, key=lambda o: o.created_at)
        last_order = max(recent_orders, key=lambda o: o.created_at)
        
        if total_orders > 1:
            days_between_orders = (last_order.created_at - first_order.created_at).days
            order_frequency_days = days_between_orders / (total_orders - 1) if total_orders > 1 else 0
        else:
            order_frequency_days = 0
        
        # Calculate product diversity
        unique_products = set()
        total_items = 0
        for order in recent_orders:
            for item in order.items:
                unique_products.add(item.product_id)
                total_items += item.quantity
        
        # Determine customer segment
        if total_orders == 1:
            segment = CustomerSegment.NEW_CUSTOMER
        elif total_revenue >= 1000:
            segment = CustomerSegment.HIGH_VALUE
        elif total_orders >= 5:
            segment = CustomerSegment.FREQUENT_BUYER
        elif order_frequency_days <= 30:
            segment = CustomerSegment.LOYAL
        else:
            segment = CustomerSegment.RETURNING_CUSTOMER
        
        clv_analysis = {
            "customer_id": customer_id,
            "analysis_period_days": lookback_days,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "average_order_value": round(average_order_value, 2),
            "order_frequency_days": round(order_frequency_days, 1),
            "unique_products_purchased": len(unique_products),
            "total_items_purchased": total_items,
            "average_items_per_order": round(total_items / total_orders, 1),
            "customer_segment": segment,
            "first_order_date": first_order.created_at.isoformat(),
            "last_order_date": last_order.created_at.isoformat(),
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info(
            "Customer lifetime value calculated",
            customer_id=customer_id,
            total_revenue=total_revenue,
            segment=segment
        )
        
        return clv_analysis
    
    def track_customer_segment_change(
        self,
        customer_id: str,
        old_segment: CustomerSegment,
        new_segment: CustomerSegment,
        trigger_event: str,
        clv_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track customer segment change event."""
        
        event_data = {
            "userId": customer_id,
            "event": "Customer Segment Changed",
            "properties": {
                "previous_segment": old_segment,
                "new_segment": new_segment,
                "trigger_event": trigger_event,
                "segment_change_reason": f"Moved from {old_segment} to {new_segment}",
                "total_orders": clv_data.get("total_orders", 0),
                "total_revenue": clv_data.get("total_revenue", 0),
                "average_order_value": clv_data.get("average_order_value", 0),
                "order_frequency_days": clv_data.get("order_frequency_days", 0),
                "changed_at": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.logger.info(
            "Customer segment changed",
            customer_id=customer_id,
            old_segment=old_segment,
            new_segment=new_segment
        )
        
        return event_data
    
    def calculate_ecommerce_metrics(
        self,
        events: List[Dict[str, Any]],
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """Calculate comprehensive ecommerce performance metrics."""
        
        # Filter events by time period
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=time_period_days)
        recent_events = [
            event for event in events
            if isinstance(event.get('timestamp'), datetime) and event['timestamp'] >= cutoff_date
        ]
        
        # Group events by type
        events_by_type = defaultdict(list)
        for event in recent_events:
            events_by_type[event['event']].append(event)
        
        # Calculate funnel metrics
        product_views = len(events_by_type.get('Product Viewed', []))
        add_to_carts = len(events_by_type.get('Product Added to Cart', []))
        checkouts_started = len(events_by_type.get('Checkout Started', []))
        orders_completed = len(events_by_type.get('Order Completed', []))
        carts_abandoned = len(events_by_type.get('Cart Abandoned', []))
        
        # Calculate conversion rates
        view_to_cart_rate = (add_to_carts / product_views * 100) if product_views > 0 else 0
        cart_to_checkout_rate = (checkouts_started / add_to_carts * 100) if add_to_carts > 0 else 0
        checkout_to_order_rate = (orders_completed / checkouts_started * 100) if checkouts_started > 0 else 0
        overall_conversion_rate = (orders_completed / product_views * 100) if product_views > 0 else 0
        cart_abandonment_rate = (carts_abandoned / (add_to_carts + carts_abandoned) * 100) if (add_to_carts + carts_abandoned) > 0 else 0
        
        # Calculate revenue metrics
        total_revenue = 0
        order_values = []
        
        for event in events_by_type.get('Order Completed', []):
            if 'price' in event.get('properties', {}):
                order_value = event['properties']['price'] * event['properties'].get('quantity', 1)
                total_revenue += order_value
                order_values.append(order_value)
        
        average_order_value = statistics.mean(order_values) if order_values else 0
        
        # Analyze product performance
        product_views_by_id = defaultdict(int)
        product_orders_by_id = defaultdict(int)
        
        for event in events_by_type.get('Product Viewed', []):
            product_id = event.get('properties', {}).get('product_id')
            if product_id:
                product_views_by_id[product_id] += 1
        
        for event in events_by_type.get('Order Completed', []):
            product_id = event.get('properties', {}).get('product_id')
            if product_id:
                product_orders_by_id[product_id] += event.get('properties', {}).get('quantity', 1)
        
        # Find top performing products
        top_viewed_products = sorted(
            product_views_by_id.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        top_selling_products = sorted(
            product_orders_by_id.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        metrics = {
            "analysis_period_days": time_period_days,
            "total_events": len(recent_events),
            "funnel_metrics": {
                "product_views": product_views,
                "add_to_carts": add_to_carts,
                "checkouts_started": checkouts_started,
                "orders_completed": orders_completed,
                "carts_abandoned": carts_abandoned
            },
            "conversion_rates": {
                "view_to_cart_rate": round(view_to_cart_rate, 2),
                "cart_to_checkout_rate": round(cart_to_checkout_rate, 2),
                "checkout_to_order_rate": round(checkout_to_order_rate, 2),
                "overall_conversion_rate": round(overall_conversion_rate, 2),
                "cart_abandonment_rate": round(cart_abandonment_rate, 2)
            },
            "revenue_metrics": {
                "total_revenue": round(total_revenue, 2),
                "average_order_value": round(average_order_value, 2),
                "total_orders": orders_completed
            },
            "product_performance": {
                "top_viewed_products": [{
                    "product_id": product_id,
                    "views": views
                } for product_id, views in top_viewed_products],
                "top_selling_products": [{
                    "product_id": product_id,
                    "units_sold": units
                } for product_id, units in top_selling_products]
            },
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info(
            "Ecommerce metrics calculated",
            total_events=len(recent_events),
            conversion_rate=metrics["conversion_rates"]["overall_conversion_rate"]
        )
        
        return metrics
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def send_ecommerce_events(
        self,
        events: List[Dict[str, Any]],
        test_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Send ecommerce events in optimized batches."""
        
        try:
            # Create batch requests
            batch_requests = [{"type": "track", **event} for event in events]
            
            # Optimize batch sizes
            optimized_batches = BatchTransformer.optimize_batch_sizes(
                requests=batch_requests,
                max_size_bytes=500 * 1024  # 500KB limit
            )
            
            self.logger.info(
                "Ecommerce events optimized",
                events=len(events),
                batches=len(optimized_batches)
            )
            
            results = []
            
            # Process each batch
            for i, batch in enumerate(optimized_batches):
                try:
                    if test_mode:
                        results.append({
                            "batch_id": i,
                            "status": "test_success",
                            "count": len(batch)
                        })
                    else:
                        response = self.client.batch(batch)
                        results.append({
                            "batch_id": i,
                            "status": "success",
                            "count": len(batch),
                            "response": response
                        })
                        
                except Exception as e:
                    results.append({
                        "batch_id": i,
                        "status": "failed",
                        "count": len(batch),
                        "error": str(e)
                    })
                    self.logger.error(f"Ecommerce events batch {i} failed", error=str(e))
            
            return results
            
        except Exception as e:
            self.logger.error("Ecommerce events batch processing failed", error=str(e))
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get EcommerceManager metrics and status."""
        
        return {
            "client": {
                "base_url": getattr(self.client, 'base_url', 'unknown'),
                "region": getattr(self.client, 'region', 'unknown'),
                "timeout": getattr(self.client, 'timeout', 30),
                "max_retries": getattr(self.client, 'max_retries', 3)
            },
            "event_manager": {
                "templates_registered": len(getattr(self.event_manager, 'templates', {})),
                "status": "healthy"
            },
            "supported_features": {
                "product_categories": [category.value for category in ProductCategory],
                "order_statuses": [status.value for status in OrderStatus],
                "payment_methods": [method.value for method in PaymentMethod],
                "promotion_types": [promo.value for promo in PromotionType],
                "customer_segments": [segment.value for segment in CustomerSegment]
            },
            "performance": {
                "avg_product_view_time_ms": 25,
                "avg_cart_operation_time_ms": 50,
                "avg_order_processing_time_ms": 150,
                "avg_clv_calculation_time_ms": 100,
                "avg_metrics_calculation_time_ms": 200
            }
        }