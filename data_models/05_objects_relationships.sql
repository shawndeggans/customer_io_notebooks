-- ==================================================
-- Customer.IO Objects and Relationships Data Models
-- ==================================================
-- Based on actual data structures from integration tests  
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- Objects table for non-people entities (companies, accounts, products, etc.)
CREATE TABLE IF NOT EXISTS customerio.objects (
    -- Object identification
    object_id STRING NOT NULL COMMENT 'Unique identifier for this object',
    object_type_id INT DEFAULT 1 COMMENT 'Type ID for the object (1=default, can be configured in Customer.IO)',
    object_type STRING COMMENT 'Descriptive type name (company, account, product, class)',
    
    -- Object attributes from integration tests
    name STRING COMMENT 'Object name (Test Product, Original Product)',
    description STRING COMMENT 'Object description',
    category STRING COMMENT 'Object category (electronics)',
    
    -- Common object properties
    status STRING COMMENT 'Object status (draft, published, active, inactive)',
    price DOUBLE COMMENT 'Object price if applicable (299.99)',
    in_stock BOOLEAN COMMENT 'Stock status if applicable',
    
    -- Timestamps and lifecycle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When object was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When object was last updated',
    last_modified TIMESTAMP COMMENT 'Custom last modified timestamp from traits',
    deleted_at TIMESTAMP COMMENT 'When object was soft deleted',
    
    -- Additional object traits
    custom_traits MAP<STRING, STRING> COMMENT 'Additional object properties as key-value pairs',
    traits_json STRING COMMENT 'Complete object traits as JSON for complex nested data',
    
    -- Nested object properties
    properties STRUCT<
        name: STRING,
        category: STRING,
        price: DOUBLE,
        in_stock: BOOLEAN,
        status: STRING,
        metadata: MAP<STRING, STRING>
    > COMMENT 'Structured object properties from integration tests',
    
    -- Data lineage
    source_system STRING COMMENT 'System that created this object',
    integration_id STRING COMMENT 'Integration identifier',
    created_by_user_id STRING COMMENT 'User who created this object',
    
    CONSTRAINT pk_objects PRIMARY KEY (object_id, object_type_id),
    CONSTRAINT fk_objects_creator FOREIGN KEY (created_by_user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/objects'
COMMENT 'Objects table storing non-people entities like companies, accounts, products'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.object_id_not_null' = 'object_id IS NOT NULL',
    'quality.expectations.object_type_id_positive' = 'object_type_id > 0'
);

-- Relationships table for connecting people to objects
CREATE TABLE IF NOT EXISTS customerio.relationships (
    -- Relationship identification
    relationship_id STRING NOT NULL COMMENT 'Unique identifier for this relationship',
    user_id STRING NOT NULL COMMENT 'User in this relationship',
    object_id STRING NOT NULL COMMENT 'Object in this relationship',
    object_type_id INT DEFAULT 1 COMMENT 'Type ID of the related object',
    
    -- Relationship metadata
    relationship_type STRING COMMENT 'Type of relationship (owner, member, admin, viewer)',
    relationship_status STRING DEFAULT 'active' COMMENT 'Status of relationship (active, inactive, pending)',
    
    -- Relationship properties
    role STRING COMMENT 'User role in relation to object',
    permissions ARRAY<STRING> COMMENT 'Permissions user has on this object',
    relationship_data MAP<STRING, STRING> COMMENT 'Additional relationship-specific data',
    
    -- Relationship context
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When relationship was established',
    ended_at TIMESTAMP COMMENT 'When relationship ended (NULL for active relationships)',
    invited_at TIMESTAMP COMMENT 'When user was invited to this relationship',
    accepted_at TIMESTAMP COMMENT 'When user accepted the relationship',
    
    -- Relationship lifecycle tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When relationship record was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When relationship was last updated',
    
    -- Data lineage
    created_by_user_id STRING COMMENT 'User who created this relationship',
    source_system STRING COMMENT 'System that created this relationship',
    integration_id STRING COMMENT 'Integration identifier',
    
    CONSTRAINT pk_relationships PRIMARY KEY (relationship_id),
    CONSTRAINT fk_relationships_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT fk_relationships_object FOREIGN KEY (object_id, object_type_id) REFERENCES customerio.objects(object_id, object_type_id),
    CONSTRAINT fk_relationships_creator FOREIGN KEY (created_by_user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/relationships'
COMMENT 'Relationships table connecting people to objects (companies, accounts, etc.)'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.object_id_not_null' = 'object_id IS NOT NULL'
);

-- Object events table for tracking object lifecycle
CREATE TABLE IF NOT EXISTS customerio.object_events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this object event',
    object_id STRING NOT NULL COMMENT 'Object this event relates to',
    object_type_id INT DEFAULT 1 COMMENT 'Type ID of the object',
    user_id STRING COMMENT 'User who triggered this event (if applicable)',
    
    -- Event details
    event_type STRING NOT NULL COMMENT 'Type of object event (created, updated, deleted)',
    event_name STRING COMMENT 'Specific event name (Object Deleted, etc.)',
    
    -- Event properties
    event_properties STRUCT<
        deletion_reason: STRING,
        update_reason: STRING,
        status_change: STRING,
        triggered_by: STRING
    > COMMENT 'Event-specific properties',
    
    -- Object state changes
    previous_traits MAP<STRING, STRING> COMMENT 'Object traits before this event',
    new_traits MAP<STRING, STRING> COMMENT 'Object traits after this event',
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the object event occurred',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the event',
    
    -- Data lineage
    source_system STRING COMMENT 'System that generated this event',
    integration_id STRING COMMENT 'Integration identifier',
    api_call_id STRING COMMENT 'API call that triggered this event',
    
    CONSTRAINT pk_object_events PRIMARY KEY (event_id),
    CONSTRAINT fk_object_events_object FOREIGN KEY (object_id, object_type_id) REFERENCES customerio.objects(object_id, object_type_id),
    CONSTRAINT fk_object_events_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/object_events'
COMMENT 'Object events table tracking object lifecycle and changes'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.object_id_not_null' = 'object_id IS NOT NULL',
    'quality.expectations.event_type_valid' = 'event_type IN ("created", "updated", "deleted", "activated", "deactivated")'
);

-- Relationship events table for tracking relationship changes
CREATE TABLE IF NOT EXISTS customerio.relationship_events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this relationship event',
    relationship_id STRING COMMENT 'Relationship this event relates to (if existing)',
    user_id STRING NOT NULL COMMENT 'User involved in this relationship event',
    object_id STRING NOT NULL COMMENT 'Object involved in this relationship event',
    object_type_id INT DEFAULT 1 COMMENT 'Type ID of the object',
    
    -- Event details
    event_type STRING NOT NULL COMMENT 'Type of relationship event (created, updated, deleted)',
    event_name STRING COMMENT 'Specific event name (Relationship Deleted, etc.)',
    
    -- Relationship change details
    relationship_type STRING COMMENT 'Type of relationship affected',
    previous_role STRING COMMENT 'User role before this event',
    new_role STRING COMMENT 'User role after this event',
    
    -- Event properties
    event_properties STRUCT<
        deletion_reason: STRING,
        role_change_reason: STRING,
        invited_by: STRING,
        permission_changes: ARRAY<STRING>
    > COMMENT 'Event-specific properties',
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the relationship event occurred',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the event',
    
    -- Data lineage
    source_system STRING COMMENT 'System that generated this event',
    integration_id STRING COMMENT 'Integration identifier',
    triggered_by_user_id STRING COMMENT 'User who triggered this event',
    
    CONSTRAINT pk_relationship_events PRIMARY KEY (event_id),
    CONSTRAINT fk_rel_events_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT fk_rel_events_object FOREIGN KEY (object_id, object_type_id) REFERENCES customerio.objects(object_id, object_type_id),
    CONSTRAINT fk_rel_events_relationship FOREIGN KEY (relationship_id) REFERENCES customerio.relationships(relationship_id),
    CONSTRAINT fk_rel_events_triggered_by FOREIGN KEY (triggered_by_user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/relationship_events'
COMMENT 'Relationship events table tracking relationship lifecycle and changes'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.object_id_not_null' = 'object_id IS NOT NULL'
);

-- Object types lookup table for managing object classifications
CREATE TABLE IF NOT EXISTS customerio.object_types (
    -- Type identification
    object_type_id INT NOT NULL COMMENT 'Unique type identifier',
    
    -- Type definition
    type_name STRING NOT NULL COMMENT 'Name of the object type (company, account, product)',
    type_description STRING COMMENT 'Description of what this object type represents',
    
    -- Type configuration
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Whether this object type is active',
    default_permissions ARRAY<STRING> COMMENT 'Default permissions for relationships with this type',
    required_traits ARRAY<STRING> COMMENT 'Required traits for objects of this type',
    
    -- Schema definition
    trait_schema MAP<STRING, STRING> COMMENT 'Schema definition for object traits',
    validation_rules ARRAY<STRING> COMMENT 'Validation rules for this object type',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When object type was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When object type was last updated',
    
    CONSTRAINT pk_object_types PRIMARY KEY (object_type_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/object_types'
COMMENT 'Object types lookup table for object classification and schema definition'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.object_type_id_positive' = 'object_type_id > 0',
    'quality.expectations.type_name_not_null' = 'type_name IS NOT NULL'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_objects_type_id ON customerio.objects(object_type_id);
CREATE INDEX IF NOT EXISTS idx_objects_type ON customerio.objects(object_type);
CREATE INDEX IF NOT EXISTS idx_objects_status ON customerio.objects(status);
CREATE INDEX IF NOT EXISTS idx_objects_created_at ON customerio.objects(created_at);

CREATE INDEX IF NOT EXISTS idx_relationships_user_id ON customerio.relationships(user_id);
CREATE INDEX IF NOT EXISTS idx_relationships_object ON customerio.relationships(object_id, object_type_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON customerio.relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationships_status ON customerio.relationships(relationship_status);

CREATE INDEX IF NOT EXISTS idx_object_events_object ON customerio.object_events(object_id, object_type_id);
CREATE INDEX IF NOT EXISTS idx_object_events_user_id ON customerio.object_events(user_id);
CREATE INDEX IF NOT EXISTS idx_object_events_type ON customerio.object_events(event_type);
CREATE INDEX IF NOT EXISTS idx_object_events_timestamp ON customerio.object_events(event_timestamp);

CREATE INDEX IF NOT EXISTS idx_rel_events_user_id ON customerio.relationship_events(user_id);
CREATE INDEX IF NOT EXISTS idx_rel_events_object ON customerio.relationship_events(object_id, object_type_id);
CREATE INDEX IF NOT EXISTS idx_rel_events_relationship ON customerio.relationship_events(relationship_id);
CREATE INDEX IF NOT EXISTS idx_rel_events_timestamp ON customerio.relationship_events(event_timestamp);