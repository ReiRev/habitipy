from __future__ import annotations

import json
from datetime import date

import httpx
import pytest
import respx
from pydantic import ValidationError

from habitipy import (
    GoalPeriodicity,
    HabitCreateRequest,
    HabitipyClient,
    HabitJournalStatus,
    HabitLogActionRequest,
    HabitLogRequest,
    HabitLogResponse,
    HabitNoteCreateRequest,
    HabitNoteUpdateRequest,
    HabitType,
    HabitUpdateRequest,
    MoodLevel,
    SuccessMessageResponse,
    UnitSymbol,
)
from habitipy.errors import (
    ApiError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ResponseDecodeError,
    UnexpectedResponseShapeError,
)
from habitipy.models.habits import (
    HabitCreateDateEndCondition,
    HabitCreateGoal,
    HabitCreateHabitStack,
    HabitCreateReminderOccurrenceFilter,
    HabitCreateReminders,
    HabitCreateReminderTime,
    HabitCreateTimeTrigger,
    HabitCreateWeekDaysOccurrence,
    HabitJournalStreakUnit,
    HabitStackTimerType,
    HabitStackTriggerType,
    HabitUpdateReminders,
)


def build_habits_payload() -> dict[str, object]:
    return {
        "data": [
            {
                "id": "habit_123",
                "name": "Morning Run",
                "icon": "figure.run",
                "colorHex": "#FF6B6B",
                "type": "good",
                "description": "Run before breakfast",
                "occurrence": {"type": "daily"},
                "startDate": "2024-01-01",
                "createdAt": "2024-01-01T06:30:00Z",
                "isArchived": False,
                "logMethod": "manual",
                "challengeId": "challenge_1",
                "reminders": {
                    "timeTriggers": [
                        {
                            "time": {"hour": 6, "minute": 30},
                            "occurrenceFilter": {"weekDays": [2, 3, 4, 5, 6]},
                            "showLiveActivity": True,
                            "showAsAlarm": False,
                        }
                    ],
                    "habitStacks": [
                        {
                            "id": "stack_1",
                            "conditionHabitId": "habit_456",
                            "type": "completed",
                            "timerType": "immediately",
                        }
                    ],
                },
                "endCondition": None,
                "goals": [
                    {
                        "id": "goal_1",
                        "createdAt": "2024-01-01T06:30:00Z",
                        "periodicity": "daily",
                        "value": 5,
                        "unit": "kM",
                        "isActive": True,
                    }
                ],
                "customUnitName": None,
                "areas": [
                    {
                        "id": "area_1",
                        "name": "Health",
                        "colorHex": "#4ECDC4",
                        "icon": "heart",
                        "createdAt": "2024-01-01T06:00:00Z",
                        "description": "Health habits",
                    }
                ],
                "timeOfDays": [
                    {
                        "id": "tod_1",
                        "name": "Morning",
                        "icon": "sun.max",
                        "startTime": "06:00:00",
                        "endTime": "11:59:59",
                        "colorHex": "#FFD93D",
                    }
                ],
            }
        ],
        "pagination": {"total": 1, "limit": 25, "offset": 0},
    }


def build_habit_payload() -> dict[str, object]:
    return dict(build_habits_payload()["data"][0])


def build_habit_response_payload() -> dict[str, object]:
    return {"data": build_habit_payload()}


def build_habit_journal_payload() -> dict[str, object]:
    return {
        "data": [
            {
                "id": "habit_123",
                "name": "Morning Run",
                "status": "completed",
                "colorHex": "#FF6B6B",
                "icon": "figure.run",
                "timeOfDayIds": ["tod_1"],
                "type": "good",
                "currentStreak": {"length": 7, "unit": "day"},
                "progress": {
                    "current": 5.2,
                    "target": 5,
                    "unit": "km",
                    "periodicity": "daily",
                },
                "logInfo": {"type": "manual"},
            }
        ]
    }


def build_habit_statistics_payload() -> dict[str, object]:
    return {
        "data": {
            "id": "habit_123",
            "name": "Morning Run",
            "type": "good",
            "totalLogs": 12.5,
            "skips": 1,
            "fails": 2,
            "completions": 3,
            "unit": {
                "id": "unit_1",
                "name": "Kilometer",
                "symbol": UnitSymbol.KM.value,
            },
            "periodicity": "daily",
            "avg": 1.25,
            "dailyProgress": [
                {"date": "2024-01-01", "totalLog": 5, "status": "completed"},
                {"date": "2024-01-02", "totalLog": 0, "status": "inprogress"},
            ],
        }
    }


