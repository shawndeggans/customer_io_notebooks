# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project creates a comprehensive Customer.IO API client library using Test-Driven Development (TDD), with Jupyter notebooks as the interface for data engineers to interact with the Customer.IO Data Pipelines API.

## Core Architecture

### Purpose
- Build a complete Python client library for the Customer.IO Data Pipelines API
- Follow Test-Driven Development (TDD) methodology throughout
- Create clean, functional Jupyter notebooks that demonstrate API usage
- Provide comprehensive coverage of all endpoints in cio_pipelines_api.json

### Project Structure
```
customer_io_notebooks/
├── PYTHON_STANDARDS.md          # Python development guidelines (FOLLOW EXACTLY)
├── REQUIREMENTS.md              # Project requirements and specifications
├── ZEN_NOTEBOOKS.md             # Notebook best practices (FOLLOW EXACTLY)
├── TODO.md                      # Development tracking and milestones
├── cio_pipelines_api.json       # Complete Customer.IO API specification
├── utils/                       # API client library modules
│   ├── __init__.py
│   ├── api_client.py           # Base API client
│   ├── people_manager.py       # People management functions
│   ├── event_manager.py        # Event tracking functions
│   └── [other API modules]
├── tests/
│   ├── unit/                   # Unit tests for utils modules
│   └── integration/            # Integration tests with actual API
└── [notebook files]           # Interface notebooks for data engineers
```

## Development Philosophy

### Test-Driven Development (TDD)
**This is the cornerstone of our development process.** Every feature begins with a failing test.

1. **Red**: Write a failing test that describes the desired behavior
2. **Green**: Write the minimum code necessary to make the test pass
3. **Refactor**: Improve the code while keeping tests green

### Code Standards
- **Follow PYTHON_STANDARDS.md exactly** - no exceptions
- **Follow ZEN_NOTEBOOKS.md exactly** for notebook development
- **Type safety**: Use type hints throughout
- **Clean code**: Descriptive names, clear functions, proper documentation
- **No emojis**: NEVER use emojis anywhere in code or documentation

## Development Workflow

### Setting Up Environment
```bash
# Initialize development environment
devbox shell

# Install dependencies
uv install

# Start development
uv run jupyter lab
```

### TDD Process for Each API Feature

1. **Study the API**: Review cio_pipelines_api.json for the endpoint
2. **Write tests**: Create comprehensive tests for the functionality
3. **Run tests**: Verify they fail (Red)
4. **Implement**: Write minimal code to pass tests (Green)
5. **Refactor**: Clean up while maintaining green tests
6. **Update TODO.md**: Mark completed tasks and update progress
7. **Integration**: Test with actual Customer.IO API

### TODO.md Management (CRITICAL FOR SESSION CONTINUITY)

**ALWAYS maintain TODO.md as the single source of truth for project progress.** This ensures session-to-session continuity.

#### Required Actions:
1. **When completing tasks**: Update TODO.md immediately to mark items as `[x]` completed
2. **When starting new work**: Update TODO.md to show current priorities  
3. **Before ending sessions**: Ensure TODO.md accurately reflects all progress made
4. **When beginning sessions**: Review TODO.md to understand current project status

#### TODO.md Structure:
- **Current Status section**: Shows completed work and test counts
- **Phase sections**: Mark individual tasks as `[ ]` pending or `[x]` completed  
- **Next Priority**: Clearly indicate what should be worked on next
- **Files references**: Include relevant file paths for completed work

#### Session Continuity:
- TODO.md must always reflect actual code state
- Future sessions depend on accurate TODO.md to continue work
- Never leave TODO.md out of sync with actual progress

### Code Quality Commands
```bash
# Format and lint
ruff check --fix .
ruff format .

# Type checking
mypy utils/

# Run tests
pytest tests/unit/
pytest tests/integration/
```

## API Client Architecture

### Base Client (utils/api_client.py)
```python
class CustomerIOClient:
    """
    Customer.IO Data Pipelines API client.
    
    Features:
    - Authentication handling
    - Rate limiting (3000 requests per 3 seconds)
    - Error handling and retries
    - Support for US/EU regions
    - Request/response logging
    """
```

### Module Organization
- **people_manager.py**: identify, delete, suppress/unsuppress users
- **event_manager.py**: track custom and semantic events
- **object_manager.py**: manage objects and relationships
- **device_manager.py**: device registration and management
- **batch_manager.py**: batch operations

