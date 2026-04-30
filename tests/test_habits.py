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
    HabitLogRequest,
    HabitLogResponse,
    HabitStatisticsResponse,
    HabitType,
    UnitSymbol,
)
from habitipy.errors import (
    ApiError,
    AuthenticationError,
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


def build_habit_log_response_payload() -> dict[str, object]:
    return {"message": "Habit log created successfully"}


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

    assert page.data[0].status is HabitJournalStatus.COMPLETED
    assert page.data[0].type is HabitType.GOOD
    assert page.data[0].current_streak.unit is HabitJournalStreakUnit.DAY
    assert page.data[0].progress.periodicity is GoalPeriodicity.DAILY
    assert page.data[0].log_info.type.value == "manual"


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

    assert isinstance(statistics, HabitStatisticsResponse)
    assert statistics.data.id == "habit_123"
    assert statistics.data.type is HabitType.GOOD
    assert statistics.data.total_logs == 12.5
    assert statistics.data.skips == 1
    assert statistics.data.fails == 2
    assert statistics.data.completions == 3
    assert statistics.data.unit.symbol is UnitSymbol.KM
    assert statistics.data.periodicity is GoalPeriodicity.DAILY
    assert statistics.data.avg == 1.25
    assert statistics.data.daily_progress[0].status is HabitJournalStatus.COMPLETED
    assert statistics.data.daily_progress[1].status is HabitJournalStatus.IN_PROGRESS


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
