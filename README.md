# Customer.IO Multi-API Client Library

A comprehensive Python client library and Jupyter notebook suite for all Customer.IO APIs, built using Test-Driven Development (TDD) methodology. This project provides production-ready access to Data Pipelines API, App/Journeys API, and Webhook processing with complete API integration patterns.

## Supported APIs

- **Data Pipelines API**: User identification, event tracking, batch operations, GDPR compliance
- **App/Journeys API**: Customer management, transactional messaging, campaign triggers
- **Webhook Processing**: Signature verification, event parsing, delivery tracking

## Quick Start

### Prerequisites

- Python 3.11+
- Customer.IO API credentials
- UV package manager (recommended) or pip

### Installation

#### Using devbox (Recommended)

```bash
# Install devbox (if not already installed)
curl -fsSL https://get.jetify.com/devbox | bash

# Enter development environment
devbox shell

# Install dependencies
uv install
```

#### Using standard Python setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### Basic Usage

```python
from src.pipelines_api.api_client import CustomerIOClient
from src.pipelines_api.people_manager import identify_user
from src.pipelines_api.event_manager import track_event

# Initialize client with Basic authentication
client = CustomerIOClient(api_key="your_api_key", region="us")

# Identify a user
result = identify_user(
    client=client,
    user_id="user_123",
    traits={"email": "user@example.com", "name": "John Doe"}
)

# Track an event
result = track_event(
    client=client,
    user_id="user_123",
    event_name="Purchase Completed",
    properties={"amount": 99.99, "currency": "USD"}
)
```

### Webhook Processing

```python
from src.webhooks import verify_signature, get_event_handler

# Verify Customer.io webhook signature
is_valid = verify_signature(
    payload=webhook_body,
    signature=request.headers.get('X-CIO-Signature'),
    timestamp=request.headers.get('X-CIO-Timestamp'),
    secret=webhook_secret
)

# Process webhook event
if is_valid:
    handler = get_event_handler("email")  # or "customer", "sms", "push", etc.
    processed_event = handler.handle_event(event_data)
```

### Databricks App Deployment

```bash
# Deploy webhook receiver to Databricks
cd databricks_app
databricks apps deploy --config databricks.yml

# Test webhook endpoint
python test_webhook.py
```

### Testing Approaches

This project uses **different testing strategies** for each API based on their complexity:

#### Pipelines API - Eternal Test Data System
The Pipelines API uses an advanced **Eternal Test Data System** for comprehensive data testing:

```bash
# Preview eternal test data
python setup_eternal_data.py --dry-run

# Create permanent test data  
python setup_eternal_data.py --create

# Enable eternal data mode
# Set TEST_DATA_MODE=eternal in .env

# Run tests without creating new data
pytest tests/pipelines_api/integration/ -m "read_only" -v
```

**Test Data Modes:**
- **Eternal Mode** (recommended): Uses permanent test data, no cleanup needed
- **Create Mode** (default): Creates new data each run, requires cleanup
- **Existing Mode**: Uses specified existing data IDs

#### App API - Simple Direct Testing
The App API uses **direct email-based testing** for communications:

```bash
# Simple setup - just add credentials to .env
CUSTOMERIO_APP_API_TOKEN=your_app_api_token_here

# Run App API tests (uses email addresses directly)
pytest tests/app_api/integration/ -v
```

**App API Testing Features:**
- **Email-based testing**: No complex customer creation needed
- **Automatic cleanup**: Tests are self-contained
- **Communications focus**: Tests transactional emails, broadcasts, push notifications

#### Webhook Processing - Unit Testing
The Webhook Processing uses **unit testing** with mocked webhook payloads:

```bash
# Run webhook tests (no external dependencies)
pytest tests/webhooks/unit/ -v
```

**Webhook Testing Features:**
- **Signature verification testing**: HMAC-SHA256 validation per Customer.io spec
- **Event handler testing**: All 7 Customer.io event types (email, SMS, push, etc.)
- **Databricks App testing**: Complete webhook receiver application
- **Mock webhook payloads**: Realistic Customer.io webhook event simulation

