-- ==================================================
-- Customer.IO Video Tracking Data Models
-- ==================================================
-- Based on actual data structures from integration tests
-- Compatible with Databricks Unity Catalog
-- ==================================================

-- Video events table for all video playback and interaction events
CREATE TABLE IF NOT EXISTS customerio.video_events (
    -- Event identification
    event_id STRING NOT NULL COMMENT 'Unique identifier for this video event',
    user_id STRING NOT NULL COMMENT 'User who performed this video action',
    
    -- Video identification
    video_id STRING NOT NULL COMMENT 'Unique identifier for the video',
    content_id STRING COMMENT 'Content identifier for the video (EPISODE_123)',
    session_id STRING COMMENT 'Video session identifier for grouping related events',
    
    -- Event classification
    event_type STRING NOT NULL COMMENT 'Type of video event (playback, content, advertising, buffering)',
    event_name STRING NOT NULL COMMENT 'Specific event name (Video Playback Started, Video Ad Completed, etc.)',
    
    -- Video metadata
    title STRING COMMENT 'Video title (Integration Test Video)',
    duration INT COMMENT 'Total video duration in seconds (120)',
    quality STRING COMMENT 'Video quality (1080p, 720p, 480p)',
    
    -- Content metadata (for content events)
    series STRING COMMENT 'Series name (Test Series)',
    season INT COMMENT 'Season number (1)',
    episode INT COMMENT 'Episode number (5)',
    genre STRING COMMENT 'Content genre (Technology, Drama, Comedy)',
    
    -- Playback position and progress
    position DOUBLE COMMENT 'Current playback position in seconds (30.5)',
    completion_rate DOUBLE COMMENT 'Completion rate as decimal (0.625 = 62.5%)',
    
    -- Buffering information
    buffer_duration DOUBLE COMMENT 'Duration of buffering event in seconds (2.5)',
    buffer_start_position DOUBLE COMMENT 'Position where buffering started',
    
    -- Advertising information
    ad_id STRING COMMENT 'Advertisement identifier (AD_123)',
    ad_type STRING COMMENT 'Type of ad (pre-roll, mid-roll, post-roll)',
    ad_duration INT COMMENT 'Advertisement duration in seconds (30)',
    advertiser STRING COMMENT 'Advertiser name (Test Brand)',
    campaign STRING COMMENT 'Ad campaign name (Summer 2024)',
    
    -- Playback control events
    exit_reason STRING COMMENT 'Reason for exiting video (user_action, error, completion)',
    pause_reason STRING COMMENT 'Reason for pausing (user_action, buffering, ad_break)',
    
    -- Video quality and technical metrics
    bitrate INT COMMENT 'Video bitrate in kbps',
    fps INT COMMENT 'Frames per second',
    resolution STRUCT<
        width: INT,
        height: INT
    > COMMENT 'Video resolution dimensions',
    
    -- Player and device context
    player_version STRING COMMENT 'Video player version',
    device_type STRING COMMENT 'Device type (mobile, desktop, tv)',
    connection_type STRING COMMENT 'Network connection type (wifi, cellular)',
    
    -- Engagement metrics
    seek_count INT DEFAULT 0 COMMENT 'Number of seeks performed',
    replay_count INT DEFAULT 0 COMMENT 'Number of replays',
    fullscreen_enabled BOOLEAN COMMENT 'Whether video was watched in fullscreen',
    
    -- Raw event properties for flexibility
    raw_properties MAP<STRING, STRING> COMMENT 'All event properties as key-value pairs',
    
    -- Complex nested video properties
    video_properties STRUCT<
        title: STRING,
        duration: INT,
        quality: STRING,
        position: DOUBLE,
        completion_rate: DOUBLE,
        is_historical: BOOLEAN,
        playback_speed: DOUBLE,
        volume_level: DOUBLE,
        subtitle_enabled: BOOLEAN,
        picture_in_picture: BOOLEAN
    > COMMENT 'Complete video properties from integration tests',
    
    -- Content properties for series/episodes
    content_properties STRUCT<
        content_id: STRING,
        series: STRING,
        season: INT,
        episode: INT,
        genre: STRING,
        content_type: STRING,
        content_duration: INT,
        content_rating: STRING
    > COMMENT 'Content-specific properties for series and episodes',
    
    -- Ad properties for advertising events
    ad_properties STRUCT<
        ad_id: STRING,
        ad_type: STRING,
        ad_duration: INT,
        advertiser: STRING,
        campaign: STRING,
        ad_position: STRING,
        skip_available: BOOLEAN,
        skip_offset: INT
    > COMMENT 'Advertisement-specific properties',
    
    -- Technical performance metrics
    performance_metrics STRUCT<
        load_time: DOUBLE,
        start_time: DOUBLE,
        buffer_health: DOUBLE,
        dropped_frames: INT,
        startup_time: DOUBLE
    > COMMENT 'Video playback performance metrics',
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the video event occurred',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When Customer.IO received the event',
    
    -- Data lineage
    source_system STRING COMMENT 'System that generated this event',
    integration_id STRING COMMENT 'Integration identifier',
    player_session_id STRING COMMENT 'Player session identifier',
    
    CONSTRAINT pk_video_events PRIMARY KEY (event_id),
    CONSTRAINT fk_video_events_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT chk_completion_rate CHECK (completion_rate IS NULL OR (completion_rate >= 0 AND completion_rate <= 1))
)
USING DELTA
LOCATION 's3://your-bucket/customerio/video_events'
COMMENT 'Video events table storing all video playback, content, and advertising events'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.video_id_not_null' = 'video_id IS NOT NULL',
    'quality.expectations.event_type_valid' = 'event_type IN ("playback", "content", "advertising", "buffering")',
    'quality.expectations.valid_completion_rate' = 'completion_rate IS NULL OR (completion_rate >= 0 AND completion_rate <= 1)'
);

