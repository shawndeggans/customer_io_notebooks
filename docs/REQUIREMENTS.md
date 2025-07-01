# Customer.IO API Client Library Requirements

## Project Overview

Create a comprehensive Python client library for the Customer.IO Data Pipelines API using Test-Driven Development (TDD), with Jupyter notebooks serving as the interface for data engineers to interact with the API.

## Core Objectives

1. **Complete API Coverage**: Implement all endpoints defined in cio_pipelines_api.json
2. **Test-Driven Development**: Every feature starts with a failing test
3. **Clean Client Library**: Well-structured utils modules following Python best practices
4. **Practical Notebooks**: Clear demonstration notebooks for data engineers
5. **Production Ready**: Robust error handling, proper authentication, rate limiting

## Architecture Requirements

### Utils Module Structure

```
utils/
├── __init__.py                 # Package initialization
├── api_client.py              # Base API client with auth and common functionality
├── people_manager.py          # People identification, deletion, suppression
├── event_manager.py           # Custom and semantic event tracking
├── object_manager.py          # Objects and relationships management
├── device_manager.py          # Device registration and management
├── batch_manager.py           # Batch operations
├── validators.py              # Input validation utilities
└── exceptions.py              # Custom exception classes
```

### Test Structure

```
tests/
├── unit/                      # Fast, isolated tests with mocks
│   ├── test_api_client.py
│   ├── test_people_manager.py
│   ├── test_event_manager.py
│   ├── test_object_manager.py
│   ├── test_device_manager.py
│   ├── test_batch_manager.py
│   └── test_validators.py
└── integration/               # Tests with actual Customer.IO API
    ├── test_people_integration.py
    ├── test_event_integration.py
    └── test_batch_integration.py
```

### Notebook Structure

```
00_setup_and_configuration.ipynb     # Environment setup and authentication
01_people_management.ipynb           # People API demonstrations
02_event_tracking.ipynb             # Event tracking demonstrations
03_objects_and_relationships.ipynb  # Objects/relationships demonstrations
04_device_management.ipynb          # Device management demonstrations
05_batch_operations.ipynb           # Batch processing demonstrations
06_semantic_events.ipynb            # Semantic events (ecommerce, email, etc.)
07_complete_workflows.ipynb         # End-to-end use case examples
```

## API Client Requirements

### Base Client (api_client.py)

**Core Features:**
- Authentication with API key
- Region support (US: cdp.customer.io, EU: cdp-eu.customer.io)
- Rate limiting (3000 requests per 3 seconds)
- Automatic retry with exponential backoff
- Request/response logging
- Error handling and custom exceptions

**Implementation Requirements:**
```python
class CustomerIOClient:
    """Customer.IO Data Pipelines API client."""
    
    def __init__(self, api_key: str, region: str = "us"):
        """Initialize client with authentication and region."""
        
    def make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make authenticated API request with error handling."""
        
    def identify(self, user_id: str, traits: dict) -> dict:
        """Identify a user with traits."""
        
    def track(self, user_id: str, event: str, properties: dict = None) -> dict:
        """Track an event for a user."""
        
    def delete(self, user_id: str) -> dict:
        """Delete a user."""
```

## API Coverage Requirements

### People Management (people_manager.py)

**Required Functions:**
- `identify_user(client, user_id, traits)` - Identify users with traits
- `delete_user(client, user_id)` - Delete users
- `suppress_user(client, user_id)` - Suppress users from messaging
- `unsuppress_user(client, user_id)` - Remove suppression
- `add_device(client, user_id, device_data)` - Add device to user
- `delete_device(client, user_id, device_token)` - Remove device from user

### Event Tracking (event_manager.py)

**Required Functions:**
- `track_event(client, user_id, event_name, properties)` - Track custom events
- `track_page_view(client, user_id, page_data)` - Track page views
- `track_screen_view(client, user_id, screen_data)` - Track mobile screen views

**Semantic Events:**
- `track_ecommerce_event(client, user_id, event_type, data)` - E-commerce events
- `track_email_event(client, user_id, event_type, data)` - Email events
- `track_mobile_event(client, user_id, event_type, data)` - Mobile events
- `track_video_event(client, user_id, event_type, data)` - Video events

### Objects & Relationships (object_manager.py)

**Required Functions:**
- `create_object(client, object_type, object_id, attributes)` - Create objects
- `update_object(client, object_type, object_id, attributes)` - Update objects
- `delete_object(client, object_type, object_id)` - Delete objects
- `create_relationship(client, relationship_data)` - Create relationships
- `delete_relationship(client, relationship_data)` - Delete relationships

### Device Management (device_manager.py)

**Required Functions:**
- `add_device(client, user_id, device_data)` - Add device to user
- `update_device(client, user_id, device_token, attributes)` - Update device
- `delete_device(client, user_id, device_token)` - Remove device

### Batch Operations (batch_manager.py)

**Required Functions:**
- `batch_identify(client, users_data)` - Batch user identification
- `batch_track(client, events_data)` - Batch event tracking
- `batch_delete(client, user_ids)` - Batch user deletion

## Test-Driven Development Requirements

### Unit Test Standards

**Test Structure:**
```python
class TestPeopleManager:
    """Test people management functionality."""
    
    def test_identify_user_success(self, mock_client):
        """Test successful user identification."""
        
    def test_identify_user_invalid_data(self, mock_client):
        """Test user identification with invalid data."""
        
    def test_identify_user_api_error(self, mock_client):
        """Test user identification with API error."""
```

