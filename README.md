# habitipy
[![Coverage](https://codecov.io/gh/ReiRev/habitipy/branch/main/graph/badge.svg)](https://codecov.io/gh/ReiRev/habitipy)

A typed Python client for Habitify API v2.

`habitipy` wraps the Habitify v2 API with a resource-oriented client built on `httpx`.
It exposes typed models for reads and writes so you can work with habits, areas,
logs, notes, and statistics without passing raw dictionaries around.

## Highlights

- Resource-style API: `HabitipyClient(...).habits.list()` and `HabitipyClient(...).areas.list()`
- Typed request and response models powered by Pydantic
- Native `httpx` transport with optional client injection
- Explicit pagination objects for list endpoints
- Mapped API errors for common HTTP failure cases

## Installation

`habitipy` supports Python 3.10 through 3.13.

```bash
pip install habitipy
```

Set your Habitify API key:

```bash
export HABITIFY_API_KEY="your-api-key"
```

## Quick Start

```python
import os

from habitipy import HabitipyClient

with HabitipyClient(api_key=os.environ["HABITIFY_API_KEY"]) as client:
    habits = client.habits.list(limit=10)
    for habit in habits.data:
        print(habit.name)

    areas = client.areas.list()
    for area in areas:
        print(area.name)
```

## Resource API

Create a client and work through the `habits` and `areas` resources:

```python
from habitipy import HabitipyClient

with HabitipyClient(api_key="YOUR_API_KEY") as client:
    page = client.habits.list(limit=25)
    for habit in page.data:
        print(habit.name)

    areas = client.areas.list()
    print(len(areas))

    journal_entries = client.habits.journal()
    print(journal_entries[0].status)

    stats = client.habits.statistics("habit-id")
    print(stats.total_logs)
```

If you already manage your own `httpx.Client`, you can inject it. `HabitipyClient`
adds the `X-API-Key` header and default Habitify base URL when they are missing:

```python
import httpx

from habitipy import HabitipyClient

with httpx.Client() as http_client:
    client = HabitipyClient(api_key="YOUR_API_KEY", client=http_client)
    page = client.habits.list(limit=25)
```

When you inject your own `httpx.Client`, `HabitipyClient.close()` does not close it for you.

## Typed Results

List endpoints keep pagination metadata. For example, `client.habits.list()` returns a
`HabitListPage` with `.data` and `.pagination`.

Single-resource and non-paginated endpoints are unwrapped for convenience:

- `client.habits.get(...) -> Habit`
- `client.habits.journal(...) -> list[HabitJournalEntry]`
- `client.habits.list_notes(...) -> list[HabitNote]`
- `client.habits.statistics(...) -> HabitStatistics`
- `client.areas.list() -> list[Area]`

Write calls accept dedicated request models:

```python
from habitipy import HabitLogRequest, HabitNoteCreateRequest, UnitSymbol

with HabitipyClient(api_key="YOUR_API_KEY") as client:
    client.habits.create_log(
        "habit-id",
        HabitLogRequest(unit_symbol=UnitSymbol.KM, value=5),
    )

    note = client.habits.create_note(
        "habit-id",
        HabitNoteCreateRequest(content="Solid run today"),
    )
    print(note.id)
```

## Error Handling

HTTP status errors are mapped onto typed exceptions:

- `AuthenticationError` for `401`
- `NotFoundError` for `404`
- `RateLimitError` for `429`
- `ServerError` for `5xx`
- `ApiError` for other non-success responses

Malformed JSON or unexpected top-level payloads raise `ResponseDecodeError` and
`UnexpectedResponseShapeError`.

## Development

Use Poetry for local development:

```bash
poetry install --extras dev
poetry run pre-commit install
```

Run the full local quality pass before finishing Python changes:

```bash
poetry run isort habitipy tests
poetry run black habitipy tests
poetry run ruff check habitipy tests
poetry run mypy habitipy
```

Or use the dedicated tox environment:

```bash
poetry run tox run -e quality
```

Pre-commit is configured for the same quality stack:

```bash
poetry run pre-commit run --all-files
```

Run a focused test slice:

```bash
poetry run pytest tests/test_habits.py
```

Generate coverage locally:

```bash
poetry run pytest --cov=habitipy --cov-report=term-missing
```

Run the declared Python support matrix with `tox`:

```bash
poetry run tox run -e py310,py311,py312,py313
```

## CI

GitHub Actions runs the same quality and test commands on pull requests and on pushes to `main`:

- `poetry run tox run -e quality`
- `poetry run tox run -e py310,py311,py312,py313`
- `poetry run pytest --cov=habitipy --cov-report=xml`

Coverage reports are uploaded to Codecov from the `Coverage` job. The workflow uses
OIDC and also passes `CODECOV_TOKEN`, so repositories that require the token can use
the same workflow without further changes.
