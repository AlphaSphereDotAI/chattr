# Contributing to Chattr

First off, thank you for considering contributing to Chattr! It's people like you that make Chattr such a great tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to mohamed.hisham.abdelzaher@gmail.com.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** to demonstrate the steps
- **Describe the behavior you observed** and what behavior you expected
- **Include screenshots** if relevant
- **Include your environment details** (OS, Python version, Docker version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most Chattr users
- **List any similar features** in other applications if applicable

### Your First Code Contribution

Unsure where to begin? You can start by looking through `beginner` and `help-wanted` issues:

- **Beginner issues** - issues that should only require a few lines of code
- **Help wanted issues** - issues that are a bit more involved

### Pull Requests

The process described here has several goals:
- Maintain Chattr's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible Chattr
- Enable a sustainable system for maintainers to review contributions

## Development Setup

### Prerequisites

- Python 3.13+
- `uv` package manager
- Docker and Docker Compose (for integration testing)
- Git

### Setup Steps

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/chattr.git
   cd chattr
   ```

2. **Set up the development environment**:
   ```bash
   uv sync
   ```

3. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run the application**:
   ```bash
   uv run chattr
   ```

## Pull Request Process

1. **Update documentation** with details of changes if applicable
2. **Add tests** that prove your fix is effective or that your feature works
3. **Ensure all tests pass**:
   ```bash
   pytest
   ```
4. **Run linting and formatting**:
   ```bash
   trunk fmt --all --no-progress
   trunk check
   ```
5. **Update the CHANGELOG** if you're making significant changes
6. **Create a Pull Request** with a clear title and description

### Pull Request Template

When creating a PR, please include:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Style Guidelines

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes preferred
- **Type hints**: Required for all functions
- **Docstrings**: Google style format

### Code Style

```python
"""Module docstring explaining the purpose."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def function_name(param: str, optional: int = 0) -> dict[str, any]:
    """
    Brief description of function.

    Detailed description if needed.

    Args:
        param: Description of param.
        optional: Description of optional param.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param is invalid.
    """
    return {"result": param}


class ClassName:
    """Brief description of class."""

    def __init__(self, value: str) -> None:
        """Initialize the class."""
        self.value = value

    def method_name(self) -> str:
        """Brief description of method."""
        return self.value
```

### Import Organization

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel
from gradio import Blocks

from chattr.app.settings import Settings
```

### Naming Conventions

- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private attributes**: `_leading_underscore`
- **Type variables**: `T`, `K`, `V` (short uppercase)

## Testing Guidelines

### Writing Tests

- Tests should be isolated and independent
- Use descriptive test names: `test_<what>_<condition>_<expected>`
- Use fixtures for common setup
- Mock external dependencies
- Aim for high coverage but focus on critical paths

### Test Structure

```python
import pytest
from chattr.app.builder import App


def test_app_initialization_creates_instance():
    """Test that App can be initialized."""
    from chattr.app.settings import Settings
    
    settings = Settings()
    app = App(settings)
    
    assert app is not None
    assert app.settings == settings


def test_invalid_config_raises_error():
    """Test that invalid configuration raises appropriate error."""
    with pytest.raises(ValueError):
        # Test invalid configuration
        pass


@pytest.fixture
def mock_agent():
    """Fixture providing a mock agent."""
    # Setup
    yield mock_object
    # Teardown
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_app.py

# Run with coverage
pytest --cov=chattr --cov-report=html

# Run with verbose output
pytest -v
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semi-colons, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(agent): add support for custom character prompts

Implement ability to load custom character prompts from POML files.
This allows users to create their own character personalities.

Closes #123
```

```
fix(audio): resolve audio generation timeout issue

Increase timeout for audio generation from 30s to 60s to handle
longer text responses.

Fixes #456
```

```
docs(readme): update installation instructions

Add missing step for setting up environment variables.
```

## Documentation Guidelines

### Code Documentation

- All public functions, classes, and modules must have docstrings
- Use Google-style docstring format
- Include examples for complex functions
- Document exceptions that can be raised

### README and Docs

- Keep language clear and concise
- Use code examples
- Include screenshots where helpful
- Update table of contents when adding sections
- Keep documentation in sync with code

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Issues**: Check existing issues or create a new one
- **Direct Contact**: Email mohamed.hisham.abdelzaher@gmail.com

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation

Thank you for contributing to Chattr! 🎉
