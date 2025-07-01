-- ==================================================
-- Customer.IO Privacy and GDPR Compliance Data Models
-- ==================================================
-- Based on actual data structures from integration tests
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- GDPR compliance events table for all privacy-related events
CREATE TABLE IF NOT EXISTS customerio.gdpr_compliance_events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this GDPR compliance event',
    user_id STRING COMMENT 'User this compliance event relates to (may be null for system events)',
    
    -- Event classification
    event_type STRING NOT NULL COMMENT 'Type of compliance event (deletion, suppression, data_request, delivery)',
    event_name STRING NOT NULL COMMENT 'Specific event name (User Deleted, User Suppressed, Report Delivered, etc.)',
    
    -- Deletion event properties
    deletion_reason STRING COMMENT 'Reason for deletion (user_request, gdpr_compliance, right_to_be_forgotten)',
    deletion_method STRING COMMENT 'Method used for deletion (automated_compliance_system, manual_process)',
    processed_by STRING COMMENT 'Who/what processed the deletion (privacy_team, automated_system)',
    processed_at TIMESTAMP COMMENT 'When deletion was processed',
    confirmation_id STRING COMMENT 'Unique confirmation ID for deletion (GDPR_CONF_123)',
    
    -- Suppression event properties  
    suppression_reason STRING COMMENT 'Reason for suppression (user_request, marketing_preferences)',
    suppression_type STRING COMMENT 'Type of suppression (marketing_communications, all_communications)',
    unsuppression_reason STRING COMMENT 'Reason for unsuppression (user_consent_renewed, preference_update)',
    unsuppression_type STRING COMMENT 'Type of unsuppression (marketing_communications, specific_channels)',
    effective_date TIMESTAMP COMMENT 'When suppression/unsuppression becomes effective',
    requested_at TIMESTAMP COMMENT 'When user made the suppression/unsuppression request',
    
    -- Object/device deletion properties
    object_id STRING COMMENT 'Object identifier being deleted (OBJECT_TO_DELETE_123)',
    object_type STRING COMMENT 'Type of object (user_generated_content, personal_data)',
    device_id STRING COMMENT 'Device identifier being deleted (DEVICE_TO_DELETE_123)',
    device_type STRING COMMENT 'Type of device (ios, android)',
    relationship_id STRING COMMENT 'Relationship identifier being deleted (REL_TO_DELETE_123)',
    
    -- Report delivery properties
    report_id STRING COMMENT 'Report identifier (GDPR_REPORT_123)',
    report_type STRING COMMENT 'Type of report (data_export, deletion_confirmation, audit_log)',
    report_status STRING COMMENT 'Report status (processing, delivered, failed)',
    delivery_method STRING COMMENT 'How report was delivered (email, secure_download, portal)',
    file_format STRING COMMENT 'Format of delivered file (json, csv, pdf)',
    file_size_bytes BIGINT COMMENT 'Size of delivered file in bytes (15420)',
    
    -- Bulk operation tracking
    batch_id STRING COMMENT 'Batch identifier for bulk operations (BULK_SUPPRESS_123)',
    user_index INT COMMENT 'Index of user in batch operation',
    total_batch_size INT COMMENT 'Total number of users in batch',
    
    -- Compliance audit trail
    legal_basis STRING COMMENT 'Legal basis for processing (consent, legitimate_interest, legal_obligation)',
    retention_period_days INT COMMENT 'Data retention period in days',
    anonymization_method STRING COMMENT 'Method used for anonymization (hash, encrypt, remove)',
    
    -- Request tracking
    request_id STRING COMMENT 'Original privacy request identifier',
    request_type STRING COMMENT 'Type of privacy request (access, deletion, portability, rectification)',
    request_source STRING COMMENT 'Where request originated (user_portal, email, phone)',
    request_verification_method STRING COMMENT 'How request was verified (email, identity_document)',
    
    -- Data subject rights
    rights_exercised ARRAY<STRING> COMMENT 'Data subject rights exercised (right_to_be_forgotten, right_of_access)',
    consent_withdrawn ARRAY<STRING> COMMENT 'Types of consent withdrawn (marketing, analytics, personalization)',
    consent_granted ARRAY<STRING> COMMENT 'Types of consent granted (marketing, analytics)',
    
    -- Complex nested properties
    compliance_properties STRUCT<
        deletion_reason: STRING,
        deletion_method: STRING,
        processed_by: STRING,
        confirmation_id: STRING,
        suppression_reason: STRING,
        suppression_type: STRING,
        effective_date: STRING,
        is_historical: BOOLEAN,
        automated_processing: BOOLEAN
    > COMMENT 'Complete compliance properties from integration tests',
    
    -- Report delivery details
    delivery_properties STRUCT<
        report_type: STRING,
        delivery_method: STRING,
        file_format: STRING,
        file_size_bytes: BIGINT,
        download_expires_at: TIMESTAMP,
        access_key: STRING,
        encryption_method: STRING
    > COMMENT 'Report delivery specific properties',
    
    -- Raw event properties for flexibility
    raw_properties MAP<STRING, STRING> COMMENT 'All event properties as key-value pairs',
    
    -- Compliance metadata
    jurisdiction STRING COMMENT 'Legal jurisdiction (EU, CCPA, LGPD)',
    regulation_reference STRING COMMENT 'Specific regulation article reference (GDPR Article 17)',
    compliance_officer STRING COMMENT 'Compliance officer who approved action',
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the compliance event occurred',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the event',
    
    -- Data lineage
    source_system STRING COMMENT 'System that generated this compliance event',
    integration_id STRING COMMENT 'Integration identifier',
    compliance_workflow_id STRING COMMENT 'Workflow identifier for tracking related events',
    
    CONSTRAINT pk_gdpr_events PRIMARY KEY (event_id),
    CONSTRAINT fk_gdpr_events_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/gdpr_compliance_events'
