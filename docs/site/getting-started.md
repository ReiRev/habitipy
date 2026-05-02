# Getting Started

## Create a Client

Work through the `habits` and `areas` resources from a single `HabitipyClient` instance:

```python
from habitipie import HabitipyClient

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

from habitipie import HabitipyClient

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
from habitipie import HabitLogRequest, HabitNoteCreateRequest, UnitSymbol

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