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

### Notebook Quality Standards
- Every notebook must run sequentially from top to bottom
- Include comprehensive markdown documentation
- Extract reusable code into utility modules
- Implement proper error handling and logging
- Include both batch and streaming examples where applicable