-- Video content catalog table for video metadata
CREATE TABLE IF NOT EXISTS customerio.video_content (
    -- Content identification
    video_id STRING NOT NULL COMMENT 'Unique video identifier',
    content_id STRING COMMENT 'Content identifier (for series/episodes)',
    
    -- Content metadata
    title STRING NOT NULL COMMENT 'Video title',
    description STRING COMMENT 'Video description',
    
    -- Content classification
    content_type STRING COMMENT 'Type of content (movie, episode, clip, ad)',
    genre STRING COMMENT 'Content genre',
    category STRING COMMENT 'Content category',
    
    -- Series/episode information
    series STRING COMMENT 'Series name',
    season INT COMMENT 'Season number',
    episode INT COMMENT 'Episode number',
    episode_title STRING COMMENT 'Individual episode title',
    
    -- Content properties
    duration INT COMMENT 'Content duration in seconds',
    release_date DATE COMMENT 'Content release date',
    content_rating STRING COMMENT 'Content rating (G, PG, R, etc.)',
    
    -- Technical specifications
    available_qualities ARRAY<STRING> COMMENT 'Available video qualities (1080p, 720p, 480p)',
    default_quality STRING COMMENT 'Default playback quality',
    supported_formats ARRAY<STRING> COMMENT 'Supported video formats (mp4, hls, dash)',
    
    -- Content URLs and assets
    video_url STRING COMMENT 'Primary video URL',
    thumbnail_url STRING COMMENT 'Video thumbnail URL',
    poster_url STRING COMMENT 'Video poster/cover URL',
    
    -- Content status
    status STRING DEFAULT 'active' COMMENT 'Content status (active, inactive, archived)',
    is_premium BOOLEAN DEFAULT FALSE COMMENT 'Whether content requires premium subscription',
    is_featured BOOLEAN DEFAULT FALSE COMMENT 'Whether content is featured',
    
    -- Metadata
    tags ARRAY<STRING> COMMENT 'Content tags for search and categorization',
    cast ARRAY<STRING> COMMENT 'Cast members',
    crew ARRAY<STRING> COMMENT 'Crew members',
    
    -- Engagement metrics
    total_views INT DEFAULT 0 COMMENT 'Total number of views',
    average_completion_rate DOUBLE COMMENT 'Average completion rate across all views',
    total_watch_time_seconds BIGINT DEFAULT 0 COMMENT 'Total watch time across all users',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When content was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When content was last updated',
    published_at TIMESTAMP COMMENT 'When content was published',
    
    CONSTRAINT pk_video_content PRIMARY KEY (video_id)
)
USING DELTA
LOCATION 's3://your-bucket/customerio/video_content'
COMMENT 'Video content catalog storing metadata for all videos'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.video_id_not_null' = 'video_id IS NOT NULL',
    'quality.expectations.title_not_null' = 'title IS NOT NULL',
    'quality.expectations.valid_duration' = 'duration IS NULL OR duration > 0'
);

