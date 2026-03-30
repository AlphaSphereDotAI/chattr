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
uvx pre-commit run --all-files  # Run all linters and formatting checks
```

### Testing

```bash
pytest  # Run all tests
pytest tests/test_app.py::test_app  # Run single test
```

## Code Style Guidelines

### General

- **Python Version**: >= 3.14.3
- **Line length**: 88 characters
- **Indentation**: 4 spaces
- **Quote style**: Double quotes (`"`)
- **File encoding**: UTF-8

### Agentic Architecture

- **Orchestration**: Use `Agno` for multi-agent systems and task orchestration.
- **Prompts**: Use `Poml` for defining prompt templates in `assets/prompts`.
- **Integrations**: Use `MCP` (Model Context Protocol) for external tool integrations and asset generation (e.g., audio, video).
- **Safety**: Use Agno guardrails (e.g., `PIIDetectionGuardrail`, `PromptInjectionGuardrail`) to ensure agent behavior integrity.
- **Configuration**: Use `Pydantic-Settings` for application settings and environment variable management.

### Imports

- Group imports: standard library, third-party, and local modules.
- Use `from __future__ import annotations` for forward-looking type hints.
- Use `TYPE_CHECKING` for conditional imports to avoid circular dependencies.

### Type Hints

- Use type hints for all function parameters and return values.
- **Modern Types**: Prefer built-in types for generics (e.g., `list[str]`, `dict[str, int]`) over `typing.List` or `typing.Dict`.
- Use `Self` for methods returning the same class instance.
- Use `Path` from `pathlib` for file paths.

### Naming Conventions

- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private attributes**: `_leading_underscore`

### Error Handling

- Use specific exception types (e.g., `OSError`, `ValueError`, `ValidationError`).
- Log errors with appropriate levels (`logger.error`, `logger.warning`).
- Raise `Error` from `gradio` for user-facing errors.
- Use `try/except` blocks with meaningful error messages.

### Async/Await

- Use `async def` for coroutines.
- Use `await` for all async operations.
- Return `AsyncGenerator` for streaming responses from agents.

### Documentation

- Use docstrings for all public functions, classes, and modules.
- Follow Google-style docstring format.
- Document parameters, return values, and exceptions.

### Logging

- Import `logger` from `chattr.app.settings` (or `chattr.app.logger`).
- Use appropriate log levels: `debug`, `info`, `warning`, `error`.
- Use `rich` for enhanced console output and log formatting.

### Testing Guidelines

- Use `pytest` framework.
- Test functions named `test_*`.
- Use descriptive assertions.
- Mock external dependencies when needed.
