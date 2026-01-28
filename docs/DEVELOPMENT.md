# Development Guide

Comprehensive guide for developers contributing to Chattr.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Debugging](#debugging)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.13+
- `uv` package manager
- Docker & Docker Compose
- Git
- Code editor (VS Code recommended)

### Initial Setup

1. **Fork the repository**:
   ```bash
   # On GitHub, click Fork button
   ```

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/chattr.git
   cd chattr
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/AlphaSphereDotAI/chattr.git
   ```

4. **Install dependencies**:
   ```bash
   uv sync
   ```

5. **Install development tools**:
   ```bash
   uv run pre-commit install
   ```

6. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Development Setup

### Virtual Environment

UV automatically manages virtual environments:

```bash
# Sync dependencies
uv sync

# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update dependencies
uv sync --upgrade
```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. Open project in PyCharm
2. Configure Python interpreter: Settings > Project > Python Interpreter
3. Select the UV virtual environment (`.venv`)
4. Enable pytest: Settings > Tools > Python Integrated Tools > Testing

### Environment Variables

Development `.env` file:

```env
# Required
MODEL__API_KEY=your-api-key

# Model Configuration
MODEL__URL=https://api.groq.com/openai/v1
MODEL__NAME=llama3-70b-8192
MODEL__TEMPERATURE=0.0

# Database
VECTOR_DATABASE__URL=http://localhost:6333
VECTOR_DATABASE__NAME=chattr_dev

# Directories
DIRECTORY__BASE=.
DIRECTORY__ASSETS=./assets

# Debug
DEBUG=true
```

## Project Structure

```
chattr/
├── src/
│   └── chattr/
│       ├── __init__.py           # Package initialization
│       ├── __main__.py           # CLI entry point
│       └── app/
│           ├── __init__.py
│           ├── builder.py        # Main app orchestration
│           ├── runner.py         # Launch configuration
│           ├── settings.py       # Configuration management
│           ├── scheme.py         # Data models
│           └── logger.py         # Logging setup
├── tests/
│   └── test_app.py              # Test suite
├── docs/
│   ├── API.md                   # API documentation
│   ├── ARCHITECTURE.md          # System architecture
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── DEVELOPMENT.md           # This file
│   └── TROUBLESHOOTING.md       # Troubleshooting
├── assets/
│   ├── prompts/                 # Character prompts
│   ├── image/                   # Character images
│   ├── audio/                   # Generated audio
│   └── video/                   # Generated video
├── .github/
│   ├── workflows/               # CI/CD workflows
│   └── lint/                    # Linting configs
├── docker-compose.yaml          # Production compose
├── docker-compose-dev.yaml      # Development compose
├── Dockerfile                   # Container definition
├── pyproject.toml              # Project configuration
├── README.md                   # Main documentation
├── CONTRIBUTING.md             # Contribution guide
└── AGENTS.md                   # Agent guidelines
```

## Development Workflow

### Feature Development

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**:
   - Write code
   - Add tests
   - Update documentation

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Format and lint**:
   ```bash
   trunk fmt --all --no-progress
   trunk check
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

6. **Push to fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**:
   - Go to GitHub
   - Click "New Pull Request"
   - Fill in PR template

### Keeping Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge into main
git checkout main
git merge upstream/main

# Update your feature branch
git checkout feature/your-feature
git rebase main
```

### Running Locally

#### Development Mode

```bash
# Run with hot reload
uv run chattr
```

#### Docker Development

```bash
# Build local image
docker build -t chattr:dev .

# Run with docker-compose
docker-compose -f docker-compose-dev.yaml up
```

## Coding Standards

### Python Style

Follow PEP 8 with these specifics:

- **Line length**: 88 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes preferred
- **Type hints**: Required for all functions
- **Docstrings**: Google style format

### Type Hints

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def function(param: str, optional: int | None = None) -> dict[str, str]:
    """Function with proper type hints."""
    return {"result": param}
```

### Docstrings

```python
def complex_function(param: str, count: int = 10) -> list[str]:
    """
    Brief one-line description.

    Detailed description explaining what the function does,
    why it exists, and any important details.

    Args:
        param: Description of param parameter.
        count: Description of count parameter. Defaults to 10.

    Returns:
        List of processed strings.

    Raises:
        ValueError: When param is empty.
        TypeError: When count is negative.

    Examples:
        >>> complex_function("test", 5)
        ['test1', 'test2', 'test3', 'test4', 'test5']
    """
    if not param:
        raise ValueError("param cannot be empty")
    return [f"{param}{i}" for i in range(count)]
```

### Import Organization

```python
# Standard library
from pathlib import Path
from typing import TYPE_CHECKING

# Third-party
from pydantic import BaseModel
from gradio import Blocks

# Local
from chattr.app.settings import Settings
from chattr.app.logger import logger

if TYPE_CHECKING:
    from agno.agent import Agent
```

### Error Handling

```python
from gradio import Error


def risky_operation() -> None:
    """Demonstrate proper error handling."""
    try:
        # Risky code
        result = perform_operation()
    except ValueError as e:
        logger.error("Value error occurred: %s", e)
        raise Error(f"Invalid value: {e}") from e
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise
    else:
        logger.info("Operation succeeded")
    finally:
        cleanup()
```

## Testing

### Writing Tests

```python
import pytest
from chattr.app.settings import Settings


def test_settings_initialization():
    """Test that Settings can be initialized with defaults."""
    settings = Settings()
    assert settings is not None
    assert settings.model.temperature == 0.0


def test_invalid_temperature_raises_error():
    """Test that invalid temperature raises validation error."""
    with pytest.raises(ValueError):
        Settings(model={"temperature": 2.0})


@pytest.fixture
def mock_settings():
    """Fixture providing mock settings."""
    return Settings(
        model={
            "url": "http://localhost:8000",
            "name": "test-model",
            "api_key": "test-key"
        }
    )


def test_with_fixture(mock_settings):
    """Test using fixture."""
    assert mock_settings.model.name == "test-model"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_app.py

# Run specific test
pytest tests/test_app.py::test_settings_initialization

# Run with coverage
pytest --cov=chattr --cov-report=html

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf

# Run with markers
pytest -m "slow"
```

### Test Organization

```
tests/
├── unit/
│   ├── test_settings.py
│   ├── test_builder.py
│   └── test_logger.py
├── integration/
│   ├── test_agent.py
│   └── test_tools.py
└── fixtures/
    └── conftest.py
```

### Coverage Goals

- Aim for 80%+ coverage
- 100% for critical paths
- Test edge cases
- Test error conditions

## Debugging

### Debug Mode

Enable debug mode:

```python
from chattr.app.settings import Settings

settings = Settings(debug=True)
```

### Logging

```python
from chattr.app.logger import logger

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception with traceback")
```

### Interactive Debugging

#### Using pdb

```python
import pdb

def function():
    pdb.set_trace()  # Breakpoint
    # Code continues
```

#### Using ipdb

```bash
uv add --dev ipdb
```

```python
import ipdb

def function():
    ipdb.set_trace()  # Better breakpoint
```

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Chattr",
      "type": "python",
      "request": "launch",
      "module": "chattr",
      "console": "integratedTerminal",
      "env": {
        "MODEL__API_KEY": "your-key",
        "DEBUG": "true"
      }
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

## Documentation

### Code Documentation

- All public APIs must have docstrings
- Use Google-style format
- Include examples for complex functions
- Document exceptions

### README Updates

When adding features:
1. Update feature list
2. Add usage examples
3. Update configuration tables
4. Add to table of contents

### API Documentation

Update `docs/API.md` when:
- Adding new endpoints
- Changing parameters
- Modifying return types
- Adding examples

### Architecture Documentation

Update `docs/ARCHITECTURE.md` when:
- Adding new components
- Changing data flow
- Modifying design decisions

## Release Process

### Version Bumping

Chattr uses semantic versioning (MAJOR.MINOR.PATCH):

```bash
# Update version in pyproject.toml
# Then commit
git commit -m "chore: bump version to 0.0.101"
```

### Building

```bash
# Build package
uv build

# Verify build
ls dist/
```

### Testing Release

```bash
# Install from dist
uv pip install dist/chattr-0.0.101-py3-none-any.whl

# Test
chattr --version
```

### Creating Release

1. Tag the release:
   ```bash
   git tag -a v0.0.101 -m "Release v0.0.101"
   git push origin v0.0.101
   ```

2. GitHub Actions will:
   - Run tests
   - Build package
   - Create release
   - Publish to PyPI (if configured)

### Changelog

Update CHANGELOG.md:

```markdown
## [0.0.101] - 2024-01-28

### Added
- New feature X
- Support for Y

### Changed
- Improved Z performance
- Updated documentation

### Fixed
- Bug in W
- Issue with V

### Security
- Fixed vulnerability in U
```

## Best Practices

### Code Review

- Review your own code first
- Test thoroughly
- Keep PRs small and focused
- Respond to feedback promptly
- Be respectful and constructive

### Git Commits

- Use conventional commits
- Keep commits atomic
- Write clear commit messages
- Reference issues when applicable

### Performance

- Profile before optimizing
- Use appropriate data structures
- Minimize I/O operations
- Cache when beneficial
- Use async for I/O-bound tasks

### Security

- Never commit secrets
- Validate all inputs
- Use type hints
- Handle errors properly
- Keep dependencies updated

## Tools and Commands

### Linting and Formatting

```bash
# Format code
trunk fmt --all --no-progress

# Check formatting
trunk check

# Auto-fix issues
trunk check --fix
```

### Type Checking

```bash
# Run mypy
mypy src/

# Check specific file
mypy src/chattr/app/builder.py
```

### Dependency Management

```bash
# Add dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Remove dependency
uv remove package-name

# Update dependencies
uv sync --upgrade

# Show dependency tree
uv pip tree
```

### Useful Scripts

```bash
# Run all checks
./scripts/check.sh

# Run tests with coverage
./scripts/test.sh

# Build Docker image
./scripts/build.sh

# Release new version
./scripts/release.sh
```

## Resources

- [Python Style Guide](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## Getting Help

- Read [CONTRIBUTING.md](../CONTRIBUTING.md)
- Check [Troubleshooting Guide](TROUBLESHOOTING.md)
- Ask on GitHub Discussions
- Email: mohamed.hisham.abdelzaher@gmail.com

Happy coding! 🚀