See [TESTING.md](docs/TESTING.md) for comprehensive testing documentation.

## Project Structure

```
customer_io_notebooks/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── devbox.json                         # Development environment
├── pytest.ini                         # Test configuration
├── setup_eternal_data.py               # Eternal test data setup script
├── docs/                               # Project documentation
│   ├── CLAUDE.md                       # AI assistant guidelines
│   ├── PYTHON_STANDARDS.md             # Development standards
│   ├── REQUIREMENTS.md                 # Detailed project requirements
│   ├── TESTING.md                      # Comprehensive testing guide
│   └── WAVE2_PLAN.md                   # Multi-API development strategy
├── specs/                              # API specifications
│   ├── cio_pipelines_api.json          # Data Pipelines API spec
│   ├── cio_journeys_app_api.json       # App/Journeys API spec
│   └── cio_reporting_webhooks.json     # Webhook events spec
├── TODO.md                             # Development progress tracking
├── databricks_app/                    # Databricks App for webhook processing
│   ├── app.py                          # Main Flask webhook receiver
│   ├── config.py                       # Configuration and secrets management
│   ├── requirements.txt                # App dependencies
│   ├── databricks.yml                  # Deployment configuration
│   ├── test_webhook.py                 # Webhook testing utilities
│   └── README.md                       # Deployment guide
│
├── notebooks/                         # Jupyter notebooks organized by API
│   ├── 00_multi_api_overview.ipynb    # Multi-API workflow demonstration
│   ├── pipelines_api/                 # Data Pipelines API notebooks
│   │   ├── 00_setup_and_configuration.ipynb   # Basic setup and authentication
│   │   ├── 01_people_management.ipynb          # User identification and management
│   │   ├── 02_event_tracking.ipynb             # Event tracking and semantic events
│   │   ├── 03_objects_and_relationships.ipynb # Objects and relationships management
│   │   ├── 04_device_management.ipynb          # Device registration and management
│   │   ├── 05_batch_operations.ipynb           # Bulk operations and batch processing
│   │   ├── 06_page_screen_tracking.ipynb      # Page and screen tracking
│   │   └── 07_profile_aliasing.ipynb           # Profile aliasing and identity management
│   ├── app_api/                       # App API notebooks
│   │   └── 01_communications.ipynb     # Transactional emails, broadcasts, push
│   └── webhooks/                      # Webhook processing notebooks
│       └── 01_webhook_processing.ipynb # Complete webhook implementation demo
├── data_models/                       # SQL data models for Databricks
│   ├── README.md                      # Data models documentation
│   ├── 01_core_people.sql             # People management tables
│   ├── 02_events.sql                  # Event tracking tables
│   ├── 10_app_api_communications.sql  # App API analytics tables
│   ├── 11_webhook_events.sql          # Webhook events analytics tables
│   └── 99_create_all.sql              # Master creation script
│
├── src/                                # Source code organized by API
│   ├── pipelines_api/                  # Data Pipelines API client library
│   │   ├── __init__.py
│   │   ├── api_client.py               # Core API client with Basic auth
│   │   ├── people_manager.py           # User identification and management
│   │   ├── event_manager.py            # Core event tracking
│   │   ├── device_manager.py           # Device management
│   │   ├── object_manager.py           # Objects and relationships
│   │   ├── batch_manager.py            # Batch operations
│   │   ├── alias_manager.py            # Profile aliasing operations
│   │   ├── gdpr_manager.py             # GDPR compliance operations
│   │   ├── ecommerce_manager.py        # E-commerce semantic events
│   │   ├── mobile_manager.py           # Mobile app semantic events
│   │   ├── video_manager.py            # Video semantic events
│   │   ├── page_manager.py             # Page tracking
│   │   ├── screen_manager.py           # Screen tracking
│   │   ├── validators.py               # Input validation utilities
│   │   └── exceptions.py               # Custom exception classes
│   ├── app_api/                        # App/Journeys API client library
│   │   ├── __init__.py
│   │   ├── auth.py                     # Bearer token authentication
│   │   └── client.py                   # Customer management, messaging
│   └── webhooks/                       # Webhook processing utilities
│       ├── __init__.py
│       ├── processor.py                # Signature verification, event parsing
│       ├── event_handlers.py           # Event handlers for all Customer.io event types
│       └── config_manager.py           # Webhook configuration and management
│
└── tests/                              # Comprehensive test suite
    ├── conftest.py                     # Global test configuration
    ├── eternal_config.py               # Eternal data configuration
    ├── eternal_test_data.py            # Test data definitions
    ├── eternal_utils.py                # Data discovery utilities
    ├── fixtures/                       # Test data files
    ├── pipelines_api/                  # Pipelines API tests
    │   ├── unit/                       # Unit tests with mocks
    │   │   ├── test_api_client.py
    │   │   ├── test_people_manager.py
    │   │   ├── test_event_manager.py
    │   │   └── [other unit tests]
    │   └── integration/                # Real API integration tests
    │       ├── README.md               # Integration testing guide
    │       ├── conftest.py             # Integration test fixtures
    │       ├── base.py                 # Base test class
    │       ├── utils.py                # Test utilities
    │       ├── test_people_integration.py
    │       ├── test_event_integration.py
    │       └── [other integration tests]
    ├── app_api/                        # App API tests
    │   ├── unit/                       # Unit tests with mocks
    │   │   ├── test_auth.py
    │   │   └── test_client.py
    │   └── integration/                # Simple integration tests
    │       └── test_messaging_integration.py
    └── webhooks/                       # Webhook tests
        └── unit/                       # Unit tests for webhook processing
            ├── test_processor.py       # Signature verification tests
            └── test_event_handlers.py  # Event handler tests
```

