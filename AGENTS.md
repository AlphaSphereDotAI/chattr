# Agent Guidelines for Chattr

[byterover-mcp]

## Byterover MCP Server Tools Reference

There are two main workflows with Byterover tools and recommended tool call strategies that you **MUST** follow precisely.

### Onboarding workflow

If users particularly ask you to start the onboarding process, you **MUST STRICTLY** follow these steps.

1. **ALWAYS USE** **byterover-check-handbook-existence** first to check if the byterover handbook already exists. If not, You **MUST** call **byterover-create-handbook** to create the byterover handbook.
2. If the byterover handbook already exists, first you **MUST** USE **byterover-check-handbook-sync** to analyze the gap between the current codebase and the existing byterover handbook.
3. Then **IMMEDIATELY USE** **byterover-update-handbook** to update these changes to the byterover handbook.
4. During the onboarding, you **MUST** use **byterover-list-modules** **FIRST** to get the available modules, and then **byterover-store-modules** and **byterover-update-modules** if there are new modules or changes to existing modules in the project.

### Planning workflow

Based on user request, you **MUST** follow these sequences of tool calls

1. If asked to continue an unfinished implementation, **CALL** **byterover-retrieve-active-plans** to find the most relevant active plan.
2. **CRITICAL PLAN PERSISTENCE RULE**: Once a user approves a plan, you **MUST IMMEDIATELY CALL** **byterover-save-implementation-plan** to save it.
3. Throughout the plan, you **MUST** run **byterover-retrieve-knowledge** several times to retrieve sufficient knowledge and context for the plan's tasks.
4. In addition, you might need to run **byterover-search-modules** and **byterover-update-modules** if the tasks require or update knowledge about certain modules. However, **byterover-retrieve-knowledge** should **ALWAYS** be considered **FIRST**.
5. **MUST** use **byterover-update-plan-progress** to mark tasks (and then the whole plan) as completed.
   Example:

- Task: `byterover-update-plan-progress(plan_name="Feature X", task_name="Task 1", is_completed=true)`
- All done: `byterover-update-plan-progress(plan_name="Feature X", is_completed=true)`

1. Then, you might call **byterover-store-knowledge** to save knowledge and experience implemented throughout the plan or in important tasks.
2. During the plan's implementation, you **MUST** frequently call **byterover-think-about-collected-information** and **byterover-assess-context-completeness** to make sure you're on the right track and gather sufficient context for the tasks.

### Recommended Workflow Sequence

1. **MOST IMPORTANT**: **ALWAYS USE** **byterover-retrieve-knowledge** once or several times for **EACH TASK** of the plan to gather necessary context to complete that task.
2. **MOST IMPORTANT**: **ALWAYS USE** **byterover-store-knowledge** once or several times to store critical knowledge and context for future implementations
3. Over 15 provided tools, **byterover-retrieve-knowledge** and **byterover-store-knowledge** ARE the two main tools, which **MUST** be used regularly. You can use these two main tools outside the two main workflows for retrieval and storage purposes.
4. You **MUST** include phrases like **"According to Byterover memory layer"**, **"Based on memory extracted from Byterover"**, **"From Byterover memory tools"**, ... to explicitly showcase that these sources are from **Byterover**.
5. **Implementation & Progress Tracking** → Execute implementation following saved plan → Mark tasks complete as you go → Mark entire plan done when all tasks finished.
6. You **MUST** use **byterover-update-module** **IMMEDIATELY** on changes to the module's purposes, technical details, or critical insights that essential for future implementations.

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
