-- Customer.IO Webhook Events Data Models
-- 
-- These tables store webhook events from Customer.IO for comprehensive analytics
-- All tables use Delta format and are partitioned for optimal performance

-- =============================================================================
-- RAW WEBHOOK LANDING TABLE
-- =============================================================================
-- Stores all incoming webhook events before processing (audit trail)

CREATE TABLE IF NOT EXISTS webhook_raw_events (
    received_at STRING,
    event_id STRING,
    object_type STRING,
    metric STRING,
    timestamp LONG,
    event_data STRING,  -- JSON string of full event payload
    date_partition STRING  -- YYYY-MM-DD format for partitioning
) 
USING DELTA
PARTITIONED BY (date_partition)
LOCATION '/mnt/customerio/webhook_landing/'
COMMENT 'Raw webhook events received from Customer.IO for audit trail';

-- =============================================================================
-- EMAIL EVENTS TABLE
-- =============================================================================
-- Processed email events with all metrics (opened, clicked, delivered, etc.)

CREATE TABLE IF NOT EXISTS webhook_email_events (
    event_id STRING,
    object_type STRING,
    metric STRING,
    timestamp LONG,
    event_date STRING,
    customer_id STRING,
    email_address STRING,
    delivery_id STRING,
    campaign_id LONG,
    action_id LONG,
    journey_id LONG,
    parent_action_id LONG,
    subject STRING,
    recipient STRING,
    -- Click-specific fields
    href STRING,
    link_id STRING,
    machine_click BOOLEAN,
    -- Open-specific fields
    proxied BOOLEAN,
    prefetched BOOLEAN,
    -- Failure-specific fields
    failure_message STRING,
    -- Conversion fields
    conversion_event_id STRING,
    unsubscribe_event_id STRING,
    processed_at STRING
) 
USING DELTA
PARTITIONED BY (event_date, metric)
LOCATION '/mnt/customerio/processed_events/email_events/'
COMMENT 'Processed email webhook events from Customer.IO';

-- =============================================================================
-- CUSTOMER EVENTS TABLE
-- =============================================================================
-- Customer subscription and preference events

CREATE TABLE IF NOT EXISTS webhook_customer_events (
    event_id STRING,
    object_type STRING,
    metric STRING,
    timestamp LONG,
    event_date STRING,
    customer_id STRING,
    email_address STRING,
    identifiers STRING,  -- JSON string of customer identifiers
    content STRING,      -- Subscription preferences content
    delivery_type STRING,
    processed_at STRING
) 
USING DELTA
PARTITIONED BY (event_date, metric)
LOCATION '/mnt/customerio/processed_events/customer_events/'
COMMENT 'Customer subscription and preferences webhook events';

-- =============================================================================
-- SMS EVENTS TABLE
-- =============================================================================
-- SMS message events (sent, delivered, clicked, etc.)

CREATE TABLE IF NOT EXISTS webhook_sms_events (
    event_id STRING,
    object_type STRING,
    metric STRING,
    timestamp LONG,
    event_date STRING,
    customer_id STRING,
    delivery_id STRING,
    recipient STRING,  -- MSISDN phone number
    campaign_id LONG,
    action_id LONG,
    journey_id LONG,
    parent_action_id LONG,
    content STRING,
    -- Click-specific fields
    href STRING,
    link_id STRING,
    -- Failure fields
    failure_message STRING,
    -- Conversion fields
    conversion_event_id STRING,
    processed_at STRING
) 
USING DELTA
PARTITIONED BY (event_date, metric)
LOCATION '/mnt/customerio/processed_events/sms_events/'
COMMENT 'SMS webhook events from Customer.IO';

-- =============================================================================
-- PUSH NOTIFICATION EVENTS TABLE
-- =============================================================================
-- Push notification events (sent, delivered, opened, etc.)

CREATE TABLE IF NOT EXISTS webhook_push_events (
    event_id STRING,
    object_type STRING,
    metric STRING,
    timestamp LONG,
    event_date STRING,
    customer_id STRING,
    delivery_id STRING,
    campaign_id LONG,
    action_id LONG,
    journey_id LONG,
    parent_action_id LONG,
    recipients STRING,  -- JSON array of recipients
    primary_device_id STRING,  -- First device ID from recipients
    content STRING,
    -- Click-specific fields
    href STRING,
    link_id STRING,
    -- Failure fields
    failure_message STRING,
    -- Conversion fields
    conversion_event_id STRING,
    processed_at STRING
) 
USING DELTA
PARTITIONED BY (event_date, metric)
LOCATION '/mnt/customerio/processed_events/push_events/'
COMMENT 'Push notification webhook events from Customer.IO';

-- =============================================================================
-- IN-APP MESSAGE EVENTS TABLE
-- =============================================================================
-- In-app message events

