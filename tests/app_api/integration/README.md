# Customer.IO App API Integration Tests

This directory contains integration tests for the Customer.IO App API that test real API functionality with different data management modes.

## Test Data Modes

The integration tests support three different data modes to minimize test data creation:

### `existing` Mode (Recommended)
- Uses existing test data from your Customer.IO workspace
- No creation or deletion of resources
- Minimal impact on your data
- Some tests are skipped if they require data creation

### `create` Mode (Default)
- Creates new test data for each run
- Full test coverage including create/delete operations
- Requires cleanup after tests
- Can accumulate test data over time

### `hybrid` Mode
- Uses existing data when possible
- Creates data only when necessary
- Moderate cleanup requirements

## Configuration

### 1. Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
# Required: App API Bearer Token
CUSTOMERIO_APP_API_TOKEN=your_app_api_token_here

# Optional: Test data mode (default: existing for safety)
TEST_DATA_MODE=existing

# Required for existing/hybrid modes: Existing test data IDs
# These should be REAL IDs from your Customer.IO workspace
TEST_EXISTING_CUSTOMER_ID=actual_customer_id_from_workspace
TEST_EXISTING_EMAIL=real_email@your_domain.com
TEST_EXISTING_TRANSACTIONAL_MESSAGE_ID=actual_message_id
TEST_EXISTING_BROADCAST_ID=actual_broadcast_id

# Optional: Device token for push notification tests
TEST_EXISTING_DEVICE_TOKEN=actual_device_token
```

### ⚠️ **Important**: Use Real Data
The test data IDs in `.env.example` are just placeholders. You **must** replace them with actual IDs from your Customer.IO workspace:

- `TEST_EXISTING_CUSTOMER_ID`: A real customer ID from your workspace
- `TEST_EXISTING_TRANSACTIONAL_MESSAGE_ID`: An actual transactional email template ID
- `TEST_EXISTING_BROADCAST_ID`: An actual broadcast campaign ID

If you don't have these, the tests will skip gracefully with helpful messages.

### 2. Get App API Token

1. Log into Customer.IO
2. Go to Settings > API Credentials
3. Navigate to App API Keys section
4. Generate or copy your Bearer token

### 3. Configure Existing Test Data (for existing/hybrid modes)

You'll need existing resources in your Customer.IO workspace:

- **Customer**: A test customer with known ID and email
- **Transactional Message**: A configured transactional email template
- **Broadcast**: A configured broadcast campaign
- **Device Token**: (Optional) For push notification tests

## Running Tests

### Basic Usage

```bash
# Run all App API integration tests
pytest tests/app_api/integration/

# Run specific test file
pytest tests/app_api/integration/test_customer_integration.py

# Run specific test
pytest tests/app_api/integration/test_messaging_integration.py::TestMessagingIntegration::test_send_transactional_with_existing_customer
```

### Mode-Specific Examples

```bash
# Use existing data only (recommended)
TEST_DATA_MODE=existing pytest tests/app_api/integration/

# Create new data with full cleanup
TEST_DATA_MODE=create pytest tests/app_api/integration/

# Hybrid approach
TEST_DATA_MODE=hybrid pytest tests/app_api/integration/

# Run with cleanup report
SHOW_CLEANUP_REPORT=true pytest tests/app_api/integration/
```

### Filtering Tests

```bash
# Skip tests that modify data
pytest tests/app_api/integration/ -m "not modifies_data"

# Run only messaging tests
pytest tests/app_api/integration/test_messaging_integration.py

