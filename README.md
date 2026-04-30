# habitipy
A Python client for Habitify: manage habits, logs, completions, skips, and progress from code.

## Setup

This repository uses `poetry-core` as the build backend, but you can work with either Poetry or a regular virtual environment.

With Poetry:

```bash
poetry install --extras dev
```

Without Poetry:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
```

This repository does not commit a project-local virtual environment.

## Format And Lint

Run Ruff before finishing Python changes.

With Poetry:

```bash
poetry run python -m ruff format habitipy tests
poetry run python -m ruff check habitipy tests
```

Without Poetry:

```bash
python -m ruff format habitipy tests
python -m ruff check habitipy tests
```

## Running Tests

Use `python -m pytest` instead of plain `pytest` so the tests run with the same interpreter where you installed the dependencies.

With Poetry:

```bash
poetry run python -m pytest tests/test_habits.py
```

Without Poetry:

```bash
python -m pytest tests/test_habits.py
```

For the declared support matrix, use `tox`:

With Poetry:

```bash
poetry run python -m tox run -e py310,py311,py312,py313
```

Without Poetry:

```bash
python -m tox run -e py310,py311,py312,py313
```

`tox` creates isolated environments under `.tox/`; that is separate from your local `.venv`.

## Usage

Create a client with the built-in `httpx.Client` setup:

```python
from habitipy import HabitipyClient

with HabitipyClient(api_key="YOUR_API_KEY") as client:
	page = client.habits.list(limit=25)
	for habit in page.data:
		print(habit.name)
```

Or inject your own configured `httpx.Client` if you want tighter control over transport settings:

```python
import httpx

from habitipy import HabitipyClient

http_client = httpx.Client(
	base_url="https://api.habitify.me/v2",
	headers={"X-API-Key": "YOUR_API_KEY"},
	timeout=10.0,
)

with http_client:
	client = HabitipyClient(client=http_client)
	page = client.habits.list(limit=25)
```

If you inject your own `httpx.Client`, `HabitipyClient.close()` does not close it for you.
