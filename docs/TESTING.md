# Testing Guide for Customer.IO Multi-API Client Library

This document provides comprehensive guidance on testing practices, test data management, and the eternal test data system implemented in this project.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Data Management](#test-data-management)
3. [Test Organization](#test-organization)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [Integration Testing](#integration-testing)
7. [Eternal Data System](#eternal-data-system)
8. [Troubleshooting](#troubleshooting)
9. [CI/CD Integration](#cicd-integration)

## Testing Philosophy

### Test-Driven Development (TDD)

This project follows strict Test-Driven Development methodology. Every feature begins with a failing test that defines the expected behavior.

#### The TDD Cycle

1. **Red**: Write a failing test that describes the desired behavior
2. **Green**: Write the minimum code necessary to make the test pass
3. **Refactor**: Improve the code while keeping tests green

```python
# Example TDD workflow
def test_identify_user_basic():
    """Test basic user identification."""
    # Red: Write test first
    client = CustomerIOClient(api_key="test", region="us")
    user_id = "test_user_123"
    traits = {"email": "test@example.com", "name": "Test User"}
    
    # This will fail initially
    result = identify_user(client, user_id, traits)
    
    assert result["status"] == "success"

# Green: Implement minimal code to pass
def identify_user(client, user_id, traits):
    # Minimal implementation
    return {"status": "success"}

# Refactor: Improve while keeping tests green
```

### Test Quality Standards

- **Comprehensive Coverage**: Test all functions, edge cases, and error conditions
- **Clear Test Names**: Use descriptive names that explain what is being tested
- **Fast Execution**: Unit tests should run quickly (< 1 second each)
- **Isolation**: Tests should not depend on each other
- **Deterministic**: Tests should produce consistent results

## Test Data Management

### Overview

The project implements an advanced test data management system with three distinct modes:

1. **Create Mode** (default): Creates new test data for each run
2. **Existing Mode**: Uses pre-specified existing data IDs
3. **Eternal Mode** (recommended): Uses permanent test data

### The Problem: Test Data Pollution

Traditional integration testing creates significant data pollution:
- Hundreds of test records created on each run
- Manual cleanup required
- Difficult to maintain test environments
- Inconsistent test data across runs

### The Solution: Eternal Test Data

The eternal test data system addresses these issues by:
- Using a fixed set of permanent test data
- Eliminating data creation during normal test runs
- Providing consistent, predictable test scenarios
- Reducing cleanup overhead

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                     # Global test configuration
├── eternal_config.py               # Eternal data configuration
├── eternal_test_data.py            # Test data definitions
├── eternal_utils.py                # Data discovery utilities
├── fixtures/                       # Test data files
├── pipelines_api/                  # Pipelines API tests
│   ├── unit/                       # Fast, isolated unit tests
│   │   ├── test_api_client.py
│   │   ├── test_people_manager.py
│   │   └── test_event_manager.py
│   └── integration/                # Real API integration tests
│       ├── conftest.py             # Integration test configuration
│       ├── base.py                 # Base integration test class
│       ├── test_people_integration.py
│       └── test_event_integration.py
├── app_api/                        # App API tests
│   ├── unit/
│   └── integration/
└── webhooks/                       # Webhook tests
    └── unit/
```

### Test Categories

#### Unit Tests
- **Fast**: Run in milliseconds
- **Isolated**: No external dependencies
- **Mocked**: Use mocks for API calls and external services
- **Comprehensive**: Cover all code paths and edge cases

```python
@pytest.mark.unit
def test_calculate_discount():
    """Test discount calculation logic."""
    user = User(is_premium=True)
    order = Order(total=Decimal("100.00"))
    
    discount = calculate_discount(user, order)
    
    assert discount == Decimal("10.00")
```

#### Integration Tests
- **Real API**: Test against actual Customer.IO API
- **End-to-end**: Test complete workflows
- **Data Management**: Use eternal data system
- **Cleanup**: Automatic resource cleanup

```python
@pytest.mark.integration
@pytest.mark.read_only
def test_identify_user_integration(authenticated_client, eternal_data_check):
    """Test user identification with real API."""
    user_data = get_test_user_data("basic")
    
    result = identify_user(authenticated_client, user_data["id"], user_data["traits"])
    
    assert_successful_response(result)
```

#### End-to-End Tests
- **Complete Workflows**: Test entire business processes
- **Cross-API**: Test interactions between multiple APIs
- **Real Scenarios**: Mimic actual usage patterns

### Test Markers

The project uses pytest markers to categorize tests:

```python
# Test speed
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # API integration tests
@pytest.mark.slow          # Long-running tests

# Data requirements
@pytest.mark.read_only     # Safe for eternal data
@pytest.mark.mutation     # Modifies data (use carefully)

# API requirements
@pytest.mark.eternal_data("user")    # Requires eternal user data
@pytest.mark.eternal_data("device")  # Requires eternal device data
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run unit tests only (fast)
pytest tests/pipelines_api/unit/ -v

# Run integration tests (requires API credentials)
pytest tests/pipelines_api/integration/ -v

# Run with coverage
pytest --cov=src/ --cov-report=term-missing
```

### Test Selection

```bash
# Run tests by marker
pytest -m "unit"                    # Only unit tests
pytest -m "integration"             # Only integration tests
pytest -m "read_only"               # Only read-only tests
pytest -m "not slow"                # Exclude slow tests

# Run specific test files
pytest tests/pipelines_api/unit/test_people_manager.py -v

# Run specific test functions
pytest tests/pipelines_api/unit/test_people_manager.py::test_identify_user_basic -v
```

### Test Data Modes

```bash
# Run with eternal data (recommended)
TEST_DATA_MODE=eternal pytest tests/pipelines_api/integration/ -v

# Run with create mode (default)
TEST_DATA_MODE=create pytest tests/pipelines_api/integration/ -v

# Run read-only tests only (safe for eternal data)
pytest tests/pipelines_api/integration/ -m "read_only" -v
```

### Debug and Verbose Output

```bash
# Enable debug output
DEBUG_INTEGRATION_TESTS=true pytest tests/integration/ -v -s

# Show test output
pytest -v -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

## Writing Tests

### Unit Test Best Practices

#### 1. Test Structure
Use the Arrange-Act-Assert pattern:

```python
def test_calculate_total_with_discount():
    """Test total calculation with discount applied."""
    # Arrange
    order = Order(subtotal=Decimal("100.00"))
    discount = Decimal("10.00")
    
    # Act
    total = calculate_total(order, discount)
    
    # Assert
    assert total == Decimal("90.00")
```

#### 2. Descriptive Test Names
Test names should clearly describe what is being tested:

```python
# Good
def test_identify_user_with_valid_data_returns_success():
def test_identify_user_with_empty_email_raises_validation_error():
def test_identify_user_with_long_traits_truncates_data():

# Bad
def test_identify_user():
def test_user_creation():
def test_api_call():
```

#### 3. Mock External Dependencies

```python
@pytest.fixture
def mock_api_client():
    """Mock API client for unit tests."""
    client = Mock(spec=CustomerIOClient)
    client.make_request.return_value = {"status": "success"}
    return client

def test_identify_user_calls_api_correctly(mock_api_client):
    """Test that identify_user makes correct API call."""
    user_id = "test_123"
    traits = {"email": "test@example.com"}
    
    identify_user(mock_api_client, user_id, traits)
    
    mock_api_client.make_request.assert_called_once_with(
        "PUT",
        f"/customers/{user_id}",
        json=traits
    )
```

#### 4. Test Error Conditions

```python
def test_identify_user_with_invalid_email_raises_validation_error():
    """Test that invalid email raises appropriate error."""
    client = CustomerIOClient(api_key="test", region="us")
    
    with pytest.raises(ValidationError, match="Invalid email format"):
        identify_user(client, "user_123", {"email": "invalid-email"})
```

### Integration Test Best Practices

#### 1. Use Eternal Data System

```python
@pytest.mark.integration
@pytest.mark.read_only
@pytest.mark.eternal_data("user")
def test_user_identification_with_eternal_data(authenticated_client, eternal_data_check):
    """Test user identification using eternal test data."""
    # Get eternal user data
    user_data = get_test_user_data("basic")
    
    if eternal_config.is_eternal_mode and user_data:
        # Use eternal data
        result = identify_user(authenticated_client, user_data["id"], user_data["traits"])
    else:
        # Fallback to create mode
        pytest.skip("Eternal data not available")
    
    assert_successful_response(result)
```

#### 2. Handle Different Test Modes

```python
def test_user_operations(authenticated_client, test_user_id, eternal_data_check):
    """Test user operations in any data mode."""
    user_data = get_test_user_data("basic")
    
    if eternal_config.is_eternal_mode and user_data:
        # Use eternal data - read-only operations
        user_id = user_data["id"]
        traits = user_data["traits"]
    else:
        # Create mode - full CRUD operations
        user_id = test_user_id
        traits = {"email": f"{test_user_id}@test.example.com", "name": "Test User"}
        
        # Track for cleanup
        self.track_user(user_id)
    
    # Test operations
    result = identify_user(authenticated_client, user_id, traits)
    assert_successful_response(result)
    
    # Cleanup only in create mode
    if not eternal_config.is_eternal_mode:
        cleanup_user(authenticated_client, user_id)
```

#### 3. Resource Tracking and Cleanup

```python
class TestPeopleIntegration(BaseIntegrationTest):
    """Integration tests for people management."""
    
    def test_create_and_delete_user(self, authenticated_client, test_user_id):
        """Test user creation and deletion."""
        # Create user
        traits = {"email": f"{test_user_id}@test.example.com"}
        result = identify_user(authenticated_client, test_user_id, traits)
        
        # Track for cleanup
        self.track_user(test_user_id)
        
        # Test operations
        assert_successful_response(result)
        
        # Cleanup happens automatically in teardown
```

## Integration Testing

### Prerequisites

#### 1. API Credentials
Obtain Customer.IO API credentials:
- Data Pipelines API key
- App API bearer token
- Regional configuration (US/EU)

#### 2. Environment Configuration
Create `.env` file with credentials:

```bash
# Customer.IO API Configuration
CUSTOMERIO_API_KEY=your_pipelines_api_key
CUSTOMERIO_REGION=us

# App API Configuration  
CUSTOMERIO_APP_API_TOKEN=your_app_api_bearer_token

# Test Data Configuration
TEST_DATA_MODE=eternal
ETERNAL_DATA_ENABLED=true
SKIP_IF_NO_ETERNAL_DATA=true
```

### Running Integration Tests

#### Setup and Validation
```bash
# Validate credentials
pytest tests/pipelines_api/integration/test_people_integration.py::test_api_credentials -v

# Run read-only tests (safe)
pytest tests/pipelines_api/integration/ -m "read_only" -v

# Run all integration tests
pytest tests/pipelines_api/integration/ -v
```

#### Common Integration Test Patterns

```python
# Base integration test class
class TestAPIIntegration(BaseIntegrationTest):
    """Base class for API integration tests."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.created_resources = []
    
    def teardown_method(self):
        """Cleanup after each test method."""
        for resource in self.created_resources:
            self.cleanup_resource(resource)
    
    def test_api_workflow(self, authenticated_client):
        """Test complete API workflow."""
        # Implementation
        pass
```

### Test Environment Management

#### Development Environment
- Use separate Customer.IO workspace for testing
- Enable debug logging for detailed output
- Use lower rate limits to avoid API throttling

#### CI/CD Environment
- Use dedicated test credentials
- Implement proper secret management
- Configure appropriate timeout values

## Eternal Data System

### Overview

The eternal data system provides a sophisticated approach to integration testing that eliminates data pollution and provides consistent test scenarios.

### Key Concepts

#### Eternal Test Data
Permanent test data that exists in your Customer.IO workspace:
- **Users**: Various user types (basic, premium, inactive, etc.)
- **Devices**: iOS, Android, and web devices
- **Objects**: Companies, products, and other business entities
- **Relationships**: Connections between users and objects

#### Test Scenarios
Predefined scenarios that map to specific data combinations:
- **user_identification**: Basic user management operations
- **event_tracking**: Event tracking with different event types
- **device_management**: Device registration and updates
- **object_relationships**: Object and relationship management

### Setup and Configuration

#### 1. Create Eternal Test Data

```bash
# Preview what will be created
python setup_eternal_data.py --dry-run

# Create the eternal test data
python setup_eternal_data.py --create

# Verify data was created
python setup_eternal_data.py --verify
```

#### 2. Configure Environment

```bash
# Enable eternal data mode
TEST_DATA_MODE=eternal
ETERNAL_DATA_ENABLED=true
ETERNAL_DATA_VERSION=2025_01_02_v1

# Configure behavior
SKIP_IF_NO_ETERNAL_DATA=true
```

#### 3. Update Tests

```python
# Use eternal data utilities
from tests.eternal_utils import get_test_user_data

def test_with_eternal_data():
    """Test using eternal data."""
    user_data = get_test_user_data("basic")
    
    if user_data:
        # Use eternal data
        user_id = user_data["id"]
        traits = user_data["traits"]
    else:
        # Fallback or skip
        pytest.skip("Eternal data not available")
```

### Data Discovery

The system includes utilities to discover and validate eternal data:

```python
from tests.eternal_utils import (
    discover_eternal_user,
    validate_eternal_data_integrity,
    get_eternal_data_summary
)

# Check if eternal user exists
exists, user_data = discover_eternal_user(client, "basic")

# Validate all eternal data
report = validate_eternal_data_integrity(client)

# Get summary of available data
summary = get_eternal_data_summary()
```

### Migration from Create Mode

#### Step 1: Assess Current Tests
Review existing tests to understand data requirements:

```bash
# Find tests that create data
grep -r "identify_user\|create_object\|register_device" tests/integration/
```

#### Step 2: Create Eternal Data
Set up permanent test data that covers your test scenarios:

```bash
python setup_eternal_data.py --create
```

#### Step 3: Update Test Code
Modify tests to use eternal data utilities:

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

#### Step 4: Enable Eternal Mode
Update configuration and run tests:

```bash
TEST_DATA_MODE=eternal pytest tests/integration/ -m "read_only" -v
```

### Maintenance

#### Regular Validation
Periodically validate eternal data integrity:

```bash
python setup_eternal_data.py --verify
```

#### Data Version Management
Update eternal data version when schema changes:

```python
# Update version in eternal_test_data.py
ETERNAL_DATA_VERSION = "2025_02_01_v2"

# Recreate data with new version
python setup_eternal_data.py --create
```

#### Cleanup (Use with Caution)
Remove eternal data if needed:

```bash
# This will require confirmation
python setup_eternal_data.py --cleanup
```

## Troubleshooting

### Common Issues

#### Authentication Errors
```
401 Unauthorized: Authentication failed
```
**Solutions**:
- Verify API key is correct
- Check API key permissions in Customer.IO dashboard
- Ensure using correct region (US/EU)
- For App API, verify bearer token format

#### Rate Limiting
```
429 Too Many Requests: Rate limit exceeded
```
**Solutions**:
- Reduce `TEST_RATE_LIMIT_PER_SECOND` in configuration
- Add delays between test executions
- Use eternal data mode to reduce API calls

#### Eternal Data Not Found
```
Eternal test data not found: user type 'basic' not available
```
**Solutions**:
- Run `python setup_eternal_data.py --create`
- Verify `ETERNAL_DATA_ENABLED=true` in configuration
- Check eternal data version matches

#### Test Data Pollution
```
Error: Too many test records in workspace
```
**Solutions**:
- Switch to eternal data mode: `TEST_DATA_MODE=eternal`
- Implement proper cleanup in existing tests
- Use read-only tests when possible

#### Network Timeouts
```
NetworkError: Request timeout after 30 seconds
```
**Solutions**:
- Check internet connection
- Verify Customer.IO API status
- Increase timeout in client configuration
- Use retry logic for transient failures

### Debug Mode

Enable detailed debugging:

```bash
# Enable debug logging
DEBUG_INTEGRATION_TESTS=true pytest tests/integration/ -v -s

# Show API request/response details
CUSTOMERIO_DEBUG=true pytest tests/integration/ -v -s
```

### Test Health Monitoring

#### Track Test Performance
```bash
# Run tests with timing
pytest --durations=10 tests/integration/

# Generate performance report
pytest --benchmark-only tests/integration/
```

#### Monitor API Usage
- Track API call volume during tests
- Monitor rate limit usage
- Review Customer.IO dashboard for test impact

### Environment Issues

#### Virtual Environment Problems
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Dependency Conflicts
```bash
# Check for conflicts
pip check

# Update dependencies
pip install --upgrade -r requirements.txt
```

## CI/CD Integration

### GitHub Actions

#### Basic Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run unit tests
        run: |
          pytest tests/pipelines_api/unit/ -v --cov=src/

  integration-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run integration tests
        env:
          CUSTOMERIO_API_KEY: ${{ secrets.CUSTOMERIO_API_KEY }}
          CUSTOMERIO_REGION: us
          TEST_DATA_MODE: eternal
          ETERNAL_DATA_ENABLED: true
        run: |
          pytest tests/pipelines_api/integration/ -m "read_only" -v
```

#### Advanced Workflow with Eternal Data
```yaml
      - name: Setup eternal test data
        env:
          CUSTOMERIO_API_KEY: ${{ secrets.CUSTOMERIO_API_KEY }}
        run: |
          python setup_eternal_data.py --verify || python setup_eternal_data.py --create
      
      - name: Run integration tests with eternal data
        env:
          CUSTOMERIO_API_KEY: ${{ secrets.CUSTOMERIO_API_KEY }}
          TEST_DATA_MODE: eternal
        run: |
          pytest tests/pipelines_api/integration/ -v
```

### Jenkins

#### Pipeline Configuration
```groovy
pipeline {
    agent any
    
    environment {
        CUSTOMERIO_API_KEY = credentials('customerio-api-key')
        TEST_DATA_MODE = 'eternal'
    }
    
    stages {
        stage('Unit Tests') {
            steps {
                sh 'pytest tests/pipelines_api/unit/ -v --junit-xml=unit-results.xml'
            }
        }
        
        stage('Integration Tests') {
            when {
                branch 'main'
            }
            steps {
                sh 'pytest tests/pipelines_api/integration/ -m "read_only" -v --junit-xml=integration-results.xml'
            }
        }
    }
    
    post {
        always {
            junit 'unit-results.xml,integration-results.xml'
        }
    }
}
```

### Best Practices for CI/CD

#### Secret Management
- Store API credentials as encrypted secrets
- Use separate test workspace/credentials
- Rotate credentials regularly
- Limit permissions to minimum required

#### Test Strategy
- Run unit tests on every commit
- Run integration tests on main branch only
- Use eternal data mode to minimize API usage
- Implement test result caching

#### Performance Optimization
- Cache dependencies between runs
- Run tests in parallel when possible
- Use read-only tests for faster execution
- Monitor and optimize slow tests

## Summary

This testing guide provides comprehensive coverage of:

- **TDD Methodology**: Test-first development approach
- **Test Organization**: Unit, integration, and e2e test structure
- **Data Management**: Eternal data system for eliminating test pollution
- **Best Practices**: Writing maintainable and reliable tests
- **Integration Testing**: Real API testing patterns and strategies
- **Troubleshooting**: Common issues and solutions
- **CI/CD Integration**: Automated testing in deployment pipelines

The eternal test data system is a key differentiator that allows for:
- **Consistent Test Environment**: Same data across all test runs
- **Reduced API Usage**: Minimal data creation during testing
- **Improved Test Reliability**: Predictable test scenarios
- **Easier Maintenance**: Less cleanup and data management overhead

For additional information, refer to:
- `tests/eternal_test_data.py` - Test data definitions
- `tests/eternal_config.py` - Configuration options
- `tests/eternal_utils.py` - Utility functions
- `setup_eternal_data.py` - Data setup script