from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from .errors import ResponseDecodeError, UnexpectedResponseShapeError, raise_for_api_status
from .models.habits import (
    Habit,
    HabitCreateRequest,
    HabitJournalPage,
    HabitJournalParams,
    HabitListPage,
    HabitListParams,
    HabitType,
)


class HabitsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(
        self,
        *,
        archived: bool | None = None,
        area_id: str | None = None,
        habit_type: HabitType | None = None,
        time_of_day: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> HabitListPage:
        params = HabitListParams(
            archived=archived,
            area_id=area_id,
            habit_type=habit_type,
            time_of_day=time_of_day,
            limit=limit,
            offset=offset,
        )
        response = self._client.get("/habits", params=params.to_query_params())
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return HabitListPage.model_validate(payload)

    def create(self, request: HabitCreateRequest) -> Habit:
        response = self._client.post("/habits", json=request.to_request_body())
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return Habit.model_validate(payload)

    def delete(self, habit_id: str) -> None:
        response = self._client.delete(f"/habits/{habit_id}")
        raise_for_api_status(response)
        if response.status_code != 204:
            raise httpx.HTTPStatusError(
                f"Expected HTTP 204 No Content for habit deletion, got {response.status_code}.",
                request=response.request,
                response=response,
            )

    def journal(self, *, date: date | None = None) -> HabitJournalPage:
        params = HabitJournalParams(journal_date=date)
        response = self._client.get("/habits/journal", params=params.to_query_params())
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return HabitJournalPage.model_validate(payload)


def _decode_json_object(response: httpx.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as exc:
        raise ResponseDecodeError(
            "Habitify API returned invalid JSON.", request=response.request
        ) from exc

    if not isinstance(payload, dict):
        raise UnexpectedResponseShapeError(
            "Habitify API response payload must be a JSON object.",
            request=response.request,
        )
    return payload
