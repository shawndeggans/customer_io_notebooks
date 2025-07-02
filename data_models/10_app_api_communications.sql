-- ==================================================
-- Customer.IO App API Communications Data Models
-- ==================================================
-- Based on App API integration patterns and message tracking needs
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- Transactional email message tracking and analytics
CREATE TABLE IF NOT EXISTS customerio.app_transactional_messages (
    -- Message identification
    delivery_id STRING NOT NULL COMMENT 'Unique delivery identifier returned by Customer.IO',
    transactional_message_id INT NOT NULL COMMENT 'Template ID of the transactional message',
    message_unique_id STRING NOT NULL COMMENT 'Unique identifier for this specific message send',
    
    -- Recipient information
    recipient_email STRING COMMENT 'Email address of the recipient (when using direct email)',
    recipient_identifiers STRUCT<
        email: STRING,
        id: STRING,
        user_id: STRING
    > COMMENT 'Customer identifiers used for targeting',
    
    -- Message content and data
    message_data MAP<STRING, STRING> COMMENT 'Dynamic data passed to message template',
    template_variables STRUCT<
        subject_line: STRING,
        customer_name: STRING,
        first_name: STRING,
        order_number: STRING,
        order_total: STRING,
        product_name: STRING,
        download_link: STRING,
        support_email: STRING,
        tracking_number: STRING
    > COMMENT 'Common template variables used in messages',
    
    -- Delivery tracking
    sent_timestamp TIMESTAMP NOT NULL COMMENT 'When the message was sent to Customer.IO',
    delivery_status STRING DEFAULT 'sent' COMMENT 'Status: sent, delivered, bounced, failed',
    delivered_timestamp TIMESTAMP COMMENT 'When message was delivered to inbox',
    opened_timestamp TIMESTAMP COMMENT 'When recipient opened the message',
    clicked_timestamp TIMESTAMP COMMENT 'When recipient clicked a link',
    
    -- Performance metrics
    open_count INT DEFAULT 0 COMMENT 'Number of times message was opened',
    click_count INT DEFAULT 0 COMMENT 'Number of link clicks',
    conversion_events ARRAY<STRING> COMMENT 'Events triggered after message delivery',
    revenue_attributed DOUBLE COMMENT 'Revenue attributed to this message',
    
    -- Error handling
    error_code STRING COMMENT 'Error code if delivery failed',
    error_message STRING COMMENT 'Detailed error message',
    retry_count INT DEFAULT 0 COMMENT 'Number of delivery retry attempts',
    
    -- Metadata
    workspace_id STRING COMMENT 'Customer.IO workspace identifier',
    campaign_context STRING COMMENT 'Campaign or flow context that triggered message',
    api_request_id STRING COMMENT 'API request identifier for debugging',
    
    -- Technical fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record last update timestamp'
) 
USING DELTA
PARTITIONED BY (DATE(sent_timestamp))
LOCATION 's3://your-bucket/customerio/app_transactional_messages'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.compatibility.symlinkFormatManifest.enabled' = 'true'
);

-- Create optimized indexes for common queries
CREATE INDEX IF NOT EXISTS idx_transactional_delivery_id 
ON customerio.app_transactional_messages (delivery_id);

CREATE INDEX IF NOT EXISTS idx_transactional_recipient_email 
ON customerio.app_transactional_messages (recipient_email);

CREATE INDEX IF NOT EXISTS idx_transactional_message_id 
ON customerio.app_transactional_messages (transactional_message_id);

-- ==================================================