COMMENT 'GDPR compliance events table storing all privacy and data protection events'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.event_id_not_null' = 'event_id IS NOT NULL',
    'quality.expectations.event_type_valid' = 'event_type IN ("deletion", "suppression", "data_request", "delivery", "consent")',
    'quality.expectations.file_size_positive' = 'file_size_bytes IS NULL OR file_size_bytes > 0'
);

-- Privacy requests table for tracking data subject requests
CREATE TABLE IF NOT EXISTS customerio.privacy_requests (
    -- Request identification
    request_id STRING NOT NULL COMMENT 'Unique privacy request identifier',
    user_id STRING COMMENT 'User making the request (may be null for third-party requests)',
    
    -- Request details
    request_type STRING NOT NULL COMMENT 'Type of request (access, deletion, portability, rectification, objection)',
    request_status STRING DEFAULT 'received' COMMENT 'Request status (received, verified, processing, completed, rejected)',
    request_source STRING COMMENT 'Where request originated (user_portal, email, phone, letter)',
    
    -- Request content
    request_description STRING COMMENT 'Description of the request',
    specific_data_types ARRAY<STRING> COMMENT 'Specific data types requested (email_data, behavioral_data, device_data)',
    
    -- Requester information
    requester_email STRING COMMENT 'Email of person making request',
    requester_name STRING COMMENT 'Name of person making request',
    relationship_to_data_subject STRING COMMENT 'Relationship (self, legal_guardian, attorney)',
    
    -- Verification and authentication
    verification_method STRING COMMENT 'How identity was verified (email_verification, identity_document)',
    verification_status STRING COMMENT 'Verification status (pending, verified, failed)',
    verification_documents ARRAY<STRING> COMMENT 'Types of verification documents provided',
    verified_at TIMESTAMP COMMENT 'When identity was verified',
    verified_by STRING COMMENT 'Who verified the identity',
    
    -- Legal basis and compliance
    legal_basis STRING COMMENT 'Legal basis for the request (gdpr_article_15, ccpa_section_1798)',
    jurisdiction STRING COMMENT 'Applicable jurisdiction (EU, California, Brazil)',
    applicable_regulations ARRAY<STRING> COMMENT 'Applicable regulations (GDPR, CCPA, LGPD)',
    
    -- Processing details
    assigned_to STRING COMMENT 'Team member assigned to process request',
    estimated_completion_date DATE COMMENT 'Estimated completion date',
    actual_completion_date DATE COMMENT 'Actual completion date',
    processing_notes STRING COMMENT 'Notes about processing the request',
    
    -- Response details
    response_method STRING COMMENT 'How response was delivered (email, secure_portal, postal_mail)',
    response_format STRING COMMENT 'Format of response (json, pdf, csv)',
    response_size_bytes BIGINT COMMENT 'Size of response data',
    response_delivered_at TIMESTAMP COMMENT 'When response was delivered',
    
    -- Compliance tracking
    response_time_hours INT COMMENT 'Time taken to respond in hours',
    within_regulatory_timeframe BOOLEAN COMMENT 'Whether response was within required timeframe',
    escalation_required BOOLEAN DEFAULT FALSE COMMENT 'Whether request required escalation',
    
    -- Request lifecycle timestamps
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When request was submitted',
    acknowledged_at TIMESTAMP COMMENT 'When request was acknowledged',
    started_processing_at TIMESTAMP COMMENT 'When processing started',
    completed_at TIMESTAMP COMMENT 'When request was completed',
    
    CONSTRAINT pk_privacy_requests PRIMARY KEY (request_id),
    CONSTRAINT fk_privacy_requests_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/privacy_requests'
COMMENT 'Privacy requests table for tracking data subject requests and compliance'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.request_id_not_null' = 'request_id IS NOT NULL',
    'quality.expectations.valid_request_type' = 'request_type IN ("access", "deletion", "portability", "rectification", "objection", "restriction")',
    'quality.expectations.valid_status' = 'request_status IN ("received", "verified", "processing", "completed", "rejected", "cancelled")'
);

