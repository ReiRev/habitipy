# habitipy
A Python client for Habitify: manage habits, logs, completions, skips, and progress from code.

## Usage

Create a client with the built-in `httpx.Client` setup:

```python
from habitipy import HabitipyClient

with HabitipyClient(api_key="YOUR_API_KEY") as client:
    page = client.habits.list(limit=25)
    for habit in page.data:
        print(habit.name)
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

## Development Setup

Use Poetry for local development:

```bash
poetry install --extras dev
```

## Format And Lint

Run Ruff before finishing Python changes.

```bash
poetry run ruff format habitipy tests
poetry run ruff check habitipy tests
```

## Running Tests

Run the focused test slice with Poetry:

```bash
poetry run pytest tests/test_habits.py
```

For the declared support matrix, use `tox`:

```bash
poetry run tox run -e py310,py311,py312,py313
```