**Test Requirements:**
- Test all happy path scenarios
- Test all error conditions
- Test input validation
- Test rate limiting behavior
- Mock all external dependencies
- Fast execution (< 1 second per test file)

### Integration Test Standards

**Requirements:**
- Use actual Customer.IO API endpoints
- Test with valid test data only
- Clean up test data after tests
- Handle API rate limits appropriately
- Document test environment setup

## Notebook Requirements

### Notebook Standards

**Follow ZEN_NOTEBOOKS.md exactly:**
- Clear title and purpose statement
- Sequential execution from top to bottom
- Code cells ≤ 15 lines when possible
- Comprehensive markdown documentation
- Practical, working examples
- Error handling demonstrations

**Content Requirements:**
- Import utils functions at the beginning
- Show basic and advanced usage patterns
- Include error handling examples
- Demonstrate batch operations
- Provide real-world use case scenarios

### Example Notebook Structure

```markdown
# Customer.IO People Management

## Purpose
This notebook demonstrates how to manage people in Customer.IO using the utils library.

## Setup
[Import statements and client initialization]

## Basic Operations
[Simple examples of identify, delete, etc.]

## Advanced Usage
[Batch operations, error handling, etc.]

## Real-World Examples
[Complete workflows]
```

## Data Validation Requirements

### Input Validation (validators.py)

**Required Validators:**
- Email format validation
- User ID format validation
- Event name validation
- Properties schema validation
- Rate limit validation
- Batch size validation

### Error Handling (exceptions.py)

**Custom Exceptions:**
```python
class CustomerIOError(Exception):
    """Base exception for Customer.IO API errors."""

class AuthenticationError(CustomerIOError):
    """Authentication failed."""

class RateLimitError(CustomerIOError):
    """Rate limit exceeded."""

class ValidationError(CustomerIOError):
    """Input validation failed."""
```

## Documentation Requirements

### Code Documentation

**Docstring Standards:**
- Every function must have comprehensive docstrings
- Include parameter types and descriptions
- Include return type and description
- Include example usage
- Document raised exceptions

**Example:**
```python
def identify_user(client: CustomerIOClient, user_id: str, traits: dict) -> dict:
    """
    Identify a user in Customer.IO with the provided traits.
    
    Parameters
    ----------
    client : CustomerIOClient
        Initialized Customer.IO API client
    user_id : str
        Unique identifier for the user
    traits : dict
        User attributes to store
        
    Returns
    -------
    dict
        API response containing operation status
        
    Raises
    ------
    ValidationError
        If user_id or traits are invalid
    CustomerIOError
        If API request fails
        
    Example
    -------
    >>> client = CustomerIOClient(api_key="your_key")
    >>> result = identify_user(client, "user123", {"email": "user@example.com"})
    >>> print(result["status"])
    success
    """
```

### Notebook Documentation

**Markdown Standards:**
- Clear section headings
- Explain the "why" before code sections
- Include context and background
- Document prerequisites and setup
- Provide troubleshooting guidance

## Quality Standards

### Code Quality

**Follow PYTHON_STANDARDS.md exactly:**
- Type hints on all functions
- Clean, descriptive variable names
- Single-responsibility functions
- Proper error handling
- No magic numbers or strings

### Performance Standards

**Requirements:**
- Efficient batch processing
- Proper rate limit handling
- Minimal memory usage
- Fast test execution
- Optimal API usage patterns

## Security Requirements

### API Key Management

**Requirements:**
- Never hardcode API keys
- Support environment variables
- Clear documentation for credential setup
- Support both test and production environments

### Data Privacy

**Requirements:**
- Proper handling of PII
- Secure logging practices
- No sensitive data in test fixtures
- GDPR compliance considerations

## Deliverables

### Phase 1: Foundation
- [ ] Updated CLAUDE.md and REQUIREMENTS.md
- [ ] Base API client with authentication
- [ ] Test infrastructure setup
- [ ] Basic validation utilities

### Phase 2: Core API Functions
- [ ] People management module with tests
- [ ] Event tracking module with tests
- [ ] Object management module with tests
- [ ] Device management module with tests
- [ ] Batch operations module with tests

### Phase 3: Notebooks
- [ ] Setup and configuration notebook
- [ ] People management demonstration notebook
- [ ] Event tracking demonstration notebook
- [ ] Objects and relationships demonstration notebook
- [ ] Batch operations demonstration notebook
- [ ] Complete workflows notebook

### Phase 4: Integration
- [ ] Integration tests with actual API
- [ ] Performance testing
- [ ] Documentation review
- [ ] Final validation

## Success Criteria

The project will be considered complete when:

1. **100% API Coverage**: All endpoints from cio_pipelines_api.json are implemented
2. **Comprehensive Tests**: Full unit and integration test coverage
3. **Working Notebooks**: All notebooks run cleanly and demonstrate functionality
4. **TDD Compliance**: All code developed using test-first methodology
5. **Documentation**: Clear, comprehensive documentation throughout
6. **Production Ready**: Proper error handling, authentication, and rate limiting
7. **Standards Compliance**: Follows PYTHON_STANDARDS.md and ZEN_NOTEBOOKS.md exactly

Remember: The goal is to create a practical, production-ready Customer.IO API client library that data engineers can immediately use, with clear examples and comprehensive documentation.