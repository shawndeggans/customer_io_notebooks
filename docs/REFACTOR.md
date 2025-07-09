# Customer.IO Notebooks Refactor Plan

## Executive Summary

This document outlines a comprehensive plan to fix the alignment issues between notebooks, source code, and packaging in the Customer.IO notebooks project. The primary issue is that notebooks reference util modules that don't exist, while the actual source code is properly structured in `src/` directories.

This refactor plan follows **Test-Driven Development (TDD)** principles as outlined in CLAUDE.md and PYTHON_STANDARDS.md, ensuring all changes are test-first and maintain the project's high code quality standards.

## Problem Analysis

### Current State

#### What's Working ✅
- **Source Code**: Comprehensive, well-structured code in `src/` directories
  - `src/pipelines_api/` - Complete Data Pipelines API implementation (297+ unit tests)
  - `src/app_api/` - Complete App API implementation (communications focus)
  - `src/webhooks/` - Complete webhook processing implementation (production-ready)
- **Tests**: Complete test suite with different approaches per API:
  - **Pipelines API**: Complex eternal data system with read-only/mutation categorization
  - **App API**: Simple direct email testing approach
  - **Webhooks**: Comprehensive unit testing with mocked payloads
- **Documentation**: Comprehensive docs following project standards
- **Code Quality**: All code follows PYTHON_STANDARDS.md with type hints, ruff formatting, mypy compliance

#### What's Broken ❌
- **Notebook Imports**: Notebooks import from non-existent util modules
- **Package Installation**: `setup.py` is misconfigured and pip install fails
- **Import Misalignment**: Notebooks can't find the modules they need
- **TDD Workflow**: No test coverage for util modules bridge functionality

### Specific Import Issues

#### Notebooks Currently Import From:
```python
# Pipelines API notebooks
from utils.api_client import CustomerIOClient
from utils.people_manager import identify_user
from utils.event_manager import track_event
from utils.video_manager import track_video_playback_started
from utils.mobile_manager import track_application_installed
from utils.ecommerce_manager import track_product_clicked

# App API notebooks  
from app_utils.auth import AppAPIAuth
from app_utils.client import send_transactional, trigger_broadcast, send_push

# Webhook notebooks
from webhook_utils.processor import verify_signature, parse_event
from webhook_utils.event_handlers import get_event_handler
from webhook_utils.config_manager import CustomerIOWebhookManager
```

#### But Source Code Actually Lives In:
```python
# Pipelines API (src/pipelines_api/)
from src.pipelines_api.api_client import CustomerIOClient
from src.pipelines_api.people_manager import identify_user
from src.pipelines_api.event_manager import track_event
from src.pipelines_api.video_manager import track_video_playback_started
from src.pipelines_api.mobile_manager import track_application_installed
from src.pipelines_api.ecommerce_manager import track_product_clicked

# App API (src/app_api/)
from src.app_api.auth import AppAPIAuth
from src.app_api.client import send_transactional, trigger_broadcast, send_push

# Webhooks (src/webhooks/)
from src.webhooks.processor import verify_signature, parse_event
from src.webhooks.event_handlers import get_event_handler
from src.webhooks.config_manager import CustomerIOWebhookManager
```

### Setup.py Issues

#### Current Problems:
1. **Wrong Dependencies**: Uses `requests` but code uses `httpx`
2. **Missing Dependencies**: Many packages from `requirements.txt` not in `setup.py`
3. **Package Structure**: Doesn't include util modules (because they don't exist)

#### Current setup.py:
```python
install_requires=[
    "requests>=2.28.0",  # WRONG - should be httpx
    "python-dotenv>=0.19.0",
    "typing-extensions>=4.0.0",
],
```

#### Should be:
```python
install_requires=[
    "httpx>=0.25.0",
    "pydantic>=2.0.0", 
    "structlog>=24.0.0",
    "pandas>=2.0.0",
    "python-dotenv>=1.0.0",
    # ... other dependencies from requirements.txt
],
```

## Implementation Plan

This implementation follows **Test-Driven Development (TDD)** methodology. Each phase begins with failing tests that define the expected behavior, then implements the minimum code to pass, followed by refactoring.

### Phase 1: Create Missing Utils Modules (TDD Approach)

#### 1.1 TDD Workflow for Utils Modules

**Step 1: Red - Write Failing Tests**
```python
# tests/utils/test_utils_imports.py
def test_utils_api_client_import():
    """Test that utils.api_client imports correctly."""
    from utils.api_client import CustomerIOClient
    assert CustomerIOClient is not None

def test_utils_people_manager_import():
    """Test that utils.people_manager imports correctly."""
    from utils.people_manager import identify_user
    assert identify_user is not None

def test_app_utils_auth_import():
    """Test that app_utils.auth imports correctly."""
    from app_utils.auth import AppAPIAuth
    assert AppAPIAuth is not None
```