## Core Components

### API Client (`src/pipelines_api/api_client.py`)

The `CustomerIOClient` provides a robust interface to the Customer.IO Data Pipelines API with:

- **Basic Authentication**: Uses API key with Basic auth (not Bearer)
- **Rate Limiting**: Respects 3000 requests per 3 seconds limit
- **Regional Support**: Both US and EU regions
- **Error Handling**: Comprehensive error handling with retries
- **Request/Response Logging**: Built-in logging capabilities

```python
from src.pipelines_api.api_client import CustomerIOClient

# Initialize with Basic authentication
client = CustomerIOClient(
    api_key="your_api_key",
    region="us",  # or "eu"
    timeout=30,
    max_retries=3
)
```

### Pipelines API Modules

Each module provides specific Customer.IO Data Pipelines functionality:

#### People Management (`src/pipelines_api/people_manager.py`)
```python
from src.pipelines_api.people_manager import identify_user, delete_user, suppress_user, unsuppress_user

# User identification
identify_user(client, user_id, traits)

# User suppression
suppress_user(client, user_id)
unsuppress_user(client, user_id)

# User deletion (uses semantic event)
delete_user(client, user_id)
```

#### Event Tracking (`src/pipelines_api/event_manager.py`)
```python
from src.pipelines_api.event_manager import track_event, track_page_view, track_screen_view

# Custom events
track_event(client, user_id, event_name, properties)

# Page/screen events
track_page_view(client, user_id, page_name, properties)
track_screen_view(client, user_id, screen_name, properties)
```

#### Device Management (`src/pipelines_api/device_manager.py`)
```python
from src.pipelines_api.device_manager import register_device, update_device, delete_device

# Device registration (requires user_id, device_token, device_type)
register_device(client, user_id, device_token, device_type="ios", metadata={})
```