-- Video sessions table for tracking complete viewing sessions
CREATE TABLE IF NOT EXISTS customerio.video_sessions (
    -- Session identification
    session_id STRING NOT NULL COMMENT 'Unique session identifier',
    user_id STRING NOT NULL COMMENT 'User who owns this session',
    video_id STRING NOT NULL COMMENT 'Video being watched in this session',
    
    -- Session metrics
    session_start TIMESTAMP NOT NULL COMMENT 'When session started',
    session_end TIMESTAMP COMMENT 'When session ended (NULL for active sessions)',
    session_duration_seconds INT COMMENT 'Total session duration in seconds',
    
    -- Playback metrics
    total_watch_time_seconds INT DEFAULT 0 COMMENT 'Actual time spent watching (excluding pauses)',
    max_position_reached DOUBLE DEFAULT 0 COMMENT 'Furthest position reached in video',
    completion_rate DOUBLE COMMENT 'Final completion rate achieved',
    
    -- Interaction metrics
    pause_count INT DEFAULT 0 COMMENT 'Number of pauses during session',
    seek_count INT DEFAULT 0 COMMENT 'Number of seeks during session',
    buffer_count INT DEFAULT 0 COMMENT 'Number of buffering events',
    total_buffer_time_seconds DOUBLE DEFAULT 0 COMMENT 'Total time spent buffering',
    
    -- Ad metrics
    ads_played INT DEFAULT 0 COMMENT 'Number of ads played during session',
    ads_completed INT DEFAULT 0 COMMENT 'Number of ads completed',
    ads_skipped INT DEFAULT 0 COMMENT 'Number of ads skipped',
    
    -- Quality and performance
    primary_quality STRING COMMENT 'Primary quality used during session',
    quality_changes INT DEFAULT 0 COMMENT 'Number of quality changes',
    startup_time_seconds DOUBLE COMMENT 'Time to start playback',
    
    -- Session context
    device_type STRING COMMENT 'Device type used for session',
    player_version STRING COMMENT 'Video player version',
    connection_type STRING COMMENT 'Network connection type',
    
    -- Session outcome
    session_outcome STRING COMMENT 'How session ended (completed, abandoned, error)',
    exit_reason STRING COMMENT 'Specific reason for session end',
    
    -- Engagement indicators
    fullscreen_time_seconds INT DEFAULT 0 COMMENT 'Time spent in fullscreen mode',
    picture_in_picture_time_seconds INT DEFAULT 0 COMMENT 'Time spent in PiP mode',
    
    CONSTRAINT pk_video_sessions PRIMARY KEY (session_id),
    CONSTRAINT fk_video_sessions_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT fk_video_sessions_content FOREIGN KEY (video_id) REFERENCES customerio.video_content(video_id),
    CONSTRAINT chk_session_completion CHECK (completion_rate IS NULL OR (completion_rate >= 0 AND completion_rate <= 1))
)
USING DELTA
LOCATION 's3://your-bucket/customerio/video_sessions'
COMMENT 'Video sessions table for tracking complete viewing sessions'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.session_id_not_null' = 'session_id IS NOT NULL',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.video_id_not_null' = 'video_id IS NOT NULL'
);