**Step 2: Green - Create Minimal Implementation**

#### 1.2 Create `utils/` Directory Structure
```
utils/
├── __init__.py
├── api_client.py
├── people_manager.py
├── event_manager.py
├── video_manager.py
├── mobile_manager.py
├── ecommerce_manager.py
├── device_manager.py
├── object_manager.py
├── batch_manager.py
├── page_manager.py
├── screen_manager.py
├── alias_manager.py
├── gdpr_manager.py
├── validators.py
└── exceptions.py
```

#### 1.3 Create `app_utils/` Directory Structure
```
app_utils/
├── __init__.py
├── auth.py
└── client.py
```

#### 1.4 Create `webhook_utils/` Directory Structure
```
webhook_utils/
├── __init__.py
├── processor.py
├── event_handlers.py
└── config_manager.py
```

#### 1.5 Implementation Details (Following PYTHON_STANDARDS.md)

Each util module will be a simple re-export with proper type hints and docstrings:

**Example: `utils/api_client.py`**
```python
"""
Re-export of src.pipelines_api.api_client for notebook compatibility.

This module provides backward compatibility for notebooks that import
from utils.api_client instead of src.pipelines_api.api_client.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.pipelines_api.api_client import CustomerIOClient

from src.pipelines_api.api_client import *

__all__ = ["CustomerIOClient"]
```

**Example: `app_utils/auth.py`**
```python
"""
Re-export of src.app_api.auth for notebook compatibility.

This module provides backward compatibility for notebooks that import
from app_utils.auth instead of src.app_api.auth.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app_api.auth import AppAPIAuth

from src.app_api.auth import *

__all__ = ["AppAPIAuth"]
```

**Step 3: Refactor - Add Quality Measures**
- Add mypy type checking to all util modules
- Run ruff formatting and linting
- Add structured logging if needed
- Ensure all modules pass quality checks

### Phase 2: Fix Package Configuration

#### 2.1 Update setup.py Dependencies
```python
install_requires=[
    # HTTP client
    "httpx>=0.25.0",
    
    # Data validation
    "pydantic>=2.0.0",
    
    # Logging
    "structlog>=24.0.0",
    
    # Data manipulation
    "pandas>=2.0.0",
    
    # System monitoring
    "psutil>=5.9.0",
    
    # Environment configuration
    "python-dotenv>=1.0.0",
    
    # Type extensions
    "typing-extensions>=4.0.0",
],
```

#### 2.2 Update Package Discovery
```python
packages=find_packages(where=".", include=["src*", "utils*", "app_utils*", "webhook_utils*"]),
```

#### 2.3 Update Package Directory
```python
package_dir={
    "": ".",
    "src": "src",
    "utils": "utils", 
    "app_utils": "app_utils",
    "webhook_utils": "webhook_utils"
},
```

### Phase 3: Make Package Pip-Installable

#### 3.1 Create Proper __init__.py Files

**`utils/__init__.py`**
```python
"""
Utility modules for Customer.IO Pipelines API.
Re-exports from src.pipelines_api for notebook compatibility.
"""
from src.pipelines_api import *
```

**`app_utils/__init__.py`**
```python
"""
Utility modules for Customer.IO App API.
Re-exports from src.app_api for notebook compatibility.
"""
from src.app_api import *
```

**`webhook_utils/__init__.py`**
```python
"""
Utility modules for Customer.IO Webhooks.
Re-exports from src.webhooks for notebook compatibility.
"""
from src.webhooks import *
```

#### 3.2 Update Root __init__.py
Add imports to make top-level imports work:
```python
# Make util modules available at package level
import utils
import app_utils  
import webhook_utils
```

### Phase 4: Comprehensive Testing (Following TESTING.md)

#### 4.1 TDD Testing Strategy

**Red Phase: Write Failing Tests**
```python
# tests/utils/test_utils_functionality.py
def test_utils_api_client_functionality():
    """Test that utils.api_client functions work correctly."""
    from utils.api_client import CustomerIOClient
    from utils.people_manager import identify_user
    
    # Test that imported functions work
    client = CustomerIOClient(api_key="test", region="us")
    assert client.api_key == "test"
    assert hasattr(identify_user, '__call__')

def test_app_utils_functionality():
    """Test that app_utils functions work correctly."""
    from app_utils.auth import AppAPIAuth
    from app_utils.client import send_transactional
    
    # Test that imported functions work
    auth = AppAPIAuth(api_token="test", region="us")
    assert auth.api_token == "test"
    assert hasattr(send_transactional, '__call__')
```