-- Data exports table for tracking GDPR data export deliveries
CREATE TABLE IF NOT EXISTS customerio.data_exports (
    -- Export identification
    export_id STRING NOT NULL COMMENT 'Unique data export identifier',
    request_id STRING COMMENT 'Privacy request this export fulfills',
    user_id STRING NOT NULL COMMENT 'User whose data is being exported',
    report_id STRING COMMENT 'Report identifier from compliance events',
    
    -- Export details
    export_type STRING NOT NULL COMMENT 'Type of export (full_profile, specific_data, behavioral_data)',
    export_format STRING DEFAULT 'json' COMMENT 'Export file format (json, csv, xml)',
    compression_format STRING COMMENT 'Compression format (zip, gzip)',
    
    -- Data scope
    data_categories ARRAY<STRING> COMMENT 'Categories of data included (profile, events, devices, objects)',
    date_range_start DATE COMMENT 'Start date for data inclusion',
    date_range_end DATE COMMENT 'End date for data inclusion',
    include_deleted_data BOOLEAN DEFAULT FALSE COMMENT 'Whether to include soft-deleted data',
    
    -- File information
    file_name STRING COMMENT 'Generated file name',
    file_size_bytes BIGINT COMMENT 'File size in bytes',
    file_hash STRING COMMENT 'File hash for integrity verification',
    encryption_method STRING COMMENT 'Encryption method used (AES256, GPG)',
    
    -- Delivery information
    delivery_method STRING COMMENT 'How export was delivered (email, secure_download, api)',
    delivery_url STRING COMMENT 'Secure download URL if applicable',
    delivery_expires_at TIMESTAMP COMMENT 'When download link expires',
    access_count INT DEFAULT 0 COMMENT 'Number of times export was accessed',
    
    -- Export status
    export_status STRING DEFAULT 'generating' COMMENT 'Export status (generating, ready, delivered, expired, failed)',
    generation_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When export generation started',
    generation_completed_at TIMESTAMP COMMENT 'When export generation completed',
    delivered_at TIMESTAMP COMMENT 'When export was delivered',
    
    -- Error tracking
    error_message STRING COMMENT 'Error message if generation failed',
    retry_count INT DEFAULT 0 COMMENT 'Number of retry attempts',
    
    -- Compliance and audit
    generated_by STRING COMMENT 'System or user who generated export',
    approved_by STRING COMMENT 'Compliance officer who approved export',
    retention_period_days INT DEFAULT 30 COMMENT 'How long export is retained',
    auto_delete_at TIMESTAMP COMMENT 'When export will be automatically deleted',
    
    CONSTRAINT pk_data_exports PRIMARY KEY (export_id),
    CONSTRAINT fk_data_exports_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT fk_data_exports_request FOREIGN KEY (request_id) REFERENCES customerio.privacy_requests(request_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/data_exports'
COMMENT 'Data exports table for tracking GDPR and privacy compliance data exports'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.export_id_not_null' = 'export_id IS NOT NULL',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.valid_file_size' = 'file_size_bytes IS NULL OR file_size_bytes > 0'
);

-- Consent management table for tracking user consent
CREATE TABLE IF NOT EXISTS customerio.consent_management (
    -- Consent record identification
    consent_id STRING NOT NULL COMMENT 'Unique consent record identifier',
    user_id STRING NOT NULL COMMENT 'User this consent record belongs to',
    
    -- Consent details
    consent_type STRING NOT NULL COMMENT 'Type of consent (marketing, analytics, personalization, cookies)',
    consent_status STRING NOT NULL COMMENT 'Current consent status (granted, withdrawn, pending)',
    consent_source STRING COMMENT 'Where consent was captured (registration, preferences, cookie_banner)',
    
    -- Consent metadata
    consent_version STRING COMMENT 'Version of consent terms when granted',
    consent_language STRING COMMENT 'Language consent was provided in',
    legal_basis STRING COMMENT 'Legal basis for processing (consent, legitimate_interest)',
    
    -- Consent capture details
    capture_method STRING COMMENT 'How consent was captured (opt_in, opt_out, pre_checked)',
    capture_ip_address STRING COMMENT 'IP address when consent was captured',
    capture_user_agent STRING COMMENT 'User agent when consent was captured',
    capture_page_url STRING COMMENT 'Page URL where consent was captured',
    
    -- Consent granularity
    specific_purposes ARRAY<STRING> COMMENT 'Specific purposes consented to (email_marketing, sms_marketing)',
    data_categories ARRAY<STRING> COMMENT 'Data categories consented to (personal_data, behavioral_data)',
    
    -- Consent lifecycle
    granted_at TIMESTAMP COMMENT 'When consent was granted',
    withdrawn_at TIMESTAMP COMMENT 'When consent was withdrawn',
    expires_at TIMESTAMP COMMENT 'When consent expires (if applicable)',
    last_confirmed_at TIMESTAMP COMMENT 'When consent was last confirmed',
    
    -- Consent changes tracking
    previous_status STRING COMMENT 'Previous consent status',
    change_reason STRING COMMENT 'Reason for consent change',
    change_triggered_by STRING COMMENT 'What triggered the change (user_action, system_update)',
    
    -- Withdrawal details
    withdrawal_method STRING COMMENT 'How consent was withdrawn (unsubscribe_link, preferences)',
    withdrawal_reason STRING COMMENT 'Reason provided for withdrawal',
    
    -- Processing impact
    processing_stopped_at TIMESTAMP COMMENT 'When processing based on this consent stopped',
    data_deleted_at TIMESTAMP COMMENT 'When data was deleted after withdrawal',
    
    -- Audit trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When consent record was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When consent record was last updated',
    
    CONSTRAINT pk_consent_management PRIMARY KEY (consent_id),
    CONSTRAINT fk_consent_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/consent_management'
COMMENT 'Consent management table for tracking user consent for GDPR compliance'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.consent_id_not_null' = 'consent_id IS NOT NULL',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.valid_consent_status' = 'consent_status IN ("granted", "withdrawn", "pending", "expired")'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_gdpr_events_user_id ON customerio.gdpr_compliance_events(user_id);
CREATE INDEX IF NOT EXISTS idx_gdpr_events_type ON customerio.gdpr_compliance_events(event_type);
CREATE INDEX IF NOT EXISTS idx_gdpr_events_timestamp ON customerio.gdpr_compliance_events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_gdpr_events_batch_id ON customerio.gdpr_compliance_events(batch_id);

CREATE INDEX IF NOT EXISTS idx_privacy_requests_user_id ON customerio.privacy_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_privacy_requests_type ON customerio.privacy_requests(request_type);
CREATE INDEX IF NOT EXISTS idx_privacy_requests_status ON customerio.privacy_requests(request_status);
CREATE INDEX IF NOT EXISTS idx_privacy_requests_submitted ON customerio.privacy_requests(submitted_at);

CREATE INDEX IF NOT EXISTS idx_data_exports_user_id ON customerio.data_exports(user_id);
CREATE INDEX IF NOT EXISTS idx_data_exports_request_id ON customerio.data_exports(request_id);
CREATE INDEX IF NOT EXISTS idx_data_exports_status ON customerio.data_exports(export_status);
CREATE INDEX IF NOT EXISTS idx_data_exports_generated ON customerio.data_exports(generation_started_at);

CREATE INDEX IF NOT EXISTS idx_consent_user_id ON customerio.consent_management(user_id);
CREATE INDEX IF NOT EXISTS idx_consent_type ON customerio.consent_management(consent_type);
CREATE INDEX IF NOT EXISTS idx_consent_status ON customerio.consent_management(consent_status);
CREATE INDEX IF NOT EXISTS idx_consent_granted_at ON customerio.consent_management(granted_at);