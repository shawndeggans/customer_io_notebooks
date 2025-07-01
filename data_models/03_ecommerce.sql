-- ==================================================
-- Customer.IO E-commerce Data Models
-- ==================================================
-- Based on actual data structures from integration tests
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- E-commerce events table for all e-commerce semantic events
CREATE TABLE IF NOT EXISTS customerio.ecommerce_events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this e-commerce event',
    user_id STRING NOT NULL COMMENT 'User who performed this e-commerce action',
    
    -- Event classification
    event_type STRING NOT NULL COMMENT 'Type of e-commerce event (search, product_click, checkout, etc.)',
    event_name STRING NOT NULL COMMENT 'Specific event name (Products Searched, Product Clicked, etc.)',
    
    -- Product information (for product-related events)
    product_id STRING COMMENT 'Product identifier',
    sku STRING COMMENT 'Product SKU (WH-1000XM4)',
    product_name STRING COMMENT 'Product name (Sony WH-1000XM4 Headphones)',
    product_category STRING COMMENT 'Product category (Electronics > Audio > Headphones)',
    brand STRING COMMENT 'Product brand (Sony)',
    
    -- Pricing information
    price DOUBLE COMMENT 'Product price (349.99)',
    currency STRING DEFAULT 'USD' COMMENT 'Currency code (USD)',
    original_price DOUBLE COMMENT 'Original price before discounts',
    discount_amount DOUBLE COMMENT 'Amount of discount applied',
    
    -- Position and listing context
    position INT COMMENT 'Position in search results or product list',
    list_id STRING COMMENT 'Identifier of the product list (category_electronics)',
    list_category STRING COMMENT 'Category of the product list',
    
    -- Search-specific properties
    search_query STRING COMMENT 'Search query used (wireless headphones)',
    search_results_count INT COMMENT 'Number of search results returned',
    search_filters ARRAY<STRING> COMMENT 'Applied filters ([brand:sony, price:under-200])',
    sort_by STRING COMMENT 'Sort criteria applied (price_low_to_high)',
    
    -- Checkout and cart information
    checkout_id STRING COMMENT 'Checkout session identifier',
    checkout_step INT COMMENT 'Step number in checkout process',
    checkout_step_name STRING COMMENT 'Name of checkout step (shipping_info, payment)',
    payment_method STRING COMMENT 'Payment method used (credit_card)',
    
    -- Order totals and quantities
    quantity INT COMMENT 'Quantity of items',
    order_total DOUBLE COMMENT 'Total order amount',
    subtotal DOUBLE COMMENT 'Subtotal before taxes and fees',
    tax_amount DOUBLE COMMENT 'Tax amount',
    shipping_amount DOUBLE COMMENT 'Shipping cost',
    
    -- Coupon and promotion data
    coupon_id STRING COMMENT 'Coupon identifier (SAVE20)',
    coupon_name STRING COMMENT 'Coupon name (20% Off Everything)',
    coupon_discount_type STRING COMMENT 'Discount type (percentage, fixed)',
    coupon_discount_value DOUBLE COMMENT 'Discount value (20.0)',
    coupon_denial_reason STRING COMMENT 'Reason coupon was denied (expired)',
    
    promotion_id STRING COMMENT 'Promotion identifier (SUMMER2024)',
    promotion_name STRING COMMENT 'Promotion name (Summer Sale 2024)',
    promotion_creative STRING COMMENT 'Promotion creative/banner (banner_top)',
    promotion_position STRING COMMENT 'Promotion position (header)',
    
    -- Social and review data
    share_via STRING COMMENT 'Platform used for sharing (facebook)',
    share_message STRING COMMENT 'Message included with share',
    review_id STRING COMMENT 'Review identifier',
    rating INT COMMENT 'Product rating (1-5)',
    review_body STRING COMMENT 'Review text content',
    
    -- Complex nested properties
    products ARRAY<STRUCT<
        product_id: STRING,
        name: STRING,
        price: DOUBLE,
        position: INT,
        quantity: INT,
        category: STRING,
        brand: STRING,
        sku: STRING
    >> COMMENT 'Array of products (for cart and list events)',
    
    -- Raw event properties for flexibility
    raw_properties MAP<STRING, STRING> COMMENT 'All event properties as key-value pairs',
    custom_properties STRUCT<
        filters_applied: ARRAY<STRING>,
        sort_criteria: STRING,
        recommendation_source: STRING,
        campaign_id: STRING,
        affiliate_id: STRING
    > COMMENT 'Custom e-commerce properties',
    
    -- Attribution and source tracking
    referrer_url STRING COMMENT 'Page that referred to this action',
    campaign_source STRING COMMENT 'Marketing campaign source',
    affiliate_code STRING COMMENT 'Affiliate tracking code',
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the e-commerce event occurred',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the event',
    
    -- Data lineage
    source_system STRING COMMENT 'System that generated this event',
    integration_id STRING COMMENT 'Integration identifier',
    session_id STRING COMMENT 'User session identifier',
    journey_id STRING COMMENT 'User journey identifier for funnel analysis',
    
    CONSTRAINT pk_ecommerce_events PRIMARY KEY (event_id),
    CONSTRAINT fk_ecommerce_events_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/ecommerce_events'