# Skip tests requiring device tokens
pytest tests/app_api/integration/ -m "not requires_device"
```

## Test Categories

### Messaging Tests (`test_messaging_integration.py`)
- **Transactional emails**: Send emails using message templates
- **Broadcasts**: Trigger broadcast campaigns
- **Push notifications**: Send push messages to devices
- **Error handling**: Test invalid parameters and IDs
- **Unicode support**: Test international content

### Customer Management Tests (`test_customer_integration.py`)
- **Search**: Find customers by email and other criteria
- **CRUD operations**: Create, read, update, delete customers
- **Activities**: Retrieve customer activity history
- **Messages**: Get customer message history
- **Segments**: View customer segment membership
- **Suppression**: Manage customer suppression status

## Test Markers

The tests use pytest markers for organization:

- `@pytest.mark.app_integration`: All App API integration tests
- `@pytest.mark.modifies_data`: Tests that modify existing data
- `@pytest.mark.creates_data`: Tests that create new data
- `@pytest.mark.requires_existing_data`: Tests requiring existing data

## Skipping Logic

Tests are automatically skipped when:

1. **No credentials**: App API token not configured
2. **Existing mode**: Create/delete tests skip in existing data mode
3. **Missing data**: Tests skip if required existing data not available
4. **Missing device**: Push tests skip without device token

## Data Management

### Resource Tracking
- Created customers are tracked for cleanup
- Modified customers have their state backed up
- All changes are restored where possible

### Cleanup Strategy
- **Existing mode**: Restore modifications, no deletions
- **Create mode**: Delete all created resources
- **Hybrid mode**: Delete created, restore modified

### Restoration
When tests modify existing data, the original state is:
1. Captured before modification
2. Restored after test completion
3. Tracked across test session

## Rate Limiting

Tests respect Customer.IO App API rate limits:
- **General endpoints**: 10 requests/second
- **Transactional messages**: 100 requests/second  
- **Broadcasts**: 1 request/10 seconds

## Troubleshooting

### Common Issues

1. **Tests are All Skipped**
   - **Cause**: Invalid or missing `CUSTOMERIO_APP_API_TOKEN`
   - **Solution**: Get a valid Bearer token from Customer.IO UI > Settings > API Credentials > App API Keys
   - **Test**: Run `python -c "from tests.app_api.integration.conftest import validate_api_access; print(validate_api_access())"` - should return `True`

2. **Individual Tests Skip with "not found" Messages**
   - **Cause**: Test data IDs don't exist in your workspace
   - **Solution**: Replace placeholder IDs with real ones from your Customer.IO workspace
   - **Example**: `TEST_EXISTING_CUSTOMER_ID=test_customer_123` → `TEST_EXISTING_CUSTOMER_ID=actual_cust_abc123`

3. **Authentication Errors (401 Unauthorized)**
   - **Cause**: Token is invalid or lacks permissions
   - **Solution**: Generate a new token with appropriate permissions
   - **Note**: Different from 404 errors - this means the token itself is wrong

4. **Rate Limit Errors (429)**
   - **Cause**: Tests running too fast (should be rare)
   - **Solution**: Tests have built-in rate limiting, but you can increase delays
   - **Config**: Reduce `TEST_RATE_LIMIT_PER_SECOND` if needed

5. **Push Test Failures**
   - **Cause**: No valid device token configured
   - **Solution**: These tests skip automatically if `TEST_EXISTING_DEVICE_TOKEN` is not set
   - **Optional**: Add a real device token if you want to test push notifications

### Debug Options

```bash
# Enable debug logging
DEBUG_INTEGRATION_TESTS=true pytest tests/app_api/integration/ -v

# Show cleanup report
SHOW_CLEANUP_REPORT=true pytest tests/app_api/integration/

# Skip tests without retries
SKIP_IF_NO_CREDENTIALS=false pytest tests/app_api/integration/
```

## Best Practices

1. **Use existing mode** for regular testing to minimize data creation
2. **Configure real test data** for meaningful test coverage
3. **Run tests in isolation** to avoid conflicts
4. **Monitor rate limits** during development
5. **Review cleanup reports** to track resource usage

## Architecture

The integration tests follow a layered architecture:

- **conftest.py**: Fixtures and configuration
- **base.py**: Common test utilities and cleanup
- **test_*.py**: Specific test implementations
- **skip decorators**: Conditional test execution
- **resource tracking**: Automatic cleanup management