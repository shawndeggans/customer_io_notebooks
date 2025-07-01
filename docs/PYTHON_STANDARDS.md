# Python Development Guidelines 2024-2025

A comprehensive guide for modern Python development with Test-Driven Development, strict type safety, and functional programming principles.

## Core Philosophy: Test-Driven Development

**Test-Driven Development (TDD) is the cornerstone of our development process.** Every feature begins with a failing test that defines the expected behavior. This approach ensures our code is testable, well-designed, and meets requirements from the start.

### The TDD Cycle

1. **Red**: Write a failing test that describes the desired behavior
2. **Green**: Write the minimum code necessary to make the test pass
3. **Refactor**: Improve the code while keeping tests green

```python
# Step 1: Red - Write failing test
def test_calculate_discount_for_premium_user():
    user = User(username="alice", is_premium=True)
    order = Order(total=100.0)
    
    discount = calculate_discount(user, order)
    
    assert discount == 10.0  # 10% for premium users

# Step 2: Green - Minimal implementation
def calculate_discount(user: User, order: Order) -> float:
    if user.is_premium:
        return order.total * 0.1
    return 0.0

# Step 3: Refactor - Improve design
from decimal import Decimal
from typing import Protocol

class DiscountStrategy(Protocol):
    def calculate(self, order: Order) -> Decimal: ...

@dataclass(frozen=True)
class PremiumDiscount:
    rate: Decimal = Decimal("0.1")
    
    def calculate(self, order: Order) -> Decimal:
        return order.total * self.rate
```

## Project Structure

### Modern Python Project Layout

Use the **src layout** for better import isolation and testing:

```
my-project/
├── pyproject.toml          # Single source of truth
├── README.md
├── LICENSE
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── __main__.py    # Entry point
│       ├── core/
│       │   ├── __init__.py
│       │   └── domain.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── api.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_domain.py
│   ├── integration/
│   │   └── test_api.py
│   └── e2e/
│       └── test_workflows.py
├── docs/
│   ├── mkdocs.yml
│   └── index.md
└── .venv/                  # Virtual environment
```

### Configuration: pyproject.toml

All configuration in a single file:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-package"
version = "0.1.0"
description = "A modern Python package"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "your.email@example.com"}]
dependencies = [
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
    "structlog>=24.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.12.0",
    "mypy>=1.8.0",
    "ruff>=0.1.9",
    "pre-commit>=3.6.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

## Type Safety with mypy

### Strict Mode Configuration

Enable maximum type safety from the start:

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_any_generics = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Per-module overrides for gradual adoption
[mypy-tests.*]
disallow_untyped_defs = false
```

### Type Hints Best Practices

#### Use Modern Python 3.11+ Features

```python
from typing import Self, TypeAlias, assert_never
from collections.abc import Sequence, Mapping

# Type aliases for clarity
UserId: TypeAlias = int
Username: TypeAlias = str

# Self type for fluent interfaces
class QueryBuilder:
    def where(self, condition: str) -> Self:
        self._conditions.append(condition)
        return self
    
    def order_by(self, field: str) -> Self:
        self._order = field
        return self

# TypedDict for structured data
from typing import TypedDict, Required, NotRequired

class UserData(TypedDict):
    id: Required[int]
    username: Required[str]
    email: Required[str]
    avatar_url: NotRequired[str]
```

#### Prefer Protocols Over ABCs

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Persistable(Protocol):
    def save(self) -> None: ...
    def delete(self) -> None: ...
    
class User:
    def save(self) -> None:
        # Implementation
        pass
    
    def delete(self) -> None:
        # Implementation
        pass

# User satisfies Persistable without inheritance
def persist_all(items: Sequence[Persistable]) -> None:
    for item in items:
        item.save()
```

## Testing with pytest

### Test Organization

```python
# tests/conftest.py
import pytest
from typing import AsyncGenerator
import structlog

@pytest.fixture(autouse=True)
def reset_structlog():
    """Reset structlog for each test."""
    structlog.clear_threadlocal()
    structlog.configure(
        processors=[structlog.testing.LogCapture()],
        cache_logger_on_first_use=True,
    )

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# tests/unit/test_user_service.py
import pytest
from unittest.mock import AsyncMock

class TestUserService:
    """Test user service functionality."""
    
    @pytest.fixture
    def user_service(self, mock_repository):
        return UserService(repository=mock_repository)
    
    @pytest.fixture
    def mock_repository(self):
        repo = AsyncMock()
        repo.find_by_id.return_value = None
        return repo
    
    async def test_get_user_returns_none_when_not_found(
        self,
        user_service: UserService,
        mock_repository: AsyncMock,
    ):
        # Given
        user_id = 123
        mock_repository.find_by_id.return_value = None
        
        # When
        result = await user_service.get_user(user_id)
        
        # Then
        assert result is None
        mock_repository.find_by_id.assert_called_once_with(user_id)
```

### Behavior-Driven Testing

```python
@pytest.mark.asyncio
async def test_user_registration_workflow():
    """
    Given: A new user registration request
    When: The user provides valid credentials
    Then: The user should be created and a welcome email sent
    """
    # Given
    registration_data = UserRegistration(
        username="newuser",
        email="newuser@example.com",
        password="SecurePass123!"
    )
    
    # When
    async with TestClient() as client:
        response = await client.post("/api/register", json=registration_data.dict())
    
    # Then
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    
    # Verify welcome email was sent
    email_service = get_email_service()
    assert email_service.send.called_once()
    assert email_service.send.call_args[0][0] == "newuser@example.com"
```

### Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(
    st.lists(st.integers(), min_size=1),
    st.integers(min_value=0, max_value=100)
)
def test_paginate_returns_correct_page_size(items: list[int], page_size: int):
    """Pagination should never return more items than page_size."""
    paginator = Paginator(items, page_size=page_size or 1)
    
    for page in paginator:
        assert len(page) <= (page_size or 1)
