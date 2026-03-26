# Agent Guidelines for Chattr

## Build/Lint/Test Commands

### Installation

```bash
uv sync  # Install dependencies and create a virtual environment
```

### Building

```bash
uv build  # Build source and wheel distributions
```

### Linting & Formatting

```bash
uvx pre-commit run --all-files  # Primary command for all linters and formatting checks
uvx ty check  # Optional: Run all project checks and diagnostics (including type-checking)
```

### Testing

```bash
pytest  # Run all tests
pytest tests/test_app.py::test_app  # Run a specific test
```

### Dependency Management

```bash
uv lock  # Update the lockfile
uv lock --check  # Verify if the lockfile is up to date
```

## Code Style Guidelines

### General

- **Python version**: Requires Python **3.14.3** or higher (pre-release compatibility)
- **Line length**: 88 characters (Black/Ruff standard)
- **Indentation**: 4 spaces
- **Quote style**: Double quotes (`"`)
- **File encoding**: UTF-8

### Imports

- Use `from __future__ import annotations` at the top of every module
- Group imports: standard library, third-party, local
- Use `TYPE_CHECKING` for imports only needed for type hints
- Use `isort` compatible grouping (already handled by Ruff)

### Type Hints

- Use type hints for all function parameters and return values
- Use `Self` (from `typing`) for methods returning the same class instance
- Use **built-in generics** (`list[int]`, `dict[str, Any]`) instead of `typing.List` or `typing.Dict`
- Use the **pipe operator** (`|`) for unions (e.g., `str | None` instead of `Optional[str]`)
- Use `Annotated` for complex type hints with metadata (e.g., `Annotated[T, Field(...)]`)
- Use `Path` from `pathlib` for all file system paths

### Naming Conventions

- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private attributes**: `_leading_underscore`

### Error Handling

- Use specific exception types (e.g., `OSError`, `ValueError`, `ValidationError`)
- Log errors with appropriate levels (`logger.error`, `logger.warning`)
- Raise `gradio.Error` for errors that should be displayed to the user
- Use `try/except/finally` blocks to ensure resources (like MCP connections) are closed

### Async/Await

- The core application and MCP tools are heavily asynchronous
- Use `async def` for coroutines and `await` for I/O-bound operations
- Return `AsyncGenerator` for streaming data (e.g., in `Agent` responses)

### Documentation

- Use docstrings for all public functions, classes, and modules
- Follow **Google-style** docstring format
- Document parameters (`Args`), return values (`Returns`), and raised exceptions (`Raises`)

### Logging

- Import `logger` from `chattr.app.logger` (or re-exported from `chattr.app.settings`)
- Use appropriate log levels: `debug`, `info`, `warning`, `error`
- Include relevant context in log messages for easier debugging

## Core Frameworks & Tools

- **Agents**: [Agno](https://github.com/agno/agno) (formerly Phidata) for multi-agent orchestration
- **Configuration**: [Pydantic Settings](https://docs.pydantic.dev/latest/usage/pypy/settings/)
- **UI**: [Gradio](https://gradio.app/) for the chat interface
- **Prompts**: [Poml](https://github.com/AlphaSphereDotAI/poml) for template-based prompt engineering
- **Task Runner**: [Ty](https://github.com/AlphaSphereDotAI/ty) for project checks and diagnostics

## Testing Guidelines

- Use `pytest` framework
- Test functions should be named `test_*`
- Use descriptive assertions
- Mock external dependencies when needed (especially MCP services)