#### Objects and Relationships (`src/pipelines_api/object_manager.py`)
```python
from src.pipelines_api.object_manager import create_object, update_object, delete_object

# Object management (requires user_id, object_id, traits)
create_object(client, user_id, object_id, traits, object_type_id="1")
```

#### Video Events (`src/pipelines_api/video_manager.py`)
```python
from src.pipelines_api.video_manager import track_video_playback_started, track_video_playback_completed

# Video tracking (requires video_id as separate parameter)
track_video_playback_started(client, user_id, video_id, properties)
```

#### E-commerce Events (`src/pipelines_api/ecommerce_manager.py`)
```python
from src.pipelines_api.ecommerce_manager import track_product_clicked, track_checkout_step_completed

# E-commerce semantic events
track_product_clicked(client, user_id, properties)
track_checkout_step_completed(client, user_id, properties)
```

#### Batch Operations (`src/pipelines_api/batch_manager.py`)
```python
from src.pipelines_api.batch_manager import send_batch, create_batch_operations

# Batch processing
operations = create_batch_operations("identify", user_data_list)
send_batch(client, operations)
```

### Webhook Processing (`src/webhooks/`)

The webhook processing system provides secure webhook reception and event processing for all Customer.io event types:

#### Webhook Signature Verification (`src/webhooks/processor.py`)
```python
from src.webhooks import verify_signature, parse_event, get_event_type

# Verify Customer.io webhook signature (HMAC-SHA256 with v0:timestamp:body format)
is_valid = verify_signature(
    payload=webhook_body,
    signature=request.headers.get('X-CIO-Signature'),
    timestamp=request.headers.get('X-CIO-Timestamp'),
    secret=webhook_secret
)

# Parse and route webhook events
event = parse_event(webhook_body)
object_type, metric = get_event_type(event)  # e.g., ("email", "opened")
```

#### Event Handlers (`src/webhooks/event_handlers.py`)
```python
from src.webhooks import get_event_handler

# Process different event types with dedicated handlers
email_handler = get_event_handler("email")        # Email events (opened, clicked, etc.)
customer_handler = get_event_handler("customer")  # Customer subscription events
sms_handler = get_event_handler("sms")            # SMS delivery events
push_handler = get_event_handler("push")          # Push notification events

# Process event and get analytics-ready data
processed_event = email_handler.handle_event(event_data)
```

#### Webhook Configuration (`src/webhooks/config_manager.py`)
```python
from src.webhooks import CustomerIOWebhookManager, setup_databricks_webhook

# Set up webhooks via Customer.io App API
manager = CustomerIOWebhookManager(api_token="your_app_token", region="us")
webhook = manager.create_webhook(
    webhook_url="https://your-databricks-app.com/webhook/customerio",
    events=["email_opened", "email_clicked", "customer_subscribed"]
)

# Or use the simplified setup function
webhook = setup_databricks_webhook(api_token, databricks_url)
```

### Databricks App (`databricks_app/`)

Production-ready webhook receiver application for Databricks deployment:

- **Flask Application** (`app.py`): Complete webhook endpoint with signature verification
- **Event Processing**: Automatic routing to event handlers and Delta Lake storage
- **Configuration Management** (`config.py`): Secure secrets and environment handling
- **Testing Utilities** (`test_webhook.py`): Complete webhook simulation and testing
- **Deployment Ready** (`databricks.yml`): One-command deployment to Databricks

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd customer_io_notebooks
   ```

2. **Enter development environment**
   ```bash
   devbox shell  # or manually activate virtual environment
   ```

3. **Install dependencies**
   ```bash
   uv install
   ```

4. **Configure credentials**
   ```bash
   # Create .env file from template
   cp .env.example .env
   # Edit .env with your Customer.IO API key
   ```

### Running Tests

This project follows Test-Driven Development (TDD) with comprehensive test coverage.

#### Run all tests
```bash
pytest
```

#### Run unit tests only (297 tests)
```bash
pytest tests/unit/ -v
```

#### Run integration tests (requires API credentials)
```bash
# Set up credentials first
export CUSTOMERIO_API_KEY="your_api_key"
export CUSTOMERIO_REGION="us"

