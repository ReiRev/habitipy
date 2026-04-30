# Habitipy AI Guide

This document is for AI agents working in this repository.

## Product Intent

`habitipy` is a Python client for Habitify API v2. The client should feel like a Python package with resource namespaces rather than a thin dump of HTTP endpoints.

Primary examples:

- `HabitipyClient(...).habits.list()`
- `HabitipyClient(...).habits.get(habit_id)`
- `HabitipyClient(...).habits.create(payload)`
- `HabitipyClient(...).areas.list()`

Avoid centering the public API around flat transport methods such as `list_habits()` unless the user explicitly asks for a compatibility wrapper.

## Agent Topology

The workspace agent setup is split into one orchestrator and focused specialists.

- `Habitipy Orchestrator`: parent agent that coordinates planning, review, testing, and final synthesis
- `Habitipy Planner`: implementation planning and endpoint-to-module mapping
- `Habitipy Implementer`: focused implementation for the approved slice
- `Habitipy Spec Reviewer`: checks whether plans and code still match the Habitify OpenAPI specification
- `Habitipy API Reviewer`: public API shape and OpenAPI-alignment review
- `Habitipy Architecture Reviewer`: transport, model, and module-boundary review
- `Habitipy DX Reviewer`: developer-experience and usability review
- `Habitipy Test Author`: focused test planning or authoring for the changed slice

When a task spans planning, critique, and tests, route it through the orchestrator so specialist subagents can be used instead of overloading one prompt.

## Source of Truth

- Docs UI: `https://api-docs.habitify.me/`
- OpenAPI: `https://api-docs.habitify.me/openapi/v2/openapi-bundled.yaml`
- Base URL: `https://api.habitify.me/v2`
- Primary auth for this project: `X-API-Key`
- Rate limit: 500 requests per minute per account

## Python Support And Validation

- `pyproject.toml` currently declares `requires-python = ">=3.10"`.
- Agents should treat the supported Python-version matrix as an explicit project concern, not an implicit assumption.
- When tests, CI, or local validation commands are introduced or changed, validate across every supported Python version in the declared support matrix.
- If the matrix is too vague to automate safely, make it explicit in project tooling or documentation before calling the test setup complete.

Agents should verify endpoint details against the OpenAPI spec before implementing or changing API-facing behavior.

## Required Technical Decisions

### HTTP stack

- Use `httpx`.
- Keep HTTP concerns isolated from resource logic, but do not add a thin transport wrapper when direct `httpx.Client` injection is enough.
- Centralize auth header handling, timeout configuration, error mapping, and response parsing.
- Prefer native `httpx` exceptions when they already express the failure clearly; add custom subclasses only for Habitify-specific semantics such as rate limiting or auth-specific handling.

### Formatting and linting

- Use Ruff for both formatting and linting.
- After Python changes, run `poetry run ruff format` and `poetry run ruff check` on the touched Python files.
- Do not skip Ruff validation when changing Python code.

### Public API shape

- Favor namespaced resources.
- The intended package ergonomics are closer to `client.habits.list(...)` than `client.list_habits(...)`.
- Keep the public entry point centered on `HabitipyClient` rather than a package-level singleton runtime.
- Do not let transport abstractions leak into the public API.

### Modeling

- Enforce strong typing across the package.
- Create explicit models for read and write payloads where the schema differs.
- Model discriminated unions explicitly.
- Avoid leaking `dict[str, Any]` or untyped payloads across the public API unless a raw escape hatch is explicitly requested.
- Important unions from the spec:
  - `occurrence`
  - `endCondition`
- Shared concepts likely deserve their own module:
  - pagination
  - goals
  - reminders
  - logs
  - notes
  - areas

### Resource boundaries

Preferred resource grouping:

- `habits`
- `areas`
- `habits.logs`
- `habits.notes`
- `habits.journal`
- `habits.statistics`

The user-facing surface can still flatten some of these into `client.habits.*` methods if that is cleaner.

## Suggested Package Shape

This is guidance, not a locked file tree.

```text
habitipy/
  __init__.py
  errors.py
  pagination.py
  habits.py
  areas.py
  models/
    habits.py
    areas.py
    logs.py
    notes.py
    shared.py
```

If the package grows, split resources and models further instead of overloading one file.

## Delivery Order

When implementation starts, prefer this sequence:

1. transport layer with `httpx`
2. error hierarchy
3. shared enums and union models
4. areas resource
5. habits CRUD
6. journal and statistics
7. logs and notes
8. tests and usage docs

After a concrete implementation slice is finished and validated, prefer making a checkpoint commit before moving on to unrelated work. If the current agent environment has a higher-priority rule that forbids committing, call that out explicitly instead of silently skipping the step.

Validation should cover every supported Python version in the project's declared support matrix, not just the active interpreter.

## Guardrails For Future Agents

- Do not implement broad code generation from the OpenAPI document unless explicitly requested.
- Do not switch away from `httpx`.
- Do not design a public API that requires callers to manually build URLs.
- Do not skip documenting changes when public API direction changes.

## What To Optimize For

- Pythonic ergonomics
- Strong typing
- Small, composable modules
- Clear mapping from spec to code
- Predictable public API names