-- Broadcast campaign execution tracking and analytics
CREATE TABLE IF NOT EXISTS customerio.app_broadcast_campaigns (
    -- Campaign identification
    trigger_id STRING NOT NULL COMMENT 'Unique identifier for this broadcast trigger',
    broadcast_id INT NOT NULL COMMENT 'ID of the broadcast campaign in Customer.IO',
    campaign_name STRING COMMENT 'Name of the broadcast campaign',
    
    -- Trigger information
    trigger_timestamp TIMESTAMP NOT NULL COMMENT 'When the broadcast was triggered',
    triggered_by STRING COMMENT 'API user or system that triggered the broadcast',
    
    -- Campaign data and configuration
    campaign_data MAP<STRING, STRING> COMMENT 'Dynamic data passed to broadcast',
    campaign_variables STRUCT<
        headline: STRING,
        discount_percentage: INT,
        sale_end_date: STRING,
        campaign_name: STRING,
        feature_name: STRING,
        beta_signup_url: STRING,
        expiration_date: STRING,
        featured_products: ARRAY<STRING>
    > COMMENT 'Common campaign variables',
    
    -- Targeting and recipients
    recipients_config STRUCT<
        segment: STRUCT<id: INT>,
        emails: ARRAY<STRING>,
        customers: ARRAY<STRING>,
        tags: ARRAY<STRING>
    > COMMENT 'Recipient targeting configuration',
    targeting_criteria STRING COMMENT 'Description of targeting logic used',
    estimated_recipients INT COMMENT 'Estimated number of recipients',
    actual_recipients INT COMMENT 'Actual number of messages sent',
    
    -- Execution tracking
    execution_status STRING DEFAULT 'triggered' COMMENT 'Status: triggered, processing, completed, failed',
    start_timestamp TIMESTAMP COMMENT 'When broadcast processing started',
    completion_timestamp TIMESTAMP COMMENT 'When broadcast processing completed',
    processing_duration_seconds INT COMMENT 'Time taken to process broadcast',
    
    -- Performance metrics
    messages_sent INT DEFAULT 0 COMMENT 'Total messages sent',
    messages_delivered INT DEFAULT 0 COMMENT 'Messages successfully delivered',
    messages_bounced INT DEFAULT 0 COMMENT 'Messages that bounced',
    unique_opens INT DEFAULT 0 COMMENT 'Unique recipients who opened',
    unique_clicks INT DEFAULT 0 COMMENT 'Unique recipients who clicked',
    total_opens INT DEFAULT 0 COMMENT 'Total open events',
    total_clicks INT DEFAULT 0 COMMENT 'Total click events',
    unsubscribes INT DEFAULT 0 COMMENT 'Unsubscribes triggered by this broadcast',
    
    -- Conversion tracking
    conversion_events ARRAY<STRING> COMMENT 'Events triggered after broadcast',
    conversion_count INT DEFAULT 0 COMMENT 'Number of conversions attributed',
    revenue_attributed DOUBLE COMMENT 'Revenue attributed to this broadcast',
    
    -- Error handling
    error_details ARRAY<STRUCT<
        error_code: STRING,
        error_message: STRING,
        affected_count: INT
    >> COMMENT 'Errors encountered during processing',
    
    -- Metadata
    workspace_id STRING COMMENT 'Customer.IO workspace identifier',
    api_request_id STRING COMMENT 'API request identifier for debugging',
    
    -- Technical fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record last update timestamp'
) 
USING DELTA
PARTITIONED BY (DATE(trigger_timestamp))
LOCATION 's3://your-bucket/customerio/app_broadcast_campaigns'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.compatibility.symlinkFormatManifest.enabled' = 'true'
);

-- Create optimized indexes for common queries
CREATE INDEX IF NOT EXISTS idx_broadcast_trigger_id 
ON customerio.app_broadcast_campaigns (trigger_id);

CREATE INDEX IF NOT EXISTS idx_broadcast_campaign_id 
ON customerio.app_broadcast_campaigns (broadcast_id);

CREATE INDEX IF NOT EXISTS idx_broadcast_name 
ON customerio.app_broadcast_campaigns (campaign_name);

-- ==================================================