# Run integration tests
pytest tests/integration/ -v
```

#### Run with coverage
```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

#### Test Categories
- `unit`: Fast unit tests with mocks (297 tests)
- `integration`: Tests with real Customer.IO API
- `read_only`: Safe tests for eternal data mode
- `mutation`: Tests that modify data (use carefully)
- `slow`: Longer-running tests

#### Test Data Markers
- `@pytest.mark.eternal_data("user")`: Requires eternal user data
- `@pytest.mark.read_only`: Safe for eternal data mode
- `@pytest.mark.mutation`: Modifies data, handle carefully

### Code Quality

#### Type Checking
```bash
mypy utils/ --strict
```

#### Linting and Formatting
```bash
ruff check --fix .
ruff format .
```

#### Running Quality Checks
```bash
# All quality checks
ruff check --fix . && ruff format . && mypy utils/ && pytest tests/unit/
```

## Integration Testing

### Real API Testing

The project includes comprehensive integration tests that work with actual Customer.IO APIs using **different strategies per API**:

#### Pipelines API Integration Testing

1. **Get API Credentials**: Obtain your Customer.IO API key
2. **Configure Environment**:
   ```bash
   # Create .env file with credentials
   CUSTOMERIO_API_KEY=your_api_key
   CUSTOMERIO_REGION=us  # or "eu"
   
   # Enable eternal data mode (recommended)
   TEST_DATA_MODE=eternal
   ETERNAL_DATA_ENABLED=true
   ```

3. **Setup Eternal Test Data** (recommended):
   ```bash
   # Create permanent test data (one-time setup)
   python setup_eternal_data.py --create
   ```

4. **Run Pipelines API Tests**:
   ```bash
   # Run safe read-only tests
   pytest tests/pipelines_api/integration/ -m "read_only" -v
   
   # Run all Pipelines API tests
   pytest tests/pipelines_api/integration/ -v
   ```

#### App API Integration Testing

1. **Get App API Token**: Obtain your Customer.IO App API Bearer token
2. **Configure Environment**:
   ```bash
   # Add App API credentials to .env file
   CUSTOMERIO_APP_API_TOKEN=your_app_api_token_here
   CUSTOMERIO_REGION=us  # or "eu"
   ```

3. **Run App API Tests** (no setup required):
   ```bash
   # Run App API integration tests (simple email-based approach)
   pytest tests/app_api/integration/ -v
   ```

#### Integration Test Coverage

**Pipelines API Tests:**
- **People Management**: User identification, suppression, deletion
- **Event Tracking**: Custom events, semantic events, video, mobile
- **Device Management**: Device registration, updates, deletion
- **Object Management**: Objects, relationships, complex hierarchies
- **Batch Operations**: Bulk processing, size validation
- **E-commerce Events**: Product interactions, checkout funnel
- **Video Events**: Playback lifecycle, content tracking
- **GDPR Compliance**: User suppression, data deletion

**App API Tests:**
- **Transactional Messaging**: Email sending using identifiers and direct email
- **Broadcast Triggers**: Campaign triggering with configuration
- **Push Notifications**: Mobile push notification delivery
- **Error Handling**: API error response validation
- **Unicode Support**: International content handling

#### Key Integration Test Features

**Pipelines API Features:**
- **Eternal Data System**: Eliminates test data pollution with permanent test data
- **Smart Data Mode**: Automatically uses eternal data when available
- **Test Categorization**: Read-only vs mutation tests for safe execution
- **Complex Resource Tracking**: Manages relationships between users, devices, objects

**App API Features:**
- **Direct Email Testing**: No customer creation needed, uses email addresses directly
- **Automatic Cleanup**: Self-contained tests with no persistent data
- **Simple Configuration**: Just requires API token, no complex setup

