-- ==================================================
-- Customer.IO Core People Data Models
-- ==================================================
-- Based on actual data structures from integration tests
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- Core people/users table for user identification and traits
CREATE TABLE IF NOT EXISTS customerio.people (
    -- Primary identifiers
    user_id STRING NOT NULL COMMENT 'Unique identifier for a person across systems',
    anonymous_id STRING COMMENT 'Anonymous identifier before user signup/login',
    
    -- Core contact information
    email STRING COMMENT 'Primary email address for the user',
    first_name STRING COMMENT 'User first name',
    last_name STRING COMMENT 'User last name', 
    name STRING COMMENT 'Full name when first/last not separated',
    
    -- User classification and status
    plan STRING COMMENT 'User subscription plan (free, basic, premium, enterprise)',
    user_type STRING COMMENT 'User type classification',
    status STRING COMMENT 'User account status (active, inactive, suspended)',
    
    -- Demographics and profile data
    age INT COMMENT 'User age',
    location_city STRING COMMENT 'User city from profile.location.city',
    location_country STRING COMMENT 'User country from profile.location.country',
    location_full STRUCT<
        city: STRING,
        country: STRING,
        state: STRING,
        postal_code: STRING,
        timezone: STRING
    > COMMENT 'Complete location information nested object',
    
    -- Interests and preferences
    interests ARRAY<STRING> COMMENT 'Array of user interests from profile.interests',
    tags ARRAY<STRING> COMMENT 'User tags for segmentation',
    
    -- Engagement metrics
    engagement_score DOUBLE COMMENT 'User engagement score from scores.engagement',
    activity_score DOUBLE COMMENT 'User activity score from scores.activity', 
    scores STRUCT<
        engagement: DOUBLE,
        activity: DOUBLE,
        retention: DOUBLE,
        satisfaction: DOUBLE
    > COMMENT 'All user scoring metrics',
    
    -- GDPR and compliance
    gdpr_consent BOOLEAN COMMENT 'GDPR consent status',
    marketing_consent BOOLEAN COMMENT 'Marketing communications consent',
    is_suppressed BOOLEAN DEFAULT FALSE COMMENT 'User suppression status for GDPR',
    suppressed_at TIMESTAMP COMMENT 'When user was suppressed',
    unsuppressed_at TIMESTAMP COMMENT 'When user was unsuppressed',
    
    -- Custom traits and metadata
    custom_traits MAP<STRING, STRING> COMMENT 'Additional custom user traits as key-value pairs',
    profile_data STRUCT<
        age: INT,
        interests: ARRAY<STRING>,
        location: STRUCT<city: STRING, country: STRING>,
        preferences: MAP<STRING, STRING>
    > COMMENT 'Nested profile object for complex user data',
    
    -- Special characters and internationalization
    unicode_name STRING COMMENT 'Name with unicode characters support',
    special_description STRING COMMENT 'Description with special characters',
    
    -- Timestamps and audit fields
    registered_at TIMESTAMP COMMENT 'When user registered (from traits.registered_at)',
    upgraded_at TIMESTAMP COMMENT 'When user upgraded plan',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When record was created in Customer.IO',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When record was last updated',
    identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When user was last identified',
    
    -- Data lineage and integration
    source_system STRING COMMENT 'System that created this user record',
    integration_id STRING COMMENT 'Integration identifier for data pipeline tracking',
    batch_id STRING COMMENT 'Batch operation identifier if created via batch',
    
    CONSTRAINT pk_people PRIMARY KEY (user_id)
) 
USING DELTA
LOCATION 's3://your-bucket/customerio/people'
COMMENT 'Core people table storing user identification and trait data from Customer.IO identify calls'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.valid_email' = 'email IS NULL OR email RLIKE "^[^@]+@[^@]+\\.[^@]+$"'
);