-- Push notification delivery tracking and analytics
CREATE TABLE IF NOT EXISTS customerio.app_push_notifications (
    -- Notification identification
    delivery_id STRING NOT NULL COMMENT 'Unique delivery identifier returned by Customer.IO',
    push_unique_id STRING NOT NULL COMMENT 'Unique identifier for this push notification',
    
    -- Recipient information
    recipient_identifiers STRUCT<
        email: STRING,
        id: STRING,
        user_id: STRING
    > COMMENT 'Customer identifiers used for targeting',
    device_tokens ARRAY<STRING> COMMENT 'Device tokens targeted for push delivery',
    
    -- Push notification content
    title STRING NOT NULL COMMENT 'Push notification title',
    message STRING NOT NULL COMMENT 'Push notification message body',
    push_data MAP<STRING, STRING> COMMENT 'Additional data payload',
    rich_content STRUCT<
        sound: STRING,
        badge: INT,
        category: STRING,
        deep_link: STRING,
        action_url: STRING,
        image_url: STRING,
        video_url: STRING
    > COMMENT 'Rich push notification content and actions',
    
    -- Platform and targeting
    platform STRING COMMENT 'Target platform: ios, android, web',
    app_version STRING COMMENT 'Target app version',
    device_metadata STRUCT<
        os_version: STRING,
        device_model: STRING,
        app_version: STRING,
        timezone: STRING
    > COMMENT 'Device targeting metadata',
    
    -- Delivery tracking
    sent_timestamp TIMESTAMP NOT NULL COMMENT 'When push was sent to Customer.IO',
    delivery_status STRING DEFAULT 'sent' COMMENT 'Status: sent, delivered, failed, expired',
    delivered_timestamp TIMESTAMP COMMENT 'When push was delivered to device',
    opened_timestamp TIMESTAMP COMMENT 'When user tapped the push notification',
    action_timestamp TIMESTAMP COMMENT 'When user performed push action',
    
    -- Engagement metrics
    delivery_rate DOUBLE COMMENT 'Percentage of devices that received push',
    open_rate DOUBLE COMMENT 'Percentage of delivered pushes that were opened',
    action_taken STRING COMMENT 'Action taken by user: opened, dismissed, action_button',
    conversion_events ARRAY<STRING> COMMENT 'Events triggered after push delivery',
    
    -- Error handling
    error_code STRING COMMENT 'Error code if delivery failed',
    error_message STRING COMMENT 'Detailed error message',
    failed_device_tokens ARRAY<STRING> COMMENT 'Device tokens that failed delivery',
    retry_count INT DEFAULT 0 COMMENT 'Number of delivery retry attempts',
    
    -- Metadata
    workspace_id STRING COMMENT 'Customer.IO workspace identifier',
    campaign_context STRING COMMENT 'Campaign or automation that triggered push',
    api_request_id STRING COMMENT 'API request identifier for debugging',
    
    -- Technical fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record last update timestamp'
) 
USING DELTA
PARTITIONED BY (DATE(sent_timestamp))
LOCATION 's3://your-bucket/customerio/app_push_notifications'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.compatibility.symlinkFormatManifest.enabled' = 'true'
);

-- Create optimized indexes for common queries
CREATE INDEX IF NOT EXISTS idx_push_delivery_id 
ON customerio.app_push_notifications (delivery_id);

CREATE INDEX IF NOT EXISTS idx_push_recipient_email 
ON customerio.app_push_notifications (recipient_identifiers.email);

CREATE INDEX IF NOT EXISTS idx_push_platform 
ON customerio.app_push_notifications (platform);

-- ==================================================

