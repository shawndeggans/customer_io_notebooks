# Customer.IO Integration Tests

This directory contains integration tests that validate the Customer.IO API client library against the real Customer.IO API.

## Prerequisites

### 1. Customer.IO Account
You need a Customer.IO account with API access. Sign up at [customer.io](https://customer.io) if you don't have one.

### 2. API Credentials
1. Log in to your Customer.IO account
2. Navigate to Settings → API Credentials
3. Create a new API key with appropriate permissions
4. Note your region (US or EU)

### 3. Environment Setup
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   CUSTOMERIO_API_KEY=your_api_key_here
   CUSTOMERIO_REGION=us  # or 'eu'
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install python-dotenv  # If not already installed
   ```

## Running Integration Tests

### Run All Integration Tests
```bash
pytest tests/integration/ -v
```

### Run Specific Test File
```bash
pytest tests/integration/test_people_integration.py -v
```

### Run with Debug Output
```bash
DEBU G_INTEGRATION_TESTS=true pytest tests/integration/ -v -s
```

### Skip Integration Tests (Run Only Unit Tests)
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
- `CUSTOMERIO_API_KEY` - Your Customer.IO API key (required)
- `CUSTOMERIO_REGION` - API region: 'us' or 'eu' (default: 'us')
- `TEST_ENVIRONMENT` - Test environment identifier (default: 'test')
- `DEBUG_INTEGRATION_TESTS` - Enable debug logging (default: false)
- `TEST_RATE_LIMIT_PER_SECOND` - Max requests per second (default: 10)
- `TEST_DATA_RETENTION_HOURS` - Auto-cleanup age (default: 24)
- `SKIP_IF_NO_CREDENTIALS` - Skip tests if no credentials (default: true)

## Best Practices

### 1. Test Data Naming
All test data uses predictable naming patterns:
- Users: `test_{type}_user_{timestamp}_{unique_id}`
- Objects: `test_{type}_obj_{timestamp}_{unique_id}`
- Devices: `test_{type}_device_{timestamp}_{unique_id}`

This ensures:
- Easy identification of test data
- No conflicts with production data
- Simple cleanup if needed

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

#### 4. Test Data Not Cleaned Up
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