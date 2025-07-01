# Customer.IO Data Pipelines API Client Library

A comprehensive Python client library and Jupyter notebook suite for the Customer.IO Data Pipelines API, built using Test-Driven Development (TDD) methodology. This project provides production-ready patterns for user management, event tracking, device management, and complete API integration.

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
from utils.api_client import CustomerIOClient
from utils.people_manager import identify_user
from utils.event_manager import track_event

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

## Project Structure

```
customer_io_notebooks/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── devbox.json                         # Development environment
├── pytest.ini                         # Test configuration
├── CLAUDE.md                           # AI assistant guidelines
├── PYTHON_STANDARDS.md                 # Development standards
├── REQUIREMENTS.md                     # Detailed project requirements
├── TODO.md                             # Development progress tracking
├── cio_pipelines_api.json             # Customer.IO API specification
│
├── 00_setup_and_configuration.ipynb   # Basic setup and authentication
├── 01_people_management.ipynb          # User identification and management
├── 02_event_tracking.ipynb             # Event tracking and semantic events
├── 03_objects_and_relationships.ipynb # Objects and relationships management
├── 04_device_management.ipynb          # Device registration and management
├── 05_batch_operations.ipynb           # Bulk operations and batch processing
├── 06_page_screen_tracking.ipynb      # Page and screen tracking
├── 07_profile_aliasing.ipynb           # Profile aliasing and identity management
│
├── utils/                              # Python client library modules
│   ├── __init__.py
│   ├── api_client.py                   # Core API client with Basic auth
│   ├── alias_manager.py                # Profile aliasing operations
│   ├── batch_manager.py                # Batch operations
│   ├── device_manager.py               # Device management
│   ├── ecommerce_manager.py            # E-commerce semantic events
│   ├── event_manager.py                # Core event tracking
│   ├── exceptions.py                   # Custom exception classes
│   ├── gdpr_manager.py                 # GDPR compliance operations
│   ├── mobile_manager.py               # Mobile app semantic events
│   ├── object_manager.py               # Objects and relationships
│   ├── page_manager.py                 # Page tracking
│   ├── people_manager.py               # User identification and management
│   ├── screen_manager.py               # Screen tracking
│   ├── validators.py                   # Input validation utilities
│   └── video_manager.py                # Video semantic events
│
└── tests/                              # Comprehensive test suite
    ├── conftest.py                     # Test configuration
    ├── pytest.ini                     # Test settings
    ├── unit/                           # Unit tests (297 tests)
    │   ├── test_api_client.py
    │   ├── test_alias_manager.py
    │   ├── test_batch_manager.py
    │   ├── test_device_manager.py
    │   ├── test_ecommerce_manager.py
    │   ├── test_event_manager.py
    │   ├── test_exceptions.py
    │   ├── test_gdpr_manager.py
    │   ├── test_mobile_manager.py
    │   ├── test_object_manager.py
    │   ├── test_page_manager.py
    │   ├── test_people_manager.py
    │   ├── test_screen_manager.py
    │   └── test_video_manager.py
    └── integration/                    # Integration tests with real API
        ├── README.md                   # Integration testing guide
        ├── base.py                     # Base test class
        ├── conftest.py                 # Integration test fixtures
        ├── utils.py                    # Test utilities
        ├── test_alias_integration.py
        ├── test_batch_integration.py
        ├── test_device_integration.py
        ├── test_ecommerce_integration.py
        ├── test_event_integration.py
        ├── test_gdpr_integration.py
        ├── test_object_integration.py
        ├── test_people_integration.py
        └── test_video_integration.py
```

## Core Components

### API Client (`utils/api_client.py`)

The `CustomerIOClient` provides a robust interface to the Customer.IO Data Pipelines API with:

- **Basic Authentication**: Uses API key with Basic auth (not Bearer)
- **Rate Limiting**: Respects 3000 requests per 3 seconds limit
- **Regional Support**: Both US and EU regions
- **Error Handling**: Comprehensive error handling with retries
- **Request/Response Logging**: Built-in logging capabilities