-- Cross-channel message performance analytics
CREATE TABLE IF NOT EXISTS customerio.app_message_performance (
    -- Message identification
    performance_id STRING NOT NULL COMMENT 'Unique identifier for this performance record',
    message_id STRING NOT NULL COMMENT 'Reference to source message (delivery_id or trigger_id)',
    channel STRING NOT NULL COMMENT 'Communication channel: transactional, broadcast, push',
    delivery_id STRING COMMENT 'Delivery identifier from source channel',
    
    -- Recipient and targeting
    recipient_email STRING COMMENT 'Email address of the recipient',
    customer_id STRING COMMENT 'Customer identifier if known',
    segment_name STRING COMMENT 'Segment name for broadcast messages',
    
    -- Message metadata
    template_id STRING COMMENT 'Template or message ID used',
    template_name STRING COMMENT 'Human-readable template name',
    campaign_name STRING COMMENT 'Campaign or automation name',
    subject_line STRING COMMENT 'Email subject line or push title',
    
    -- Timing metrics
    sent_timestamp TIMESTAMP NOT NULL COMMENT 'When message was sent',
    delivered_timestamp TIMESTAMP COMMENT 'When message was delivered',
    first_open_timestamp TIMESTAMP COMMENT 'First time message was opened',
    last_open_timestamp TIMESTAMP COMMENT 'Most recent open time',
    first_click_timestamp TIMESTAMP COMMENT 'First click event',
    last_click_timestamp TIMESTAMP COMMENT 'Most recent click event',
    conversion_timestamp TIMESTAMP COMMENT 'When conversion occurred',
    
    -- Engagement metrics
    delivery_status STRING COMMENT 'Final delivery status',
    open_count INT DEFAULT 0 COMMENT 'Total number of opens',
    click_count INT DEFAULT 0 COMMENT 'Total number of clicks',
    unique_opens BOOLEAN DEFAULT FALSE COMMENT 'Whether message was opened at least once',
    unique_clicks BOOLEAN DEFAULT FALSE COMMENT 'Whether message was clicked at least once',
    
    -- Conversion tracking
    conversion_events ARRAY<STRING> COMMENT 'Conversion events attributed to this message',
    conversion_value DOUBLE COMMENT 'Revenue or value attributed to conversions',
    conversion_type STRING COMMENT 'Type of conversion: purchase, signup, upgrade',
    time_to_conversion_hours DOUBLE COMMENT 'Hours from send to conversion',
    
    -- Advanced metrics
    engagement_score DOUBLE COMMENT 'Calculated engagement score (0-100)',
    spam_complaints INT DEFAULT 0 COMMENT 'Number of spam complaints',
    unsubscribes INT DEFAULT 0 COMMENT 'Unsubscribes triggered by this message',
    forwards INT DEFAULT 0 COMMENT 'Number of forwards (email only)',
    social_shares INT DEFAULT 0 COMMENT 'Social media shares',
    
    -- A/B testing and variants
    test_variant STRING COMMENT 'A/B test variant identifier',
    test_group STRING COMMENT 'Test group: control, variant_a, variant_b',
    test_name STRING COMMENT 'Name of the A/B test',
    
    -- Metadata
    workspace_id STRING COMMENT 'Customer.IO workspace identifier',
    api_request_id STRING COMMENT 'Original API request identifier',
    
    -- Technical fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record last update timestamp'
) 
USING DELTA
PARTITIONED BY (channel, DATE(sent_timestamp))
LOCATION 's3://your-bucket/customerio/app_message_performance'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.compatibility.symlinkFormatManifest.enabled' = 'true'
);

-- Create optimized indexes for cross-channel analytics
CREATE INDEX IF NOT EXISTS idx_performance_message_id 
ON customerio.app_message_performance (message_id);

CREATE INDEX IF NOT EXISTS idx_performance_recipient 
ON customerio.app_message_performance (recipient_email);

CREATE INDEX IF NOT EXISTS idx_performance_channel 
ON customerio.app_message_performance (channel);

CREATE INDEX IF NOT EXISTS idx_performance_campaign 
ON customerio.app_message_performance (campaign_name);

-- ==================================================