## Notebook Development

### Notebook Purpose
Notebooks serve as the **interface layer** for data engineers. They should:
- Demonstrate how to use the utils functions
- Provide clear examples with real data
- Show error handling patterns
- Include practical use cases

### Notebook Structure (Follow ZEN_NOTEBOOKS.md)
- **Clear title and purpose**
- **Setup and imports section**
- **Logical flow** from basic to advanced usage
- **Clean code cells** (≤15 lines when possible)
- **Comprehensive documentation**
- **Working examples** throughout

### Example Notebook Pattern
```python
# Notebook: 01_people_management.ipynb

# Setup
from utils.api_client import CustomerIOClient
from utils.people_manager import identify_user, delete_user

# Initialize client
client = CustomerIOClient(api_key="your_key", region="us")

# Basic usage example
user_data = {
    "userId": "user123",
    "traits": {
        "email": "user@example.com",
        "name": "John Doe"
    }
}

# Call the utils function
result = identify_user(client, user_data)
print(f"User identified: {result}")
```

## Testing Strategy

### Test Organization
```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_api_client.py
│   ├── test_people_manager.py
│   └── test_event_manager.py
└── integration/             # Tests with actual API
    ├── test_people_integration.py
    └── test_event_integration.py
```

### Test Quality Standards
- **Comprehensive coverage**: Test all functions and edge cases
- **Clear test names**: Describe exactly what is being tested
- **Mock external dependencies**: Use unittest.mock for API calls in unit tests
- **Test error conditions**: Verify proper error handling
- **Fast execution**: Tests should run quickly

## API Reference

### Customer.IO Data Pipelines API
- **Base URL**: https://cdp.customer.io/v1
- **EU Base URL**: https://cdp-eu.customer.io/v1
- **Rate Limits**: 3000 requests per 3 seconds
- **Request Limit**: 32KB per request, 500KB per batch

### Key API Categories (from cio_pipelines_api.json)
- **People Management**: identify, delete, suppress/unsuppress
- **Event Tracking**: custom events, semantic events
- **Objects & Relationships**: create, update, delete objects and relationships
- **Device Management**: register, update devices
- **Batch Operations**: bulk processing

## Security Requirements

### API Key Management
- Never hardcode credentials in notebooks or code
- Use environment variables or secure configuration
- Document credential setup clearly
- Support both test and production environments

### Data Privacy
- Handle PII appropriately
- Follow data retention best practices
- Implement proper logging without exposing sensitive data

## Common Commands

### Development Commands
```bash
# Run specific test file
pytest tests/unit/test_people_manager.py -v

# Run tests with coverage
pytest --cov=utils/ --cov-report=term-missing

# Check types
mypy utils/people_manager.py

# Format specific module
ruff format utils/people_manager.py
```

### Git Workflow
```bash
# Feature development
git checkout -b feature/people-management-api
# Write tests, implement, commit
git add .
git commit -m "feat: add people management API functions"
git push origin feature/people-management-api
```

## Important Guidelines

### What TO Do
- Follow TDD religiously: tests first, then implementation
- Keep functions focused and single-purpose
- Use descriptive variable and function names
- Include comprehensive docstrings
- Handle errors gracefully
- Write clean, readable code

### What NOT To Do
- Never use emojis anywhere
- Don't over-engineer solutions
- Don't create complex inheritance hierarchies
- Don't ignore the existing standards documents
- Don't hardcode credentials or configuration
- Don't write code without tests first

## Success Criteria

The project will be successful when:
1. All Customer.IO API endpoints are covered in utils modules
2. Comprehensive test coverage (unit and integration)
3. Clean, functional notebooks demonstrate all functionality
4. Code follows TDD methodology throughout
5. All code adheres to PYTHON_STANDARDS.md and ZEN_NOTEBOOKS.md
6. Ready for production use by data engineering teams

## Reference Documents

Always refer to these documents for guidance:
- **PYTHON_STANDARDS.md**: Comprehensive Python development guidelines
- **ZEN_NOTEBOOKS.md**: Clean, maintainable Jupyter notebook best practices
- **REQUIREMENTS.md**: Detailed project requirements and specifications
- **TODO.md**: Current development status and next steps
- **cio_pipelines_api.json**: Complete API specification

Remember: The goal is to create a clean, comprehensive Customer.IO API client library that data engineers can immediately use in production, with emphasis on simplicity, reliability, and clear documentation.