```python
from utils.api_client import CustomerIOClient

# Initialize with Basic authentication
client = CustomerIOClient(
    api_key="your_api_key",
    region="us",  # or "eu"
    timeout=30,
    max_retries=3
)
```

### Utils Modules

Each utils module provides specific Customer.IO functionality:

#### People Management (`utils/people_manager.py`)
```python
from utils.people_manager import identify_user, delete_user, suppress_user, unsuppress_user

# User identification
identify_user(client, user_id, traits)

# User suppression
suppress_user(client, user_id)
unsuppress_user(client, user_id)

# User deletion (uses semantic event)
delete_user(client, user_id)
```

#### Event Tracking (`utils/event_manager.py`)
```python
from utils.event_manager import track_event, track_page_view, track_screen_view

# Custom events
track_event(client, user_id, event_name, properties)

# Page/screen events
track_page_view(client, user_id, page_name, properties)
track_screen_view(client, user_id, screen_name, properties)
```

#### Device Management (`utils/device_manager.py`)
```python
from utils.device_manager import register_device, update_device, delete_device

# Device registration (requires user_id, device_token, device_type)
register_device(client, user_id, device_token, device_type="ios", metadata={})
```

#### Objects and Relationships (`utils/object_manager.py`)
```python
from utils.object_manager import create_object, update_object, delete_object

# Object management (requires user_id, object_id, traits)
create_object(client, user_id, object_id, traits, object_type_id="1")
```

#### Video Events (`utils/video_manager.py`)
```python
from utils.video_manager import track_video_playback_started, track_video_playback_completed

# Video tracking (requires video_id as separate parameter)
track_video_playback_started(client, user_id, video_id, properties)
```

#### E-commerce Events (`utils/ecommerce_manager.py`)
```python
from utils.ecommerce_manager import track_product_clicked, track_checkout_step_completed

# E-commerce semantic events
track_product_clicked(client, user_id, properties)
track_checkout_step_completed(client, user_id, properties)
```

#### Batch Operations (`utils/batch_manager.py`)
```python
from utils.batch_manager import send_batch, create_batch_operations

# Batch processing
operations = create_batch_operations("identify", user_data_list)
send_batch(client, operations)
```

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
pytest --cov=utils --cov-report=term-missing --cov-report=html
```

#### Test Categories
- `unit`: Fast unit tests with mocks (297 tests)
- `integration`: Tests with real Customer.IO API (9 test files)
- `slow`: Longer-running tests
- `api`: Tests requiring API credentials

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

The project includes comprehensive integration tests that work with the actual Customer.IO API:

#### Setup Integration Testing
1. **Get API Credentials**: Obtain your Customer.IO API key
2. **Configure Environment**:
   ```bash
   export CUSTOMERIO_API_KEY="your_api_key"
   export CUSTOMERIO_REGION="us"  # or "eu"
   ```
3. **Run Integration Tests**:
   ```bash
   pytest tests/integration/ -v
   ```

#### Integration Test Coverage
- **People Management**: User identification, suppression, deletion
- **Event Tracking**: Custom events, semantic events, video, mobile
- **Device Management**: Device registration, updates, deletion
- **Object Management**: Objects, relationships, complex hierarchies
- **Batch Operations**: Bulk processing, size validation
- **E-commerce Events**: Product interactions, checkout funnel
- **Video Events**: Playback lifecycle, content tracking
- **GDPR Compliance**: User suppression, data deletion

#### Key Integration Test Features
- **Automatic Cleanup**: Tests clean up created resources
- **Rate Limiting**: Respects Customer.IO API limits
- **Error Handling**: Tests both success and failure scenarios
- **Real API Patterns**: Validates actual API behavior

### Authentication

**Important**: Customer.IO Data Pipelines API uses **Basic Authentication**, not Bearer tokens:

```python
# Correct authentication pattern discovered through integration testing
client = CustomerIOClient(api_key="your_api_key", region="us")
# This creates Basic auth header: Authorization: Basic base64(api_key:)
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