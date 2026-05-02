# habitipie

A typed Python client for Habitify API v2.

`habitipie` gives you a resource-oriented client for working with Habitify from Python
scripts, automations, dashboards, and internal tools without hand-rolling raw HTTP calls.

## Highlights

- Resource-style API such as `HabitipyClient(...).habits.list()` and `HabitipyClient(...).areas.list()`
- Typed request and response models powered by Pydantic
- Native `httpx` transport with optional client injection
- Explicit pagination objects for list endpoints
- Mapped API errors for common HTTP failure cases

## Install

`habitipie` supports Python 3.10 through 3.13.

```bash
pip install habitipie
```

Set your Habitify API key:

```bash
export HABITIFY_API_KEY="your-api-key"
```

## Quick Start

```python
import os

from habitipie import HabitipyClient

with HabitipyClient(api_key=os.environ["HABITIFY_API_KEY"]) as client:
    habits = client.habits.list(limit=10)
    for habit in habits.data:
        print(habit.name)

    areas = client.areas.list()
    for area in areas:
        print(area.name)
```

## Read Next

- [Getting Started](getting-started.md) for client patterns and typed results
- [Development](development.md) for local validation and release workflows