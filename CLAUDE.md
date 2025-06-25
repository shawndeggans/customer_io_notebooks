# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Customer.IO API Databricks notebook collection designed to provide comprehensive coverage of the Customer.IO Data Pipelines API. The project focuses on creating production-ready Jupyter notebooks for Databricks that help data teams work with Customer.IO's API effectively.

## Architecture

### Core Purpose
- Create Jupyter notebooks for Databricks that cover 100% of Customer.IO API endpoints
- Provide both batch and streaming data processing patterns
- Implement production-ready error handling and resilience patterns
- Follow Test-Driven Development (TDD) principles

### Project Structure
```
customer_io_notebooks/
├── PYTHON_STANDARDS.md          # Comprehensive Python development guidelines
├── REQUIREMENTS.md              # Customer.IO API notebook development requirements
├── ZEN_NOTEBOOKS.md             # Clean, maintainable Jupyter notebook best practices
├── cio_pipelines_api.json       # Complete Customer.IO API specification (25k+ lines)
├── devbox.json                  # Development environment configuration
└── README.md                    # Basic project description
```

## Emojis
NEVER EVER USE EMOJIS. PERIOD. I HATE EMOJIS. DO NOT USE THEM EVER!

## Development Environment

### Setup Commands
```bash
# Initialize development environment with devbox
devbox shell

# Install Python dependencies (using uv for fast package management)
uv install

# Start development environment
uv run jupyter lab
```

### Required Tools
- **uv**: Fast Python package installer and resolver
- **Node.js**: For any web-based tooling
- **VS Code**: Recommended editor (configured in devbox)
- **Jupyter**: For notebook development and testing

## Notebook Development Standards

### Architecture Requirements
Follow the modular notebook structure defined in REQUIREMENTS.md:
- 00_setup_and_configuration.ipynb
- 01_authentication_and_utilities.ipynb
- 02_people_management.ipynb
- 03_events_and_tracking.ipynb
- [Additional numbered notebooks for each API area]

### Key Implementation Patterns

#### API Client Design
Create robust, reusable API client with:
- Automatic retry logic with exponential backoff
- Rate limiting (3000 requests per 3 seconds)
- Request/response logging to Delta tables
- Support for both US and EU regions
- Batch request optimization
- Error handling and recovery

#### Databricks Integration
- Use Databricks secrets for API key management
- Leverage Delta Lake for data persistence and versioning
- Implement proper Spark DataFrame operations
- Include structured streaming examples for real-time processing
- Provide both batch and streaming approaches

#### Error Handling Patterns
- Graceful degradation with fallback to local storage
- Circuit breaker pattern for preventing cascading failures
- Retry queue management with exponential backoff
- Comprehensive logging and monitoring

## Python Development Guidelines

### Core Philosophy
- **Test-Driven Development (TDD)**: Every feature begins with a failing test
- **Type Safety**: Use mypy strict mode for maximum type safety
- **Functional Principles**: Prefer immutability and pure functions
- **Modern Async**: Use structured concurrency and proper resource management

### Code Quality Tools
```bash
# Format and lint code
ruff check --fix .
ruff format .

# Type checking
mypy src/

# Run tests with coverage
pytest --cov=src/ --cov-report=term-missing
```

### Required Dependencies
- pydantic >= 2.0.0 (for data validation)
- httpx >= 0.25.0 (for async HTTP requests)
- structlog >= 24.0.0 (for structured logging)
- pytest >= 7.4.0 (for testing)
- mypy >= 1.8.0 (for type checking)
- ruff >= 0.1.9 (for linting and formatting)

## API Reference

### Customer.IO Data Pipelines API
- **Base URL**: https://cdp.customer.io/v1
- **Rate Limits**: 3000 requests per 3 seconds
- **Request Limit**: 32KB per request, 500KB per batch
- **Regions**: US (cdp.customer.io) and EU (cdp-eu.customer.io)

### Key API Categories
- People Management (identify, delete, suppress/unsuppress)
- Event Tracking (custom events, semantic events)
- Objects and Relationships
- Device Management
- Batch Operations
- Semantic Events (ecommerce, email, mobile, video)

## Testing Strategy

### Test Coverage Requirements
- Unit tests for all utility functions
- Integration tests for API calls with test data
- Data validation tests for schema compliance
- Performance tests for batch operations

### Test Organization
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # API integration tests
└── e2e/           # End-to-end workflow tests
```

## Security and Compliance

### Required Security Measures
- Never hardcode API credentials
- Use Databricks secrets for key management
- Implement PII encryption at rest
- Follow GDPR compliance patterns
- Audit all API key usage

### Data Privacy
- Data retention policies
- GDPR compliance helpers
- Audit logging for all operations
- Proper access control and authorization

## Performance Optimization

### Batch Processing
- Intelligent batching with 500KB limit respect
- Group similar operations for efficiency
- Implement parallel processing where safe
- Use Databricks Delta Cache

### Monitoring Requirements
- API performance metrics (response times, success rates)
- Data quality metrics (validation failures, completeness)
- Business metrics (events tracked, users identified)
- Real-time alerting on anomalies

## Common Commands

### Development Workflow
```bash
# Setup development environment
devbox shell