def build_habit_statistics_live_unit_payload() -> dict[str, object]:
    payload = build_habit_statistics_payload()
    payload["data"]["unit"] = {"symbol": UnitSymbol.REP.value, "type": "scalar"}
    return payload


def build_habit_log_response_payload() -> dict[str, object]:
    return {"message": "Habit log created successfully"}


def build_success_message_payload(message: str) -> dict[str, object]:
    return {"message": message}


def build_habit_note_payload() -> dict[str, object]:
    return {
        "id": "note_123",
        "content": "Solid run today",
        "moodLevel": "high",
        "photos": ["https://example.com/photo1.jpg"],
        "createdAt": "2024-01-02T08:00:00Z",
    }


def build_habit_notes_payload() -> dict[str, object]:
    return {"data": [build_habit_note_payload()]}


@respx.mock
def test_client_habits_get_sends_expected_path_and_parses_response() -> None:
    route = respx.get("https://api.habitify.me/v2/habits/habit_123").mock(
        return_value=httpx.Response(200, json=build_habit_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        habit = client.habits.get("habit_123")
    finally:
        client.close()

    request = route.calls[0].request
    assert request.headers["X-API-Key"] == "test-key"
    assert request.url.path == "/v2/habits/habit_123"
    assert habit.id == "habit_123"
    assert habit.type is HabitType.GOOD
    assert habit.time_of_days[0].name == "Morning"


@respx.mock
def test_client_habits_get_parses_enveloped_response() -> None:
    route = respx.get("https://api.habitify.me/v2/habits/habit_123").mock(
        return_value=httpx.Response(200, json=build_habit_response_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        habit = client.habits.get("habit_123")
    finally:
        client.close()

    assert route.called
    assert route.calls[0].request.url.path == "/v2/habits/habit_123"
    assert route.calls[0].request.headers["X-API-Key"] == "test-key"
    assert habit.id == "habit_123"
    assert habit.type is HabitType.GOOD


@respx.mock
def test_client_habits_get_url_encodes_path_segment() -> None:
    route = respx.get("https://api.habitify.me/v2/habits/habit%2Fwith%20spaces%3F%23").mock(
        return_value=httpx.Response(200, json=build_habit_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        habit = client.habits.get("habit/with spaces?#")
    finally:
        client.close()

    assert route.called
    assert route.calls[0].request.url.raw_path == b"/v2/habits/habit%2Fwith%20spaces%3F%23"
    assert habit.id == "habit_123"


@respx.mock
def test_client_habits_statistics_parses_live_unit_shape_without_id_or_name() -> None:
    route = respx.get("https://api.habitify.me/v2/habits/habit_123/statistics").mock(
        return_value=httpx.Response(200, json=build_habit_statistics_live_unit_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        statistics = client.habits.statistics("habit_123")
    finally:
        client.close()

    assert route.called
    assert route.calls[0].request.url.path == "/v2/habits/habit_123/statistics"
    assert route.calls[0].request.headers["X-API-Key"] == "test-key"
    assert statistics.unit.id is None
    assert statistics.unit.name is None
    assert statistics.unit.symbol is UnitSymbol.REP


@respx.mock
def test_client_habits_list_sends_expected_query_params_and_parses_response() -> None:
    route = respx.get("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(200, json=build_habits_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        page = client.habits.list(
            archived=False,
            area_id="area_1",
            habit_type=HabitType.GOOD,
            time_of_day="tod_1",
            limit=25,
            offset=0,
        )
    finally:
        client.close()

    request = route.calls[0].request
    assert request.headers["X-API-Key"] == "test-key"
    assert request.url.params["archived"] == "false"
    assert request.url.params["areaId"] == "area_1"
    assert request.url.params["type"] == "good"
    assert request.url.params["timeOfDay"] == "tod_1"
    assert request.url.params["limit"] == "25"
    assert request.url.params["offset"] == "0"

    assert page.pagination.total == 1
    assert page.data[0].type is HabitType.GOOD
    assert page.data[0].time_of_days[0].name == "Morning"
    assert page.data[0].reminders.habit_stacks[0].type is HabitStackTriggerType.COMPLETED
    assert page.data[0].reminders.habit_stacks[0].timer_type is HabitStackTimerType.IMMEDIATELY
    assert page.data[0].reminders.habit_stacks[0].timer_delay_secs is None


@respx.mock
def test_client_habits_create_sends_expected_json_and_parses_response() -> None:
    route = respx.post("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(201, json=build_habit_payload())
    )

    request = HabitCreateRequest(
        name="Morning Run",
        type=HabitType.GOOD,
        description="Run before breakfast",
        occurrence=HabitCreateWeekDaysOccurrence(type="weekDays", days=[2, 3, 4, 5, 6]),
        startDate="2024-01-01",
        icon="figure.run",
        colorHex="#FF6B6B",
        customUnitName="laps",
        areaIds=["area_1"],
        timeOfDayIds=["tod_1"],
        goal=HabitCreateGoal(
            periodicity=GoalPeriodicity.DAILY,
            value=5,
            unit=UnitSymbol.KM,
        ),
        reminders=HabitCreateReminders(
            timeTriggers=[
                HabitCreateTimeTrigger(
                    time=HabitCreateReminderTime(hour=6, minute=30),
                    occurrenceFilter=HabitCreateReminderOccurrenceFilter(weekDays=[2, 3, 4]),
                    showLiveActivity=True,
                    showAsAlarm=False,
                )
            ],
            habitStacks=[
                HabitCreateHabitStack(
                    conditionHabitId="habit_abc",
                    type=HabitStackTriggerType.COMPLETED,
                    timerType=HabitStackTimerType.AFTER,
                    timerDelaySecs=300,
                )
            ],
        ),
        endCondition=HabitCreateDateEndCondition(type="date", date="2024-12-31"),
    )

    client = HabitipyClient(api_key="test-key")
    try:
        habit = client.habits.create(request)
    finally:
        client.close()

    http_request = route.calls[0].request
    assert http_request.headers["X-API-Key"] == "test-key"

    payload = json.loads(http_request.content.decode("utf-8"))
    assert payload["name"] == "Morning Run"
    assert payload["type"] == "good"
    assert payload["occurrence"] == {"type": "weekDays", "days": [2, 3, 4, 5, 6]}
    assert payload["startDate"] == "2024-01-01"
    assert payload["colorHex"] == "#FF6B6B"
    assert payload["customUnitName"] == "laps"
    assert payload["areaIds"] == ["area_1"]
    assert payload["timeOfDayIds"] == ["tod_1"]
    assert payload["goal"] == {"periodicity": "daily", "value": 5.0, "unit": "kM"}
    assert payload["endCondition"] == {"type": "date", "date": "2024-12-31"}
    assert payload["reminders"]["timeTriggers"][0]["occurrenceFilter"] == {"weekDays": [2, 3, 4]}
    assert payload["reminders"]["habitStacks"][0] == {
        "conditionHabitId": "habit_abc",
        "type": "completed",
        "timerType": "after",
        "timerDelaySecs": 300,
    }

    assert habit.id == "habit_123"
    assert habit.name == "Morning Run"
    assert habit.type is HabitType.GOOD
    assert habit.reminders.habit_stacks[0].type is HabitStackTriggerType.COMPLETED
    assert habit.reminders.habit_stacks[0].timer_type is HabitStackTimerType.IMMEDIATELY
    assert habit.reminders.habit_stacks[0].timer_delay_secs is None


@respx.mock
def test_client_habits_update_sends_expected_json_and_returns_none() -> None:
    route = respx.put("https://api.habitify.me/v2/habits/habit_123").mock(
        return_value=httpx.Response(200)
    )

    request = HabitUpdateRequest(
        name="Morning Run Updated",
        description="Run before breakfast",
        occurrence=HabitCreateWeekDaysOccurrence(type="weekDays", days=[2, 3, 4, 5, 6]),
        startDate="2024-01-02",
        icon="figure.run",
        colorHex="#123456",
        customUnitName="laps",
        areaIds=["area_1"],
        timeOfDayIds=["tod_1"],
        goal=HabitCreateGoal(
            periodicity=GoalPeriodicity.DAILY,
            value=7,
            unit=UnitSymbol.KM,
        ),
        reminders=HabitUpdateReminders(
            timeTriggers=[
                HabitCreateTimeTrigger(
                    time=HabitCreateReminderTime(hour=7, minute=0),
                    occurrenceFilter=HabitCreateReminderOccurrenceFilter(weekDays=[2, 3, 4]),
                    showLiveActivity=True,
                    showAsAlarm=False,
                )
            ]
        ),
        endCondition=HabitCreateDateEndCondition(type="date", date="2024-12-31"),
    )

    client = HabitipyClient(api_key="test-key")
    try:
        result = client.habits.update("habit_123", request)
    finally:
        client.close()

    assert result is None

    http_request = route.calls[0].request
    assert http_request.headers["X-API-Key"] == "test-key"

    payload = json.loads(http_request.content.decode("utf-8"))
    assert payload == {
        "name": "Morning Run Updated",
        "description": "Run before breakfast",
        "occurrence": {"type": "weekDays", "days": [2, 3, 4, 5, 6]},
        "startDate": "2024-01-02",
        "icon": "figure.run",
        "colorHex": "#123456",
        "customUnitName": "laps",
        "areaIds": ["area_1"],
        "timeOfDayIds": ["tod_1"],
        "goal": {"periodicity": "daily", "value": 7.0, "unit": UnitSymbol.KM.value},
        "reminders": {
            "timeTriggers": [
                {
                    "time": {"hour": 7, "minute": 0},
                    "occurrenceFilter": {"weekDays": [2, 3, 4]},
                    "showLiveActivity": True,
                    "showAsAlarm": False,
                }
            ]
        },
        "endCondition": {"type": "date", "date": "2024-12-31"},
    }


@respx.mock
def test_client_habits_update_serializes_only_provided_fields() -> None:
    route = respx.put("https://api.habitify.me/v2/habits/habit_123").mock(
        return_value=httpx.Response(200)
    )

    client = HabitipyClient(api_key="test-key")
    try:
        result = client.habits.update(
            "habit_123",
            HabitUpdateRequest(name="Updated", reminders=HabitUpdateReminders()),
        )
    finally:
        client.close()

    assert result is None
    assert route.called
    assert json.loads(route.calls[0].request.content.decode("utf-8")) == {"name": "Updated"}


@respx.mock
def test_client_habits_update_maps_not_found_error() -> None:
    respx.put("https://api.habitify.me/v2/habits/missing").mock(
        return_value=httpx.Response(404, json={"message": "Habit not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Habit not found") as exc_info:
            client.habits.update("missing", HabitUpdateRequest(name="Updated"))
    finally:
        client.close()

    assert exc_info.value.response.status_code == 404


@respx.mock
def test_client_habits_update_maps_validation_error() -> None:
    respx.put("https://api.habitify.me/v2/habits/habit_123").mock(
        return_value=httpx.Response(422, json={"message": "Validation error"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Validation error"):
            client.habits.update("habit_123", HabitUpdateRequest(name="Updated"))
    finally:
        client.close()


@respx.mock
def test_client_habits_delete_sends_expected_path_and_returns_none() -> None:
    route = respx.delete("https://api.habitify.me/v2/habits/habit_123").mock(
        return_value=httpx.Response(204)
    )

    client = HabitipyClient(api_key="test-key")
    try:
        result = client.habits.delete("habit_123")
    finally:
        client.close()

    assert result is None
    assert route.called
    assert route.calls[0].request.headers["X-API-Key"] == "test-key"
    assert route.calls[0].request.url.path == "/v2/habits/habit_123"


@respx.mock
def test_client_habits_delete_rejects_unexpected_success_status() -> None:
    respx.delete("https://api.habitify.me/v2/habits/habit_123").mock(
        return_value=httpx.Response(200)
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Expected HTTP 204 No Content"):
            client.habits.delete("habit_123")
    finally:
        client.close()


@respx.mock
def test_client_habits_delete_maps_not_found_error() -> None:
    respx.delete("https://api.habitify.me/v2/habits/missing").mock(
        return_value=httpx.Response(404, json={"message": "Habit not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Habit not found") as exc_info:
            client.habits.delete("missing")
    finally:
        client.close()

    assert exc_info.value.response.status_code == 404


@respx.mock
def test_client_habits_archive_sends_expected_path_and_returns_none() -> None:
    route = respx.post("https://api.habitify.me/v2/habits/habit_123/archive").mock(
        return_value=httpx.Response(204)
    )

    client = HabitipyClient(api_key="test-key")
    try:
        result = client.habits.archive("habit_123")
    finally:
        client.close()

    assert result is None
    assert route.calls[0].request.headers["X-API-Key"] == "test-key"
    assert route.calls[0].request.url.path == "/v2/habits/habit_123/archive"


@respx.mock
def test_client_habits_archive_surfaces_conflict_api_error_message() -> None:
    respx.post("https://api.habitify.me/v2/habits/already-archived/archive").mock(
        return_value=httpx.Response(409, json={"message": "Habit is already archived"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Habit is already archived") as exc_info:
            client.habits.archive("already-archived")
    finally:
        client.close()

    assert exc_info.value.response.status_code == 409


@respx.mock
def test_client_habits_journal_sends_expected_query_params_and_parses_response() -> None:
    route = respx.get("https://api.habitify.me/v2/habits/journal").mock(
        return_value=httpx.Response(200, json=build_habit_journal_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        page = client.habits.journal(date=date(2024, 1, 2))
    finally:
        client.close()

    request = route.calls[0].request
    assert request.headers["X-API-Key"] == "test-key"
    assert request.url.params["date"] == "2024-01-02"

    assert page[0].status is HabitJournalStatus.COMPLETED
    assert page[0].type is HabitType.GOOD
    assert page[0].current_streak.unit is HabitJournalStreakUnit.DAY
    assert page[0].progress.periodicity is GoalPeriodicity.DAILY
    assert page[0].log_info.type.value == "manual"


@respx.mock
def test_client_habits_statistics_sends_expected_query_params_and_parses_response() -> None:
    route = respx.get("https://api.habitify.me/v2/habits/habit_123/statistics").mock(
        return_value=httpx.Response(200, json=build_habit_statistics_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        statistics = client.habits.statistics(
            "habit_123",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
    finally:
        client.close()

    request = route.calls[0].request
    assert request.headers["X-API-Key"] == "test-key"
    assert request.url.params["startDate"] == "2024-01-01"
    assert request.url.params["endDate"] == "2024-01-31"

    assert statistics.id == "habit_123"
    assert statistics.type is HabitType.GOOD
    assert statistics.total_logs == 12.5
    assert statistics.skips == 1
    assert statistics.fails == 2
    assert statistics.completions == 3
    assert statistics.unit.symbol is UnitSymbol.KM
    assert statistics.periodicity is GoalPeriodicity.DAILY
    assert statistics.avg == 1.25
    assert statistics.daily_progress[0].status is HabitJournalStatus.COMPLETED
    assert statistics.daily_progress[1].status is HabitJournalStatus.IN_PROGRESS


@respx.mock
def test_client_habits_statistics_maps_bad_request_error() -> None:
    respx.get("https://api.habitify.me/v2/habits/habit_123/statistics").mock(
        return_value=httpx.Response(400, json={"message": "Invalid date range"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Invalid date range"):
            client.habits.statistics(
                "habit_123",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
            )
    finally:
        client.close()


@respx.mock
def test_client_habits_statistics_maps_not_found_error() -> None:
    respx.get("https://api.habitify.me/v2/habits/missing/statistics").mock(
        return_value=httpx.Response(404, json={"message": "Habit not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Habit not found") as exc_info:
            client.habits.statistics("missing")
    finally:
        client.close()

    assert exc_info.value.response.status_code == 404


@respx.mock
def test_client_habits_statistics_raises_response_decode_error_for_invalid_json() -> None:
    respx.get("https://api.habitify.me/v2/habits/habit_123/statistics").mock(
        return_value=httpx.Response(
            200,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ResponseDecodeError, match="invalid JSON"):
            client.habits.statistics("habit_123")
    finally:
        client.close()


@respx.mock
def test_client_habits_create_log_sends_expected_body_and_parses_response() -> None:
    route = respx.post("https://api.habitify.me/v2/habits/habit_123/logs").mock(
        return_value=httpx.Response(201, json=build_habit_log_response_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        response = client.habits.create_log(
            "habit_123",
            HabitLogRequest(
                unit_symbol=UnitSymbol.KM,
                value=5,
                target_date=date(2024, 1, 31),
            ),
        )
    finally:
        client.close()

    request = route.calls[0].request
    assert request.headers["X-API-Key"] == "test-key"
    assert json.loads(request.content) == {
        "unitSymbol": "kM",
        "value": 5,
        "targetDate": "2024-01-31",
    }

    assert isinstance(response, HabitLogResponse)
    assert response.message == "Habit log created successfully"


@respx.mock
def test_client_habits_create_log_omits_target_date_when_not_provided() -> None:
    route = respx.post("https://api.habitify.me/v2/habits/habit_123/logs").mock(
        return_value=httpx.Response(201, json=build_habit_log_response_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        response = client.habits.create_log(
            "habit_123",
            HabitLogRequest(unit_symbol=UnitSymbol.KM, value=5),
        )
    finally:
        client.close()

    assert route.called
    assert json.loads(route.calls[0].request.content.decode("utf-8")) == {
        "unitSymbol": "kM",
        "value": 5,
    }
    assert response.message == "Habit log created successfully"


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (400, "Invalid input data"),
        (422, "Validation error"),
    ],
)
@respx.mock
def test_client_habits_create_log_maps_client_errors(status_code: int, message: str) -> None:
    respx.post("https://api.habitify.me/v2/habits/habit_123/logs").mock(
        return_value=httpx.Response(status_code, json={"message": message})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match=message):
            client.habits.create_log(
                "habit_123",
                HabitLogRequest(unit_symbol=UnitSymbol.KM, value=5),
            )
    finally:
        client.close()


@respx.mock
def test_client_habits_create_log_maps_not_found_error() -> None:
    respx.post("https://api.habitify.me/v2/habits/missing/logs").mock(
        return_value=httpx.Response(404, json={"message": "Habit not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Habit not found") as exc_info:
            client.habits.create_log(
                "missing",
                HabitLogRequest(unit_symbol=UnitSymbol.KM, value=5),
            )
    finally:
        client.close()

    assert exc_info.value.response.status_code == 404


@respx.mock
def test_client_habits_create_log_raises_response_decode_error_for_invalid_json() -> None:
    respx.post("https://api.habitify.me/v2/habits/habit_123/logs").mock(
        return_value=httpx.Response(
            201,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ResponseDecodeError, match="invalid JSON"):
            client.habits.create_log(
                "habit_123",
                HabitLogRequest(unit_symbol=UnitSymbol.KM, value=5),
            )
    finally:
        client.close()


@pytest.mark.parametrize(
    ("method_name", "path_suffix", "message"),
    [
        ("complete_log", "complete", "Habit marked as completed successfully"),
        ("fail_log", "failed", "Habit marked as failed successfully"),
        ("skip_log", "skipped", "Habit marked as skipped successfully"),
        ("undo_log", "undo", "Habit progress undone successfully"),
    ],
)
@respx.mock
def test_client_habit_log_actions_send_optional_target_date_and_parse_message(
    method_name: str,
    path_suffix: str,
    message: str,
) -> None:
    route = respx.post(f"https://api.habitify.me/v2/habits/habit_123/logs/{path_suffix}").mock(
        return_value=httpx.Response(
            201 if path_suffix != "undo" else 200, json=build_success_message_payload(message)
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        response = getattr(client.habits, method_name)(
            "habit_123",
            HabitLogActionRequest(target_date=date(2024, 1, 15)),
        )
    finally:
        client.close()

    assert route.called
    assert json.loads(route.calls[0].request.content.decode("utf-8")) == {
        "targetDate": "2024-01-15"
    }
    assert isinstance(response, SuccessMessageResponse)
    assert response.message == message


@respx.mock
def test_client_habit_log_actions_omit_request_body_when_no_target_date_is_provided() -> None:
    route = respx.post("https://api.habitify.me/v2/habits/habit_123/logs/complete").mock(
        return_value=httpx.Response(
            201,
            json=build_success_message_payload("Habit marked as completed successfully"),
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        response = client.habits.complete_log("habit_123")
    finally:
        client.close()

    assert route.called
    assert route.calls[0].request.content == b""
    assert response.message == "Habit marked as completed successfully"


@respx.mock
def test_client_habits_delete_log_sends_expected_path_and_parses_response() -> None:
    route = respx.delete("https://api.habitify.me/v2/habits/habit_123/logs/log_456").mock(
        return_value=httpx.Response(
            200,
            json=build_success_message_payload("Habit log removed successfully"),
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        response = client.habits.delete_log("habit_123", "log_456")
    finally:
        client.close()

    assert route.called
    assert route.calls[0].request.url.path == "/v2/habits/habit_123/logs/log_456"
    assert response.message == "Habit log removed successfully"


@respx.mock
def test_client_habits_delete_log_maps_not_found_error() -> None:
    respx.delete("https://api.habitify.me/v2/habits/habit_123/logs/missing").mock(
        return_value=httpx.Response(404, json={"message": "Habit or log entry not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(NotFoundError, match="Habit or log entry not found"):
            client.habits.delete_log("habit_123", "missing")
    finally:
        client.close()


@respx.mock
def test_client_habits_list_notes_parses_response() -> None:
    route = respx.get("https://api.habitify.me/v2/habits/habit_123/notes").mock(
        return_value=httpx.Response(200, json=build_habit_notes_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        notes = client.habits.list_notes("habit_123")
    finally:
        client.close()

    assert route.called
    assert isinstance(notes, list)
    assert notes[0].mood_level is MoodLevel.HIGH
    assert notes[0].photos == ["https://example.com/photo1.jpg"]


@respx.mock
def test_client_habits_list_notes_maps_not_found_error() -> None:
    respx.get("https://api.habitify.me/v2/habits/habit_123/notes").mock(
        return_value=httpx.Response(404, json={"message": "Habit not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(NotFoundError, match="Habit not found"):
            client.habits.list_notes("habit_123")
    finally:
        client.close()


@respx.mock
def test_client_habits_create_note_sends_expected_json_and_parses_response() -> None:
    route = respx.post("https://api.habitify.me/v2/habits/habit_123/notes").mock(
        return_value=httpx.Response(201, json=build_habit_note_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        note = client.habits.create_note(
            "habit_123",
            HabitNoteCreateRequest(
                content="Solid run today",
                mood_level=MoodLevel.HIGH,
                photos=["https://example.com/photo1.jpg"],
            ),
        )
    finally:
        client.close()

    assert route.called
    assert json.loads(route.calls[0].request.content.decode("utf-8")) == {
        "content": "Solid run today",
        "moodLevel": "high",
        "photos": ["https://example.com/photo1.jpg"],
    }
    assert note.id == "note_123"
    assert note.mood_level is MoodLevel.HIGH


@respx.mock
def test_client_habits_update_note_sends_expected_json_and_parses_response() -> None:
    route = respx.put("https://api.habitify.me/v2/habits/habit_123/notes/note_123").mock(
        return_value=httpx.Response(200, json=build_habit_note_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        note = client.habits.update_note(
            "habit_123",
            "note_123",
            HabitNoteUpdateRequest(content="Updated note"),
        )
    finally:
        client.close()

    assert route.called
    assert json.loads(route.calls[0].request.content.decode("utf-8")) == {"content": "Updated note"}
    assert note.id == "note_123"


@respx.mock
def test_client_habits_update_note_url_encodes_path_segments() -> None:
    route = respx.put(
        "https://api.habitify.me/v2/habits/habit%2Fwith%20spaces/notes/note%3Fwith%23chars"
    ).mock(return_value=httpx.Response(200, json=build_habit_note_payload()))

    client = HabitipyClient(api_key="test-key")
    try:
        note = client.habits.update_note(
            "habit/with spaces",
            "note?with#chars",
            HabitNoteUpdateRequest(content="Updated note"),
        )
    finally:
        client.close()

    assert route.called
    assert (
        route.calls[0].request.url.raw_path
        == b"/v2/habits/habit%2Fwith%20spaces/notes/note%3Fwith%23chars"
    )
    assert note.id == "note_123"


@respx.mock
def test_client_habits_delete_note_returns_none_on_204() -> None:
    route = respx.delete("https://api.habitify.me/v2/habits/habit_123/notes/note_123").mock(
        return_value=httpx.Response(204)
    )

    client = HabitipyClient(api_key="test-key")
    try:
        result = client.habits.delete_note("habit_123", "note_123")
    finally:
        client.close()

    assert route.called
    assert result is None


@respx.mock
def test_client_habits_delete_note_rejects_unexpected_success_status() -> None:
    respx.delete("https://api.habitify.me/v2/habits/habit_123/notes/note_123").mock(
        return_value=httpx.Response(200)
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Expected HTTP 204 No Content"):
            client.habits.delete_note("habit_123", "note_123")
    finally:
        client.close()


@respx.mock
def test_client_habits_delete_note_maps_not_found_error() -> None:
    respx.delete("https://api.habitify.me/v2/habits/habit_123/notes/note_123").mock(
        return_value=httpx.Response(404, json={"message": "Note not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(NotFoundError, match="Note not found"):
            client.habits.delete_note("habit_123", "note_123")
    finally:
        client.close()


def test_habit_note_requests_require_at_least_one_field() -> None:
    with pytest.raises(ValidationError, match="At least one note field must be provided"):
        HabitNoteCreateRequest()

    with pytest.raises(ValidationError, match="At least one note field must be provided"):
        HabitNoteUpdateRequest()


@respx.mock
def test_client_habits_update_note_sends_explicit_null_to_clear_field() -> None:
    route = respx.put("https://api.habitify.me/v2/habits/habit_123/notes/note_123").mock(
        return_value=httpx.Response(200, json=build_habit_note_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        note = client.habits.update_note(
            "habit_123",
            "note_123",
            HabitNoteUpdateRequest(content=None),
        )
    finally:
        client.close()

    assert route.called
    assert json.loads(route.calls[0].request.content.decode("utf-8")) == {"content": None}
    assert note.id == "note_123"


@respx.mock
def test_client_habits_list_uses_injected_httpx_client() -> None:
    route = respx.get("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(200, json=build_habits_payload())
    )

    with httpx.Client() as injected_client:
        client = HabitipyClient(api_key="injected-key", client=injected_client)
        page = client.habits.list(limit=25)
        client.close()
        assert not injected_client.is_closed

    assert route.calls[0].request.headers["X-API-Key"] == "injected-key"
    assert page.data[0].name == "Morning Run"


def test_habit_create_request_requires_name_and_type() -> None:
    with pytest.raises(ValidationError):
        HabitCreateRequest()  # type: ignore[call-arg]


@respx.mock
def test_client_accepts_injected_httpx_client_with_existing_api_key_header() -> None:
    route = respx.get("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(200, json=build_habits_payload())
    )

    with httpx.Client(headers={"X-API-Key": "preset-key"}) as injected_client:
        client = HabitipyClient(client=injected_client)
        page = client.habits.list(limit=25)

    assert route.calls[0].request.headers["X-API-Key"] == "preset-key"
    assert page.data[0].name == "Morning Run"


def test_client_requires_api_key_without_injected_client() -> None:
    with pytest.raises(ValueError, match="api_key is required"):
        HabitipyClient()


def test_client_requires_api_key_when_injected_client_has_no_header() -> None:
    with httpx.Client() as injected_client:
        with pytest.raises(ValueError, match="provided client already has an X-API-Key header"):
            HabitipyClient(client=injected_client)


@respx.mock
def test_client_empty_api_key_does_not_overwrite_injected_client_header() -> None:
    route = respx.get("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(200, json=build_habits_payload())
    )

    with httpx.Client(headers={"X-API-Key": "preset-key"}) as injected_client:
        client = HabitipyClient(api_key="", client=injected_client)
        page = client.habits.list(limit=25)

    assert route.calls[0].request.headers["X-API-Key"] == "preset-key"
    assert page.data[0].name == "Morning Run"


@respx.mock
def test_client_habits_list_uses_generic_api_error_for_bad_request() -> None:
    respx.get("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(
            400,
            json={
                "error": "Validation Error",
                "message": "Request validation failed",
            },
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Request validation failed") as exc_info:
            client.habits.list(limit=50)
    finally:
        client.close()

    assert exc_info.value.response.status_code == 400


@respx.mock
def test_client_habits_create_maps_bad_request_error() -> None:
    respx.post("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(400, json={"message": "Request validation failed"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Request validation failed"):
            client.habits.create(HabitCreateRequest(name="Morning Run", type=HabitType.GOOD))
    finally:
        client.close()


@respx.mock
def test_client_habits_create_maps_authentication_error() -> None:
    respx.post("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(401, json={"message": "Missing API key"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(AuthenticationError, match="Missing API key"):
            client.habits.create(HabitCreateRequest(name="Morning Run", type=HabitType.GOOD))
    finally:
        client.close()


@respx.mock
def test_client_habits_journal_maps_bad_request_error() -> None:
    respx.get("https://api.habitify.me/v2/habits/journal").mock(
        return_value=httpx.Response(400, json={"message": "Invalid date format"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ApiError, match="Invalid date format"):
            client.habits.journal(date=date(2024, 1, 2))
    finally:
        client.close()


@respx.mock
def test_client_habits_get_maps_not_found_error() -> None:
    respx.get("https://api.habitify.me/v2/habits/missing").mock(
        return_value=httpx.Response(404, json={"message": "Habit not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(NotFoundError, match="Habit not found") as exc_info:
            client.habits.get("missing")
    finally:
        client.close()

    assert exc_info.value.response.status_code == 404


@respx.mock
def test_client_habits_list_maps_rate_limit_error() -> None:
    respx.get("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(
            429,
            json={
                "error": "Too Many Requests",
                "message": "Rate limit exceeded. Please wait before making more requests.",
            },
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            client.habits.list()
    finally:
        client.close()


@respx.mock
def test_client_habits_list_raises_httpx_timeout_errors() -> None:
    respx.get("https://api.habitify.me/v2/habits").mock(side_effect=httpx.ReadTimeout("timed out"))

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(httpx.ReadTimeout, match="timed out"):
            client.habits.list()
    finally:
        client.close()


@respx.mock
def test_client_habits_list_rejects_non_object_payloads() -> None:
    respx.get("https://api.habitify.me/v2/habits").mock(return_value=httpx.Response(200, json=[]))

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(UnexpectedResponseShapeError, match="JSON object"):
            client.habits.list()
    finally:
        client.close()


@respx.mock
def test_client_habits_list_raises_response_decode_error_for_invalid_json() -> None:
    respx.get("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(
            200,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ResponseDecodeError, match="invalid JSON"):
            client.habits.list()
    finally:
        client.close()


@respx.mock
def test_client_habits_create_raises_response_decode_error_for_invalid_json() -> None:
    respx.post("https://api.habitify.me/v2/habits").mock(
        return_value=httpx.Response(
            201,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ResponseDecodeError, match="invalid JSON"):
            client.habits.create(HabitCreateRequest(name="Morning Run", type=HabitType.GOOD))
    finally:
        client.close()


@respx.mock
def test_client_habits_get_raises_response_decode_error_for_invalid_json() -> None:
    respx.get("https://api.habitify.me/v2/habits/habit_123").mock(
        return_value=httpx.Response(
            200,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ResponseDecodeError, match="invalid JSON"):
            client.habits.get("habit_123")
    finally:
        client.close()


@respx.mock
def test_client_habits_journal_raises_response_decode_error_for_invalid_json() -> None:
    respx.get("https://api.habitify.me/v2/habits/journal").mock(
        return_value=httpx.Response(
            200,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ResponseDecodeError, match="invalid JSON"):
            client.habits.journal()
    finally:
        client.close()
