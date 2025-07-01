-- ==================================================
-- Customer.IO Events Data Models
-- ==================================================
-- Based on actual data structures from integration tests
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- Core events table for all custom event tracking
CREATE TABLE IF NOT EXISTS customerio.events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this event',
    user_id STRING NOT NULL COMMENT 'User who performed this event',
    anonymous_id STRING COMMENT 'Anonymous user identifier if event occurred before identification',
    
    -- Event core data
    event_name STRING NOT NULL COMMENT 'Name of the event (Product Purchase, App Opened, etc.)',
    event_type STRING DEFAULT 'track' COMMENT 'Type of event (track, page, screen)',
    
    -- Event properties and metadata
    properties STRUCT<
        -- Common e-commerce properties
        product_id: STRING,
        category: STRING,
        price: DOUBLE,
        quantity: INT,
        
        -- App/Platform properties
        app_version: STRING,
        platform: STRING,
        source: STRING,
        
        -- Content properties
        title: STRING,
        description: STRING,
        url: STRING,
        
        -- User interaction properties
        button_id: STRING,
        page: STRING,
        plan: STRING,
        
        -- Location and context
        location: STRING,
        priority: STRING,
        
        -- Test and integration properties
        test_type: STRING,
        integration: BOOLEAN,
        batch: STRING,
        index: INT
    > COMMENT 'Event-specific properties based on integration test patterns',
    
    -- Complex nested properties
    nested_properties STRUCT<
        location: STRING,
        priority: STRING,
        metadata: MAP<STRING, STRING>
    > COMMENT 'Nested object properties from integration tests',
    
    -- Arrays and lists
    tags ARRAY<STRING> COMMENT 'Array of tags associated with the event',
    
    -- Raw properties for flexibility
    raw_properties MAP<STRING, STRING> COMMENT 'All event properties as key-value pairs for flexibility',
    raw_properties_json STRING COMMENT 'Original JSON properties for complex nested data',
    
    -- Special characters and internationalization
    unicode_text STRING COMMENT 'Text with unicode characters support',
    special_chars STRING COMMENT 'Text with special characters (!@#$%^&*())',
    emoji_text STRING COMMENT 'Text containing emoji characters',
    
    -- Timestamps
    event_timestamp TIMESTAMP COMMENT 'When the event actually occurred (can be historical)',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the event',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the event was processed',
    
    -- Data lineage and tracking
    source_system STRING COMMENT 'System that generated this event',
    integration_id STRING COMMENT 'Integration identifier',
    api_call_id STRING COMMENT 'API call that created this event',
    batch_id STRING COMMENT 'Batch identifier if sent via batch operation',
    sequence_number INT COMMENT 'Sequence number for ordered events',
    
    -- Event classification
    is_anonymous BOOLEAN DEFAULT FALSE COMMENT 'Whether this was an anonymous user event',
    is_historical BOOLEAN DEFAULT FALSE COMMENT 'Whether this event was backfilled',
    is_test_event BOOLEAN DEFAULT FALSE COMMENT 'Whether this is a test/integration event',
    
    CONSTRAINT pk_events PRIMARY KEY (event_id),
    CONSTRAINT fk_events_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/events'
COMMENT 'Core events table storing all custom event tracking from Customer.IO track calls'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.event_name_not_null' = 'event_name IS NOT NULL',
    'quality.expectations.valid_event_timestamp' = 'event_timestamp IS NULL OR event_timestamp <= CURRENT_TIMESTAMP()'
);