# Install dependencies
uv install

# Run notebook server
uv run jupyter lab

# Format code
ruff format .

# Type check
mypy .

# Run tests
pytest
```

### Git Workflow
```bash
# Standard development workflow
git checkout -b feature/new-notebook
# Make changes
git add .
git commit -m "feat: add new Customer.IO notebook"
git push origin feature/new-notebook
```

## Important Notes

### Customer.IO API Specifics
- API responses are logged to Delta tables for debugging
- Regional endpoints must be configured correctly (US vs EU)
- Rate limiting is enforced - implement proper backoff strategies
- Semantic events have specific schemas that must be followed exactly

### Databricks Best Practices
- Use OPTIMIZE regularly on Delta tables
- Implement Z-ORDER for query optimization
- Enable Delta Cache for performance
- Use proper partitioning strategies
- Configure clusters optimally for workload

### Advanced Development Pattern

### **The Refined Notebook Pattern (Established in Notebooks 05-12)**

All notebooks should follow this sophisticated 6-section structure:

#### **Section 1: Comprehensive Documentation Header**
```markdown
# Customer.IO [Feature Name]

Comprehensive [feature description] for Customer.IO data pipelines including:
- [Key capability 1]
- [Key capability 2]
- [Key capability 3]
- [Additional capabilities as bullet points]
```

#### **Section 2: Core Imports and Setup**
```python
# Essential imports for [feature name]
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
import structlog
from pydantic import BaseModel, Field, validator
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Import Customer.IO utilities
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'utils'))

from api_client import CustomerIOClient
from error_handlers import retry_on_error, ErrorContext, CustomerIOError
from validators import validate_request_size

print("SUCCESS: [Feature] imports loaded")
```

#### **Section 3: Type-Safe Model Definitions**
- **Enumerations first** (str, Enum classes for all constants)
- **Pydantic models** with comprehensive validators
- **BaseModel classes** with proper Field definitions
- **Type safety** throughout all model definitions

#### **Section 4: Main Manager Class**
```python
class [Feature]Manager:
    """Comprehensive [feature] management system."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("[feature]_manager")
        
        # Component initialization
        # System state tracking
        
        self.logger.info("[Feature]Manager initialized")
    
    # Comprehensive methods with type hints
    # Error handling with retry decorators
    # Structured logging throughout
    # Thread-safe operations where needed
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get [Feature]Manager metrics and status."""
        return {
            "manager": {...},
            "components": {...},
            "features": {...}
        }
```

#### **Section 5: Example Usage and Testing**
- **Comprehensive examples** demonstrating all features
- **Error handling demonstrations**
- **Performance testing examples**
- **Real-world use case scenarios**

#### **Section 6: Summary Documentation**
```markdown
## Summary

This notebook demonstrates a comprehensive [feature] solution including:

**Core Features:**
- **[Component1]**: Description of functionality
- **[Component2]**: Description of functionality

**Key Capabilities:**
- List of major capabilities
- Integration points
- Performance characteristics

**Production Features:**
- Error handling and resilience
- Monitoring and metrics
- Security considerations

The system is designed for production use with [specific benefits].
```

### **Manager Class Pattern**

#### **Required Components:**
1. **Dependency Injection**: Accept client and other managers in constructor
2. **Structured Logging**: Use structlog with contextual information
3. **Type Safety**: All methods use type hints and Pydantic models
4. **Error Handling**: Use retry decorators and comprehensive error handling
5. **Metrics**: Implement get_metrics() method for monitoring
6. **Thread Safety**: Use threading.Lock() for shared state when needed
7. **Production Features**: Include monitoring, health checks, performance optimization

#### **Method Patterns:**
```python
@retry_on_error(max_retries=3, backoff_factor=2.0)
def core_operation(self, param: TypedModel) -> ResultModel:
    """Comprehensive operation with full error handling."""
    
    # Validation
    # Core logic
    # Logging
    # Return typed result

def get_metrics(self) -> Dict[str, Any]:
    """Always implement metrics for observability."""
    return {
        "component_stats": {...},
        "performance_metrics": {...},
        "feature_flags": {...}
    }
