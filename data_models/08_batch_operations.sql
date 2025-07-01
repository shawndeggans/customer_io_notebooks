-- ==================================================
-- Customer.IO Batch Operations Data Models
-- ==================================================
-- Based on actual data structures from integration tests
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- Batch jobs table for tracking batch operation requests
CREATE TABLE IF NOT EXISTS customerio.batch_jobs (
    -- Job identification
    batch_job_id STRING NOT NULL COMMENT 'Unique identifier for this batch job',
    batch_id STRING COMMENT 'Customer.IO batch identifier returned by API',
    
    -- Job metadata
    job_name STRING COMMENT 'Human-readable name for this batch job',
    job_description STRING COMMENT 'Description of the batch job purpose',
    job_type STRING NOT NULL COMMENT 'Type of batch job (identify, track, mixed)',
    
    -- Batch configuration
    operation_count INT NOT NULL COMMENT 'Total number of operations in this batch',
    chunk_count INT DEFAULT 1 COMMENT 'Number of chunks this batch was split into',
    max_chunk_size_kb INT COMMENT 'Maximum chunk size in KB for splitting',
    
    -- Batch size and validation
    total_size_bytes BIGINT COMMENT 'Total size of batch data in bytes',
    largest_operation_bytes INT COMMENT 'Size of largest individual operation',
    validation_errors INT DEFAULT 0 COMMENT 'Number of validation errors encountered',
    
    -- Processing status
    job_status STRING DEFAULT 'pending' COMMENT 'Job status (pending, processing, completed, failed, partial)',
    processing_started_at TIMESTAMP COMMENT 'When batch processing started',
    processing_completed_at TIMESTAMP COMMENT 'When batch processing completed',
    
    -- Success/failure tracking
    successful_operations INT DEFAULT 0 COMMENT 'Number of operations that succeeded',
    failed_operations INT DEFAULT 0 COMMENT 'Number of operations that failed',
    skipped_operations INT DEFAULT 0 COMMENT 'Number of operations that were skipped',
    
    -- Performance metrics
    processing_duration_seconds DOUBLE COMMENT 'Total processing time in seconds',
    operations_per_second DOUBLE COMMENT 'Processing rate (operations per second)',
    api_calls_made INT COMMENT 'Number of API calls made for this batch',
    
    -- Error handling
    has_errors BOOLEAN DEFAULT FALSE COMMENT 'Whether batch encountered any errors',
    error_message STRING COMMENT 'Primary error message if batch failed',
    retry_count INT DEFAULT 0 COMMENT 'Number of retry attempts made',
    max_retries INT DEFAULT 3 COMMENT 'Maximum number of retries allowed',
    
    -- Batch data classification
    operation_types ARRAY<STRING> COMMENT 'Types of operations in batch (identify, track)',
    unique_users_count INT COMMENT 'Number of unique users in batch',
    has_timestamps BOOLEAN DEFAULT FALSE COMMENT 'Whether batch includes custom timestamps',
    is_backfill BOOLEAN DEFAULT FALSE COMMENT 'Whether batch is for historical data backfill',
    
    -- Source tracking
    source_system STRING COMMENT 'System that created this batch',
    source_file STRING COMMENT 'Source file name if batch was from file upload',
    integration_id STRING COMMENT 'Integration identifier',
    created_by_user STRING COMMENT 'User who created this batch job',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When batch job was created',
    submitted_at TIMESTAMP COMMENT 'When batch was submitted to Customer.IO',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When batch job was last updated',
    
    CONSTRAINT pk_batch_jobs PRIMARY KEY (batch_job_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/batch_jobs'
COMMENT 'Batch jobs table for tracking batch operation requests and status'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.batch_job_id_not_null' = 'batch_job_id IS NOT NULL',
    'quality.expectations.operation_count_positive' = 'operation_count > 0',
    'quality.expectations.valid_job_status' = 'job_status IN ("pending", "processing", "completed", "failed", "partial")',
    'quality.expectations.successful_plus_failed_equals_total' = 'successful_operations + failed_operations + skipped_operations <= operation_count'
);

-- Batch operations table for individual operations within batches
CREATE TABLE IF NOT EXISTS customerio.batch_operations (
    -- Operation identification
    operation_id STRING NOT NULL COMMENT 'Unique identifier for this operation',
    batch_job_id STRING NOT NULL COMMENT 'Batch job this operation belongs to',
    chunk_index INT DEFAULT 0 COMMENT 'Which chunk this operation was in',
    operation_index INT NOT NULL COMMENT 'Position of operation within batch',
    
    -- Operation details
    operation_type STRING NOT NULL COMMENT 'Type of operation (identify, track)',
    user_id STRING NOT NULL COMMENT 'User this operation applies to',
    
    -- Operation data for identify operations
    identify_traits MAP<STRING, STRING> COMMENT 'User traits for identify operations',
    identify_email STRING COMMENT 'Email address for identify operations',
    identify_name STRING COMMENT 'User name for identify operations',
    
    -- Operation data for track operations
    event_name STRING COMMENT 'Event name for track operations',
    event_properties MAP<STRING, STRING> COMMENT 'Event properties for track operations',
    
    -- Raw operation data
    raw_operation_data STRING COMMENT 'Complete operation data as JSON',
    operation_size_bytes INT COMMENT 'Size of this operation in bytes',
    
    -- Custom timestamp support
    custom_timestamp TIMESTAMP COMMENT 'Custom timestamp provided for this operation',
    is_historical BOOLEAN DEFAULT FALSE COMMENT 'Whether operation is for historical data',
    
    -- Processing status
    operation_status STRING DEFAULT 'pending' COMMENT 'Status (pending, processed, failed, skipped)',
    processed_at TIMESTAMP COMMENT 'When this operation was processed',
    
    -- Error tracking
    error_message STRING COMMENT 'Error message if operation failed',
    error_code STRING COMMENT 'Error code if operation failed',
    validation_errors ARRAY<STRING> COMMENT 'List of validation errors',
    
    -- Response tracking
    api_response_code INT COMMENT 'HTTP response code for this operation',
    api_response_body STRING COMMENT 'API response body',
    
    -- Large data handling
    has_large_data BOOLEAN DEFAULT FALSE COMMENT 'Whether operation contains large data fields',
    data_truncated BOOLEAN DEFAULT FALSE COMMENT 'Whether data was truncated for size limits',
    
    -- Nested operation properties from integration tests
    operation_properties STRUCT<
        type: STRING,
        userId: STRING,
        email: STRING,
        name: STRING,
        plan: STRING,
        event: STRING,
        source: STRING,
        index: INT,
        method: STRING,
        page: STRING,
        segment: STRING,
        backfill: BOOLEAN,
        large_data: STRING,
        more_data: STRING
    > COMMENT 'Complete operation properties from integration tests',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When operation was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When operation was last updated',
    
    CONSTRAINT pk_batch_operations PRIMARY KEY (operation_id),
    CONSTRAINT fk_batch_operations_job FOREIGN KEY (batch_job_id) REFERENCES customerio.batch_jobs(batch_job_id),
    CONSTRAINT fk_batch_operations_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/batch_operations'
COMMENT 'Batch operations table storing individual operations within batch jobs'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.operation_id_not_null' = 'operation_id IS NOT NULL',
    'quality.expectations.batch_job_id_not_null' = 'batch_job_id IS NOT NULL',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.valid_operation_type' = 'operation_type IN ("identify", "track", "page", "screen", "group", "alias")',
    'quality.expectations.valid_operation_status' = 'operation_status IN ("pending", "processed", "failed", "skipped")'
);

-- Batch chunks table for tracking batch splitting
CREATE TABLE IF NOT EXISTS customerio.batch_chunks (
    -- Chunk identification
    chunk_id STRING NOT NULL COMMENT 'Unique identifier for this chunk',
    batch_job_id STRING NOT NULL COMMENT 'Parent batch job',
    chunk_index INT NOT NULL COMMENT 'Index of this chunk within the batch',
    
    -- Chunk configuration
    chunk_size_bytes BIGINT NOT NULL COMMENT 'Size of this chunk in bytes',
    operation_count INT NOT NULL COMMENT 'Number of operations in this chunk',
    chunk_data STRING COMMENT 'Actual chunk data as JSON',
    
    -- Chunk processing
    chunk_status STRING DEFAULT 'pending' COMMENT 'Chunk processing status (pending, sent, completed, failed)',
    sent_at TIMESTAMP COMMENT 'When chunk was sent to Customer.IO API',
    completed_at TIMESTAMP COMMENT 'When chunk processing completed',
    
    -- API interaction
    api_request_id STRING COMMENT 'Customer.IO request ID for this chunk',
    api_response_code INT COMMENT 'HTTP response code',
    api_response_body STRING COMMENT 'API response body',
    
    -- Performance metrics
    send_duration_seconds DOUBLE COMMENT 'Time taken to send chunk',
    processing_duration_seconds DOUBLE COMMENT 'Time taken for API to process chunk',
    
    -- Error handling
    error_message STRING COMMENT 'Error message if chunk failed',
    retry_count INT DEFAULT 0 COMMENT 'Number of retries for this chunk',
    
    -- Chunk optimization
    was_split_from_large_batch BOOLEAN DEFAULT FALSE COMMENT 'Whether chunk was created by splitting large batch',
    split_reason STRING COMMENT 'Reason for splitting (size_limit, operation_limit)',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When chunk was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When chunk was last updated',
    
    CONSTRAINT pk_batch_chunks PRIMARY KEY (chunk_id),
    CONSTRAINT fk_batch_chunks_job FOREIGN KEY (batch_job_id) REFERENCES customerio.batch_jobs(batch_job_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/batch_chunks'
COMMENT 'Batch chunks table for tracking individual chunks of split batches'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.chunk_id_not_null' = 'chunk_id IS NOT NULL',
    'quality.expectations.batch_job_id_not_null' = 'batch_job_id IS NOT NULL',
    'quality.expectations.positive_chunk_size' = 'chunk_size_bytes > 0',
    'quality.expectations.positive_operation_count' = 'operation_count > 0'
);

-- Batch errors table for tracking specific errors
CREATE TABLE IF NOT EXISTS customerio.batch_errors (
    -- Error identification
    error_id STRING NOT NULL COMMENT 'Unique identifier for this error',
    batch_job_id STRING NOT NULL COMMENT 'Batch job where error occurred',
    operation_id STRING COMMENT 'Specific operation that caused error (if applicable)',
    chunk_id STRING COMMENT 'Chunk where error occurred (if applicable)',
    
    -- Error details
    error_type STRING NOT NULL COMMENT 'Type of error (validation, api, network, timeout)',
    error_code STRING COMMENT 'Specific error code',
    error_message STRING NOT NULL COMMENT 'Error message',
    error_details STRING COMMENT 'Detailed error information',
    
    -- Error context
    operation_type STRING COMMENT 'Type of operation that failed',
    user_id STRING COMMENT 'User ID associated with failed operation',
    operation_data STRING COMMENT 'Data that caused the error',
    
    -- Error classification
    is_retryable BOOLEAN DEFAULT FALSE COMMENT 'Whether error is retryable',
    is_user_error BOOLEAN DEFAULT FALSE COMMENT 'Whether error is due to user data',
    is_system_error BOOLEAN DEFAULT FALSE COMMENT 'Whether error is due to system issue',
    
    -- Resolution tracking
    error_status STRING DEFAULT 'open' COMMENT 'Error status (open, investigating, resolved, ignored)',
    resolved_at TIMESTAMP COMMENT 'When error was resolved',
    resolution_notes STRING COMMENT 'Notes about error resolution',
    
    -- API response details
    http_status_code INT COMMENT 'HTTP status code from API',
    api_response_body STRING COMMENT 'Full API response body',
    
    -- Timestamps
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When error occurred',
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When error was first seen',
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When error was last seen',
    
    CONSTRAINT pk_batch_errors PRIMARY KEY (error_id),
    CONSTRAINT fk_batch_errors_job FOREIGN KEY (batch_job_id) REFERENCES customerio.batch_jobs(batch_job_id),
    CONSTRAINT fk_batch_errors_operation FOREIGN KEY (operation_id) REFERENCES customerio.batch_operations(operation_id),
    CONSTRAINT fk_batch_errors_chunk FOREIGN KEY (chunk_id) REFERENCES customerio.batch_chunks(chunk_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/batch_errors'
COMMENT 'Batch errors table for tracking and resolving batch processing errors'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.error_id_not_null' = 'error_id IS NOT NULL',
    'quality.expectations.batch_job_id_not_null' = 'batch_job_id IS NOT NULL',
    'quality.expectations.error_message_not_null' = 'error_message IS NOT NULL',
    'quality.expectations.valid_error_type' = 'error_type IN ("validation", "api", "network", "timeout", "authentication", "rate_limit")'
);

-- Batch performance metrics table
CREATE TABLE IF NOT EXISTS customerio.batch_performance_metrics (
    -- Metric identification
    metric_id STRING NOT NULL COMMENT 'Unique identifier for this metric record',
    batch_job_id STRING NOT NULL COMMENT 'Batch job these metrics relate to',
    
    -- Performance measurements
    total_processing_time_seconds DOUBLE NOT NULL COMMENT 'Total time to process entire batch',
    average_operation_time_ms DOUBLE COMMENT 'Average time per operation in milliseconds',
    operations_per_second DOUBLE COMMENT 'Processing rate in operations per second',
    
    -- Throughput metrics
    total_bytes_processed BIGINT COMMENT 'Total bytes of data processed',
    bytes_per_second DOUBLE COMMENT 'Data throughput in bytes per second',
    api_calls_per_minute DOUBLE COMMENT 'API call rate per minute',
    
    -- Latency metrics
    min_operation_time_ms DOUBLE COMMENT 'Fastest operation time',
    max_operation_time_ms DOUBLE COMMENT 'Slowest operation time',
    p50_operation_time_ms DOUBLE COMMENT '50th percentile operation time',
    p95_operation_time_ms DOUBLE COMMENT '95th percentile operation time',
    p99_operation_time_ms DOUBLE COMMENT '99th percentile operation time',
    
    -- API performance
    average_api_response_time_ms DOUBLE COMMENT 'Average API response time',
    api_success_rate DOUBLE COMMENT 'API success rate (0.0 to 1.0)',
    rate_limit_hits INT DEFAULT 0 COMMENT 'Number of rate limit encounters',
    
    -- Resource utilization
    peak_memory_usage_mb DOUBLE COMMENT 'Peak memory usage during processing',
    cpu_time_seconds DOUBLE COMMENT 'Total CPU time consumed',
    network_bytes_sent BIGINT COMMENT 'Total network bytes sent',
    network_bytes_received BIGINT COMMENT 'Total network bytes received',
    
    -- Efficiency metrics
    chunk_split_efficiency DOUBLE COMMENT 'Efficiency of chunk splitting (0.0 to 1.0)',
    retry_overhead_percent DOUBLE COMMENT 'Percentage overhead due to retries',
    
    -- Comparison metrics
    expected_completion_time_seconds DOUBLE COMMENT 'Expected completion time',
    actual_vs_expected_ratio DOUBLE COMMENT 'Actual time vs expected time ratio',
    
    -- Quality metrics
    data_quality_score DOUBLE COMMENT 'Overall data quality score (0.0 to 1.0)',
    validation_pass_rate DOUBLE COMMENT 'Percentage of operations that passed validation',
    
    -- Timestamps
    measurement_start_time TIMESTAMP COMMENT 'When measurement period started',
    measurement_end_time TIMESTAMP COMMENT 'When measurement period ended',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When metrics were recorded',
    
    CONSTRAINT pk_batch_performance_metrics PRIMARY KEY (metric_id),
    CONSTRAINT fk_batch_metrics_job FOREIGN KEY (batch_job_id) REFERENCES customerio.batch_jobs(batch_job_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/batch_performance_metrics'
COMMENT 'Batch performance metrics for analyzing and optimizing batch processing'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.metric_id_not_null' = 'metric_id IS NOT NULL',
    'quality.expectations.batch_job_id_not_null' = 'batch_job_id IS NOT NULL',
    'quality.expectations.positive_processing_time' = 'total_processing_time_seconds > 0'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON customerio.batch_jobs(job_status);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_type ON customerio.batch_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_created_at ON customerio.batch_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_source_system ON customerio.batch_jobs(source_system);

CREATE INDEX IF NOT EXISTS idx_batch_operations_job_id ON customerio.batch_operations(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_batch_operations_user_id ON customerio.batch_operations(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_operations_type ON customerio.batch_operations(operation_type);
CREATE INDEX IF NOT EXISTS idx_batch_operations_status ON customerio.batch_operations(operation_status);

CREATE INDEX IF NOT EXISTS idx_batch_chunks_job_id ON customerio.batch_chunks(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_batch_chunks_status ON customerio.batch_chunks(chunk_status);
CREATE INDEX IF NOT EXISTS idx_batch_chunks_sent_at ON customerio.batch_chunks(sent_at);

CREATE INDEX IF NOT EXISTS idx_batch_errors_job_id ON customerio.batch_errors(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_batch_errors_type ON customerio.batch_errors(error_type);
CREATE INDEX IF NOT EXISTS idx_batch_errors_status ON customerio.batch_errors(error_status);
CREATE INDEX IF NOT EXISTS idx_batch_errors_occurred_at ON customerio.batch_errors(occurred_at);

CREATE INDEX IF NOT EXISTS idx_batch_metrics_job_id ON customerio.batch_performance_metrics(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_batch_metrics_recorded_at ON customerio.batch_performance_metrics(recorded_at);