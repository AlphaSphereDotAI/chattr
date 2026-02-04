# Contributing to Chattr

Thank you for your interest in contributing to Chattr! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Ways to Contribute

- 🐛 **Report bugs**: Submit detailed bug reports
- ✨ **Suggest features**: Propose new features or improvements
- 📝 **Improve documentation**: Fix typos, clarify content, add examples
- 🔧 **Submit code**: Fix bugs or implement features
- 🧪 **Write tests**: Improve test coverage
- 🎨 **Design**: Improve UI/UX

## Getting Started

### Prerequisites

- Python 3.13
- [uv](https://github.com/astral-sh/uv) package manager
- Git
- Redis (for local development)

### Development Setup

1. **Fork the repository** on GitHub

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

5. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

6. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## Development Workflow

### 1. Make Changes

- Write code following our [code style guidelines](#code-style)
- Add or update tests for your changes
- Update documentation as needed
- Keep changes focused and atomic

### 2. Test Your Changes

```bash
# Run tests
pytest

# Run linters
trunk check

# Format code
trunk fmt --all --no-progress
```

### 3. Commit Your Changes

Use conventional commit messages:

```
feat: add video generation support
fix: correct Redis connection handling
docs: update configuration guide
test: add tests for agent setup
refactor: simplify tool loading logic
style: format code with ruff
chore: update dependencies
```

Format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 4. Push Changes

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to the GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template:
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (if applicable)

## Code Style

### Python Style

We follow these conventions:

- **PEP 8** with modifications
- **Line length**: 88 characters (Black standard)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes (`"`)
- **Type hints**: Required for all public APIs

### Code Formatting

We use automated formatters:

```bash
# Format code
trunk fmt --all --no-progress

# Check formatting
trunk check
```

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

### Type Hints

Always use type hints:

```python
def process_message(text: str, metadata: dict) -> str:
    """Process a user message."""
    return f"Processed: {text}"

async def stream_data() -> AsyncGenerator[str, None]:
    """Stream data asynchronously."""
    yield "data"
```

### Documentation

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """Short one-line description.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When arg1 is empty
    """
    pass
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Follow Arrange-Act-Assert pattern

Example:

```python
def test_message_processing():
    """Test that messages are processed correctly."""
    # Arrange
    message = "test message"
    processor = MessageProcessor()
    
    # Act
    result = processor.process(message)
    
    # Assert
    assert result == "Processed: test message"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_app.py::test_app

# Run with coverage
pytest --cov=chattr --cov-report=html

# Run with verbose output
pytest -v
```

### Test Coverage

Aim for high test coverage:

- New features should include tests
- Bug fixes should include regression tests
- Maintain or improve existing coverage

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### PR Checklist

Your PR should include:

1. **Clear description** of changes
2. **Related issue** reference (if applicable)
3. **Test coverage** for changes
4. **Documentation** updates (if needed)
5. **Screenshots** (for UI changes)

### Review Process

1. **Automated checks** will run (tests, linting, build)
2. **Maintainers** will review your code
3. **Address feedback** by pushing new commits
4. **Approval** required before merge
5. **Squash and merge** to main branch

### After Merge

- Delete your feature branch
- Update your local main branch:
  ```bash
  git checkout main
  git pull upstream main
  ```

## Reporting Issues

### Bug Reports

Include:

- **Clear title**: Describe the bug concisely
- **Description**: What happened vs. what you expected
- **Steps to reproduce**: Detailed steps to reproduce the bug
- **Environment**: OS, Python version, dependency versions
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

### Feature Requests

Include:

- **Clear title**: Describe the feature concisely
- **Use case**: Why is this feature needed?
- **Description**: Detailed description of the feature
- **Examples**: How would it work?
- **Alternatives**: Have you considered alternatives?

## Documentation

### Documentation Updates

Documentation is located in:

- `docs/`: Comprehensive guides
- `README.md`: Project overview
- Code docstrings: API documentation

### Writing Documentation

- Use clear, concise language
- Include examples
- Keep formatting consistent
- Test commands and code examples
- Update table of contents

## Release Process

Releases are managed by maintainers:

1. Version bump in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag
4. GitHub Actions builds and publishes

## Community

### Getting Help

- **GitHub Issues**: Ask questions
- **GitHub Discussions**: General discussions
- **Documentation**: Check the docs first

### Recognition

Contributors are recognized:

- Listed in release notes
- Acknowledged in `CHANGELOG.md`
- GitHub contributor graph

## License

By contributing, you agree that your contributions will be licensed under the project's license.

## Questions?

If you have questions about contributing:

1. Check this guide
2. Search existing issues
3. Ask in GitHub Discussions
4. Create a new issue

Thank you for contributing to Chattr! 🎉