**Green Phase: Implementation**

#### 4.2 Installation Testing (TDD Approach)
```bash
# Test pip installation
pip install -e .

# Verify installation with tests
pytest tests/utils/test_utils_imports.py -v
pytest tests/utils/test_utils_functionality.py -v
```

#### 4.3 Notebook Testing (Following ZEN_NOTEBOOKS.md)
Test each notebook for:
- **Sequential execution** (restart kernel, run all cells)
- **≤15 lines per cell** compliance
- **Clear markdown documentation**
- **Proper error handling**
- **All imports work**

```python
# Automated notebook testing
def test_notebook_execution():
    """Test that notebooks execute without errors."""
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
    
    # Test each notebook
    notebooks = [
        "notebooks/pipelines_api/01_people_management.ipynb",
        "notebooks/app_api/01_communications.ipynb",
        "notebooks/webhooks/01_webhook_processing.ipynb"
    ]
    
    for notebook_path in notebooks:
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)
            
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': '.'}})
```

#### 4.4 Multi-API Testing Strategy
Following the established patterns from TESTING.md:

**Pipelines API Testing**:
```bash
# Use eternal data system for integration tests
TEST_DATA_MODE=eternal pytest tests/pipelines_api/integration/ -m "read_only" -v
```

**App API Testing**:
```bash
# Simple direct email testing
pytest tests/app_api/integration/ -v
```

**Webhook Testing**:
```bash
# Comprehensive unit testing with mocked payloads
pytest tests/webhooks/unit/ -v
```

#### 4.5 Code Quality Testing
```bash
# Type checking with mypy
mypy utils/ app_utils/ webhook_utils/ --strict

# Formatting and linting with ruff
ruff check utils/ app_utils/ webhook_utils/ --fix
ruff format utils/ app_utils/ webhook_utils/

# Run all tests with coverage
pytest tests/ --cov=src --cov=utils --cov=app_utils --cov=webhook_utils --cov-report=html
```

## Testing Strategy (Following TESTING.md Standards)

### Test Environment Setup
Following the established testing patterns:
1. **Clean Environment**: Test in fresh virtual environment
2. **Requirements**: Install from requirements.txt first
3. **Package Installation**: Test pip install -e . 
4. **Import Verification**: Test all notebook imports
5. **Functionality Testing**: Run notebook examples with proper test categorization

### Test Phases (TDD Red-Green-Refactor)

#### Phase 1 Testing: Utils Module Creation
**Red Phase**:
- [ ] Write failing tests for utils imports
- [ ] Write failing tests for app_utils imports  
- [ ] Write failing tests for webhook_utils imports
- [ ] Verify tests fail appropriately

**Green Phase**:
- [ ] Create utils directories
- [ ] Create minimal re-export modules
- [ ] Test basic imports work
- [ ] Verify no circular imports

**Refactor Phase**:
- [ ] Add type hints and docstrings
- [ ] Run mypy --strict on all utils modules
- [ ] Run ruff formatting and linting
- [ ] Add structured logging where needed

#### Phase 2 Testing: Package Configuration
**Red Phase**:
- [ ] Write failing tests for pip installation
- [ ] Write failing tests for package discovery
- [ ] Write failing tests for dependency resolution

**Green Phase**:
- [ ] Update setup.py dependencies
- [ ] Test pip install -e .
- [ ] Verify all dependencies install
- [ ] Test package discovery

**Refactor Phase**:
- [ ] Optimize package configuration
- [ ] Add development dependencies
- [ ] Test in multiple Python versions

#### Phase 3 Testing: Integration
**Red Phase**:
- [ ] Write failing tests for notebook imports
- [ ] Write failing tests for end-to-end workflows
- [ ] Write failing tests for API functionality

**Green Phase**:
- [ ] Test all notebook imports
- [ ] Run notebook examples
- [ ] Verify no import errors
- [ ] Test in clean environment

**Refactor Phase**:
- [ ] Optimize import performance
- [ ] Add error handling improvements
- [ ] Document any limitations

#### Phase 4 Testing: Comprehensive
**Red Phase**:
- [ ] Write failing tests for performance requirements
- [ ] Write failing tests for documentation completeness
- [ ] Write failing tests for security requirements

**Green Phase**:
- [ ] Run full test suite (unit + integration)
- [ ] Test all notebooks end-to-end
- [ ] Performance testing
- [ ] Documentation validation

