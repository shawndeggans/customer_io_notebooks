# Customer.IO Data Pipelines API - Databricks Notebooks

A comprehensive suite of Jupyter notebooks and Python utilities for working with the Customer.IO Data Pipelines API in Databricks environments. This project provides production-ready patterns for data ingestion, event tracking, user management, and analytics integration.

## Quick Start

### Prerequisites

- Python 3.11+
- Databricks workspace (optional, can run locally)
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
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

#### Using standard Python setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -e .
```

### Basic Usage

```python
from utils.api_client import CustomerIOClient
from utils.people_manager import PeopleManager

# Initialize client
client = CustomerIOClient(api_key="your_api_key", region="us")

# Use managers for specific operations
people_manager = PeopleManager(client)

# Identify a user
result = people_manager.identify_user(
    user_id="user_123",
    traits={"email": "user@example.com", "name": "John Doe"}
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
│
├── notebooks/                          # Jupyter notebooks
│   ├── 00_setup_and_configuration.ipynb
│   ├── 01_authentication_and_utilities.ipynb
│   ├── 02_people_management.ipynb
│   ├── 03_events_and_tracking.ipynb
│   ├── 04_objects_and_relationships.ipynb
│   ├── 05_device_management.ipynb
│   ├── 06_advanced_tracking.ipynb
│   ├── 07_ecommerce_events.ipynb
│   ├── 08_suppression_and_gdpr.ipynb
│   ├── 09_batch_operations.ipynb
│   ├── 10_data_pipelines_integration.ipynb
│   ├── 11_monitoring_and_observability.ipynb
│   └── 12_production_deployment.ipynb
│
├── utils/                              # Reusable Python modules
│   ├── __init__.py
│   ├── api_client.py                   # Core API client
│   ├── authentication_manager.py       # Authentication handling
│   ├── deployment_manager.py           # Production deployment
│   ├── device_manager.py               # Device management
│   ├── error_handlers.py               # Error handling utilities
│   ├── event_manager.py                # Event tracking
│   ├── group_manager.py                # Groups and relationships
│   ├── observability_manager.py        # Monitoring and metrics
│   ├── people_manager.py               # People/user management
│   ├── pipeline_manager.py             # Data pipeline integration
│   ├── setup_manager.py                # Environment setup
│   ├── transformers.py                 # Data transformation
│   └── validators.py                   # Data validation
│
└── tests/                              # Test suite
    ├── conftest.py                     # Test configuration
    ├── unit/                           # Unit tests
    │   ├── test_api_client.py
    │   ├── test_authentication_manager.py
    │   ├── test_deployment_manager.py
    │   ├── test_device_manager.py
    │   ├── test_event_manager.py
    │   ├── test_group_manager.py
    │   ├── test_observability_manager.py
    │   ├── test_people_manager.py
    │   ├── test_pipeline_manager.py
    │   ├── test_transformers.py
    │   └── test_validators.py
    └── integration/                    # Integration tests
        └── test_api_integration.py
```

## Core Components

### API Client (`utils/api_client.py`)

The `CustomerIOClient` provides a robust interface to the Customer.IO Data Pipelines API with:

- Automatic retry logic with exponential backoff
- Rate limiting (3000 requests per 3 seconds)
- Support for both US and EU regions
- Comprehensive error handling
- Request/response logging

```python
from utils.api_client import CustomerIOClient

client = CustomerIOClient(
    api_key="your_api_key",
    region="us",  # or "eu"
    timeout=30,
    max_retries=3
)
```

### Manager Classes

Each manager class encapsulates specific Customer.IO functionality:

- **PeopleManager**: User identification, traits, suppression
- **EventManager**: Event tracking and semantic events
- **DeviceManager**: Device registration and management
- **GroupManager**: Groups, objects, and relationships
- **PipelineManager**: Data pipeline integration
- **ObservabilityManager**: Monitoring and analytics
- **DeploymentManager**: Production deployment patterns

### Data Validation (`utils/validators.py`)

Pydantic v2-based validation models ensure data quality:

```python
from utils.validators import IdentifyPayload, TrackPayload

# Validate user identification data
payload = IdentifyPayload(
    userId="user_123",
    traits={"email": "user@example.com"}
)
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
   uv pip install -r requirements.txt
   ```

4. **Configure secrets** (for Databricks)
   ```python
   # In Databricks
   dbutils.secrets.put("customer-io", "api-key", "your_api_key")
   ```

### Running Tests

This project follows Test-Driven Development (TDD) principles with comprehensive test coverage.

#### Run all tests
```bash
pytest
```

#### Run with coverage
```bash
pytest --cov=utils --cov-report=term-missing --cov-report=html
```

#### Run specific test categories
```bash
# Unit tests only
pytest tests/unit/ -m unit

# Integration tests (requires API credentials)
pytest tests/integration/ -m integration

# Fast tests only
pytest -m "not slow"
```

#### Test Configuration

Tests are configured in `pytest.ini` with the following markers:

- `unit`: Fast unit tests that don't require external dependencies
- `integration`: Tests that may require API access or Spark
- `slow`: Tests that take longer to run
- `api`: Tests that make actual API calls (require valid credentials)

### Code Quality

This project maintains high code quality standards:

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
ruff check --fix . && ruff format . && mypy utils/ && pytest
```

## Databricks Integration

### Environment Setup

1. **Create Databricks cluster** with these specifications:
   - Runtime: 11.3.x-scala2.12 or later
   - Python: 3.9+
   - Workers: 2+ (depending on data volume)

2. **Install required libraries**:
   ```python
   %pip install pydantic>=2.0.0 httpx>=0.25.0 structlog>=24.0.0
   ```

3. **Configure secrets**:
   ```python
   # Store API credentials securely
   dbutils.secrets.put("customer-io", "api-key", "your_api_key")
   dbutils.secrets.put("customer-io", "region", "us")  # or "eu"
   ```

### Notebook Usage

Each notebook is designed to be self-contained with clear prerequisites:

1. **00_setup_and_configuration.ipynb**: Initial environment setup
2. **01_authentication_and_utilities.ipynb**: Authentication patterns
3. **02_people_management.ipynb**: User identification and management
4. **03_events_and_tracking.ipynb**: Event tracking fundamentals
5. **04_objects_and_relationships.ipynb**: Groups and relationships
6. **05_device_management.ipynb**: Device registration
7. **06_advanced_tracking.ipynb**: Advanced event patterns
8. **07_ecommerce_events.ipynb**: E-commerce specific events
9. **08_suppression_and_gdpr.ipynb**: Privacy and compliance
10. **09_batch_operations.ipynb**: Bulk data operations
11. **10_data_pipelines_integration.ipynb**: Pipeline integration
12. **11_monitoring_and_observability.ipynb**: Monitoring and metrics
13. **12_production_deployment.ipynb**: Production deployment

### Delta Lake Integration

All notebooks leverage Delta Lake for:

- Data persistence and versioning
- ACID transactions
- Time travel capabilities
- Schema evolution
- Performance optimization

Example usage:
```python
# Save API responses to Delta Lake
df.write.format("delta").mode("append").saveAsTable("customerio_events")

# Read with time travel
historical_df = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .table("customerio_events")
```

## Performance Optimization

### Batch Processing

- **Batch size**: Optimized for 100-500 records per batch
- **Rate limiting**: Respects Customer.IO's 3000 req/3sec limit
- **Parallel processing**: Uses Spark for distributed processing
- **Error handling**: Failed requests are queued for retry

### Caching Strategy

- **API response caching**: Temporary storage of successful responses
- **Delta Cache**: Leverages Databricks Delta Cache
- **User lookup caching**: Reduces redundant API calls

### Monitoring

Track key metrics:
- API request success rates
- Response times
- Error categories
- Data quality metrics
- Processing throughput

## Security and Compliance

### API Key Management

- Never hardcode credentials in notebooks
- Use Databricks secrets for secure storage
- Implement key rotation procedures
- Audit key usage patterns

### Data Privacy

- PII encryption at rest in Delta Lake
- GDPR compliance utilities
- Data retention policy enforcement
- Comprehensive audit logging

### Access Control

- Notebook-level permissions
- Data access restrictions based on roles
- Operation authorization tracking
- Change logging and monitoring

## Troubleshooting

### Common Issues

#### Import Errors
```python
# Issue: ModuleNotFoundError for utils modules
# Solution: Ensure you're running from project root
import sys
sys.path.append('/path/to/customer_io_notebooks')
```

#### API Authentication Errors
```python
# Issue: 401 Unauthorized
# Solution: Verify API key and region
client = CustomerIOClient(
    api_key=dbutils.secrets.get("customer-io", "api-key"),
    region="us"  # Ensure correct region
)
```

#### Rate Limiting
```python
# Issue: 429 Too Many Requests
# Solution: Implement exponential backoff (built into client)
# Or reduce batch size and add delays
```

#### PySpark Import Errors (Local Development)
```python
# Issue: No module named 'pyspark'
# Solution: PySpark imports are optional for local development
# Only required for Databricks-specific features
```

### Test Failures

If tests fail, common causes:

1. **Missing dependencies**: Run `uv pip install -r requirements.txt`
2. **Pydantic version mismatch**: Ensure Pydantic v2.0+ is installed
3. **API credentials**: Set test credentials in environment variables
4. **Test expectations**: Some tests expect specific error message formats

### Performance Issues

For slow performance:

1. **Optimize batch sizes**: Reduce if memory issues, increase for throughput
2. **Enable Delta optimizations**: Use OPTIMIZE and Z-ORDER commands
3. **Tune Spark settings**: Adjust parallelism and memory allocation
4. **Review query patterns**: Use appropriate filters and partitioning

## Contributing

### Development Guidelines

1. **Follow TDD**: Write tests before implementation
2. **Type hints**: All functions must have type annotations
3. **Documentation**: Comprehensive docstrings required
4. **Error handling**: Explicit error handling for all API calls
5. **Performance**: Consider batch processing and caching

### Code Standards

- **Formatting**: Use `ruff format` for consistent formatting
- **Linting**: Pass `ruff check` with no errors
- **Type checking**: Pass `mypy --strict` validation
- **Testing**: Minimum 80% test coverage required

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite: `pytest`
4. Run quality checks: `ruff check --fix . && mypy utils/`
5. Update documentation if needed
6. Submit pull request with clear description

## API Reference

### Core Client Methods

```python
# User identification
client.identify(userId="123", traits={"email": "user@example.com"})

# Event tracking
client.track(userId="123", event="Purchase", properties={"amount": 100})

# Device management
client.add_device(userId="123", device={"platform": "ios", "token": "..."})

# Object operations
client.create_object(type="product", id="prod_123", attributes={"name": "Widget"})
```

### Manager Classes API

Each manager provides high-level operations:

```python
# People operations
people_manager.identify_user(user_id, traits)
people_manager.suppress_user(user_id)
people_manager.bulk_identify(users_df)

# Event operations
event_manager.track_event(user_id, event_name, properties)
event_manager.track_purchase(user_id, order_data)
event_manager.batch_track_events(events_df)

# Device operations
device_manager.register_device(user_id, device_data)
device_manager.update_device(device_id, updates)
```

## Best Practices

### Data Pipeline Design

1. **Idempotency**: Design operations to be safely retryable
2. **Error recovery**: Implement dead letter queues for failed operations
3. **Monitoring**: Track data quality and pipeline health
4. **Testing**: Comprehensive unit and integration tests

### Performance Optimization

1. **Batching**: Process data in optimal batch sizes
2. **Caching**: Cache frequently accessed data
3. **Partitioning**: Use appropriate Delta Lake partitioning
4. **Monitoring**: Track and optimize bottlenecks

### Error Handling

1. **Graceful degradation**: Continue processing despite individual failures
2. **Retry logic**: Implement exponential backoff for transient failures
3. **Logging**: Comprehensive error logging and alerting
4. **Recovery**: Automated recovery for common failure scenarios

## Support

### Documentation

- **API Documentation**: [Customer.IO API Docs](https://customer.io/docs/api/)
- **Project Requirements**: See `REQUIREMENTS.md` for detailed specifications
- **Development Standards**: See `PYTHON_STANDARDS.md` for coding guidelines

### Getting Help

For issues with this project:

1. Check this README and project documentation
2. Review existing issues and tests
3. Consult Customer.IO API documentation
4. Create issue with reproduction steps

---

**License**: MIT

**Maintainer**: Development Team

**Last Updated**: 2024-12-26