COMMENT 'E-commerce events table storing all semantic e-commerce tracking events'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.event_type_valid' = 'event_type IN ("search", "product_interaction", "checkout", "coupon", "promotion", "social")',
    'quality.expectations.valid_rating' = 'rating IS NULL OR (rating >= 1 AND rating <= 5)'
);

-- Products catalog table for product master data
CREATE TABLE IF NOT EXISTS customerio.products (
    -- Product identification
    product_id STRING NOT NULL COMMENT 'Unique product identifier',
    sku STRING COMMENT 'Stock keeping unit identifier',
    
    -- Product information
    name STRING NOT NULL COMMENT 'Product name',
    description STRING COMMENT 'Product description',
    category STRING COMMENT 'Product category hierarchy',
    subcategory STRING COMMENT 'Product subcategory',
    brand STRING COMMENT 'Product brand',
    
    -- Pricing information
    price DOUBLE COMMENT 'Current product price',
    original_price DOUBLE COMMENT 'Original/MSRP price',
    cost DOUBLE COMMENT 'Product cost (for margin calculation)',
    currency STRING DEFAULT 'USD' COMMENT 'Price currency',
    
    -- Inventory information
    in_stock BOOLEAN DEFAULT TRUE COMMENT 'Whether product is in stock',
    stock_quantity INT COMMENT 'Available stock quantity',
    low_stock_threshold INT COMMENT 'Threshold for low stock alerts',
    
    -- Product attributes
    color STRING COMMENT 'Product color',
    size STRING COMMENT 'Product size',
    weight DOUBLE COMMENT 'Product weight',
    dimensions STRUCT<
        length: DOUBLE,
        width: DOUBLE,
        height: DOUBLE,
        unit: STRING
    > COMMENT 'Product dimensions',
    
    -- Content and media
    image_url STRING COMMENT 'Primary product image URL',
    product_url STRING COMMENT 'Product page URL',
    images ARRAY<STRING> COMMENT 'Array of product image URLs',
    
    -- SEO and metadata
    meta_title STRING COMMENT 'SEO meta title',
    meta_description STRING COMMENT 'SEO meta description',
    tags ARRAY<STRING> COMMENT 'Product tags for search and categorization',
    
    -- Status and lifecycle
    status STRING DEFAULT 'active' COMMENT 'Product status (active, discontinued, draft)',
    is_featured BOOLEAN DEFAULT FALSE COMMENT 'Whether product is featured',
    is_on_sale BOOLEAN DEFAULT FALSE COMMENT 'Whether product is on sale',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When product was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When product was last updated',
    discontinued_at TIMESTAMP COMMENT 'When product was discontinued',
    
    CONSTRAINT pk_products PRIMARY KEY (product_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/products'
COMMENT 'Products catalog table storing master product data'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.product_id_not_null' = 'product_id IS NOT NULL',
    'quality.expectations.name_not_null' = 'name IS NOT NULL',
    'quality.expectations.valid_price' = 'price IS NULL OR price >= 0'
);

-- Shopping carts table for cart state tracking
CREATE TABLE IF NOT EXISTS customerio.shopping_carts (
    -- Cart identification
    cart_id STRING NOT NULL COMMENT 'Unique cart identifier',
    user_id STRING NOT NULL COMMENT 'User who owns this cart',
    session_id STRING COMMENT 'Session during which cart was created',
    
    -- Cart status
    cart_status STRING DEFAULT 'active' COMMENT 'Cart status (active, abandoned, converted, expired)',
    is_guest_cart BOOLEAN DEFAULT FALSE COMMENT 'Whether this is a guest user cart',
    
    -- Cart totals
    item_count INT DEFAULT 0 COMMENT 'Total number of items in cart',
    total_quantity INT DEFAULT 0 COMMENT 'Total quantity of all items',
    subtotal DOUBLE DEFAULT 0.0 COMMENT 'Subtotal before discounts',
    discount_amount DOUBLE DEFAULT 0.0 COMMENT 'Total discount amount applied',
    tax_amount DOUBLE DEFAULT 0.0 COMMENT 'Tax amount',
    shipping_amount DOUBLE DEFAULT 0.0 COMMENT 'Shipping cost',
    total_amount DOUBLE DEFAULT 0.0 COMMENT 'Final total amount',
    currency STRING DEFAULT 'USD' COMMENT 'Cart currency',
    
    -- Applied promotions
    applied_coupons ARRAY<STRUCT<
        coupon_id: STRING,
        coupon_name: STRING,
        discount_type: STRING,
        discount_value: DOUBLE,
        discount_amount: DOUBLE
    >> COMMENT 'Applied coupons and their discounts',
    
    -- Cart items
    items ARRAY<STRUCT<
        product_id: STRING,
        sku: STRING,
        name: STRING,
        price: DOUBLE,
        quantity: INT,
        subtotal: DOUBLE,
        added_at: TIMESTAMP
    >> COMMENT 'Items currently in the cart',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When cart was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When cart was last updated',
    abandoned_at TIMESTAMP COMMENT 'When cart was abandoned',
    converted_at TIMESTAMP COMMENT 'When cart was converted to order',
    expires_at TIMESTAMP COMMENT 'When cart expires',
    
    -- Attribution
    source_campaign STRING COMMENT 'Marketing campaign that led to cart creation',
    referrer_url STRING COMMENT 'Referrer URL',
    
    CONSTRAINT pk_shopping_carts PRIMARY KEY (cart_id),
    CONSTRAINT fk_carts_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/shopping_carts'
COMMENT 'Shopping carts table for tracking cart state and abandonment'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.cart_id_not_null' = 'cart_id IS NOT NULL',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.valid_totals' = 'total_amount >= 0'
);

-- Wishlist table for saved products
CREATE TABLE IF NOT EXISTS customerio.wishlists (
    -- Wishlist identification
    wishlist_id STRING NOT NULL COMMENT 'Unique wishlist identifier',
    user_id STRING NOT NULL COMMENT 'User who owns this wishlist',
    
    -- Wishlist metadata
    wishlist_name STRING DEFAULT 'My Wishlist' COMMENT 'Name of the wishlist',
    is_public BOOLEAN DEFAULT FALSE COMMENT 'Whether wishlist is publicly viewable',
    is_default BOOLEAN DEFAULT TRUE COMMENT 'Whether this is the default wishlist',
    
    -- Wishlist items
    items ARRAY<STRUCT<
        product_id: STRING,
        name: STRING,
        price: DOUBLE,
        category: STRING,
        added_at: TIMESTAMP,
        notes: STRING
    >> COMMENT 'Products saved in the wishlist',
    
    item_count INT DEFAULT 0 COMMENT 'Number of items in wishlist',
    total_value DOUBLE DEFAULT 0.0 COMMENT 'Total value of wishlist items',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When wishlist was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When wishlist was last updated',
    
    CONSTRAINT pk_wishlists PRIMARY KEY (wishlist_id),
    CONSTRAINT fk_wishlists_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/wishlists'
COMMENT 'Wishlists table for tracking saved products'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.wishlist_id_not_null' = 'wishlist_id IS NOT NULL',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL'
);

-- Product reviews table
CREATE TABLE IF NOT EXISTS customerio.product_reviews (
    -- Review identification
    review_id STRING NOT NULL COMMENT 'Unique review identifier',
    product_id STRING NOT NULL COMMENT 'Product being reviewed',
    user_id STRING NOT NULL COMMENT 'User who wrote the review',
    
    -- Review content
    rating INT NOT NULL COMMENT 'Product rating (1-5 stars)',
    review_title STRING COMMENT 'Review title/headline',
    review_body STRING COMMENT 'Review text content',
    
    -- Review metadata
    is_verified_purchase BOOLEAN DEFAULT FALSE COMMENT 'Whether reviewer purchased the product',
    helpful_votes INT DEFAULT 0 COMMENT 'Number of helpful votes',
    total_votes INT DEFAULT 0 COMMENT 'Total number of votes',
    
    -- Review status
    status STRING DEFAULT 'pending' COMMENT 'Review status (pending, approved, rejected)',
    moderation_notes STRING COMMENT 'Notes from content moderation',
    
    -- Timestamps
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When review was submitted',
    approved_at TIMESTAMP COMMENT 'When review was approved',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When review was last updated',
    
    CONSTRAINT pk_product_reviews PRIMARY KEY (review_id),
    CONSTRAINT fk_reviews_product FOREIGN KEY (product_id) REFERENCES customerio.products(product_id),
    CONSTRAINT fk_reviews_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT chk_rating_valid CHECK (rating >= 1 AND rating <= 5)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/product_reviews'
COMMENT 'Product reviews and ratings table'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.review_id_not_null' = 'review_id IS NOT NULL',
    'quality.expectations.rating_valid' = 'rating >= 1 AND rating <= 5'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_ecommerce_events_user_id ON customerio.ecommerce_events(user_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_events_type ON customerio.ecommerce_events(event_type);
CREATE INDEX IF NOT EXISTS idx_ecommerce_events_product_id ON customerio.ecommerce_events(product_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_events_timestamp ON customerio.ecommerce_events(event_timestamp);

CREATE INDEX IF NOT EXISTS idx_products_category ON customerio.products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON customerio.products(brand);
CREATE INDEX IF NOT EXISTS idx_products_status ON customerio.products(status);
CREATE INDEX IF NOT EXISTS idx_products_price ON customerio.products(price);

CREATE INDEX IF NOT EXISTS idx_carts_user_id ON customerio.shopping_carts(user_id);
CREATE INDEX IF NOT EXISTS idx_carts_status ON customerio.shopping_carts(cart_status);
CREATE INDEX IF NOT EXISTS idx_carts_updated_at ON customerio.shopping_carts(updated_at);

CREATE INDEX IF NOT EXISTS idx_wishlists_user_id ON customerio.wishlists(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON customerio.product_reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON customerio.product_reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON customerio.product_reviews(rating);