-- Video advertising table for ad campaign tracking
CREATE TABLE IF NOT EXISTS customerio.video_advertising (
    -- Ad identification
    ad_event_id STRING NOT NULL COMMENT 'Unique ad event identifier',
    ad_id STRING NOT NULL COMMENT 'Advertisement identifier',
    user_id STRING NOT NULL COMMENT 'User who viewed the ad',
    video_id STRING COMMENT 'Video context where ad was shown',
    session_id STRING COMMENT 'Video session identifier',
    
    -- Ad metadata
    ad_type STRING NOT NULL COMMENT 'Type of ad (pre-roll, mid-roll, post-roll)',
    ad_duration INT COMMENT 'Ad duration in seconds',
    advertiser STRING COMMENT 'Advertiser name',
    campaign STRING COMMENT 'Ad campaign name',
    creative_id STRING COMMENT 'Creative identifier',
    
    -- Ad placement
    ad_position STRING COMMENT 'Position in video (start, middle, end)',
    ad_break_id STRING COMMENT 'Ad break identifier',
    ad_sequence INT COMMENT 'Position in ad sequence (1, 2, 3)',
    
    -- Ad performance
    event_type STRING NOT NULL COMMENT 'Ad event type (started, completed, skipped, clicked)',
    watched_duration_seconds DOUBLE COMMENT 'Actual duration watched',
    skip_available BOOLEAN DEFAULT FALSE COMMENT 'Whether skip was available',
    skip_offset INT COMMENT 'When skip became available (in seconds)',
    
    -- Engagement metrics
    clicked BOOLEAN DEFAULT FALSE COMMENT 'Whether ad was clicked',
    click_url STRING COMMENT 'URL clicked if applicable',
    interaction_count INT DEFAULT 0 COMMENT 'Number of interactions with ad',
    
    -- Ad completion
    completion_rate DOUBLE COMMENT 'Ad completion rate (0.0 to 1.0)',
    completed BOOLEAN DEFAULT FALSE COMMENT 'Whether ad was completed',
    
    -- Timestamps
    ad_start_time TIMESTAMP NOT NULL COMMENT 'When ad started playing',
    ad_end_time TIMESTAMP COMMENT 'When ad ended (completed, skipped, or errored)',
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When this ad event occurred',
    
    -- Data lineage
    source_system STRING COMMENT 'System that generated this ad event',
    integration_id STRING COMMENT 'Integration identifier',
    
    CONSTRAINT pk_video_advertising PRIMARY KEY (ad_event_id),
    CONSTRAINT fk_video_ads_user FOREIGN KEY (user_id) REFERENCES customerio.people(user_id),
    CONSTRAINT fk_video_ads_content FOREIGN KEY (video_id) REFERENCES customerio.video_content(video_id),
    CONSTRAINT chk_ad_completion CHECK (completion_rate IS NULL OR (completion_rate >= 0 AND completion_rate <= 1))
)
USING DELTA
LOCATION 's3://your-bucket/customerio/video_advertising'
COMMENT 'Video advertising table for tracking ad events and performance'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'quality.expectations.ad_event_id_not_null' = 'ad_event_id IS NOT NULL',
    'quality.expectations.ad_id_not_null' = 'ad_id IS NOT NULL',
    'quality.expectations.user_id_not_null' = 'user_id IS NOT NULL',
    'quality.expectations.valid_ad_type' = 'ad_type IN ("pre-roll", "mid-roll", "post-roll", "overlay", "companion")'
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_video_events_user_id ON customerio.video_events(user_id);
CREATE INDEX IF NOT EXISTS idx_video_events_video_id ON customerio.video_events(video_id);
CREATE INDEX IF NOT EXISTS idx_video_events_type ON customerio.video_events(event_type);
CREATE INDEX IF NOT EXISTS idx_video_events_session_id ON customerio.video_events(session_id);
CREATE INDEX IF NOT EXISTS idx_video_events_timestamp ON customerio.video_events(event_timestamp);

CREATE INDEX IF NOT EXISTS idx_video_content_genre ON customerio.video_content(genre);
CREATE INDEX IF NOT EXISTS idx_video_content_series ON customerio.video_content(series);
CREATE INDEX IF NOT EXISTS idx_video_content_status ON customerio.video_content(status);
CREATE INDEX IF NOT EXISTS idx_video_content_type ON customerio.video_content(content_type);

CREATE INDEX IF NOT EXISTS idx_video_sessions_user_id ON customerio.video_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_video_sessions_video_id ON customerio.video_sessions(video_id);
CREATE INDEX IF NOT EXISTS idx_video_sessions_start ON customerio.video_sessions(session_start);
CREATE INDEX IF NOT EXISTS idx_video_sessions_outcome ON customerio.video_sessions(session_outcome);

CREATE INDEX IF NOT EXISTS idx_video_ads_user_id ON customerio.video_advertising(user_id);
CREATE INDEX IF NOT EXISTS idx_video_ads_ad_id ON customerio.video_advertising(ad_id);
CREATE INDEX IF NOT EXISTS idx_video_ads_campaign ON customerio.video_advertising(campaign);
CREATE INDEX IF NOT EXISTS idx_video_ads_type ON customerio.video_advertising(ad_type);
CREATE INDEX IF NOT EXISTS idx_video_ads_event_type ON customerio.video_advertising(event_type);