-- People lifecycle events table for tracking user management actions
CREATE TABLE IF NOT EXISTS customerio.people_events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this event',
    user_id STRING NOT NULL COMMENT 'User this event relates to',
    event_type STRING NOT NULL COMMENT 'Type of people event (identified, deleted, suppressed, unsuppressed)',
    event_name STRING COMMENT 'Specific event name (User Deleted, User Suppressed, etc.)',
    
    -- Event details
    event_properties STRUCT<
        deletion_reason: STRING,
        suppression_reason: STRING,
        suppression_type: STRING,
        unsuppression_reason: STRING,
        unsuppression_type: STRING,
        deletion_method: STRING,
        processed_at: TIMESTAMP,
        confirmation_id: STRING
    > COMMENT 'Event-specific properties based on event type',
    
    -- Historical data context
    previous_traits MAP<STRING, STRING> COMMENT 'User traits before this event',
    new_traits MAP<STRING, STRING> COMMENT 'User traits after this event',
    
    -- GDPR and compliance tracking
    gdpr_request_id STRING COMMENT 'GDPR request identifier for compliance events',
    compliance_type STRING COMMENT 'Type of compliance action (gdpr_right_to_be_forgotten, etc.)',
    
    -- Timestamps and metadata
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the event occurred',
    processed_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the event was processed',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the event',
    
    -- Data lineage
    source_system STRING COMMENT 'System that triggered this event',
    integration_id STRING COMMENT 'Integration that processed this event',
    api_call_id STRING COMMENT 'API call identifier that generated this event',
    
    CONSTRAINT pk_people_events PRIMARY KEY (event_id),
    CONSTRAINT fk_people_events_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/people_events'
COMMENT 'People lifecycle events tracking user management actions (deletion, suppression, etc.)'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.event_type_valid' = 'event_type IN ("identified", "deleted", "suppressed", "unsuppressed", "updated")'
);

-- User traits history table for tracking changes over time
CREATE TABLE IF NOT EXISTS customerio.people_traits_history (
    -- Record identification
    history_id STRING NOT NULL COMMENT 'Unique identifier for this history record',
    user_id STRING NOT NULL COMMENT 'User this history record relates to',
    
    -- Trait change tracking
    trait_name STRING NOT NULL COMMENT 'Name of the trait that changed',
    old_value STRING COMMENT 'Previous value of the trait',
    new_value STRING COMMENT 'New value of the trait',
    value_type STRING COMMENT 'Data type of the trait value (string, number, boolean, object, array)',
    
    -- Change metadata
    change_type STRING NOT NULL COMMENT 'Type of change (created, updated, deleted)',
    change_reason STRING COMMENT 'Reason for the change (user_update, migration, etc.)',
    
    -- Timestamps
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the trait changed',
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When this trait value became effective',
    effective_to TIMESTAMP COMMENT 'When this trait value was superseded (NULL for current)',
    
    -- Data lineage
    source_system STRING COMMENT 'System that made this change',
    api_call_id STRING COMMENT 'API call that triggered this change',
    
    CONSTRAINT pk_people_traits_history PRIMARY KEY (history_id),
    CONSTRAINT fk_traits_history_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/people_traits_history'
COMMENT 'Historical tracking of user trait changes for audit and analysis'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.trait_name_not_null' = 'trait_name IS NOT NULL'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_people_email ON customerio.people(email);
CREATE INDEX IF NOT EXISTS idx_people_plan ON customerio.people(plan);
CREATE INDEX IF NOT EXISTS idx_people_status ON customerio.people(status);
CREATE INDEX IF NOT EXISTS idx_people_suppressed ON customerio.people(is_suppressed);
CREATE INDEX IF NOT EXISTS idx_people_created_at ON customerio.people(created_at);

CREATE INDEX IF NOT EXISTS idx_people_events_user_id ON customerio.people_events(user_id);
CREATE INDEX IF NOT EXISTS idx_people_events_type ON customerio.people_events(event_type);
CREATE INDEX IF NOT EXISTS idx_people_events_timestamp ON customerio.people_events(event_timestamp);

CREATE INDEX IF NOT EXISTS idx_traits_history_user_id ON customerio.people_traits_history(user_id);
CREATE INDEX IF NOT EXISTS idx_traits_history_trait_name ON customerio.people_traits_history(trait_name);
CREATE INDEX IF NOT EXISTS idx_traits_history_changed_at ON customerio.people_traits_history(changed_at);