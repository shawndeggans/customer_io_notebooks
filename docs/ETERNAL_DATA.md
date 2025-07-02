# Eternal Test Data System

The eternal test data system is an advanced approach to integration testing that eliminates test data pollution by using a fixed set of permanent test data in your Customer.IO workspace.

## Table of Contents

1. [Overview](#overview)
2. [Key Benefits](#key-benefits)
3. [System Architecture](#system-architecture)
4. [Setup and Configuration](#setup-and-configuration)
5. [Test Data Structure](#test-data-structure)
6. [Usage Patterns](#usage-patterns)
7. [Migration Guide](#migration-guide)
8. [Maintenance](#maintenance)
9. [Troubleshooting](#troubleshooting)

## Overview

### The Problem

Traditional integration testing creates significant data pollution:
- Hundreds of test records created on each test run
- Manual cleanup required after test failures
- Inconsistent test data across different runs
- Difficulty maintaining clean test environments
- API rate limit consumption for data creation

### The Solution

Eternal test data provides a permanent, consistent set of test data:
- **Fixed Data Set**: Predefined users, devices, objects, and relationships
- **No Creation**: Tests use existing data instead of creating new records
- **Consistent Results**: Same data available across all test runs
- **Reduced API Usage**: Minimal API calls during testing
- **Easy Maintenance**: No cleanup required for read-only operations

## Key Benefits

### 1. Eliminates Test Data Pollution
- No more hundreds of temporary test records
- Clean workspace maintained automatically
- Reduced manual cleanup overhead

### 2. Provides Consistent Test Environment
- Same test data across all runs
- Predictable test scenarios
- Deterministic test results

### 3. Improves Test Performance
- Faster test execution (no data creation overhead)
- Reduced API calls during testing
- Better resource utilization

### 4. Simplifies Test Maintenance
- No cleanup logic required for read-only tests
- Clear separation between read-only and mutation tests
- Simplified test data management

## System Architecture

### Core Components

#### 1. Test Data Definitions (`tests/eternal_test_data.py`)
```python
ETERNAL_TEST_DATA = {
    "users": {
        "basic": {"id": "eternal_test_user_basic", ...},
        "premium": {"id": "eternal_test_user_premium", ...},
        # ... more user types
    },
    "devices": {
        "ios_basic": {"id": "eternal_test_device_ios_basic", ...},
        # ... more devices
    },
    "objects": {
        "company_a": {"type": "company", "id": "eternal_test_company_a", ...},
        # ... more objects
    }
}
```

#### 2. Configuration Management (`tests/eternal_config.py`)
```python
class EternalDataConfig:
    def is_eternal_mode(self) -> bool:
        return self.test_data_mode == "eternal"
    
    def get_user_for_test(self, scenario: str) -> Dict[str, Any]:
        # Returns appropriate user data based on mode
```

#### 3. Discovery Utilities (`tests/eternal_utils.py`)
```python
def get_test_user_data(user_type: str) -> Optional[Dict[str, Any]]:
    """Get user data appropriate for current test mode."""

def discover_eternal_user(client: CustomerIOClient, user_type: str):
    """Check if eternal user exists in workspace."""
```

#### 4. Setup Script (`setup_eternal_data.py`)
```python
class EternalDataSetup:
    def run_setup(self) -> None:
        """Create all eternal test data in workspace."""
```

### Test Data Flow

1. **Setup Phase**: Run `setup_eternal_data.py` to create permanent test data
2. **Test Execution**: Tests use utilities to access eternal data
3. **Data Discovery**: System validates data existence before tests
4. **Test Categories**: Read-only vs mutation tests handle data differently

## Setup and Configuration

### Prerequisites

1. **Customer.IO Workspace**: Dedicated test workspace recommended
2. **API Credentials**: Valid Data Pipelines API key
3. **Permissions**: Ability to create users, objects, devices, and relationships

### Step 1: Environment Configuration

Create or update `.env` file:
```bash
# Customer.IO API Configuration
CUSTOMERIO_API_KEY=your_api_key_here
CUSTOMERIO_REGION=us

# Eternal Data Configuration
TEST_DATA_MODE=eternal
ETERNAL_DATA_ENABLED=true
ETERNAL_DATA_VERSION=2025_01_02_v1
SKIP_IF_NO_ETERNAL_DATA=true
```

### Step 2: Create Eternal Test Data

#### Preview Data (Recommended First Step)
```bash
# See what data will be created
python setup_eternal_data.py --dry-run
```

#### Create the Data
```bash
# Create permanent test data (one-time setup)
python setup_eternal_data.py --create
```

#### Verify Data Creation
```bash
# Verify data exists in workspace
python setup_eternal_data.py --verify
```

### Step 3: Validate Setup

Run a simple test to verify the system works:
```bash
# Run read-only tests to verify eternal data
pytest tests/pipelines_api/integration/ -m "read_only" -v
```

## Test Data Structure

### Users

#### Basic User
```python
{
    "id": "eternal_test_user_basic",
    "email": "eternal_test_user_basic@eternal.test",
    "traits": {
        "first_name": "Basic",
        "last_name": "User",
        "plan": "free",
        "status": "active",
        "eternal_data": True
    }
}
```

#### Premium User
```python
{
    "id": "eternal_test_user_premium",
    "email": "eternal_test_user_premium@eternal.test", 
    "traits": {
        "first_name": "Premium",
        "last_name": "User",
        "plan": "premium",
        "status": "active",
        "company": "Eternal Test Corp",
        "lifetime_value": 1000,
        "eternal_data": True
    }
}
```

#### Specialized Users
- **Inactive User**: For testing edge cases with inactive accounts
- **Suppression User**: Dedicated user for GDPR suppression testing
- **Alias User**: For testing user aliasing functionality
- **GDPR User**: For GDPR compliance testing

### Devices

#### iOS Device
```python
{
    "id": "eternal_test_device_ios_basic",
    "platform": "ios",
    "last_used": "2025-01-01T00:00:00Z",
    "eternal_data": True
}
```

#### Android and Web Devices
Similar structure with appropriate platform identifiers.

### Objects

#### Company Objects
```python
{
    "type": "company",
    "id": "eternal_test_company_a",
    "attributes": {
        "name": "Eternal Test Company A",
        "industry": "Technology",
        "size": "medium",
        "eternal_data": True
    }
}
```

#### Product Objects
```python
{
    "type": "product", 
    "id": "eternal_test_product_x",
    "attributes": {
        "name": "Eternal Test Product X",
        "category": "Software",
        "price": 99.99,
        "eternal_data": True
    }
}
```

### Relationships

Predefined relationships between users and objects:
```python
{
    "user_id": "eternal_test_user_basic",
    "object_type": "company",
    "object_id": "eternal_test_company_a", 
    "relationship": "employee"
}
```

### Test Scenarios

Predefined scenarios map to specific data combinations:

#### User Identification Scenario
```python
{
    "description": "Test user identification with various user types",
    "users": ["basic", "premium", "inactive"],
    "read_only": True
}
```

#### Device Management Scenario
```python
{
    "description": "Test device registration and management",
    "users": ["basic"],
    "devices": ["ios_basic", "android_basic", "web_basic"],
    "read_only": True
}
```

## Usage Patterns

### Read-Only Tests (Recommended)

Most tests should be read-only and use eternal data without modification:

```python
@pytest.mark.read_only
@pytest.mark.eternal_data("user")
def test_user_identification(authenticated_client, eternal_data_check):
    """Test user identification using eternal data."""
    # Get eternal user data
    user_data = get_test_user_data("basic")
    
    if eternal_config.is_eternal_mode and user_data:
        # Use eternal data
        user_id = user_data["id"]
        traits = user_data["traits"]
        
        # Re-identify user (safe operation)
        result = identify_user(authenticated_client, user_id, traits)
        assert_successful_response(result)
    else:
        # Fallback for non-eternal modes
        pytest.skip("Eternal data not available")
```

### Mutation Tests (Use Carefully)

Some tests need to modify data. Use dedicated test users and restore state:

```python
@pytest.mark.mutation
@pytest.mark.eternal_data("user")
def test_user_suppression(authenticated_client, eternal_data_check):
    """Test user suppression with eternal data."""
    user_data = get_test_user_data("suppression")
    
    if eternal_config.is_eternal_mode and user_data:
        user_id = user_data["id"]
        
        # Suppress user
        suppress_result = suppress_user(authenticated_client, user_id)
        assert_successful_response(suppress_result)
        
        # IMPORTANT: Restore original state
        unsuppress_result = unsuppress_user(authenticated_client, user_id)
        assert_successful_response(unsuppress_result)
    else:
        pytest.skip("Eternal suppression data not available")
```

### Conditional Logic for Multiple Modes

Write tests that work in both eternal and create modes:

```python
def test_user_operations(authenticated_client, test_user_id, eternal_data_check):
    """Test that works in any data mode."""
    user_data = get_test_user_data("basic")
    
    if eternal_config.is_eternal_mode and user_data:
        # Use eternal data
        user_id = user_data["id"]
        traits = user_data["traits"]
        cleanup_needed = False
    else:
        # Create mode
        user_id = test_user_id
        traits = {"email": f"{test_user_id}@test.example.com"}
        cleanup_needed = True
    
    # Test operations
    result = identify_user(authenticated_client, user_id, traits)
    assert_successful_response(result)
    
    # Conditional cleanup
    if cleanup_needed:
        cleanup_user(authenticated_client, user_id)
```

### Using Test Fixtures

The system provides fixtures that automatically handle mode detection:

```python
def test_with_fixtures(authenticated_client, test_user_data, eternal_data_check):
    """Test using automatic fixtures."""
    # test_user_data automatically provides eternal or created data
    user_id = test_user_data["userId"]
    traits = test_user_data["traits"]
    
    result = identify_user(authenticated_client, user_id, traits)
    assert_successful_response(result)
    # Cleanup handled automatically based on mode
```

## Migration Guide

### Migrating from Create Mode to Eternal Mode

#### Step 1: Assess Current Tests

Review existing tests to understand data requirements:
```bash
# Find tests that create data
grep -r "identify_user\|create_object\|register_device" tests/integration/

# Find cleanup patterns
grep -r "cleanup\|delete_user\|track_user" tests/integration/
```

#### Step 2: Create Eternal Data

Set up the permanent test data:
```bash
# Create eternal data
python setup_eternal_data.py --create

# Verify creation
python setup_eternal_data.py --verify
```

#### Step 3: Update Test Code

Transform tests to use eternal data patterns:

##### Before (Create Mode)
```python
def test_user_identification(authenticated_client, test_user_id):
    """Test user identification."""
    # Create test data
    traits = {
        "email": f"{test_user_id}@test.example.com",
        "name": "Test User"
    }
    
    # Test operations
    result = identify_user(authenticated_client, test_user_id, traits)
    self.track_user(test_user_id)
    
    # Assert results
    assert_successful_response(result)
    
    # Cleanup
    self.cleanup_user(authenticated_client, test_user_id)
```

##### After (Eternal Mode)
```python
@pytest.mark.read_only
@pytest.mark.eternal_data("user")
def test_user_identification(authenticated_client, eternal_data_check):
    """Test user identification using eternal data."""
    # Get eternal data
    user_data = get_test_user_data("basic")
    
    if user_data:
        # Use eternal data
        result = identify_user(authenticated_client, user_data["id"], user_data["traits"])
        assert_successful_response(result)
    else:
        pytest.skip("Eternal data not available")
    # No cleanup needed
```

#### Step 4: Enable Eternal Mode

Update configuration and test:
```bash
# Enable eternal mode in .env
TEST_DATA_MODE=eternal

# Test with eternal data
pytest tests/pipelines_api/integration/ -m "read_only" -v
```

#### Step 5: Gradual Migration Strategy

Migrate tests incrementally:

1. **Start with Read-Only Tests**: Migrate tests that only read/query data
2. **Update Fixtures**: Modify test fixtures to support eternal mode
3. **Handle Mutations**: Update tests that modify data to use restoration patterns
4. **Test Both Modes**: Ensure tests work in both eternal and create modes
5. **Remove Create-Mode Dependencies**: Gradually eliminate create-only patterns

### Handling Special Cases

#### Tests Requiring Unique Data
```python
def test_user_uniqueness(authenticated_client):
    """Test requiring truly unique data."""
    if eternal_config.is_eternal_mode:
        pytest.skip("Test requires unique data, not compatible with eternal mode")
    
    # Create unique test data
    unique_id = f"unique_{uuid.uuid4().hex}"
    # ... test implementation
```

#### Tests Requiring Data Deletion
```python
@pytest.mark.mutation
def test_user_deletion(authenticated_client):
    """Test user deletion."""
    if eternal_config.is_eternal_mode:
        # Use create mode for this specific test
        with temporary_create_mode():
            user_id = create_temporary_user()
            delete_user(authenticated_client, user_id)
    else:
        # Normal create mode logic
        pass
```

## Maintenance

### Regular Validation

Periodically validate eternal data integrity:

```bash
# Check data integrity
python setup_eternal_data.py --verify

# Run validation tests
pytest tests/pipelines_api/integration/ -m "eternal_data" -v
```

### Data Version Management

When test data schema changes:

#### Update Version
```python
# In eternal_test_data.py
ETERNAL_DATA_VERSION = "2025_02_01_v2"
```

#### Migrate Data
```bash
# Remove old data (if needed)
python setup_eternal_data.py --cleanup

# Create new version
python setup_eternal_data.py --create
```

#### Update Configuration
```bash
# In .env
ETERNAL_DATA_VERSION=2025_02_01_v2
```

### Monitoring and Health Checks

#### Automated Validation
```python
# Add to CI pipeline
def test_eternal_data_health():
    """Validate eternal data system health."""
    config = EternalDataConfig()
    assert config.is_eternal_mode
    
    # Validate data exists
    validation_results = validate_eternal_data_integrity(client)
    assert validation_results["valid"]
```

#### Data Integrity Checks
```python
def validate_eternal_data():
    """Comprehensive data validation."""
    report = validate_eternal_data_integrity(client)
    
    if not report["valid"]:
        print("Validation errors:")
        for error in report["errors"]:
            print(f"- {error}")
        
        return False
    
    return True
```

### Backup and Restore

#### Export Current State
```bash
# Export eternal data configuration
python -c "from tests.eternal_test_data import ETERNAL_TEST_DATA; import json; print(json.dumps(ETERNAL_TEST_DATA, indent=2))" > eternal_data_backup.json
```

#### Restore from Backup
```bash
# Restore eternal data
python setup_eternal_data.py --create --from-backup eternal_data_backup.json
```

## Troubleshooting

### Common Issues

#### 1. Eternal Data Not Found
```
Error: Eternal test data not found: user type 'basic' not available
```

**Causes:**
- Eternal data not created yet
- Wrong workspace or credentials
- Data version mismatch

**Solutions:**
```bash
# Create eternal data
python setup_eternal_data.py --create

# Verify configuration
python -c "from tests.eternal_config import eternal_config; print(eternal_config.is_eternal_mode)"

# Check data version
grep ETERNAL_DATA_VERSION .env
```

#### 2. Test Skipped Due to Missing Data
```
SKIPPED [1] eternal_data_check: Eternal test user data not found
```

**Causes:**
- `SKIP_IF_NO_ETERNAL_DATA=true` and data missing
- Network issues preventing data validation

**Solutions:**
```bash
# Check if data exists
python setup_eternal_data.py --verify

# Disable skipping temporarily
SKIP_IF_NO_ETERNAL_DATA=false pytest tests/integration/ -v

# Create missing data
python setup_eternal_data.py --create
```

#### 3. Version Mismatch
```
Warning: Eternal data version mismatch: expected 2025_01_02_v1, got 2024_12_01_v1
```

**Causes:**
- Configuration version doesn't match data version
- Old data still present after version update

**Solutions:**
```bash
# Update configuration
ETERNAL_DATA_VERSION=2025_01_02_v1

# Recreate data with new version
python setup_eternal_data.py --create
```

#### 4. Authentication Errors
```
401 Unauthorized: Authentication failed during eternal data setup
```

**Causes:**
- Invalid API key
- Wrong region configuration
- Insufficient permissions

**Solutions:**
```bash
# Verify credentials
python -c "import os; print(f'API Key: {os.getenv(\"CUSTOMERIO_API_KEY\")[:10]}...')"

# Test authentication
python -c "from src.pipelines_api.api_client import CustomerIOClient; client = CustomerIOClient(api_key=os.getenv('CUSTOMERIO_API_KEY')); print('Auth OK')"

# Check permissions in Customer.IO dashboard
```

### Debug Mode

Enable detailed debugging:

```bash
# Enable debug output
DEBUG_INTEGRATION_TESTS=true python setup_eternal_data.py --create

# Verbose test execution
pytest tests/pipelines_api/integration/ -v -s --tb=long

# Check configuration
python -c "from tests.eternal_config import get_test_data_summary; import json; print(json.dumps(get_test_data_summary(), indent=2))"
```

### Data Validation

Comprehensive data validation:

```python
from tests.eternal_utils import validate_eternal_data_integrity
from src.pipelines_api.api_client import CustomerIOClient

client = CustomerIOClient(api_key="your_key", region="us")
report = validate_eternal_data_integrity(client)

print("Validation Report:")
print(f"Valid: {report['valid']}")
print(f"Errors: {len(report['errors'])}")
print(f"Warnings: {len(report['warnings'])}")

for error in report['errors']:
    print(f"Error: {error}")
```

### Performance Issues

If eternal data operations are slow:

```bash
# Check network connectivity
ping cdp.customer.io

# Reduce rate limiting
TEST_RATE_LIMIT_PER_SECOND=5 python setup_eternal_data.py --create

# Use smaller data set
python setup_eternal_data.py --create --minimal
```

## Best Practices

### 1. Design Principles

- **Read-Only by Default**: Most tests should be read-only
- **Restore State**: Mutation tests must restore original state
- **Clear Naming**: Use descriptive names for test data
- **Version Control**: Version eternal data schema changes
- **Documentation**: Document test scenarios and data usage

### 2. Test Organization

- **Separate Read-Only and Mutation Tests**: Use pytest markers
- **Group Related Tests**: Organize by functionality
- **Use Descriptive Names**: Test names should indicate data requirements
- **Handle Multiple Modes**: Tests should work in different data modes

### 3. Data Management

- **Minimal Data Set**: Only create necessary test data
- **Logical Grouping**: Group related data together
- **Clear Metadata**: Mark all eternal data clearly
- **Regular Validation**: Periodically verify data integrity

### 4. Migration Strategy

- **Incremental Migration**: Migrate tests gradually
- **Maintain Compatibility**: Support both modes during transition
- **Test Coverage**: Ensure migration doesn't break tests
- **Documentation Updates**: Update test documentation

## Summary

The eternal test data system provides a robust, scalable approach to integration testing that eliminates common problems with test data management. By using permanent, well-defined test data, teams can:

- **Eliminate Test Data Pollution**: No more hundreds of temporary records
- **Improve Test Reliability**: Consistent data across all test runs
- **Reduce Maintenance Overhead**: Less cleanup and data management
- **Accelerate Test Execution**: Faster tests with reduced API usage
- **Simplify CI/CD Integration**: Predictable test environment

For additional information and examples, refer to:
- [TESTING.md](TESTING.md) - Comprehensive testing guide
- `tests/eternal_test_data.py` - Test data definitions
- `tests/eternal_config.py` - Configuration management
- `tests/eternal_utils.py` - Utility functions
- `setup_eternal_data.py` - Setup script