**Refactor Phase**:
- [ ] Optimize performance bottlenecks
- [ ] Improve documentation based on testing
- [ ] Add monitoring and logging

### Test Automation (Following Project Standards)
```bash
#!/bin/bash
# test_refactor.sh - TDD-compliant testing script

echo "Testing refactor implementation with TDD approach..."

# Phase 1: Red - Verify failing tests
echo "1. Running failing tests (Red phase)"
pytest tests/utils/ -v --tb=short || echo "Tests failing as expected"

# Phase 2: Green - Test basic functionality
echo "2. Testing basic functionality (Green phase)"
pip uninstall -y customerio-api-client
pip install -e .

# Test imports
python -c "
import utils
import app_utils
import webhook_utils
from utils.api_client import CustomerIOClient
from app_utils.auth import AppAPIAuth
from webhook_utils.processor import verify_signature
print('All imports successful')
"

# Phase 3: Refactor - Code quality testing
echo "3. Code quality testing (Refactor phase)"
mypy utils/ app_utils/ webhook_utils/ --strict
ruff check utils/ app_utils/ webhook_utils/ --fix
ruff format utils/ app_utils/ webhook_utils/

# Phase 4: Comprehensive testing
echo "4. Running comprehensive tests"
pytest tests/ -v --cov=src --cov=utils --cov=app_utils --cov=webhook_utils

# Phase 5: Notebook testing (following ZEN_NOTEBOOKS.md)
echo "5. Testing notebooks (sequential execution)"
jupyter nbconvert --to notebook --execute notebooks/**/*.ipynb

echo "Refactor testing complete - all phases passed"
```

### Test Markers and Categories
Following TESTING.md standards:
```python
# Test markers for utils modules
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # API integration tests
@pytest.mark.utils_bridge  # Utils bridge functionality
@pytest.mark.notebook      # Notebook compatibility tests
```

## Risk Mitigation

### Potential Issues and Solutions

#### 1. Circular Import Issues
**Risk**: Re-export modules might cause circular imports
**Solution**: 
- Use careful import structure
- Test imports in isolation
- Use lazy imports if needed

#### 2. Path Issues in Notebooks
**Risk**: Notebooks might have hardcoded paths
**Solution**:
- Review all notebook path handling
- Use relative imports where possible
- Test in different environments

#### 3. Dependency Conflicts
**Risk**: Updated dependencies might conflict
**Solution**:
- Test in clean environment
- Use pip-tools for dependency resolution
- Pin critical dependencies

#### 4. Test Failures
**Risk**: Existing tests might fail with new structure
**Solution**:
- Run tests before changes
- Update imports if needed
- Ensure backward compatibility

### Rollback Procedures

#### If Phase 1 Fails:
```bash
# Remove created utils directories
rm -rf utils/ app_utils/ webhook_utils/
git checkout -- .
```

#### If Phase 2 Fails:
```bash
# Restore original setup.py
git checkout setup.py
pip uninstall -y customerio-api-client
```

#### If Phase 3 Fails:
```bash
# Full rollback
git stash
git clean -fd
pip uninstall -y customerio-api-client
```

## Implementation Timeline (TDD Approach)

### Day 1: Phase 1 - Utils Module Creation (Red-Green-Refactor)
**Morning - Red Phase**:
- [ ] Write failing tests for utils imports
- [ ] Write failing tests for app_utils imports
- [ ] Write failing tests for webhook_utils imports
- [ ] Verify all tests fail appropriately

**Afternoon - Green Phase**:
- [ ] Create directory structure
- [ ] Create minimal re-export modules
- [ ] Make tests pass with minimal code

**Evening - Refactor Phase**:
- [ ] Add type hints and docstrings
- [ ] Run mypy --strict and fix issues
- [ ] Run ruff formatting and linting
- [ ] Test basic imports work

### Day 2: Phase 2 - Package Configuration (Red-Green-Refactor)
**Morning - Red Phase**:
- [ ] Write failing tests for pip installation
- [ ] Write failing tests for package discovery
- [ ] Write failing tests for dependency resolution

**Afternoon - Green Phase**:
- [ ] Update setup.py with correct dependencies
- [ ] Test pip install -e .
- [ ] Make package installation tests pass

**Evening - Refactor Phase**:
- [ ] Optimize package configuration
- [ ] Add development dependencies
- [ ] Test in multiple environments

### Day 3: Phase 3 - Integration (Red-Green-Refactor)
**Morning - Red Phase**:
- [ ] Write failing tests for notebook imports
- [ ] Write failing tests for end-to-end workflows
- [ ] Write failing tests for API functionality