```

## Modern Async/Await Patterns

### Structured Concurrency with TaskGroup

```python
from typing import Any
import asyncio
from contextlib import asynccontextmanager

class DataProcessor:
    def __init__(self, config: Config):
        self.config = config
        self._shutdown = False
    
    async def process_batch(self, items: list[dict[str, Any]]) -> list[Result]:
        """Process items concurrently with proper error handling."""
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self._process_item(item))
                for item in items
            ]
        
        # All tasks completed successfully
        return [task.result() for task in tasks]
    
    async def _process_item(self, item: dict[str, Any]) -> Result:
        async with asyncio.timeout(30.0):
            return await self._transform(item)
```

### Resource Management

```python
@asynccontextmanager
async def managed_connection(url: str) -> AsyncGenerator[Connection, None]:
    """Properly manage async resources."""
    conn = await create_connection(url)
    try:
        yield conn
    finally:
        await conn.close()

# Usage
async def fetch_data(url: str) -> list[dict[str, Any]]:
    async with managed_connection(url) as conn:
        return await conn.fetch_all("SELECT * FROM users")
```

### Error Handling in Async Code

```python
from typing import TypeVar, Awaitable
from functools import wraps
import structlog

T = TypeVar('T')
logger = structlog.get_logger()

def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
):
    """Retry async operations with exponential backoff."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = backoff_factor ** attempt
                        logger.warning(
                            "Operation failed, retrying",
                            attempt=attempt + 1,
                            delay=delay,
                            error=str(e)
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error("Max retries exceeded", error=str(e))
            
            raise last_exception
        
        return wrapper
    return decorator
```

## Functional Programming Principles

### Immutability First

```python
from dataclasses import dataclass, replace
from typing import Self

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
    
    def add(self, other: Self) -> Self:
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: Decimal) -> Self:
        return Money(self.amount * factor, self.currency)

# Immutable updates
original = Money(Decimal("100.00"), "USD")
with_tax = original.multiply(Decimal("1.08"))  # New instance
```

### Pure Functions and Composition

```python
from functools import partial
from typing import Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

def compose(f: Callable[[U], V], g: Callable[[T], U]) -> Callable[[T], V]:
    """Function composition: (f ∘ g)(x) = f(g(x))"""
    return lambda x: f(g(x))

# Pure transformation functions
def normalize_text(text: str) -> str:
    return text.strip().lower()

def remove_punctuation(text: str) -> str:
    return ''.join(c for c in text if c.isalnum() or c.isspace())

def tokenize(text: str) -> list[str]:
    return text.split()

# Compose pipeline
process_text = compose(
    tokenize,
    compose(remove_punctuation, normalize_text)
)

# Usage
tokens = process_text("  Hello, World!  ")  # ["hello", "world"]
```

### Functional Error Handling

```python
from typing import Generic, TypeVar, Union, Callable
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

Result = Union[Ok[T], Err[E]]

def parse_int(value: str) -> Result[int, str]:
    """Parse string to int, returning Result."""
    try:
        return Ok(int(value))
    except ValueError:
        return Err(f"'{value}' is not a valid integer")

def divide(a: int, b: int) -> Result[float, str]:
    """Safe division that returns Result."""
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

# Chaining operations
def calculate(a: str, b: str) -> Result[float, str]:
    match parse_int(a):
        case Err(e):
            return Err(e)
        case Ok(val_a):
            match parse_int(b):
                case Err(e):
                    return Err(e)
                case Ok(val_b):
                    return divide(val_a, val_b)
```

## Error Handling Patterns

### Custom Exception Hierarchy

```python
class AppError(Exception):
    """Base exception for application errors."""
    
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code or self.__class__.__name__

class ValidationError(AppError):
    """Raised when validation fails."""
    
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field

class NotFoundError(AppError):
    """Raised when resource is not found."""
    
    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, code="NOT_FOUND")
        self.resource = resource
        self.identifier = identifier
```

### Structured Logging

```python
import structlog
from typing import Any

logger = structlog.get_logger()

class UserService:
    async def create_user(self, data: UserCreate) -> User:
        log = logger.bind(
            operation="create_user",
            username=data.username,
            email=data.email
        )
        
        try:
            log.info("Creating new user")
            
            # Validate
            if await self._user_exists(data.email):
                log.warning("User already exists")
                raise ValidationError(
                    f"User with email {data.email} already exists",
                    field="email"
                )
            
            # Create user
            user = await self._repository.create(data)
            
            log.info("User created successfully", user_id=user.id)
            return user
            
        except Exception as e:
            log.error("Failed to create user", error=str(e))
            raise
```

## Code Quality Tools

### Ruff Configuration

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "ARG",  # flake8-unused-arguments
    "SIM",  # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["ARG001"]  # unused arguments okay in tests
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, types-requests]
        args: [--strict]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
```

## Common Anti-Patterns to Avoid

### Anti-Pattern: Mutable Default Arguments

```python
# Bad
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)  # Modifies shared default list!
    return items

# Good
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

### Anti-Pattern: Overly Broad Exception Handling

```python
# Bad
try:
    result = risky_operation()
except Exception:  # Too broad!
    return None

# Good
try:
    result = risky_operation()
except (ValueError, KeyError) as e:
    logger.error("Operation failed", error=str(e), exc_info=True)
    raise OperationError(f"Failed to complete operation: {e}") from e
```

### Anti-Pattern: Testing Implementation Details

```python
# Bad - Testing private methods
def test_user_service_private_method():
    service = UserService()
    result = service._validate_email("test@example.com")  # Don't test private methods
    assert result is True

# Good - Test public behavior
def test_user_service_creates_user_with_valid_email():
    service = UserService()
    user = service.create_user(UserCreate(
        username="testuser",
        email="test@example.com"
    ))
    assert user.email == "test@example.com"
```

### Anti-Pattern: Blocking the Event Loop

```python
# Bad - Blocks event loop
async def fetch_data():
    response = requests.get("https://api.example.com")  # Blocking!
    return response.json()

# Good - Non-blocking
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()
```

## Development Workflow

### Setup New Project

```bash
# Create project structure
mkdir my-project && cd my-project
git init

# Initialize with uv (fast) or poetry
uv init
uv add pydantic httpx structlog
uv add --dev pytest pytest-cov pytest-asyncio mypy ruff

# Setup pre-commit
pre-commit install

# Create initial structure
mkdir -p src/my_package tests/unit docs
touch src/my_package/__init__.py
touch tests/conftest.py
```

### Daily Development Cycle

1. **Write failing test first**
2. **Implement minimal code to pass**
3. **Refactor while keeping tests green**
4. **Run type checker**: `mypy src/`
5. **Format and lint**: `ruff check --fix . && ruff format .`
6. **Run tests with coverage**: `pytest --cov=src/ --cov-report=term-missing`
7. **Commit with conventional commits**: `git commit -m "feat: add user authentication"`

## Summary

This guide emphasizes:

- **Test-First Development**: Every feature starts with a test
- **Type Safety**: Leverage Python's type system with mypy strict mode
- **Functional Principles**: Prefer immutability and pure functions
- **Modern Async**: Use structured concurrency and proper resource management
- **Code Quality**: Automated formatting and linting with fast tools
- **Clear Error Handling**: Structured logging and explicit error types

Remember: these guidelines are meant to improve code quality and developer experience. Apply them pragmatically, always considering your team's context and project requirements.