-- Page views table for web page tracking
CREATE TABLE IF NOT EXISTS customerio.page_views (
    -- Page view identification
    page_view_id STRING NOT NULL COMMENT 'Unique identifier for this page view',
    user_id STRING NOT NULL COMMENT 'User who viewed the page',
    anonymous_id STRING COMMENT 'Anonymous user identifier',
    
    -- Page information
    page_name STRING COMMENT 'Name or identifier of the page',
    page_path STRING COMMENT 'URL path of the page (/integration/test)',
    page_title STRING COMMENT 'Title of the page (Integration Test Page)',
    page_url STRING COMMENT 'Full URL of the page',
    
    -- Page categorization
    page_category STRING COMMENT 'Category of the page (testing, dashboard, etc.)',
    page_type STRING COMMENT 'Type of page (landing, product, checkout, etc.)',
    
    -- Referrer and source information
    referrer_url STRING COMMENT 'URL of the referring page',
    referrer_domain STRING COMMENT 'Domain of the referrer',
    utm_source STRING COMMENT 'UTM source parameter',
    utm_medium STRING COMMENT 'UTM medium parameter',
    utm_campaign STRING COMMENT 'UTM campaign parameter',
    utm_term STRING COMMENT 'UTM term parameter',
    utm_content STRING COMMENT 'UTM content parameter',
    
    -- Browser and device context
    user_agent STRING COMMENT 'User agent string',
    browser_name STRING COMMENT 'Browser name',
    browser_version STRING COMMENT 'Browser version',
    device_type STRING COMMENT 'Device type (desktop, mobile, tablet)',
    screen_resolution STRING COMMENT 'Screen resolution',
    
    -- Page interaction metrics
    time_on_page INT COMMENT 'Time spent on page in seconds',
    scroll_depth DOUBLE COMMENT 'Maximum scroll depth as percentage',
    
    -- Custom properties
    properties MAP<STRING, STRING> COMMENT 'Additional page view properties',
    
    -- Timestamps
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the page was viewed',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the page view',
    
    -- Data lineage
    source_system STRING COMMENT 'System that tracked this page view',
    integration_id STRING COMMENT 'Integration identifier',
    session_id STRING COMMENT 'User session identifier',
    
    CONSTRAINT pk_page_views PRIMARY KEY (page_view_id),
    CONSTRAINT fk_page_views_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/page_views'
COMMENT 'Page views table storing web page tracking from Customer.IO page calls'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.page_name_not_null' = 'page_name IS NOT NULL OR page_path IS NOT NULL'
);

-- Screen views table for mobile app screen tracking
CREATE TABLE IF NOT EXISTS customerio.screen_views (
    -- Screen view identification
    screen_view_id STRING NOT NULL COMMENT 'Unique identifier for this screen view',
    user_id STRING NOT NULL COMMENT 'User who viewed the screen',
    anonymous_id STRING COMMENT 'Anonymous user identifier',
    
    -- Screen information
    screen_name STRING NOT NULL COMMENT 'Name of the screen (Settings Screen, Dashboard, etc.)',
    screen_class STRING COMMENT 'Class or type of the screen',
    screen_category STRING COMMENT 'Category of the screen',
    
    -- App context
    app_name STRING COMMENT 'Name of the mobile application',
    app_version STRING COMMENT 'Version of the mobile application (1.0.0)',
    app_build STRING COMMENT 'Build number of the application',
    
    -- Platform information
    platform STRING COMMENT 'Mobile platform (ios, android)',
    os_name STRING COMMENT 'Operating system name',
    os_version STRING COMMENT 'Operating system version',
    device_model STRING COMMENT 'Device model',
    device_manufacturer STRING COMMENT 'Device manufacturer',
    
    -- Screen interaction metrics
    time_on_screen INT COMMENT 'Time spent on screen in seconds',
    previous_screen STRING COMMENT 'Previous screen in navigation',
    next_screen STRING COMMENT 'Next screen in navigation',
    
    -- Navigation context
    entry_point STRING COMMENT 'How user entered this screen (tab, button, deeplink)',
    exit_point STRING COMMENT 'How user left this screen',
    
    -- Custom properties
    properties STRUCT<
        app_version: STRING,
        platform: STRING,
        screen_category: STRING,
        navigation_source: STRING,
        custom_data: MAP<STRING, STRING>
    > COMMENT 'Screen-specific properties',
    
    -- Timestamps
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the screen was viewed',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the screen view',
    
    -- Data lineage
    source_system STRING COMMENT 'System that tracked this screen view',
    integration_id STRING COMMENT 'Integration identifier',
    session_id STRING COMMENT 'App session identifier',
    
    CONSTRAINT pk_screen_views PRIMARY KEY (screen_view_id),
    CONSTRAINT fk_screen_views_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/screen_views'
COMMENT 'Screen views table storing mobile app screen tracking from Customer.IO screen calls'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.screen_name_not_null' = 'screen_name IS NOT NULL',
    'quality.expectations.platform_valid' = 'platform IS NULL OR platform IN ("ios", "android", "web")'
);

