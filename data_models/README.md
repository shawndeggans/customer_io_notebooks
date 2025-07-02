# Customer.IO Data Models for Databricks Unity Catalog

This directory contains SQL table definitions for Customer.IO data models, designed for use with Databricks Unity Catalog. These data models are based on actual data structures extracted from working integration tests, ensuring they accurately represent the data being sent to Customer.IO.

## Overview

These SQL table definitions serve as a foundation for mapping data from other systems to Customer.IO. Each file represents a different aspect of the Customer.IO Data Pipelines API and includes comprehensive table structures with proper relationships, indexes, and constraints.

## File Structure

```
data_models/
├── README.md                           # This documentation
├── 99_create_all.sql                   # Master script to create all tables
├── 01_core_people.sql                  # People management and user profiles
├── 02_events.sql                       # Event tracking and behavioral data
├── 03_ecommerce.sql                    # E-commerce and semantic events
├── 04_devices.sql                      # Device registration and management
├── 05_objects_relationships.sql        # Objects and relationships
├── 06_video.sql                        # Video tracking and playback events
├── 07_privacy_gdpr.sql                 # GDPR compliance and privacy
├── 08_batch_operations.sql             # Batch processing operations
├── 09_user_aliases.sql                 # User aliases and profile merging
└── 10_app_api_communications.sql       # App API message delivery and analytics
```

## Table Descriptions

### 01_core_people.sql
**Core people management and user profiles**
- `people` - Main user profiles table
- `people_events` - User lifecycle events (User Deleted, User Suppressed)
- `people_traits_history` - Historical tracking of trait changes

**Key Features:**
- Complete user profile management
- Nested profile data structures
- Suppression/unsuppression tracking
- Trait change history

### 02_events.sql
**Event tracking and behavioral analytics**
- `events` - Main events table for custom event tracking
- `page_views` - Page view tracking with URL and referrer data
- `screen_views` - Mobile screen view tracking
- `event_sequences` - Event sequencing and funnel analysis

**Key Features:**
- Custom event properties
- Page and screen view tracking
- Event sequencing
- User journey analysis

### 03_ecommerce.sql
**E-commerce and semantic events**
- `ecommerce_events` - All e-commerce semantic events
- `products` - Product catalog and metadata
- `shopping_carts` - Cart state and abandonment tracking
- `wishlists` - Product wishlist management
- `product_reviews` - Reviews and ratings

**Key Features:**
- Complete e-commerce event tracking
- Product search and interaction
- Cart abandonment analysis
- Coupon and promotion tracking
- Review and rating management

### 04_devices.sql
**Device registration and management**
- `devices` - Device registration and metadata
- `device_events` - Device lifecycle events
- `push_tokens` - Push notification token management
- `device_sessions` - App usage session tracking

**Key Features:**
- iOS and Android device support
- Push notification management
- Session tracking
- Device metadata collection

### 05_objects_relationships.sql
**Objects and relationships management**
- `objects` - Non-people entities (companies, accounts, products)
- `relationships` - User-to-object relationships
- `object_events` - Object lifecycle tracking
- `relationship_events` - Relationship change tracking
- `object_types` - Object type definitions

**Key Features:**
- Flexible object modeling
- User-object relationships
- Object lifecycle tracking
- Type-based object classification

### 06_video.sql
**Video tracking and playback analytics**
- `video_events` - All video playback events
- `video_content` - Video content catalog
- `video_sessions` - Complete viewing sessions
- `video_advertising` - Ad tracking and performance

**Key Features:**
- Complete video playback lifecycle
- Content and episode tracking
- Advertising analytics
- Session-based metrics

### 07_privacy_gdpr.sql
**GDPR compliance and privacy management**
- `gdpr_compliance_events` - All privacy-related events
- `privacy_requests` - Data subject request tracking
- `data_exports` - GDPR data export management
- `consent_management` - User consent tracking

**Key Features:**
- GDPR compliance tracking
- Data subject rights management
- Consent management
- Privacy request workflows

### 08_batch_operations.sql
**Batch processing operations**
- `batch_jobs` - Batch job tracking and status
- `batch_operations` - Individual operations within batches
- `batch_chunks` - Batch splitting and chunking
- `batch_errors` - Error tracking and resolution
- `batch_performance_metrics` - Performance monitoring

**Key Features:**
- Large batch processing
- Error handling and recovery
- Performance monitoring
- Chunk management

### 09_user_aliases.sql
**User aliases and profile merging**
- `user_aliases` - Profile alias relationships
- `alias_events` - Alias operation tracking
- `anonymous_identity_resolution` - Anonymous-to-known user mapping
- `alias_chains` - Complex multi-level aliases

**Key Features:**
- Profile merging and deduplication
- Anonymous user identification
- Alias chain management
- Identity resolution

### 10_app_api_communications.sql
**App API message delivery and performance analytics**
- `app_transactional_messages` - Transactional email tracking and analytics
- `app_broadcast_campaigns` - Broadcast campaign execution and performance
- `app_push_notifications` - Push notification delivery and engagement
- `app_message_performance` - Cross-channel message analytics
- `app_delivery_errors` - Centralized error tracking and resolution