CREATE TABLE IF NOT EXISTS webhook_in_app_events (
    event_id STRING,
    object_type STRING,
    metric STRING,
    timestamp LONG,
    event_date STRING,
    customer_id STRING,
    delivery_id STRING,
    campaign_id LONG,
    action_id LONG,
    journey_id LONG,
    parent_action_id LONG,
    content STRING,
    -- Click-specific fields
    href STRING,
    link_id STRING,
    -- Failure fields
    failure_message STRING,
    -- Conversion fields
    conversion_event_id STRING,
    processed_at STRING
) 
USING DELTA
PARTITIONED BY (event_date, metric)
LOCATION '/mnt/customerio/processed_events/in_app_events/'
COMMENT 'In-app message webhook events from Customer.IO';

-- =============================================================================
-- SLACK EVENTS TABLE
-- =============================================================================
-- Slack message events

CREATE TABLE IF NOT EXISTS webhook_slack_events (
    event_id STRING,
    object_type STRING,
    metric STRING,
    timestamp LONG,
    event_date STRING,
    customer_id STRING,
    delivery_id STRING,
    campaign_id LONG,
    action_id LONG,
    journey_id LONG,
    parent_action_id LONG,
    content STRING,
    -- Click-specific fields
    href STRING,
    link_id STRING,
    -- Failure fields
    failure_message STRING,
    processed_at STRING
) 
USING DELTA
PARTITIONED BY (event_date, metric)
LOCATION '/mnt/customerio/processed_events/slack_events/'
COMMENT 'Slack message webhook events from Customer.IO';

-- =============================================================================
-- WEBHOOK EVENTS TABLE
-- =============================================================================
-- Customer.IO webhook delivery tracking events

CREATE TABLE IF NOT EXISTS webhook_webhook_events (
    event_id STRING,
    object_type STRING,
    metric STRING,
    timestamp LONG,
    event_date STRING,
    customer_id STRING,
    delivery_id STRING,
    campaign_id LONG,
    action_id LONG,
    journey_id LONG,
    parent_action_id LONG,
    webhook_url STRING,
    content STRING,
    -- Click-specific fields
    href STRING,
    link_id STRING,
    -- Failure fields
    failure_message STRING,
    processed_at STRING
) 
USING DELTA
PARTITIONED BY (event_date, metric)
LOCATION '/mnt/customerio/processed_events/webhook_events/'
COMMENT 'Webhook delivery tracking events from Customer.IO';

-- =============================================================================
-- ANALYTICS VIEWS
-- =============================================================================

-- Daily email engagement metrics
CREATE OR REPLACE VIEW daily_email_engagement AS
SELECT 
    event_date,
    COUNT(*) as total_events,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(CASE WHEN metric = 'sent' THEN 1 ELSE 0 END) as emails_sent,
    SUM(CASE WHEN metric = 'delivered' THEN 1 ELSE 0 END) as emails_delivered,
    SUM(CASE WHEN metric = 'opened' THEN 1 ELSE 0 END) as emails_opened,
    SUM(CASE WHEN metric = 'clicked' THEN 1 ELSE 0 END) as emails_clicked,
    SUM(CASE WHEN metric = 'bounced' THEN 1 ELSE 0 END) as emails_bounced,
    SUM(CASE WHEN metric = 'unsubscribed' THEN 1 ELSE 0 END) as emails_unsubscribed,
    -- Calculate rates
    ROUND(SUM(CASE WHEN metric = 'delivered' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN metric = 'sent' THEN 1 ELSE 0 END), 0), 2) as delivery_rate,
    ROUND(SUM(CASE WHEN metric = 'opened' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN metric = 'delivered' THEN 1 ELSE 0 END), 0), 2) as open_rate,
    ROUND(SUM(CASE WHEN metric = 'clicked' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN metric = 'delivered' THEN 1 ELSE 0 END), 0), 2) as click_rate,
    ROUND(SUM(CASE WHEN metric = 'bounced' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN metric = 'sent' THEN 1 ELSE 0 END), 0), 2) as bounce_rate
FROM webhook_email_events
GROUP BY event_date
ORDER BY event_date DESC;

-- Campaign performance summary
CREATE OR REPLACE VIEW campaign_performance AS
SELECT 
    campaign_id,
    COUNT(*) as total_events,
    COUNT(DISTINCT customer_id) as unique_recipients,
    SUM(CASE WHEN metric = 'sent' THEN 1 ELSE 0 END) as sent_count,
    SUM(CASE WHEN metric = 'delivered' THEN 1 ELSE 0 END) as delivered_count,
    SUM(CASE WHEN metric = 'opened' THEN 1 ELSE 0 END) as opened_count,
    SUM(CASE WHEN metric = 'clicked' THEN 1 ELSE 0 END) as clicked_count,
    -- Performance rates
    ROUND(SUM(CASE WHEN metric = 'opened' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN metric = 'delivered' THEN 1 ELSE 0 END), 0), 2) as open_rate,
    ROUND(SUM(CASE WHEN metric = 'clicked' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN metric = 'delivered' THEN 1 ELSE 0 END), 0), 2) as click_rate,
    MIN(event_date) as first_event_date,
    MAX(event_date) as last_event_date
FROM webhook_email_events
WHERE campaign_id IS NOT NULL
GROUP BY campaign_id
ORDER BY sent_count DESC;

