-- ==================================================
-- Customer.IO Device Management Data Models
-- ==================================================
-- Based on actual data structures from integration tests
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- Devices table for device registration and management
CREATE TABLE IF NOT EXISTS customerio.devices (
    -- Device identification
    device_id STRING NOT NULL COMMENT 'Unique device identifier/token',
    device_token STRING COMMENT 'Push notification token for the device',
    user_id STRING NOT NULL COMMENT 'User who owns this device',
    
    -- Device classification
    device_type STRING NOT NULL COMMENT 'Type of device (ios, android)',
    platform STRING COMMENT 'Platform name (iOS, Android)',
    device_category STRING COMMENT 'Category of device (mobile, tablet, desktop)',
    
    -- Device hardware information
    model STRING COMMENT 'Device model (iPhone14,2, SM-G991B)',
    brand STRING COMMENT 'Device manufacturer (Apple, Samsung)',
    manufacturer STRING COMMENT 'Device manufacturer name',
    device_name STRING COMMENT 'User-assigned device name',
    
    -- Operating system information
    os_name STRING COMMENT 'Operating system name (iOS, Android)',
    os_version STRING COMMENT 'Operating system version (16.0.1, 13)',
    
    -- Application information
    app_version STRING COMMENT 'App version installed on device (2.1.0)',
    app_build STRING COMMENT 'App build number',
    app_name STRING COMMENT 'Application name',
    app_namespace STRING COMMENT 'Application namespace/bundle ID',
    
    -- Location and locale
    timezone STRING COMMENT 'Device timezone (America/New_York)',
    language STRING COMMENT 'Device language (en-US)',
    locale STRING COMMENT 'Device locale setting',
    country STRING COMMENT 'Device country setting',
    
    -- Device capabilities
    push_enabled BOOLEAN DEFAULT TRUE COMMENT 'Whether push notifications are enabled',
    location_enabled BOOLEAN COMMENT 'Whether location services are enabled',
    bluetooth_enabled BOOLEAN COMMENT 'Whether Bluetooth is enabled',
    
    -- Network information
    carrier STRING COMMENT 'Mobile carrier name',
    network_type STRING COMMENT 'Network type (wifi, cellular, etc.)',
    ip_address STRING COMMENT 'Device IP address',
    
    -- Additional metadata
    metadata STRUCT<
        app_version: STRING,
        os_version: STRING,
        model: STRING,
        timezone: STRING,
        language: STRING,
        brand: STRING,
        screen_resolution: STRING,
        memory_total: BIGINT,
        storage_total: BIGINT,
        custom_properties: MAP<STRING, STRING>
    > COMMENT 'Complete device metadata from integration tests',
    
    -- Device status and lifecycle
    status STRING DEFAULT 'active' COMMENT 'Device status (active, inactive, unregistered)',
    is_test_device BOOLEAN DEFAULT FALSE COMMENT 'Whether this is a test device',
    last_seen_at TIMESTAMP COMMENT 'When device was last seen/active',
    
    -- Registration and lifecycle timestamps
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When device was first registered',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When device info was last updated',
    unregistered_at TIMESTAMP COMMENT 'When device was unregistered/deleted',
    
    -- Data lineage
    source_system STRING COMMENT 'System that registered this device',
    integration_id STRING COMMENT 'Integration identifier',
    registration_source STRING COMMENT 'How device was registered (sdk, api, manual)',
    
    CONSTRAINT pk_devices PRIMARY KEY (device_id),
    CONSTRAINT fk_devices_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/devices'
COMMENT 'Devices table storing mobile device registration and metadata'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.device_id_not_null' = 'device_id IS NOT NULL',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.device_type_valid' = 'device_type IN ("ios", "android", "web", "desktop")'
);

-- Device events table for device lifecycle tracking
CREATE TABLE IF NOT EXISTS customerio.device_events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this device event',
    device_id STRING NOT NULL COMMENT 'Device this event relates to',
    user_id STRING NOT NULL COMMENT 'User who owns the device',
    
    -- Event details
    event_type STRING NOT NULL COMMENT 'Type of device event (registered, updated, deleted, activated)',
    event_name STRING COMMENT 'Specific event name (Device Created or Updated, Device Deleted)',
    
    -- Device state changes
    previous_metadata STRUCT<
        app_version: STRING,
        os_version: STRING,
        status: STRING,
        last_seen: TIMESTAMP
    > COMMENT 'Device state before this event',
    
    new_metadata STRUCT<
        app_version: STRING,
        os_version: STRING,
        status: STRING,
        last_seen: TIMESTAMP
    > COMMENT 'Device state after this event',
    
    -- Event-specific properties
    event_properties STRUCT<
        device_token: STRING,
        device_type: STRING,
        registration_source: STRING,
        deletion_reason: STRING,
        update_reason: STRING
    > COMMENT 'Properties specific to the device event',
    
    -- Context information
    app_version STRING COMMENT 'App version when event occurred',
    os_version STRING COMMENT 'OS version when event occurred',
    triggered_by STRING COMMENT 'What triggered this event (user_action, sdk, system)',
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the device event occurred',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the event',
    
    -- Data lineage
    source_system STRING COMMENT 'System that generated this event',
    integration_id STRING COMMENT 'Integration identifier',
    api_call_id STRING COMMENT 'API call that triggered this event',
    
    CONSTRAINT pk_device_events PRIMARY KEY (event_id),
    CONSTRAINT fk_device_events_device FOREIGN KEY (device_id) REFERENCES customerio.devices(device_id),
    CONSTRAINT fk_device_events_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/device_events'
