# Development Guide

This guide covers everything you need to know to contribute to Chattr development.

## Development Setup

### Prerequisites

- Python 3.13
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Git
- Docker (optional, for testing containers)
- Redis (for local testing)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/AlphaSphereDotAI/chattr.git
cd chattr

# Install dependencies with development tools
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Development Dependencies

The development dependencies include:

- **pre-commit**: Git hooks for code quality
- **pytest**: Testing framework with emoji and markdown support
- **ruff**: Fast Python linter and formatter
- **trunk**: Code quality tools
- **uv-build**: Build system
- **doppler-env**: Environment management
- **ty**: Type checking utilities

## Project Structure

```
chattr/
├── src/
│   └── chattr/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       └── app/
│           ├── __init__.py
│           ├── builder.py       # Main App class
│           ├── logger.py        # Logging
│           ├── runner.py        # App instance
│           ├── scheme.py        # Data schemas
│           └── settings.py      # Configuration
├── tests/
│   └── test_app.py              # Application tests
├── docs/                        # Documentation
├── assets/                      # Generated assets
├── mcp.json                     # MCP configuration
├── pyproject.toml              # Project metadata
├── AGENTS.md                    # Agent guidelines
└── README.md                    # Project overview
```

## Code Style Guidelines

### General Principles

- **Line length**: 88 characters (Black standard)
- **Indentation**: 4 spaces
- **Quote style**: Double quotes (`"`)
- **File encoding**: UTF-8

### Imports

Organize imports in three groups:

```python
# Standard library
from pathlib import Path
from typing import TYPE_CHECKING

# Third-party
from agno.agent import Agent
from gradio import ChatInterface

# Local
from chattr.app.settings import Settings
```

Use `TYPE_CHECKING` for type-only imports:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gradio import Blocks
```

### Type Hints

Use type hints for all public APIs:

```python
def process_message(text: str, user_id: int) -> dict[str, any]:
    """Process a user message."""
    return {"response": text, "user": user_id}

async def generate_response(message: str) -> AsyncGenerator[str, None]:
    """Generate streaming response."""
    yield "response"
```

### Naming Conventions

- **Functions/Methods**: `snake_case`
  ```python
  def calculate_score():
      pass
  ```

- **Variables**: `snake_case`
  ```python
  user_count = 10
  ```

- **Classes**: `PascalCase`
  ```python
  class MessageProcessor:
      pass
  ```

- **Constants**: `UPPER_CASE`
  ```python
  MAX_RETRIES = 3
  ```

- **Private**: `_leading_underscore`
  ```python
  def _internal_helper():
      pass
  ```

### Documentation

Use Google-style docstrings:

```python
def process_message(text: str, metadata: dict) -> str:
    """Process a user message with metadata.

    Args:
        text: The message text to process
        metadata: Additional metadata dictionary

    Returns:
        Processed message string

    Raises:
        ValueError: If text is empty
        ValidationError: If metadata is invalid

    Example:
        >>> process_message("hello", {"user_id": 1})
        "Processed: hello"
    """
    if not text:
        raise ValueError("Text cannot be empty")
    return f"Processed: {text}"
```

### Async/Await

Use async for I/O operations:

```python
async def fetch_data() -> dict:
    """Fetch data from external service."""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

async def stream_response() -> AsyncGenerator[str, None]:
    """Stream response data."""
    for chunk in data:
        yield chunk
        await asyncio.sleep(0.1)
```

### Error Handling

Use specific exception types:

```python
from gradio import Error
from pydantic import ValidationError

def process_input(data: dict) -> None:
    """Process user input."""
    try:
        validated = Model(**data)
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise Error("Invalid input provided")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise Error("An unexpected error occurred")
```

## Development Commands

### Building

```bash
# Build distributions
uv build

# Output: dist/chattr-*.whl and dist/chattr-*.tar.gz
```

### Linting and Formatting

```bash
# Auto-format code
trunk fmt --all --no-progress

# Run all linters
trunk check

# Run specific linter
ruff check src/
```

### Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_app.py::test_app

# Run with coverage
pytest --cov=chattr --cov-report=html
```

### Running Locally

```bash
# Using uv
uv run chattr

# Or if installed
chattr

# With specific Python version
uv run --python 3.13 chattr
```

## Testing

### Test Structure

Tests are located in the `tests/` directory:

```python
# tests/test_app.py
from chattr.app.builder import App
from chattr.app.settings import Settings

def test_app():
    """Test that app initializes correctly."""
    settings = Settings()
    app = App(settings)
    assert app is not None
    assert app.settings == settings
```

### Writing Tests

Follow these guidelines:

1. **Test naming**: Use `test_` prefix
   ```python
   def test_feature_works():
       pass
   ```

2. **Arrange-Act-Assert**: Structure tests clearly
   ```python
   def test_message_processing():
       # Arrange
       message = "test message"
       processor = MessageProcessor()
       
       # Act
       result = processor.process(message)
       
       # Assert
       assert result == "Processed: test message"
   ```

3. **Mock external dependencies**:
   ```python
   from unittest.mock import AsyncMock, patch
   
   @patch('chattr.app.builder.MultiMCPTools')
   def test_with_mock(mock_mcp):
       mock_mcp.return_value = AsyncMock()
       # Test code
   ```

4. **Test async functions**:
   ```python
   import pytest
   
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_function()
       assert result is not None
   ```

### Test Coverage

Aim for high test coverage:

```bash
# Generate coverage report
pytest --cov=chattr --cov-report=term-missing

# Generate HTML report
pytest --cov=chattr --cov-report=html
# Open htmlcov/index.html
```

## Git Workflow

### Branching

- `main`: Stable release branch
- `develop`: Development branch
- `feature/*`: Feature branches
- `fix/*`: Bug fix branches

### Commit Messages

Use conventional commits:

```
feat: add video generation support
fix: correct Redis connection handling
docs: update configuration guide
test: add tests for agent setup
refactor: simplify tool loading logic
style: format code with ruff
chore: update dependencies
```

### Pre-commit Hooks

Pre-commit hooks run automatically:

```bash
# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

## Debugging

### Logging

Enable debug logging:

```python
# In your code
from chattr.app.settings import logger

logger.setLevel("DEBUG")
logger.debug("Debug information")
```

### Debug Mode

The agent has debug mode enabled by default:

```python
Agent(
    ...,
    debug_mode=True,  # Enables detailed logging
    save_response_to_file="agno/response.txt",  # Saves responses
)
```

### Interactive Debugging

Use Python debugger:

```python
import pdb

def function_to_debug():
    pdb.set_trace()  # Breakpoint
    # Code to debug
```

Or use IDE debugging features in VSCode, PyCharm, etc.

## Adding Features

### Adding a New Character

1. **Modify agent description**:
   ```python
   # In src/chattr/app/builder.py
   Agent(
       description="Character description",
       instructions=["Character instructions"],
   )
   ```

2. **Test the character**:
   ```python
   def test_new_character():
       # Test character responses
       pass
   ```

### Adding a New Tool

1. **Create MCP server** or local tool
2. **Add to mcp.json**:
   ```json
   {
     "mcp_servers": [
       {
         "name": "new-tool",
         "type": "url",
         "url": "http://localhost:8003/gradio_api/mcp/sse"
       }
     ]
   }
   ```

3. **Test tool integration**:
   ```python
   def test_new_tool():
       # Test tool is loaded and available
       pass
   ```

### Adding Configuration Options

1. **Update settings**:
   ```python
   # In src/chattr/app/settings.py
   class Settings(BaseSettings):
       new_option: str = "default_value"
   ```

2. **Update documentation**:
   - Add to `docs/configuration.md`
   - Update `README.md` if needed

3. **Add tests**:
   ```python
   def test_new_configuration():
       settings = Settings(new_option="test")
       assert settings.new_option == "test"
   ```

## Code Review

Before submitting:

1. **Run tests**: `pytest`
2. **Run linters**: `trunk check`
3. **Format code**: `trunk fmt --all --no-progress`
4. **Update docs**: If adding features
5. **Write tests**: For new functionality

## Continuous Integration

The project uses GitHub Actions for CI:

- **Build**: Verifies project builds
- **Test**: Runs test suite
- **Lint**: Checks code quality
- **CodeQL**: Security analysis

View workflow files in `.github/workflows/`.

## Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md**
3. **Create release tag**:
   ```bash
   git tag -a v0.0.107 -m "Release v0.0.107"
   git push origin v0.0.107
   ```
4. **GitHub Actions** will build and publish

## Useful Resources

- [Agno Documentation](https://agno.dev)
- [Gradio Documentation](https://gradio.app/docs)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [pytest Documentation](https://docs.pytest.org)
- [Ruff Documentation](https://docs.astral.sh/ruff)

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions in GitHub Discussions
- **Contributing**: See `CONTRIBUTING.md` for guidelines

## Common Development Tasks

### Reset Development Environment

```bash
# Remove virtual environment
rm -rf .venv

# Reinstall dependencies
uv sync
```

### Update Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Update specific package
uv add agno@latest
```

### Clean Build Artifacts

```bash
# Remove build artifacts
rm -rf dist/ build/ *.egg-info

# Remove cached files
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Profile Performance

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```
