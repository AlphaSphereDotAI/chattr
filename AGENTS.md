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

### Execution

```bash
uv run chattr  # Launch the service
```

### Linting & Formatting

```bash
uvx prek run --all-files  # Run all linters and formatting checks
```

### Testing

```bash
uv run pytest  # Run all tests
uv run pytest tests/test_app.py::test_app  # Run single test
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
- Combine multiple imports from the same module (e.g., `from typing import Any, Sequence`)

### Type Hints

- Use type hints for all function parameters and return values
- Use `Self` for methods returning the same class instance
- Use `Sequence`, `list`, `dict` instead of bare generics
- Use `Path` from `pathlib` for file paths
- Use `Pydantic` models for data validation and configuration

### Naming Conventions

- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private attributes**: `_leading_underscore`

### Error Handling

- Use specific exception types (e.g., `OSError`, `ValueError`, `ValidationError`)
- Log errors with appropriate levels (`logger.error`, `logger.warning`)
- Use try/except blocks with meaningful error messages

### Async/Await

- Use `async def` for coroutines
- Use `await` for async operations
- Return `AsyncGenerator` from `collections.abc` for streaming responses

### Frameworks & Tools

- Use `agno` framework for defining agents and toolkits
- Use `pydantic` and `pydantic-settings` for configuration management

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

## Learned User Preferences

- Prefer the official MCP Python SDK (`streamable_http_client` + `ClientSession.send_ping`) for MCP reachability checks over raw TCP/socket probes.
- Prefer Agno MCP helpers or the official MCP SDK instead of inventing ad-hoc connectivity utilities.
- Remote MCP servers should be optional at startup: skip unreachable servers and continue booting rather than failing the app lifespan.
- For Agno v2→v3 migrations, apply mechanical renames directly; report items marked JUDGMENT instead of guessing.
- Prefer framework-agnostic package names for process assembly (for example `service` over `agentos` or FastAPI-oriented names).

## Learned Workspace Facts

- Chattr is an Agno v3 + AgentOS app; use one `MCPTools` instance per remote server (`MultiMCPTools` is gone in v3).
- Package layout: `core/` builds shared pieces (model, MCP tools, db, knowledge, agent), `service/` assembles them into `AgentOS` via `setup_service`, and `character/` holds persona models.
- Personas live under `chattr.character` as Pydantic `Character` subclasses (for example `NapoleonBonaparte`), not as nested Settings fields.
- Default remote MCP endpoints are voice on `http://localhost:7861/gradio_api/mcp` and video on `http://localhost:7862/gradio_api/mcp/?tools=generate_video_mcp`; additional servers come from `extra_mcp_servers`.
- `Settings` uses pydantic-settings with `env_nested_delimiter="__"`; nested fields use `__` (for example `AGENT__DEBUG_MODE`), and list fields like `extra_mcp_servers` are JSON env values.
- Agent persistence uses `JsonDb(db_path="agno")`.
- `setup_mcp_tools` only registers MCP servers that pass a reachability probe at process start; bring servers up and restart `uv run chattr` to attach newly available tools.
- `docker-compose-dev.yaml` can run the voice and video generator MCP services used in local development.