**Shared Features:**
- **Rate Limiting**: Respects Customer.IO API limits with built-in throttling
- **Error Handling**: Tests both success and failure scenarios
- **Real API Patterns**: Validates actual API behavior

### Authentication

Customer.IO APIs use **different authentication methods**:

#### Pipelines API - Basic Authentication
```python
# Pipelines API uses Basic Authentication
client = CustomerIOClient(api_key="your_api_key", region="us")
# This creates Basic auth header: Authorization: Basic base64(api_key:)
```

#### App API - Bearer Token Authentication
```python
# App API uses Bearer Token Authentication
from src.app_api.auth import AppAPIAuth
auth = AppAPIAuth(api_token="your_app_api_token", region="us")
# This creates Bearer auth header: Authorization: Bearer your_app_api_token
```

## Jupyter Notebooks

The notebooks serve as a demonstration interface for the utils library:

### Notebook Overview
1. **00_setup_and_configuration.ipynb**: Basic setup and connectivity testing
2. **01_people_management.ipynb**: User management and GDPR operations
3. **02_event_tracking.ipynb**: Event tracking and semantic events
4. **03_objects_and_relationships.ipynb**: Object and relationship management
5. **04_device_management.ipynb**: Device registration and management
6. **05_batch_operations.ipynb**: Bulk operations and batch processing
7. **06_page_screen_tracking.ipynb**: Page and screen tracking
8. **07_profile_aliasing.ipynb**: Profile aliasing and identity management

### Key Notebook Patterns
- **User Creation First**: All operations require users to be identified first
- **Utils Function Usage**: Notebooks demonstrate utils functions, not direct API calls
- **Real Examples**: Working examples with proper error handling
- **Clear Documentation**: Each notebook is self-contained with explanations

## API Patterns Discovered

Through comprehensive integration testing, key API patterns were discovered:

### Authentication
- **Basic Auth Required**: Uses `Authorization: Basic base64(api_key:)` header
- **Not Bearer Auth**: Previous Bearer token approach doesn't work

### Function Signatures
- **Device Functions**: Require `device_token` as separate parameter
- **Video Functions**: Require `video_id` as separate parameter  
- **Object Functions**: Require `user_id`, `object_id`, `traits` as separate parameters

### Operation Dependencies
- **Users First**: Users must be identified before other operations
- **Semantic Events**: Some operations use semantic events (e.g., user deletion)

### Rate Limiting
- **3000 requests per 3 seconds**: Built into client with automatic handling
- **Exponential Backoff**: Automatic retry logic for rate limit errors

## Performance and Best Practices

### Batch Processing
- **Optimal Batch Size**: 100-500 records per batch
- **Size Validation**: Automatic validation against 500KB limit
- **Batch Splitting**: Automatic splitting of oversized batches

### Error Handling
- **Comprehensive Validation**: Input validation before API calls
- **Retry Logic**: Exponential backoff for transient failures
- **Custom Exceptions**: Clear error types for different failure modes

### Resource Management
- **Automatic Cleanup**: Integration tests clean up test data
- **Rate Limit Respect**: Built-in rate limiting prevents API errors
- **Connection Reuse**: Efficient HTTP connection management

## Troubleshooting

### Common Issues

#### Authentication Errors
```
401 Unauthorized
```
**Solution**: Verify API key is correct and ensure you're using Basic auth (handled automatically by client)

#### Function Signature Errors
```
TypeError: missing required positional argument
```
**Solution**: Check function signatures in utils modules. Many functions require specific parameter order.

#### Missing User Errors
```
Customer.IO API Error: User not found
```
**Solution**: Always identify users with `identify_user()` before other operations

#### Rate Limiting
```
429 Too Many Requests
```
**Solution**: Client handles this automatically with exponential backoff

### Integration Test Issues

#### Missing Credentials
```
SKIP tests/integration/ - No API credentials configured
```
**Solution**: Set `CUSTOMERIO_API_KEY` environment variable

