# Agent Guidelines for Chattr

## Build/Lint/Test Commands

### Installation
```bash
uv sync  # Install dependencies
```

### Building
```bash
uv build  # Build source and wheel distributions
```

### Linting & Formatting
```bash
trunk fmt --all --no-progress  # Auto-format code
trunk check  # Run all linters and checks
```

### Testing
```bash
pytest  # Run all tests
pytest tests/test_app.py::test_app  # Run single test
```

## Code Style Guidelines

### General
- **Line length**: 88 characters
- **Indentation**: 4 spaces
- **Quote style**: Double quotes (`"`)
- **File encoding**: UTF-8

### Imports
- Use `from __future__ import annotations` when needed
- Group imports: standard library, third-party, local
- Use `TYPE_CHECKING` for conditional imports
- Combine as imports: `from typing import Dict, List` → `from typing import Dict, List`

### Type Hints
- Use type hints for all function parameters and return values
- Use `Self` for methods returning the same class instance
- Use `Sequence`, `list`, `dict` instead of bare generics
- Use `Path` from `pathlib` for file paths

### Naming Conventions
- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private attributes**: `_leading_underscore`

### Error Handling
- Use specific exception types (e.g., `OSError`, `ValueError`, `ValidationError`)
- Log errors with appropriate levels (`logger.error`, `logger.warning`)
- Raise `Error` from gradio for user-facing errors
- Use try/except blocks with meaningful error messages

### Async/Await
- Use `async def` for coroutines
- Use `await` for async operations
- Return `AsyncGenerator` for streaming responses

### Documentation
- Use docstrings for all public functions, classes, and modules
- Follow Google-style docstring format
- Document parameters, return values, and exceptions

### Logging
- Import logger from module settings
- Use appropriate log levels: `debug`, `info`, `warning`, `error`
- Include relevant context in log messages

### Testing Guidelines
- Use `pytest` framework
- Test functions named `test_*`
- Use descriptive assertions
- Mock external dependencies when needed