-- Event sequences table for tracking user journeys
CREATE TABLE IF NOT EXISTS customerio.event_sequences (
    -- Sequence identification
    sequence_id STRING NOT NULL COMMENT 'Unique identifier for this event sequence',
    user_id STRING NOT NULL COMMENT 'User who performed this sequence',
    session_id STRING COMMENT 'Session during which sequence occurred',
    
    -- Sequence metadata
    sequence_start_time TIMESTAMP COMMENT 'When the sequence started',
    sequence_end_time TIMESTAMP COMMENT 'When the sequence ended',
    total_events INT COMMENT 'Total number of events in sequence',
    sequence_duration_seconds INT COMMENT 'Duration of sequence in seconds',
    
    -- Events in sequence
    events ARRAY<STRUCT<
        event_id: STRING,
        event_name: STRING,
        event_timestamp: TIMESTAMP,
        order_in_sequence: INT,
        time_since_previous: INT
    >> COMMENT 'Ordered list of events in this sequence',
    
    -- Sequence patterns
    event_pattern STRING COMMENT 'Pattern of events (App Opened -> Page Viewed -> Button Clicked)',
    sequence_type STRING COMMENT 'Type of sequence (conversion_funnel, onboarding, etc.)',
    conversion_goal STRING COMMENT 'Goal of this sequence if applicable',
    
    -- Outcome
    completed_successfully BOOLEAN DEFAULT FALSE COMMENT 'Whether the sequence completed successfully',
    conversion_achieved BOOLEAN DEFAULT FALSE COMMENT 'Whether conversion goal was achieved',
    drop_off_point STRING COMMENT 'Where user dropped off if sequence incomplete',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When this sequence record was created',
    
    CONSTRAINT pk_event_sequences PRIMARY KEY (sequence_id),
    CONSTRAINT fk_sequences_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/event_sequences'
COMMENT 'Event sequences tracking user journeys and event patterns'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.total_events_positive' = 'total_events > 0'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_events_user_id ON customerio.events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_name ON customerio.events(event_name);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON customerio.events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON customerio.events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_anonymous ON customerio.events(is_anonymous);

CREATE INDEX IF NOT EXISTS idx_page_views_user_id ON customerio.page_views(user_id);
CREATE INDEX IF NOT EXISTS idx_page_views_path ON customerio.page_views(page_path);
CREATE INDEX IF NOT EXISTS idx_page_views_timestamp ON customerio.page_views(viewed_at);

CREATE INDEX IF NOT EXISTS idx_screen_views_user_id ON customerio.screen_views(user_id);
CREATE INDEX IF NOT EXISTS idx_screen_views_name ON customerio.screen_views(screen_name);
CREATE INDEX IF NOT EXISTS idx_screen_views_platform ON customerio.screen_views(platform);
CREATE INDEX IF NOT EXISTS idx_screen_views_timestamp ON customerio.screen_views(viewed_at);

CREATE INDEX IF NOT EXISTS idx_sequences_user_id ON customerio.event_sequences(user_id);
CREATE INDEX IF NOT EXISTS idx_sequences_type ON customerio.event_sequences(sequence_type);
CREATE INDEX IF NOT EXISTS idx_sequences_start_time ON customerio.event_sequences(sequence_start_time);