#### Test Data Cleanup
If integration tests fail and leave test data:
1. Check test output for created resource IDs
2. Test cleanup runs automatically on successful completion
3. Manual cleanup may be needed for failed tests

## Contributing

### Development Guidelines
1. **Follow TDD**: Write tests before implementation
2. **Type Hints**: All functions must have type annotations
3. **Documentation**: Comprehensive docstrings required
4. **Error Handling**: Explicit error handling for all API calls
5. **No Emojis**: Project standard prohibits emojis anywhere

### Code Standards
- **Formatting**: Use `ruff format` for consistent formatting
- **Linting**: Pass `ruff check` with no errors
- **Type Checking**: Pass `mypy --strict` validation
- **Testing**: Maintain high test coverage

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes following TDD
3. Run full test suite: `pytest tests/unit/`
4. Run quality checks: `ruff check --fix . && mypy utils/`
5. Test integration if API changes: `pytest tests/integration/`
6. Update documentation if needed
7. Submit pull request with clear description

## API Reference

### Complete Function Reference

#### People Management
```python
identify_user(client, user_id, traits)
delete_user(client, user_id)
suppress_user(client, user_id)
unsuppress_user(client, user_id)
```

#### Event Tracking
```python
track_event(client, user_id, event_name, properties, timestamp=None)
track_page_view(client, user_id, page_name, properties, timestamp=None)
track_screen_view(client, user_id, screen_name, properties, timestamp=None)
```

#### Device Management
```python
register_device(client, user_id, device_token, device_type, metadata, timestamp=None)
update_device(client, user_id, device_token, device_type, metadata, timestamp=None)
delete_device(client, user_id, device_token, device_type, timestamp=None)
```

#### Object Management
```python
create_object(client, user_id, object_id, traits, object_type_id="1", timestamp=None)
update_object(client, user_id, object_id, traits, object_type_id="1", timestamp=None)
delete_object(client, object_id, object_type_id="1", timestamp=None)
create_relationship(client, user_id, object_id, object_type_id="1", timestamp=None)
delete_relationship(client, user_id, object_id, object_type_id="1", timestamp=None)
```

#### Video Events
```python
track_video_playback_started(client, user_id, video_id, properties, timestamp=None)
track_video_playback_completed(client, user_id, video_id, properties, timestamp=None)
track_video_playback_paused(client, user_id, video_id, properties, timestamp=None)
```

#### Batch Operations
```python
send_batch(client, operations, context=None, integrations=None)
create_batch_operations(operation_type, data)
validate_batch_size(operations)
split_oversized_batch(operations)
```

## Project Status

### Completed Features
- **297 Unit Tests**: Complete test coverage of all utils modules
- **9 Integration Test Files**: Real API testing for all major functionality  
- **16 Utils Modules**: Complete Customer.IO API coverage
- **8 Jupyter Notebooks**: Production-ready demonstration interface
- **Authentication Fixed**: Basic auth implementation working with real API
- **Function Signatures Validated**: All signatures tested against real API

### Test Results
- **Unit Tests**: 297 tests passing
- **Integration Tests**: All tests passing with real Customer.IO API
- **Code Quality**: Passes mypy strict checking and ruff linting
- **Coverage**: High test coverage across all modules

### Ready for Production
This library is production-ready with:
- Comprehensive error handling
- Rate limiting and retry logic
- Real API validation
- Clean, typed interfaces
- Extensive documentation

## Support

### Documentation
- **Customer.IO API**: [Official API Documentation](https://customer.io/docs/api/)
- **Project Requirements**: See `REQUIREMENTS.md`
- **Development Standards**: See `PYTHON_STANDARDS.md`
- **Integration Testing**: See `tests/integration/README.md`

### Getting Help
1. Check this README and project documentation
2. Review integration test examples
3. Consult Customer.IO API documentation
4. Create issue with reproduction steps

---

**License**: MIT

**Maintainer**: Development Team

**Last Updated**: 2025-01-01