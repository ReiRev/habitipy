# habitipy
[![Coverage](https://codecov.io/gh/ReiRev/habitipy/branch/main/graph/badge.svg)](https://codecov.io/gh/ReiRev/habitipy)

A Python client for Habitify: manage habits, logs, completions, skips, and progress from code.

## Quickstart

`habitipy` supports Python 3.10 through 3.13.

Install it with pip:

```bash
pip install habitipy
```

Set your Habitify API key in the environment:

```bash
export HABITIFY_API_KEY="your-api-key"
```

Then make your first read call:

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

## Usage

Create a client with the built-in `httpx.Client` setup:

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

You can also bring your own `httpx.Client` and keep the context manager on that side. `HabitipyClient` will add the `X-API-Key` header and default Habitify base URL when they are missing:

```python
import httpx

from habitipy import HabitipyClient

with httpx.Client() as http_client:
    client = HabitipyClient(api_key="YOUR_API_KEY", client=http_client)
    page = client.habits.list(limit=25)
```

If you inject your own `httpx.Client`, `HabitipyClient.close()` does not close it for you.

## Read And Write Shapes

Methods that return collections with pagination keep the page wrapper, for example `client.habits.list()` returns a `HabitListPage` with `.data` and `.pagination`.

Methods that return a single resource or a non-paginated collection are unwrapped for you:

- `client.habits.get(...) -> Habit`
- `client.habits.journal(...) -> list[HabitJournalEntry]`
- `client.habits.list_notes(...) -> list[HabitNote]`
- `client.habits.statistics(...) -> HabitStatistics`
- `client.areas.list() -> list[Area]`

Write calls accept typed request models:

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

## Errors

Status errors are mapped onto typed `httpx` exceptions:

- `AuthenticationError` for `401`
- `NotFoundError` for `404`
- `RateLimitError` for `429`
- `ServerError` for `5xx`
- `ApiError` for other non-success responses

Malformed JSON or unexpected top-level payloads raise `ResponseDecodeError` and `UnexpectedResponseShapeError`.

## Development Setup

Use Poetry for local development:

```bash
poetry install --extras dev
poetry run pre-commit install
```

## Code Quality

Run the full local quality pass before finishing Python changes.

```bash
poetry run isort habitipy tests
poetry run black habitipy tests
poetry run ruff check habitipy tests
poetry run mypy habitipy
```

If you want the same checks behind one command, use the dedicated tox env:

```bash
poetry run tox run -e quality
```

Pre-commit is configured for the same quality stack:

```bash
poetry run pre-commit run --all-files
```

## Running Tests

Run the focused test slice with Poetry:

```bash
poetry run pytest tests/test_habits.py
```

For a quick coverage report:

```bash
poetry run pytest --cov=habitipy --cov-report=term-missing
```

Coverage uploads run from the `Coverage` GitHub Actions job and power the README badge via Codecov. The workflow uses OIDC by default and also passes `CODECOV_TOKEN` when that secret is configured, so repositories that require the token can opt in without changing the workflow.

For the declared support matrix, use `tox`:

```bash
poetry run tox run -e py310,py311,py312,py313
```

## CI

GitHub Actions runs the same local commands on every pull request and on pushes to `main`:

- `poetry run tox run -e quality`
- `poetry run tox run -e py310,py311,py312,py313`