```

### **Code Extraction Pattern**

#### **When to Extract to Utils Module:**
- **Manager classes** with 200+ lines of functionality
- **Complex business logic** used across notebooks  
- **Reusable components** with comprehensive functionality
- **Production-ready features** requiring extensive testing

#### **Extraction Requirements:**
1. **File Location**: utils/[feature]_manager.py
2. **Import Structure**: Proper relative imports from utils modules
3. **Documentation**: Comprehensive module docstring
4. **Type Safety**: Full type hints and Pydantic models
5. **Error Handling**: Comprehensive error handling and retry logic
6. **Testing**: Corresponding test file with 50+ test methods

### **Testing Pattern**

#### **Test File Structure:**
```python
"""
Comprehensive tests for Customer.IO [Feature] Manager.

Tests cover:
- [Enumeration/model testing areas]
- [Core functionality areas]
- [Integration scenarios]
- [Error handling scenarios]
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from pydantic import ValidationError

# Test classes per model/component
class TestEnumName:
    """Test [Enum] enum."""
    
    def test_enum_values(self):
        """Test all enum values."""
    
    def test_enum_membership(self):
        """Test enum membership."""

class TestModelName:
    """Test [Model] data model."""
    
    def test_valid_model(self):
        """Test valid model creation."""
    
    def test_model_validation(self):
        """Test model validation."""

class TestManagerName:
    """Test [Manager] operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
    
    @pytest.fixture
    def manager(self, mock_client):
        """Create [Manager] instance."""
    
    def test_core_functionality(self):
        """Test core manager functionality."""
    
    def test_error_handling(self):
        """Test error handling scenarios."""
    
    def test_metrics(self):
        """Test metrics collection."""

class TestIntegration:
    """Integration tests for [Manager]."""
    
    def test_complete_workflow(self):
        """Test complete end-to-end workflow."""
```

#### **Test Requirements:**
- **50+ test methods** minimum per manager
- **100+ test methods** for complex managers  
- **Mock all dependencies** using unittest.mock
- **Test all error conditions** and edge cases
- **Integration test scenarios** for complete workflows
- **Fixture usage** for common test data

## Project Progress Status

### Current Polishing Phase (December 2024)

**PHASE STATUS**:
- **PHASE 1**: Advanced pattern documentation ✅ COMPLETED
- **PHASE 2**: Manager class extractions ✅ COMPLETED  
- **PHASE 3**: Comprehensive test suites ✅ COMPLETED
- **PHASE 4A**: Notebooks 00-02 restructuring ✅ COMPLETED
- **PHASE 4B**: Notebooks 03-04 restructuring 🔄 IN PROGRESS
- **PHASE 5**: Test validation ⏳ PENDING

### Extracted Manager Classes (Production Ready)

**utils/pipeline_manager.py** (600+ lines, 50+ tests)
- PipelineOrchestrator with DAG validation
- Stage execution framework with monitoring
- Data quality metrics and validation
- Circuit breaker patterns for fault tolerance

**utils/observability_manager.py** (1000+ lines, 50+ tests)  
- MetricsCollector with buffering and aggregation
- AlertManager with rule-based threshold monitoring
- HealthMonitor with custom checks and system monitoring
- DistributedTracer with span management and context tracking

**utils/deployment_manager.py** (800+ lines, 50+ tests)
- ConfigurationManager with secure secrets handling
- InfrastructureGenerator for multi-cloud IaC templates
- DeploymentEngine with strategy execution and rollback
- Multi-environment promotion workflows

**utils/setup_manager.py** (800+ lines, planned tests)
- SetupConfiguration with type-safe validation
- SyntheticDataGenerator for realistic test data
- SchemaManager with optimized Delta Lake schemas
- Complete environment setup with validation framework

### Notebook Restructuring Progress

**✅ COMPLETED**: 
- **00_setup_and_configuration.ipynb**: Full 6-section restructure
  - Extracted SetupManager to utils/setup_manager.py
  - Cleaned up 23+ redundant cells to 6 organized sections
  - Enterprise-grade setup with circuit breakers and validation

**🔄 NEXT SESSION**:
- **01_authentication_and_utilities.ipynb**: Extract AuthenticationManager
- **02_people_management.ipynb**: Enhanced PeopleManager extraction  
- **03_events_and_tracking.ipynb**: Extract EventsManager
- **04_messaging_api_integration.ipynb**: Extract MessagingManager

### Testing Status
- **4/4 current manager test suites**: 100% complete with 50+ test methods each
- **All tests**: Mock-based, comprehensive error handling, integration scenarios
- **Test coverage**: Enums, models, manager operations, error conditions

### Session Continuation Instructions
When resuming work:
1. Continue PHASE 4B with notebook 01_authentication_and_utilities.ipynb
2. Follow established 6-section pattern restructuring
3. Extract AuthenticationManager to utils/authentication_manager.py
4. Create comprehensive test suite with 50+ test methods
5. Proceed through notebooks 02-04 with same pattern

## Notebook Quality Standards
- Every notebook must run sequentially from top to bottom
- Follow the 6-section advanced pattern structure
- Extract Manager classes to utils modules with comprehensive tests
- Implement proper error handling and logging
- Include comprehensive documentation and examples
- Use type hints and Pydantic validation throughout
- No emojis anywhere in code or documentation
- Include both batch and streaming examples where applicable