**Key Features:**
- End-to-end message delivery tracking
- Cross-channel performance analytics
- Template and campaign optimization insights
- Error monitoring and resolution tracking
- Conversion attribution and ROI analysis

## Database Schema

All tables are designed for the `customerio` schema in Databricks Unity Catalog:

```sql
-- Example table reference
customerio.people
customerio.events
customerio.ecommerce_events
customerio.app_transactional_messages
customerio.app_broadcast_campaigns
customerio.app_push_notifications
-- ... etc
```

## Data Types and Compatibility

The SQL files use Databricks-compatible data types:
- `STRING` for text data
- `INT`, `BIGINT`, `DOUBLE` for numeric data
- `BOOLEAN` for true/false values
- `TIMESTAMP` for date/time data
- `ARRAY<type>` for arrays
- `STRUCT<field: type>` for nested objects
- `MAP<key_type, value_type>` for key-value pairs

## Key Features

### Delta Lake Integration
- All tables use `USING DELTA` for optimal performance
- Auto-optimization enabled with `delta.autoOptimize.optimizeWrite`
- Auto-compaction for better query performance

### Data Quality
- Comprehensive constraints and foreign keys
- Data quality expectations in table properties
- Input validation checks
- Referential integrity enforcement

### Performance Optimization
- Strategic indexes on commonly queried columns
- Partitioning recommendations for large tables
- Optimized storage locations

### Flexibility
- Raw JSON storage for complex/evolving data structures
- Extensible schemas that can accommodate new fields
- Backward compatibility considerations

## Usage Instructions

### 1. Create All Tables
Use the master script to create all tables:

```sql
-- Run the master script
\source 99_create_all.sql
```

### 2. Create Individual Tables
Or create tables individually:

```sql
-- Example: Create people management tables
\source 01_core_people.sql

-- Example: Create event tracking tables
\source 02_events.sql
```

### 3. Customize for Your Environment

Before running, update the following in each file:

```sql
-- Update storage location
LOCATION 's3://your-bucket/customerio/table_name'

-- Update schema name if different
CREATE TABLE IF NOT EXISTS your_schema.table_name
```

### 4. Set Up Permissions

Grant appropriate permissions:

```sql
-- Grant read access
GRANT SELECT ON SCHEMA customerio TO `data_analysts`;

-- Grant write access
GRANT INSERT, UPDATE, DELETE ON SCHEMA customerio TO `data_engineers`;
```

## Data Mapping Examples

### User Identification
```sql
-- Map your user data to Customer.IO people table
INSERT INTO customerio.people (
    user_id,
    email,
    first_name,
    last_name,
    created_at
)
SELECT 
    user_id,
    email_address,
    first_name,
    last_name,
    registration_date
FROM your_system.users;
```

### Event Tracking
```sql
-- Map your events to Customer.IO events table
INSERT INTO customerio.events (
    event_id,
    user_id,
    event_name,
    event_properties,
    event_timestamp
)
SELECT 
    event_id,
    user_id,
    action_name,
    to_json(properties),
    occurred_at
FROM your_system.user_actions;
```

## Best Practices

### 1. Data Loading
- Use batch loading for large datasets
- Implement incremental loading for ongoing updates
- Validate data quality before loading

### 2. Schema Evolution
- Use schema evolution features for adding new columns
- Maintain backward compatibility
- Document schema changes

### 3. Performance
- Partition large tables by date
- Use appropriate clustering keys
- Monitor query performance and optimize indexes

### 4. Data Governance
- Implement proper access controls
- Document data lineage
- Set up monitoring and alerting

## Integration with Customer.IO

These tables are designed to facilitate:

1. **Data Mapping**: Understanding how your data maps to Customer.IO structures
2. **ETL Pipeline Design**: Building pipelines to send data to Customer.IO
3. **Data Validation**: Ensuring data quality before sending to Customer.IO
4. **Analytics**: Analyzing your Customer.IO data in Databricks

## Support and Maintenance

### Monitoring
- Set up data quality monitoring
- Monitor table sizes and growth
- Track query performance

### Maintenance
- Regular OPTIMIZE operations for Delta tables
- VACUUM old versions periodically
- Update table statistics

### Updates
- These schemas are based on integration test data
- Update schemas as Customer.IO API evolves
- Test schema changes in development environment

## Technical Notes

### Source of Truth
These data models are extracted from working integration tests in the codebase:

**Pipelines API Models:**
- `tests/integration/test_people_integration.py`
- `tests/integration/test_event_integration.py` 
- `tests/integration/test_ecommerce_integration.py`
- `tests/integration/test_device_integration.py`
- `tests/integration/test_object_integration.py`
- `tests/integration/test_video_integration.py`
- `tests/integration/test_gdpr_integration.py`
- `tests/integration/test_batch_integration.py`
- `tests/integration/test_alias_integration.py`

**App API Models:**
- `tests/app_api/integration/test_messaging_integration.py`
- `src/app_api/client.py` - Function signatures and response structures

### Compatibility
- Designed for Databricks Unity Catalog
- Compatible with Delta Lake format
- Supports Spark SQL operations
- Can be adapted for other SQL platforms

---

For questions or issues with these data models, please refer to the integration tests or contact your data engineering team.