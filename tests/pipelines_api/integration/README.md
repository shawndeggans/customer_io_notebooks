# Customer.IO Integration Tests

This directory contains integration tests that validate the Customer.IO API client library against the real Customer.IO API. The tests support multiple data management modes including an advanced **Eternal Test Data System** that eliminates test data pollution.

## Prerequisites

### 1. Customer.IO Account
You need a Customer.IO account with API access. Sign up at [customer.io](https://customer.io) if you don't have one.

### 2. API Credentials
1. Log in to your Customer.IO account
2. Navigate to Settings → API Credentials
3. Create a new API key with appropriate permissions
4. Note your region (US or EU)

### 3. Environment Setup
1. Create `.env` file with your credentials:
   ```bash
   # Customer.IO API Configuration
   CUSTOMERIO_API_KEY=your_api_key_here
   CUSTOMERIO_REGION=us  # or 'eu'
   
   # Test Data Mode Configuration
   TEST_DATA_MODE=eternal  # Recommended: eternal, create, existing
   ETERNAL_DATA_ENABLED=true
   SKIP_IF_NO_ETERNAL_DATA=true
   
   # Optional: Debug and rate limiting
   DEBUG_INTEGRATION_TESTS=false
   TEST_RATE_LIMIT_PER_SECOND=10
   ```

2. Setup eternal test data (recommended):
   ```bash
   # Preview what will be created
   python setup_eternal_data.py --dry-run
   
   # Create permanent test data (one-time setup)
   python setup_eternal_data.py --create
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Integration Tests

### Test Data Modes

#### Eternal Data Mode (Recommended)
Uses permanent test data, eliminating data pollution:
```bash
# Run safe read-only tests
pytest tests/pipelines_api/integration/ -m "read_only" -v

# Run all tests (including mutations)
pytest tests/pipelines_api/integration/ -v
```

#### Create Data Mode (Traditional)
Creates new data for each test run:
```bash
TEST_DATA_MODE=create pytest tests/pipelines_api/integration/ -v
```

### Test Selection

#### Run All Integration Tests
```bash
pytest tests/pipelines_api/integration/ -v
```

#### Run Specific Test File
```bash
pytest tests/pipelines_api/integration/test_people_integration.py -v
```

#### Run by Test Category
```bash
# Run only read-only tests (safe for eternal data)
pytest tests/pipelines_api/integration/ -m "read_only" -v

# Run only mutation tests (handle carefully)
pytest tests/pipelines_api/integration/ -m "mutation" -v

# Run tests requiring specific data types
pytest tests/pipelines_api/integration/ -m "eternal_data" -v
```

#### Run with Debug Output
```bash
DEBUG_INTEGRATION_TESTS=true pytest tests/pipelines_api/integration/ -v -s
```

#### Skip Integration Tests (Run Only Unit Tests)
```bash
pytest -m "not integration"
```

## Test Organization

### Test Files
- `test_people_integration.py` - User identification, deletion, suppression
- `test_event_integration.py` - Event tracking, semantic events
- `test_batch_integration.py` - Batch operations, bulk processing
- `test_object_integration.py` - Objects and relationships
- `test_device_integration.py` - Device management
- `test_page_screen_integration.py` - Page/screen tracking
- `test_alias_integration.py` - Profile aliasing
- `test_gdpr_integration.py` - GDPR operations

### Base Classes and Utilities
- `base.py` - Base test class with common functionality
- `utils.py` - Test data generators and helpers
- `conftest.py` - Pytest fixtures and configuration

## Configuration Options

### Environment Variables

#### Core Configuration
- `CUSTOMERIO_API_KEY` - Your Customer.IO API key (required)
- `CUSTOMERIO_REGION` - API region: 'us' or 'eu' (default: 'us')
- `TEST_ENVIRONMENT` - Test environment identifier (default: 'test')

#### Test Data Management
- `TEST_DATA_MODE` - Data mode: 'eternal', 'create', 'existing' (default: 'create')
- `ETERNAL_DATA_ENABLED` - Enable eternal data system (default: 'false')
- `ETERNAL_DATA_VERSION` - Version of eternal data (default: '2025_01_02_v1')
- `SKIP_IF_NO_ETERNAL_DATA` - Skip tests if eternal data missing (default: 'true')

#### Performance and Debugging
- `DEBUG_INTEGRATION_TESTS` - Enable debug logging (default: 'false')
- `TEST_RATE_LIMIT_PER_SECOND` - Max requests per second (default: 10)
- `TEST_DATA_RETENTION_HOURS` - Auto-cleanup age for create mode (default: 24)
- `SKIP_IF_NO_CREDENTIALS` - Skip tests if no credentials (default: 'true')

## Eternal Test Data System

### Overview

The eternal test data system provides a sophisticated approach to integration testing that eliminates data pollution and provides consistent test scenarios.

### Key Benefits

1. **No Data Pollution**: Tests use permanent data instead of creating hundreds of temporary records
2. **Consistent Results**: Same test data across all test runs
3. **Faster Execution**: Reduced API calls during testing
4. **Easy Maintenance**: No cleanup required for read-only tests

### Test Data Types

#### Users
- `basic`: Standard user with minimal data
- `premium`: User with rich profile data
- `inactive`: User for testing edge cases
- `suppression`: User for GDPR suppression testing
- `alias_primary`: User for alias testing
- `gdpr`: User for GDPR compliance testing

#### Devices
- `ios_basic`: iOS device for mobile testing
- `android_basic`: Android device for mobile testing  
- `web_basic`: Web device for browser testing

#### Objects
- `company_a`, `company_b`: Company objects for relationship testing
- `product_x`, `product_y`: Product objects for e-commerce testing

### Test Scenarios

The system includes predefined scenarios that map to specific data combinations:
- `user_identification`: Basic user management operations
- `event_tracking`: Event tracking with different event types
- `device_management`: Device registration and updates
- `object_relationships`: Object and relationship management

### Using Eternal Data in Tests

#### Read-Only Pattern (Recommended)
```python
@pytest.mark.read_only
@pytest.mark.eternal_data("user")
def test_user_identification(authenticated_client, eternal_data_check):
    """Test user identification using eternal data."""
    user_data = get_test_user_data("basic")
    
    if user_data:
        # Use eternal data for testing
        result = identify_user(authenticated_client, user_data["id"], user_data["traits"])
        assert_successful_response(result)
    else:
        pytest.skip("Eternal user data not available")
```

#### Mutation Pattern (Use Carefully)
```python
@pytest.mark.mutation
@pytest.mark.eternal_data("user")
def test_user_suppression(authenticated_client, eternal_data_check):
    """Test user suppression with eternal data."""
    user_data = get_test_user_data("suppression")
    
    if eternal_config.is_eternal_mode and user_data:
        # Use dedicated suppression test user
        user_id = user_data["id"]
        
        # Suppress and then unsuppress to restore state
        suppress_user(authenticated_client, user_id)
        unsuppress_user(authenticated_client, user_id)
    else:
        # Fallback to create mode
        pytest.skip("Eternal suppression data not available")
```

### Migration from Create Mode

#### Step 1: Create Eternal Data
```bash
python setup_eternal_data.py --create
```

#### Step 2: Update Test Code
```python
# Before (create mode)
def test_user_operations(authenticated_client, test_user_id):
    traits = {"email": f"{test_user_id}@test.com"}
    identify_user(authenticated_client, test_user_id, traits)
    # ... test operations
    cleanup_user(authenticated_client, test_user_id)

# After (eternal mode)
@pytest.mark.read_only
@pytest.mark.eternal_data("user")
def test_user_operations(authenticated_client, eternal_data_check):
    user_data = get_test_user_data("basic")
    # ... test operations (no cleanup needed)
```

#### Step 3: Enable Eternal Mode
```bash
TEST_DATA_MODE=eternal pytest tests/pipelines_api/integration/ -v
```

## Best Practices

### 1. Test Data Strategy

#### Eternal Data Mode (Recommended)
- Use permanent test data with predictable IDs
- Users: `eternal_test_user_{type}` (e.g., `eternal_test_user_basic`)
- Objects: `eternal_test_{type}_{name}` (e.g., `eternal_test_company_a`)
- Devices: `eternal_test_device_{platform}_basic`
- No cleanup required for read-only tests

#### Create Data Mode (Traditional)
- Generate unique IDs for each test run
- Users: `test_{type}_user_{timestamp}_{unique_id}`
- Objects: `test_{type}_obj_{timestamp}_{unique_id}`  
- Devices: `test_{type}_device_{timestamp}_{unique_id}`
- Requires cleanup after test completion

This ensures:
- Easy identification of test data
- No conflicts with production data
- Consistent test scenarios (eternal mode)
- Simple cleanup when needed (create mode)

### 2. Test Isolation
Each test:
- Creates its own test data
- Cleans up after completion
- Uses unique identifiers
- Doesn't depend on other tests

### 3. Rate Limiting
Tests respect Customer.IO rate limits:
- Default: 10 requests/second for tests
- Automatic delays between requests
- Exponential backoff on rate limit errors

### 4. Error Handling
Tests handle common scenarios:
- Network errors
- Rate limiting
- API errors
- Eventual consistency delays

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
AuthenticationError: Authentication failed. Check your API key.
```
**Solution**: Verify your API key in `.env` is correct and has proper permissions.

#### 2. Rate Limit Errors
```
RateLimitError: Rate limit exceeded. Please wait before making more requests.
```
**Solution**: Reduce `TEST_RATE_LIMIT_PER_SECOND` in `.env` or add delays between tests.

#### 3. Network Timeouts
```
NetworkError: Request timeout
```
**Solution**: Check your internet connection and Customer.IO API status.

#### 4. Eternal Data Not Found
```
Eternal test data not found: user type 'basic' not available
```
**Solution**: 
1. Run `python setup_eternal_data.py --create` to create eternal data
2. Verify `ETERNAL_DATA_ENABLED=true` in `.env`
3. Check eternal data version matches in configuration

#### 5. Test Data Pollution
```
Error: Too many test records in workspace (800+ records)
```
**Solution**: 
1. Switch to eternal data mode: `TEST_DATA_MODE=eternal`
2. Run read-only tests: `pytest -m "read_only" -v`
3. Implement proper cleanup in existing create-mode tests

#### 6. Test Data Not Cleaned Up (Create Mode)
If tests fail and leave data:
1. Check test output for created resource IDs
2. Use Customer.IO dashboard to manually delete
3. Or create a cleanup script using the resource IDs

### Debug Mode
Enable debug mode for detailed output:
```bash
DEBUG_INTEGRATION_TESTS=true pytest tests/integration/ -v -s
```

This shows:
- API request/response details
- Rate limiting delays
- Resource creation/cleanup
- Timing information

## Writing New Integration Tests

### 1. Inherit from BaseIntegrationTest
```python
from tests.integration.base import BaseIntegrationTest

class TestNewFeatureIntegration(BaseIntegrationTest):
    def test_new_feature(self, authenticated_client):
        # Your test code
```

### 2. Use Fixtures
```python
def test_with_user(self, authenticated_client, test_user_id):
    # test_user_id is automatically unique
    # authenticated_client is ready to use
```

### 3. Track Resources for Cleanup
```python
def test_create_resource(self, authenticated_client):
    resource_id = "test_resource_123"
    
    # Create resource
    create_resource(authenticated_client, resource_id)
    
    # Track for cleanup
    self.track_user(resource_id)  # or track_object, track_device
    
    # Test will automatically cleanup
```

### 4. Handle Rate Limits
```python
def test_multiple_requests(self, authenticated_client):
    for i in range(10):
        # Make request
        result = api_call(authenticated_client)
        
        # Add small delay
        self.wait_for_eventual_consistency(0.2)
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Integration Tests
  env:
    CUSTOMERIO_API_KEY: ${{ secrets.CUSTOMERIO_API_KEY }}
    CUSTOMERIO_REGION: us
    SKIP_IF_NO_CREDENTIALS: false
  run: |
    pytest tests/integration/ -v --junit-xml=integration-results.xml
```

### Jenkins Example
```groovy
stage('Integration Tests') {
    environment {
        CUSTOMERIO_API_KEY = credentials('customerio-api-key')
    }
    steps {
        sh 'pytest tests/integration/ -v'
    }
}
```

## Maintenance

### Regular Cleanup
While tests clean up after themselves, you may want to periodically:
1. Check for orphaned test data in Customer.IO
2. Review test performance metrics
3. Update test data patterns as needed

### Monitoring Test Health
- Track test execution time trends
- Monitor failure rates
- Review Customer.IO API usage
- Check for deprecated API features

## Support

For issues or questions:
1. Check test output for detailed error messages
2. Enable debug mode for more information
3. Review Customer.IO API documentation
4. Check Customer.IO system status

Remember: Integration tests use real API calls and count against your Customer.IO API limits. Use them judiciously, especially in CI/CD pipelines.