COMMENT 'Device events table tracking device lifecycle and changes'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.device_id_not_null' = 'device_id IS NOT NULL',
    'quality.expectations.event_type_valid' = 'event_type IN ("registered", "updated", "deleted", "activated", "deactivated")'
);

-- Push notification tokens table for managing notification delivery
CREATE TABLE IF NOT EXISTS customerio.push_tokens (
    -- Token identification
    token_id STRING NOT NULL COMMENT 'Unique identifier for this token record',
    device_id STRING NOT NULL COMMENT 'Device this token belongs to',
    user_id STRING NOT NULL COMMENT 'User who owns the device',
    
    -- Token information
    push_token STRING NOT NULL COMMENT 'Push notification token',
    token_type STRING COMMENT 'Type of token (apns, fcm, web_push)',
    platform STRING COMMENT 'Platform for this token (ios, android, web)',
    
    -- Token status
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Whether token is currently active',
    is_valid BOOLEAN DEFAULT TRUE COMMENT 'Whether token is valid for sending',
    last_validated_at TIMESTAMP COMMENT 'When token was last validated',
    
    -- Delivery tracking
    successful_deliveries INT DEFAULT 0 COMMENT 'Number of successful push deliveries',
    failed_deliveries INT DEFAULT 0 COMMENT 'Number of failed push deliveries',
    last_delivery_at TIMESTAMP COMMENT 'When last push was delivered to this token',
    last_failure_at TIMESTAMP COMMENT 'When last delivery failure occurred',
    failure_reason STRING COMMENT 'Reason for last delivery failure',
    
    -- Token lifecycle
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When token was first registered',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When token was last updated',
    expired_at TIMESTAMP COMMENT 'When token expired or became invalid',
    
    CONSTRAINT pk_push_tokens PRIMARY KEY (token_id),
    CONSTRAINT fk_push_tokens_device FOREIGN KEY (device_id) REFERENCES customerio.devices(device_id),
    CONSTRAINT fk_push_tokens_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/push_tokens'
COMMENT 'Push notification tokens for message delivery tracking'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.token_id_not_null' = 'token_id IS NOT NULL',
    'quality.expectations.push_token_not_null' = 'push_token IS NOT NULL'
);

-- Device sessions table for tracking app usage sessions
CREATE TABLE IF NOT EXISTS customerio.device_sessions (
    -- Session identification
    session_id STRING NOT NULL COMMENT 'Unique session identifier',
    device_id STRING NOT NULL COMMENT 'Device for this session',
    user_id STRING NOT NULL COMMENT 'User who owns the device',
    
    -- Session information
    session_start TIMESTAMP NOT NULL COMMENT 'When session started',
    session_end TIMESTAMP COMMENT 'When session ended (NULL for active sessions)',
    session_duration_seconds INT COMMENT 'Duration of session in seconds',
    
    -- App information during session
    app_version STRING COMMENT 'App version during this session',
    os_version STRING COMMENT 'OS version during this session',
    
    -- Session context
    entry_point STRING COMMENT 'How session was started (app_icon, push_notification, deeplink)',
    exit_point STRING COMMENT 'How session ended (background, crash, logout)',
    
    -- Activity metrics
    screen_views INT DEFAULT 0 COMMENT 'Number of screen views in session',
    events_tracked INT DEFAULT 0 COMMENT 'Number of events tracked in session',
    crashes INT DEFAULT 0 COMMENT 'Number of crashes during session',
    
    -- Network and location context
    network_type STRING COMMENT 'Network type during session (wifi, cellular)',
    country STRING COMMENT 'Country where session occurred',
    timezone STRING COMMENT 'Timezone during session',
    
    -- Session status
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Whether session is currently active',
    is_background BOOLEAN DEFAULT FALSE COMMENT 'Whether app was backgrounded',
    
    CONSTRAINT pk_device_sessions PRIMARY KEY (session_id),
    CONSTRAINT fk_sessions_device FOREIGN KEY (device_id) REFERENCES customerio.devices(device_id),
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/device_sessions'
COMMENT 'Device sessions for tracking app usage and engagement'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.session_id_not_null' = 'session_id IS NOT NULL',
    'quality.expectations.session_start_not_null' = 'session_start IS NOT NULL'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_devices_user_id ON customerio.devices(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_type ON customerio.devices(device_type);
CREATE INDEX IF NOT EXISTS idx_devices_status ON customerio.devices(status);
CREATE INDEX IF NOT EXISTS idx_devices_registered_at ON customerio.devices(registered_at);

CREATE INDEX IF NOT EXISTS idx_device_events_device_id ON customerio.device_events(device_id);
CREATE INDEX IF NOT EXISTS idx_device_events_user_id ON customerio.device_events(user_id);
CREATE INDEX IF NOT EXISTS idx_device_events_type ON customerio.device_events(event_type);
CREATE INDEX IF NOT EXISTS idx_device_events_timestamp ON customerio.device_events(event_timestamp);

CREATE INDEX IF NOT EXISTS idx_push_tokens_device_id ON customerio.push_tokens(device_id);
CREATE INDEX IF NOT EXISTS idx_push_tokens_user_id ON customerio.push_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_push_tokens_active ON customerio.push_tokens(is_active);

CREATE INDEX IF NOT EXISTS idx_sessions_device_id ON customerio.device_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON customerio.device_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start ON customerio.device_sessions(session_start);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON customerio.device_sessions(is_active);