-- Centralized error tracking and resolution
CREATE TABLE IF NOT EXISTS customerio.app_delivery_errors (
    -- Error identification
    error_id STRING NOT NULL COMMENT 'Unique identifier for this error record',
    delivery_id STRING COMMENT 'Delivery ID that encountered the error',
    message_id STRING COMMENT 'Source message identifier',
    channel STRING NOT NULL COMMENT 'Channel where error occurred: transactional, broadcast, push',
    
    -- Error details
    error_code STRING NOT NULL COMMENT 'Customer.IO or HTTP error code',
    error_message STRING NOT NULL COMMENT 'Detailed error description',
    error_category STRING COMMENT 'Error category: authentication, validation, delivery, rate_limit',
    error_severity STRING DEFAULT 'medium' COMMENT 'Severity: low, medium, high, critical',
    
    -- Context information
    recipient_email STRING COMMENT 'Email address that failed (if applicable)',
    recipient_identifiers MAP<STRING, STRING> COMMENT 'Customer identifiers for failed delivery',
    api_endpoint STRING COMMENT 'API endpoint that generated the error',
    request_payload STRING COMMENT 'JSON payload that caused the error (sanitized)',
    
    -- Resolution tracking
    retry_count INT DEFAULT 0 COMMENT 'Number of retry attempts',
    retry_strategy STRING COMMENT 'Retry strategy used: immediate, exponential, manual',
    resolved BOOLEAN DEFAULT FALSE COMMENT 'Whether error has been resolved',
    resolved_timestamp TIMESTAMP COMMENT 'When error was resolved',
    resolution_method STRING COMMENT 'How error was resolved: auto_retry, manual_fix, config_change',
    resolution_notes STRING COMMENT 'Notes about error resolution',
    
    -- Impact metrics
    affected_recipients INT DEFAULT 1 COMMENT 'Number of recipients affected by this error',
    business_impact STRING COMMENT 'Business impact assessment: low, medium, high',
    downtime_minutes INT DEFAULT 0 COMMENT 'Minutes of service disruption',
    
    -- Prevention and monitoring
    alert_triggered BOOLEAN DEFAULT FALSE COMMENT 'Whether monitoring alert was triggered',
    escalated BOOLEAN DEFAULT FALSE COMMENT 'Whether error was escalated to engineering',
    preventable BOOLEAN COMMENT 'Whether error could have been prevented',
    prevention_notes STRING COMMENT 'Notes on how to prevent similar errors',
    
    -- Metadata
    workspace_id STRING COMMENT 'Customer.IO workspace identifier',
    api_request_id STRING COMMENT 'API request identifier for debugging',
    user_agent STRING COMMENT 'User agent of the API client',
    
    -- Technical fields
    occurred_at TIMESTAMP NOT NULL COMMENT 'When the error occurred',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record last update timestamp'
) 
USING DELTA
PARTITIONED BY (channel, DATE(occurred_at))
LOCATION 's3://your-bucket/customerio/app_delivery_errors'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.compatibility.symlinkFormatManifest.enabled' = 'true'
);

-- Create optimized indexes for error analysis
CREATE INDEX IF NOT EXISTS idx_errors_delivery_id 
ON customerio.app_delivery_errors (delivery_id);

CREATE INDEX IF NOT EXISTS idx_errors_code 
ON customerio.app_delivery_errors (error_code);

CREATE INDEX IF NOT EXISTS idx_errors_channel 
ON customerio.app_delivery_errors (channel);

CREATE INDEX IF NOT EXISTS idx_errors_resolved 
ON customerio.app_delivery_errors (resolved);

-- ==================================================
-- Views for Common Analytics Queries
-- ==================================================

-- Daily message performance summary by channel
CREATE OR REPLACE VIEW customerio.daily_message_performance AS
SELECT 
    DATE(sent_timestamp) as send_date,
    channel,
    COUNT(*) as messages_sent,
    COUNT(CASE WHEN delivery_status = 'delivered' THEN 1 END) as messages_delivered,
    COUNT(CASE WHEN unique_opens THEN 1 END) as unique_opens,
    COUNT(CASE WHEN unique_clicks THEN 1 END) as unique_clicks,
    COUNT(CASE WHEN conversion_events IS NOT NULL AND SIZE(conversion_events) > 0 THEN 1 END) as conversions,
    SUM(COALESCE(conversion_value, 0)) as total_conversion_value,
    AVG(CASE WHEN delivery_status = 'delivered' THEN 1.0 ELSE 0.0 END) as delivery_rate,
    AVG(CASE WHEN unique_opens THEN 1.0 ELSE 0.0 END) as open_rate,
    AVG(CASE WHEN unique_clicks THEN 1.0 ELSE 0.0 END) as click_rate