-- Customer engagement summary across all channels
CREATE OR REPLACE VIEW customer_engagement_summary AS
SELECT 
    customer_id,
    -- Email metrics
    SUM(CASE WHEN object_type = 'email' AND metric = 'delivered' THEN 1 ELSE 0 END) as emails_received,
    SUM(CASE WHEN object_type = 'email' AND metric = 'opened' THEN 1 ELSE 0 END) as emails_opened,
    SUM(CASE WHEN object_type = 'email' AND metric = 'clicked' THEN 1 ELSE 0 END) as emails_clicked,
    -- SMS metrics  
    SUM(CASE WHEN object_type = 'sms' AND metric = 'delivered' THEN 1 ELSE 0 END) as sms_received,
    SUM(CASE WHEN object_type = 'sms' AND metric = 'clicked' THEN 1 ELSE 0 END) as sms_clicked,
    -- Push metrics
    SUM(CASE WHEN object_type = 'push' AND metric = 'delivered' THEN 1 ELSE 0 END) as push_received,
    SUM(CASE WHEN object_type = 'push' AND metric = 'opened' THEN 1 ELSE 0 END) as push_opened,
    -- Engagement rates
    ROUND(SUM(CASE WHEN object_type = 'email' AND metric = 'opened' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN object_type = 'email' AND metric = 'delivered' THEN 1 ELSE 0 END), 0), 2) as email_open_rate,
    ROUND(SUM(CASE WHEN object_type = 'email' AND metric = 'clicked' THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN object_type = 'email' AND metric = 'delivered' THEN 1 ELSE 0 END), 0), 2) as email_click_rate,
    MIN(event_date) as first_interaction,
    MAX(event_date) as last_interaction,
    COUNT(DISTINCT event_date) as active_days
FROM (
    SELECT customer_id, object_type, metric, event_date FROM webhook_email_events
    UNION ALL
    SELECT customer_id, object_type, metric, event_date FROM webhook_sms_events
    UNION ALL
    SELECT customer_id, object_type, metric, event_date FROM webhook_push_events
) all_events
WHERE customer_id IS NOT NULL
GROUP BY customer_id;

-- Error monitoring view
CREATE OR REPLACE VIEW webhook_error_summary AS
SELECT 
    event_date,
    object_type,
    metric,
    COUNT(*) as error_count,
    COUNT(DISTINCT customer_id) as affected_customers,
    -- Sample error messages
    collect_set(failure_message) as sample_error_messages
FROM (
    SELECT event_date, object_type, metric, customer_id, failure_message 
    FROM webhook_email_events WHERE failure_message IS NOT NULL
    UNION ALL
    SELECT event_date, object_type, metric, customer_id, failure_message 
    FROM webhook_sms_events WHERE failure_message IS NOT NULL
    UNION ALL
    SELECT event_date, object_type, metric, customer_id, failure_message 
    FROM webhook_push_events WHERE failure_message IS NOT NULL
    UNION ALL
    SELECT event_date, object_type, metric, customer_id, failure_message 
    FROM webhook_in_app_events WHERE failure_message IS NOT NULL
    UNION ALL
    SELECT event_date, object_type, metric, customer_id, failure_message 
    FROM webhook_slack_events WHERE failure_message IS NOT NULL
    UNION ALL
    SELECT event_date, object_type, metric, customer_id, failure_message 
    FROM webhook_webhook_events WHERE failure_message IS NOT NULL
) all_errors
GROUP BY event_date, object_type, metric
ORDER BY event_date DESC, error_count DESC;

-- Journey performance tracking
CREATE OR REPLACE VIEW journey_performance AS
SELECT 
    journey_id,
    object_type as channel,
    COUNT(*) as total_events,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT action_id) as unique_actions,
    SUM(CASE WHEN metric IN ('sent', 'delivered') THEN 1 ELSE 0 END) as messages_sent,
    SUM(CASE WHEN metric IN ('opened', 'clicked') THEN 1 ELSE 0 END) as engagement_events,
    -- Calculate engagement rate
    ROUND(SUM(CASE WHEN metric IN ('opened', 'clicked') THEN 1 ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN metric IN ('sent', 'delivered') THEN 1 ELSE 0 END), 0), 2) as engagement_rate,
    MIN(event_date) as journey_start_date,
    MAX(event_date) as journey_last_activity
FROM (
    SELECT journey_id, object_type, metric, customer_id, action_id, event_date FROM webhook_email_events WHERE journey_id IS NOT NULL
    UNION ALL
    SELECT journey_id, object_type, metric, customer_id, action_id, event_date FROM webhook_sms_events WHERE journey_id IS NOT NULL
    UNION ALL
    SELECT journey_id, object_type, metric, customer_id, action_id, event_date FROM webhook_push_events WHERE journey_id IS NOT NULL
    UNION ALL
    SELECT journey_id, object_type, metric, customer_id, action_id, event_date FROM webhook_in_app_events WHERE journey_id IS NOT NULL
) journey_events
GROUP BY journey_id, object_type
ORDER BY messages_sent DESC;