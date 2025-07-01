-- ==================================================
-- Customer.IO User Aliases and Profile Merging Data Models
-- ==================================================
-- Based on actual data structures from integration tests
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- User aliases table for tracking profile aliases and merges
CREATE TABLE IF NOT EXISTS customerio.user_aliases (
    -- Alias identification
    alias_id STRING NOT NULL COMMENT 'Unique identifier for this alias relationship',
    primary_user_id STRING NOT NULL COMMENT 'Primary user ID (the canonical identifier)',
    secondary_user_id STRING NOT NULL COMMENT 'Secondary user ID being aliased to primary',
    
    -- Alias classification
    alias_type STRING NOT NULL COMMENT 'Type of alias (profile_merge, anonymous_merge, identity_alias)',
    alias_direction STRING DEFAULT 'secondary_to_primary' COMMENT 'Direction of alias (secondary_to_primary, bidirectional)',
    
    -- Alias metadata
    alias_reason STRING COMMENT 'Reason for creating alias (user_merge, anonymous_identification, duplicate_cleanup)',
    alias_source STRING COMMENT 'Source that created alias (api, sdk, manual, automated_deduplication)',
    
    -- User identification details
    primary_user_type STRING COMMENT 'Type of primary user (known, registered, identified)',
    secondary_user_type STRING COMMENT 'Type of secondary user (anonymous, temp, duplicate)',
    
    -- Anonymous tracking support
    anonymous_id STRING COMMENT 'Anonymous ID if secondary user was anonymous',
    device_id STRING COMMENT 'Device ID associated with anonymous user',
    session_id STRING COMMENT 'Session ID when alias was created',
    
    -- Merge operation details
    merge_strategy STRING COMMENT 'Strategy used for merging (traits_merge, events_migrate, full_consolidation)',
    conflicts_resolution STRING COMMENT 'How conflicts were resolved (primary_wins, secondary_wins, merge_values)',
    
    -- Data preservation tracking
    traits_merged BOOLEAN DEFAULT FALSE COMMENT 'Whether user traits were merged',
    events_migrated BOOLEAN DEFAULT FALSE COMMENT 'Whether events were migrated to primary user',
    devices_migrated BOOLEAN DEFAULT FALSE COMMENT 'Whether devices were migrated',
    objects_migrated BOOLEAN DEFAULT FALSE COMMENT 'Whether objects/relationships were migrated',
    
    -- Alias chain tracking
    is_chain_root BOOLEAN DEFAULT FALSE COMMENT 'Whether this is the root of an alias chain',
    chain_depth INT DEFAULT 1 COMMENT 'Depth in alias chain (1 = direct alias)',
    parent_alias_id STRING COMMENT 'Parent alias if this is part of a chain',
    ultimate_primary_user_id STRING COMMENT 'Ultimate canonical user ID at end of chain',
    
    -- Special ID handling
    has_special_characters BOOLEAN DEFAULT FALSE COMMENT 'Whether user IDs contain special characters',
    id_format_type STRING COMMENT 'Format type of user IDs (email, uuid, custom, encoded)',
    normalization_applied BOOLEAN DEFAULT FALSE COMMENT 'Whether ID normalization was applied',
    
    -- Validation and quality
    alias_validated BOOLEAN DEFAULT FALSE COMMENT 'Whether alias relationship was validated',
    validation_method STRING COMMENT 'Method used to validate alias (email_match, device_match, manual)',
    confidence_score DOUBLE COMMENT 'Confidence score for alias accuracy (0.0 to 1.0)',
    
    -- Timestamps and history
    alias_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When alias was created',
    alias_effective_at TIMESTAMP COMMENT 'When alias becomes effective (for historical aliases)',
    custom_timestamp TIMESTAMP COMMENT 'Custom timestamp provided for historical aliasing',
    
    -- Status and lifecycle
    alias_status STRING DEFAULT 'active' COMMENT 'Status (active, inactive, pending, failed)',
    activated_at TIMESTAMP COMMENT 'When alias was activated',
    deactivated_at TIMESTAMP COMMENT 'When alias was deactivated',
    deactivation_reason STRING COMMENT 'Reason for deactivation',
    
    -- Processing tracking
    processing_status STRING DEFAULT 'completed' COMMENT 'Processing status (pending, processing, completed, failed)',
    processing_started_at TIMESTAMP COMMENT 'When processing started',
    processing_completed_at TIMESTAMP COMMENT 'When processing completed',
    processing_errors ARRAY<STRING> COMMENT 'List of processing errors',
    
    -- Complex alias properties from integration tests
    alias_properties STRUCT<
        primary_email: STRING,
        secondary_email: STRING,
        signup_date_primary: STRING,
        signup_date_secondary: STRING,
        role_primary: STRING,
        role_secondary: STRING,
        index: INT,
        special_id: BOOLEAN,
        after_alias: BOOLEAN
    > COMMENT 'Complex alias properties from integration tests',
    
    -- User context at time of alias
    user_context STRUCT<
        primary_traits_count: INT,
        secondary_traits_count: INT,
        primary_events_count: INT,
        secondary_events_count: INT,
        devices_count: INT,
        objects_count: INT
    > COMMENT 'User data context when alias was created',
    
    -- Merge statistics
    merge_statistics STRUCT<
        traits_merged_count: INT,
        events_migrated_count: INT,
        conflicts_resolved_count: INT,
        data_loss_incidents: INT,
        merge_duration_seconds: DOUBLE
    > COMMENT 'Statistics about the merge operation',
    
    -- Data lineage
    source_system STRING COMMENT 'System that created this alias',
    integration_id STRING COMMENT 'Integration identifier',
    created_by_user STRING COMMENT 'User or system that created alias',
    
    CONSTRAINT pk_user_aliases PRIMARY KEY (alias_id),
    CONSTRAINT fk_aliases_primary_user FOREIGN KEY (primary_user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT fk_aliases_secondary_user FOREIGN KEY (secondary_user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT fk_aliases_parent FOREIGN KEY (parent_alias_id) REFERENCES customerio.user_aliases(alias_id),
    CONSTRAINT chk_different_user_ids CHECK (primary_user_id != secondary_user_id),
    CONSTRAINT chk_valid_confidence_score CHECK (confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)),
    CONSTRAINT chk_positive_chain_depth CHECK (chain_depth > 0)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/user_aliases'
COMMENT 'User aliases table for tracking profile merges and identity resolution'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.alias_id_not_null' = 'alias_id IS NOT NULL',
    'quality.expectations.primary_user_id_not_null' = 'primary_user_id IS NOT NULL',
    'quality.expectations.secondary_user_id_not_null' = 'secondary_user_id IS NOT NULL',
    'quality.expectations.different_user_ids' = 'primary_user_id != secondary_user_id',
    'quality.expectations.valid_alias_type' = 'alias_type IN ("profile_merge", "anonymous_merge", "identity_alias", "duplicate_consolidation")'
);

-- Alias events table for tracking alias-related events
CREATE TABLE IF NOT EXISTS customerio.alias_events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this alias event',
    alias_id STRING NOT NULL COMMENT 'Alias this event relates to',
    
    -- Event details
    event_type STRING NOT NULL COMMENT 'Type of alias event (alias_created, alias_activated, merge_completed, chain_extended)',
    event_name STRING COMMENT 'Specific event name (Profile Merged, Anonymous User Identified)',
    
    -- User identification
    primary_user_id STRING NOT NULL COMMENT 'Primary user in the alias',
    secondary_user_id STRING NOT NULL COMMENT 'Secondary user in the alias',
    affected_user_ids ARRAY<STRING> COMMENT 'All user IDs affected by this event',
    
    -- Event properties
    event_properties STRUCT<
        alias_type: STRING,
        merge_strategy: STRING,
        data_migrated: BOOLEAN,
        conflicts_detected: INT,
        processing_duration_ms: BIGINT,
        validation_passed: BOOLEAN
    > COMMENT 'Properties specific to alias events',
    
    -- Migration details
    data_migration_summary STRUCT<
        traits_migrated: INT,
        events_migrated: INT,
        devices_migrated: INT,
        objects_migrated: INT,
        relationships_migrated: INT
    > COMMENT 'Summary of data migration performed',
    
    -- Before/after state
    user_state_before STRUCT<
        primary_traits_count: INT,
        secondary_traits_count: INT,
        total_events_count: INT
    > COMMENT 'User state before alias operation',
    
    user_state_after STRUCT<
        merged_traits_count: INT,
        total_events_count: INT,
        consolidated_profiles: INT
    > COMMENT 'User state after alias operation',
    
    -- Processing details
    processing_method STRING COMMENT 'Method used for processing (real_time, batch, background)',
    processing_priority STRING COMMENT 'Processing priority (high, normal, low)',
    
    -- Error tracking
    errors_encountered ARRAY<STRING> COMMENT 'List of errors during alias processing',
    warnings_generated ARRAY<STRING> COMMENT 'List of warnings during processing',
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the alias event occurred',
    processing_started_at TIMESTAMP COMMENT 'When processing started',
    processing_completed_at TIMESTAMP COMMENT 'When processing completed',
    
    -- Data lineage
    source_system STRING COMMENT 'System that generated this alias event',
    integration_id STRING COMMENT 'Integration identifier',
    triggered_by STRING COMMENT 'What triggered this alias event',
    
    CONSTRAINT pk_alias_events PRIMARY KEY (event_id),
    CONSTRAINT fk_alias_events_alias FOREIGN KEY (alias_id) REFERENCES customerio.user_aliases(alias_id),
    CONSTRAINT fk_alias_events_primary_user FOREIGN KEY (primary_user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT fk_alias_events_secondary_user FOREIGN KEY (secondary_user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/alias_events'
COMMENT 'Alias events table for tracking alias-related operations and changes'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.event_id_not_null' = 'event_id IS NOT NULL',
    'quality.expectations.alias_id_not_null' = 'alias_id IS NOT NULL',
    'quality.expectations.valid_event_type' = 'event_type IN ("alias_created", "alias_activated", "merge_completed", "chain_extended", "alias_failed")'
);

-- Anonymous identity resolution table for tracking anonymous-to-known user mapping
CREATE TABLE IF NOT EXISTS customerio.anonymous_identity_resolution (
    -- Resolution identification
    resolution_id STRING NOT NULL COMMENT 'Unique identifier for this identity resolution',
    anonymous_id STRING NOT NULL COMMENT 'Anonymous identifier (cookie, device ID, etc.)',
    resolved_user_id STRING NOT NULL COMMENT 'Resolved known user ID',
    
    -- Resolution details
    resolution_method STRING NOT NULL COMMENT 'How identity was resolved (email_match, device_fingerprint, login_event)',
    resolution_confidence DOUBLE COMMENT 'Confidence in resolution accuracy (0.0 to 1.0)',
    resolution_source STRING COMMENT 'Source of resolution (user_action, algorithm, manual)',
    
    -- Anonymous context
    anonymous_session_count INT DEFAULT 0 COMMENT 'Number of anonymous sessions',
    anonymous_events_count INT DEFAULT 0 COMMENT 'Number of events under anonymous ID',
    anonymous_first_seen TIMESTAMP COMMENT 'When anonymous ID was first seen',
    anonymous_last_seen TIMESTAMP COMMENT 'When anonymous ID was last seen',
    
    -- Device and session context
    device_fingerprint STRING COMMENT 'Device fingerprint used for resolution',
    user_agent STRING COMMENT 'User agent string',
    ip_address_hash STRING COMMENT 'Hashed IP address',
    session_ids ARRAY<STRING> COMMENT 'Session IDs associated with anonymous user',
    
    -- Resolution trigger
    trigger_event STRING COMMENT 'Event that triggered resolution (login, signup, email_click)',
    trigger_timestamp TIMESTAMP COMMENT 'When resolution was triggered',
    trigger_properties MAP<STRING, STRING> COMMENT 'Properties of trigger event',
    
    -- Data migration tracking
    events_migrated BOOLEAN DEFAULT FALSE COMMENT 'Whether anonymous events were migrated',
    traits_merged BOOLEAN DEFAULT FALSE COMMENT 'Whether anonymous traits were merged',
    devices_transferred BOOLEAN DEFAULT FALSE COMMENT 'Whether devices were transferred',
    
    -- Quality and validation
    validation_checks ARRAY<STRING> COMMENT 'Validation checks performed',
    validation_passed BOOLEAN DEFAULT FALSE COMMENT 'Whether validation passed',
    false_positive_risk DOUBLE COMMENT 'Risk of false positive match (0.0 to 1.0)',
    
    -- Business context
    marketing_attribution STRUCT<
        campaign_source: STRING,
        campaign_medium: STRING,
        campaign_name: STRING,
        first_touch_channel: STRING,
        last_touch_channel: STRING
    > COMMENT 'Marketing attribution data from anonymous sessions',
    
    -- Resolution lifecycle
    resolution_status STRING DEFAULT 'active' COMMENT 'Status (active, inactive, disputed, reversed)',
    resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When resolution was completed',
    reviewed_at TIMESTAMP COMMENT 'When resolution was manually reviewed',
    reviewed_by STRING COMMENT 'Who reviewed the resolution',
    
    CONSTRAINT pk_anonymous_resolution PRIMARY KEY (resolution_id),
    CONSTRAINT fk_resolution_user FOREIGN KEY (resolved_user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT chk_valid_confidence CHECK (resolution_confidence IS NULL OR (resolution_confidence >= 0.0 AND resolution_confidence <= 1.0)),
    CONSTRAINT chk_valid_false_positive_risk CHECK (false_positive_risk IS NULL OR (false_positive_risk >= 0.0 AND false_positive_risk <= 1.0))
)
USING DELTA
LOCATION 's3://your-bucket/customerio/anonymous_identity_resolution'
COMMENT 'Anonymous identity resolution table for tracking anonymous-to-known user mapping'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.resolution_id_not_null' = 'resolution_id IS NOT NULL',
    'quality.expectations.anonymous_id_not_null' = 'anonymous_id IS NOT NULL',
    'quality.expectations.resolved_user_id_not_null' = 'resolved_user_id IS NOT NULL'
);

-- Alias chains table for managing complex alias relationships
CREATE TABLE IF NOT EXISTS customerio.alias_chains (
    -- Chain identification
    chain_id STRING NOT NULL COMMENT 'Unique identifier for this alias chain',
    root_user_id STRING NOT NULL COMMENT 'Root (canonical) user ID at the end of chain',
    
    -- Chain metadata
    chain_depth INT NOT NULL COMMENT 'Number of levels in the chain',
    total_aliases INT NOT NULL COMMENT 'Total number of aliases in chain',
    chain_type STRING COMMENT 'Type of chain (linear, tree, complex)',
    
    -- Chain members
    user_ids_in_chain ARRAY<STRING> COMMENT 'All user IDs that are part of this chain',
    alias_ids_in_chain ARRAY<STRING> COMMENT 'All alias IDs that form this chain',
    
    -- Chain statistics
    oldest_alias_date TIMESTAMP COMMENT 'Date of oldest alias in chain',
    newest_alias_date TIMESTAMP COMMENT 'Date of newest alias in chain',
    chain_formation_duration_days INT COMMENT 'Days it took to form complete chain',
    
    -- Data consolidation status
    consolidation_status STRING DEFAULT 'pending' COMMENT 'Status of data consolidation (pending, in_progress, completed)',
    consolidated_events_count INT DEFAULT 0 COMMENT 'Number of events consolidated',
    consolidated_traits_count INT DEFAULT 0 COMMENT 'Number of traits consolidated',
    
    -- Quality metrics
    chain_confidence_score DOUBLE COMMENT 'Overall confidence in chain accuracy (0.0 to 1.0)',
    weak_links_count INT DEFAULT 0 COMMENT 'Number of weak/uncertain links in chain',
    validation_required BOOLEAN DEFAULT FALSE COMMENT 'Whether chain requires manual validation',
    
    -- Chain management
    auto_created BOOLEAN DEFAULT TRUE COMMENT 'Whether chain was automatically created',
    manually_verified BOOLEAN DEFAULT FALSE COMMENT 'Whether chain was manually verified',
    created_by_system STRING COMMENT 'System that created the chain',
    
    -- Timestamps
    chain_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When chain was first created',
    chain_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When chain was last updated',
    last_validation_at TIMESTAMP COMMENT 'When chain was last validated',
    
    CONSTRAINT pk_alias_chains PRIMARY KEY (chain_id),
    CONSTRAINT fk_alias_chains_root_user FOREIGN KEY (root_user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT chk_positive_chain_depth CHECK (chain_depth > 0),
    CONSTRAINT chk_positive_total_aliases CHECK (total_aliases > 0),
    CONSTRAINT chk_valid_chain_confidence CHECK (chain_confidence_score IS NULL OR (chain_confidence_score >= 0.0 AND chain_confidence_score <= 1.0))
)
USING DELTA
LOCATION 's3://your-bucket/customerio/alias_chains'
COMMENT 'Alias chains table for managing complex multi-level alias relationships'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.chain_id_not_null' = 'chain_id IS NOT NULL',
    'quality.expectations.root_user_id_not_null' = 'root_user_id IS NOT NULL',
    'quality.expectations.positive_chain_depth' = 'chain_depth > 0'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_user_aliases_primary_user ON customerio.user_aliases(primary_user_id);
CREATE INDEX IF NOT EXISTS idx_user_aliases_secondary_user ON customerio.user_aliases(secondary_user_id);
CREATE INDEX IF NOT EXISTS idx_user_aliases_type ON customerio.user_aliases(alias_type);
CREATE INDEX IF NOT EXISTS idx_user_aliases_status ON customerio.user_aliases(alias_status);
CREATE INDEX IF NOT EXISTS idx_user_aliases_created_at ON customerio.user_aliases(alias_created_at);

CREATE INDEX IF NOT EXISTS idx_alias_events_alias_id ON customerio.alias_events(alias_id);
CREATE INDEX IF NOT EXISTS idx_alias_events_primary_user ON customerio.alias_events(primary_user_id);
CREATE INDEX IF NOT EXISTS idx_alias_events_type ON customerio.alias_events(event_type);
CREATE INDEX IF NOT EXISTS idx_alias_events_timestamp ON customerio.alias_events(event_timestamp);

CREATE INDEX IF NOT EXISTS idx_anonymous_resolution_anonymous_id ON customerio.anonymous_identity_resolution(anonymous_id);
CREATE INDEX IF NOT EXISTS idx_anonymous_resolution_user_id ON customerio.anonymous_identity_resolution(resolved_user_id);
CREATE INDEX IF NOT EXISTS idx_anonymous_resolution_method ON customerio.anonymous_identity_resolution(resolution_method);
CREATE INDEX IF NOT EXISTS idx_anonymous_resolution_resolved_at ON customerio.anonymous_identity_resolution(resolved_at);

CREATE INDEX IF NOT EXISTS idx_alias_chains_root_user ON customerio.alias_chains(root_user_id);
CREATE INDEX IF NOT EXISTS idx_alias_chains_depth ON customerio.alias_chains(chain_depth);
CREATE INDEX IF NOT EXISTS idx_alias_chains_status ON customerio.alias_chains(consolidation_status);
CREATE INDEX IF NOT EXISTS idx_alias_chains_created_at ON customerio.alias_chains(chain_created_at);