FROM customerio.app_message_performance
WHERE sent_timestamp >= CURRENT_DATE() - INTERVAL 90 DAYS
GROUP BY DATE(sent_timestamp), channel
ORDER BY send_date DESC, channel;

-- Campaign performance leaderboard
CREATE OR REPLACE VIEW customerio.campaign_performance_leaderboard AS
SELECT 
    campaign_name,
    channel,
    COUNT(*) as total_messages,
    COUNT(CASE WHEN unique_opens THEN 1 END) as unique_opens,
    COUNT(CASE WHEN unique_clicks THEN 1 END) as unique_clicks,
    COUNT(CASE WHEN conversion_events IS NOT NULL AND SIZE(conversion_events) > 0 THEN 1 END) as conversions,
    SUM(COALESCE(conversion_value, 0)) as total_revenue,
    AVG(CASE WHEN unique_opens THEN 1.0 ELSE 0.0 END) as open_rate,
    AVG(CASE WHEN unique_clicks THEN 1.0 ELSE 0.0 END) as click_rate,
    AVG(COALESCE(conversion_value, 0)) as avg_revenue_per_message
FROM customerio.app_message_performance
WHERE sent_timestamp >= CURRENT_DATE() - INTERVAL 30 DAYS
    AND campaign_name IS NOT NULL
GROUP BY campaign_name, channel
HAVING total_messages >= 10  -- Only campaigns with significant volume
ORDER BY total_revenue DESC, open_rate DESC;

-- Error analysis dashboard
CREATE OR REPLACE VIEW customerio.error_analysis_dashboard AS
SELECT 
    DATE(occurred_at) as error_date,
    channel,
    error_category,
    error_code,
    COUNT(*) as error_count,
    COUNT(DISTINCT delivery_id) as affected_deliveries,
    SUM(affected_recipients) as total_affected_recipients,
    AVG(retry_count) as avg_retry_count,
    COUNT(CASE WHEN resolved THEN 1 END) as resolved_count,
    AVG(CASE WHEN resolved THEN 1.0 ELSE 0.0 END) as resolution_rate
FROM customerio.app_delivery_errors
WHERE occurred_at >= CURRENT_DATE() - INTERVAL 30 DAYS
GROUP BY DATE(occurred_at), channel, error_category, error_code
ORDER BY error_date DESC, error_count DESC;

-- ==================================================
-- Table Comments and Documentation
-- ==================================================

-- Add table-level comments for documentation
COMMENT ON TABLE customerio.app_transactional_messages IS 
'Tracks all transactional email messages sent through Customer.IO App API including delivery status, engagement metrics, and template performance. Used for email campaign analytics and customer communication tracking.';

COMMENT ON TABLE customerio.app_broadcast_campaigns IS 
'Records broadcast campaign executions triggered via Customer.IO App API including targeting configuration, execution metrics, and performance analytics. Enables marketing team insights and campaign optimization.';

COMMENT ON TABLE customerio.app_push_notifications IS 
'Tracks push notification deliveries sent through Customer.IO App API including device targeting, rich content, platform-specific metrics, and user engagement. Supports mobile marketing analytics.';

COMMENT ON TABLE customerio.app_message_performance IS 
'Unified analytics table aggregating performance metrics across all Customer.IO App API communication channels. Provides cross-channel insights, conversion attribution, and comprehensive engagement analytics.';

COMMENT ON TABLE customerio.app_delivery_errors IS 
'Centralized error tracking for all Customer.IO App API delivery failures including retry attempts, resolution tracking, and impact analysis. Enables operational monitoring and error prevention.';