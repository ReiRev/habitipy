# Project Guidelines

## Goal
- Build a Python client for the Habitify API v2.
- Align implementation work with the public OpenAPI spec at `https://api-docs.habitify.me/openapi/v2/openapi-bundled.yaml`.

## Non-Negotiable Conventions
- Use `httpx` for HTTP transport. Do not introduce `requests`.
- Enforce strong typing in the public client and internal boundaries; prefer explicit typed models and typed return values over untyped dictionaries or `Any`.
- Prefer a resource-oriented public API surface such as `HabitipyClient(...).habits.list(...)` and `HabitipyClient(...).areas.list(...)`.
- Do not default to flat method names such as `client.list_habits()` unless a compatibility layer is explicitly requested.
- Separate request models from response models when the API schema differs between write and read shapes.

## Architecture
- Keep transport concerns isolated from resource logic.
- Prefer native `httpx` exceptions where they are already expressive enough; only add custom exceptions when Habitify-specific semantics need to be conveyed.
- Model discriminated unions from the Habitify schema explicitly, especially `occurrence` and `endCondition`.
- Hide raw response envelopes when practical; prefer returning typed resource objects and explicit pagination helpers.

## Workflow
- Before changing API-facing code, verify the relevant endpoint shape in the Habitify OpenAPI spec.
- Keep changes incremental: transport and errors first, then shared models, then resources.
- For Python changes, run `poetry run ruff format` and `poetry run ruff check` on the touched Python files before finalizing.
- When adding or changing tests, validate across every supported Python version in the project's declared support matrix; if that matrix is not explicit yet, make it explicit before finalizing test automation.
- After implementation work is complete and validated, create a checkpoint commit unless higher-priority runtime instructions for the current environment forbid committing; if committing is blocked, say so explicitly.
- If a task is mostly design or planning, update the AI docs in `docs/ai/` before broad implementation work.

## Docs
- See `docs/ai/habitipy-agent-guide.md` for the repo-specific AI implementation plan and API-shape requirements.