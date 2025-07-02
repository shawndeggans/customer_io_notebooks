# Customer.IO App API Integration Tests

Simple integration tests for the Customer.IO App API that test real API functionality with automatic test data creation and cleanup.

## Quick Start

1. **Setup credentials**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API token
   ```

2. **Run tests**:
   ```bash
   pytest tests/app_api/integration/
   ```

That's it! Tests automatically create their own data and clean up after themselves.

## Configuration

### Required Setup

Copy `.env.example` to `.env` and add your API token:

```env
# Required: App API Bearer Token
CUSTOMERIO_APP_API_TOKEN=your_app_api_token_here

# Optional: Region (default: us)
CUSTOMERIO_REGION=us
```

### Get App API Token

1. Log into Customer.IO
2. Go to Settings > API Credentials
3. Navigate to App API Keys section
4. Generate or copy your Bearer token

### Optional: Messaging Test Configuration

For tests that send actual messages, optionally configure:

```env
# Optional: For messaging tests (if not set, those tests will be skipped)
TEST_TRANSACTIONAL_MESSAGE_ID=12345
TEST_BROADCAST_ID=67890
```

## Running Tests

### Basic Usage

```bash
# Run all App API integration tests
pytest tests/app_api/integration/

# Run specific test file
pytest tests/app_api/integration/test_customer_integration.py

# Run with verbose output
pytest tests/app_api/integration/ -v

# Run specific test
pytest tests/app_api/integration/test_customer_integration.py::test_create_and_delete_customer
```

## What the Tests Do

### Customer Management Tests (`test_customer_integration.py`)
- **Search**: Find customers by email
- **CRUD operations**: Create, read, update, delete customers  
- **Activities**: Retrieve customer activity history
- **Messages**: Get customer message history
- **Segments**: View customer segment membership
- **Suppression**: Manage customer suppression status

### Messaging Tests (`test_messaging_integration.py`)
- **Transactional emails**: Send emails using message templates
- **Broadcasts**: Trigger broadcast campaigns  
- **Push notifications**: Send push messages to devices
- **Error handling**: Test invalid parameters and IDs
- **Unicode support**: Test international content

## Automatic Test Data Management

- **Fresh data**: Each test creates its own unique test data
- **Automatic cleanup**: Test data is automatically deleted after each test
- **No pollution**: Tests don't interfere with your workspace data
- **Self-contained**: No need to pre-configure test data

## Test Behavior

### Automatic Skipping
Tests are automatically skipped when:
- **No credentials**: App API token not configured
- **Missing IDs**: Messaging tests skip if transactional/broadcast IDs not configured

### Error Handling
Tests include proper error handling for:
- Authentication errors (invalid token)
- Resource not found errors (invalid IDs)
- Rate limiting (built-in delays)
- Permission errors

## Troubleshooting

### Tests Are All Skipped
- **Cause**: Invalid or missing `CUSTOMERIO_APP_API_TOKEN`
- **Solution**: Get a valid Bearer token from Customer.IO UI

### Messaging Tests Are Skipped
- **Cause**: `TEST_TRANSACTIONAL_MESSAGE_ID` or `TEST_BROADCAST_ID` not configured
- **Solution**: Add real message/broadcast IDs to `.env` file (optional)

### Authentication Errors (401)
- **Cause**: Token is invalid or lacks permissions
- **Solution**: Generate a new token with appropriate permissions

### Rate Limit Errors (429)
- **Cause**: Tests running too fast (rare)
- **Solution**: Tests have built-in rate limiting (100ms delay between tests)

## Development Notes

- Tests use pytest fixtures for automatic setup/cleanup
- Each test is independent and self-contained
- No complex configuration or modes
- Simple `pytest` command works out of the box
- Minimal impact on your Customer.IO workspace