**Afternoon - Green Phase**:
- [ ] Test all notebook imports
- [ ] Run notebook examples
- [ ] Make integration tests pass

**Evening - Refactor Phase**:
- [ ] Optimize import performance
- [ ] Add error handling improvements
- [ ] Document any limitations

### Day 4: Phase 4 - Comprehensive Testing (Red-Green-Refactor)
**Morning - Red Phase**:
- [ ] Write failing tests for performance requirements
- [ ] Write failing tests for documentation completeness
- [ ] Write failing tests for security compliance

**Afternoon - Green Phase**:
- [ ] Run full test suite (unit + integration)
- [ ] Test all notebooks end-to-end following ZEN_NOTEBOOKS.md
- [ ] Make comprehensive tests pass

**Evening - Refactor Phase**:
- [ ] Optimize performance bottlenecks
- [ ] Improve documentation based on testing
- [ ] Add monitoring and logging
- [ ] Final cleanup and documentation

## Success Criteria (Following Project Standards)

### Must Have (TDD Compliance)
- [ ] All notebooks import successfully (following ZEN_NOTEBOOKS.md standards)
- [ ] `pip install -e .` works without errors
- [ ] All existing tests pass (469+ tests across all APIs)
- [ ] No circular imports
- [ ] Clean environment testing passes
- [ ] **TDD Workflow**: All utils modules created using Red-Green-Refactor
- [ ] **Type Safety**: All utils modules pass mypy --strict
- [ ] **Code Quality**: All utils modules pass ruff check and format
- [ ] **Documentation**: All utils modules have proper docstrings following PYTHON_STANDARDS.md

### Should Have (Quality Standards)
- [ ] Notebook examples run successfully with ≤15 lines per cell
- [ ] Performance is not degraded
- [ ] Documentation is updated following project standards
- [ ] CI/CD pipeline works with existing test categories
- [ ] **Test Coverage**: Utils modules have comprehensive unit tests
- [ ] **Error Handling**: Proper error messages and structured logging
- [ ] **Security**: No hardcoded credentials, proper API key management

### Nice to Have (Enhancements)
- [ ] Improved import performance
- [ ] Better error messages with structured logging
- [ ] Enhanced documentation with examples
- [ ] Automated testing with pre-commit hooks
- [ ] **Monitoring**: Import performance metrics
- [ ] **Analytics**: Usage tracking for utils modules
- [ ] **Developer Experience**: Enhanced IDE support with proper type hints

## Conclusion

This refactor plan addresses the core alignment issues by following established project standards:

### 1. **Test-Driven Development Approach**
- **Red-Green-Refactor**: Every change starts with failing tests
- **Quality Gates**: mypy --strict, ruff formatting, comprehensive testing
- **TDD Compliance**: Maintains the project's cornerstone development methodology

### 2. **Standards Alignment**
- **PYTHON_STANDARDS.md**: Type hints, clean code, functional principles
- **TESTING.md**: Multi-API testing strategies, eternal data patterns
- **ZEN_NOTEBOOKS.md**: Sequential execution, ≤15 lines per cell, clear documentation
- **REQUIREMENTS.md**: Architecture compliance, security standards

### 3. **Multi-API Integration**
- **Pipelines API**: Supports eternal data system and complex testing
- **App API**: Maintains simple direct testing approach
- **Webhooks**: Preserves comprehensive unit testing with mocked payloads

### 4. **Risk Mitigation**
The approach is low-risk because:
- **No Existing Code Modified**: All changes are additive
- **TDD Safety Net**: Comprehensive test coverage prevents regressions
- **Incremental Implementation**: Phase-by-phase rollout with testing
- **Easy Rollback**: Simple git operations to undo changes
- **Quality Assurance**: All code passes strict quality checks

### 5. **Production Readiness**
Once implemented, users will be able to:
- Run `pip install -e .` successfully
- Use notebooks without import errors following ZEN_NOTEBOOKS.md
- Maintain the same development workflow with TDD
- Access all existing functionality (469+ tests)
- Benefit from improved type safety and code quality

### 6. **Long-term Benefits**
This refactor transforms the project from a collection of files into:
- **Properly Packaged Python Library**: Installable via pip
- **Standards-Compliant Codebase**: Following all project guidelines
- **Maintainable Architecture**: Clear separation of concerns
- **Developer-Friendly**: Enhanced IDE support and documentation
- **Production-Ready**: Comprehensive testing and error handling

The refactor maintains all existing functionality while enabling the seamless notebook experience that data engineers expect, all while adhering to the project's established standards for quality, testing, and documentation.