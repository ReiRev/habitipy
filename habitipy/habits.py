from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import quote

import httpx

from .errors import ResponseDecodeError, UnexpectedResponseShapeError, raise_for_api_status
from .models.habits import (
    Habit,
    HabitCreateRequest,
    HabitJournalPage,
    HabitJournalParams,
    HabitListPage,
    HabitListParams,
    HabitLogActionRequest,
    HabitLogRequest,
    HabitLogResponse,
    HabitNote,
    HabitNoteCreateRequest,
    HabitNoteListResponse,
    HabitNoteUpdateRequest,
    HabitStatisticsParams,
    HabitStatisticsResponse,
    HabitType,
    HabitUpdateRequest,
    SuccessMessageResponse,
)


class HabitsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def get(self, habit_id: str) -> Habit:
        response = self._client.get(f"/habits/{_quote_path_value(habit_id)}")
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return Habit.model_validate(payload)

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

    def archive(self, habit_id: str) -> None:
        response = self._client.post(f"/habits/{_quote_path_value(habit_id)}/archive")
        raise_for_api_status(response)

    def delete(self, habit_id: str) -> None:
        response = self._client.delete(f"/habits/{_quote_path_value(habit_id)}")
        raise_for_api_status(response)
        if response.status_code != 204:
            raise httpx.HTTPStatusError(
                f"Expected HTTP 204 No Content for habit deletion, got {response.status_code}.",
                request=response.request,
                response=response,
            )

    def create_log(self, habit_id: str, request: HabitLogRequest) -> HabitLogResponse:
        response = self._client.post(
            f"/habits/{_quote_path_value(habit_id)}/logs",
            json=request.to_request_body(),
        )
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return HabitLogResponse.model_validate(payload)

    def delete_log(self, habit_id: str, log_id: str) -> SuccessMessageResponse:
        response = self._client.delete(
            f"/habits/{_quote_path_value(habit_id)}/logs/{_quote_path_value(log_id)}"
        )
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return SuccessMessageResponse.model_validate(payload)

    def complete_log(
        self,
        habit_id: str,
        request: HabitLogActionRequest | None = None,
    ) -> SuccessMessageResponse:
        return self._post_log_action(habit_id, "complete", request)

    def fail_log(
        self,
        habit_id: str,
        request: HabitLogActionRequest | None = None,
    ) -> SuccessMessageResponse:
        return self._post_log_action(habit_id, "failed", request)

    def skip_log(
        self,
        habit_id: str,
        request: HabitLogActionRequest | None = None,
    ) -> SuccessMessageResponse:
        return self._post_log_action(habit_id, "skipped", request)

    def undo_log(
        self,
        habit_id: str,
        request: HabitLogActionRequest | None = None,
    ) -> SuccessMessageResponse:
        return self._post_log_action(habit_id, "undo", request)

    def list_notes(self, habit_id: str) -> HabitNoteListResponse:
        response = self._client.get(f"/habits/{_quote_path_value(habit_id)}/notes")
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return HabitNoteListResponse.model_validate(payload)

    def create_note(self, habit_id: str, request: HabitNoteCreateRequest) -> HabitNote:
        response = self._client.post(
            f"/habits/{_quote_path_value(habit_id)}/notes",
            json=request.to_request_body(),
        )
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return HabitNote.model_validate(payload)

    def update_note(
        self,
        habit_id: str,
        note_id: str,
        request: HabitNoteUpdateRequest,
    ) -> HabitNote:
        response = self._client.put(
            f"/habits/{_quote_path_value(habit_id)}/notes/{_quote_path_value(note_id)}",
            json=request.to_request_body(),
        )
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return HabitNote.model_validate(payload)

    def delete_note(self, habit_id: str, note_id: str) -> None:
        response = self._client.delete(
            f"/habits/{_quote_path_value(habit_id)}/notes/{_quote_path_value(note_id)}"
        )
        raise_for_api_status(response)
        if response.status_code != 204:
            raise httpx.HTTPStatusError(
                "Expected HTTP 204 No Content for habit note deletion, "
                f"got {response.status_code}.",
                request=response.request,
                response=response,
            )

    def update(self, habit_id: str, request: HabitUpdateRequest) -> None:
        response = self._client.put(
            f"/habits/{_quote_path_value(habit_id)}", json=request.to_request_body()
        )
        raise_for_api_status(response)

    def journal(self, *, date: date | None = None) -> HabitJournalPage:
        params = HabitJournalParams(journal_date=date)
        response = self._client.get("/habits/journal", params=params.to_query_params())
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return HabitJournalPage.model_validate(payload)

    def statistics(
        self,
        habit_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> HabitStatisticsResponse:
        params = HabitStatisticsParams(start_date=start_date, end_date=end_date)
        response = self._client.get(
            f"/habits/{_quote_path_value(habit_id)}/statistics",
            params=params.to_query_params(),
        )
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return HabitStatisticsResponse.model_validate(payload)

    def _post_log_action(
        self,
        habit_id: str,
        action: str,
        request: HabitLogActionRequest | None,
    ) -> SuccessMessageResponse:
        request_body = request.to_request_body() if request is not None else None
        if request_body:
            response = self._client.post(
                f"/habits/{_quote_path_value(habit_id)}/logs/{action}",
                json=request_body,
            )
        else:
            response = self._client.post(f"/habits/{_quote_path_value(habit_id)}/logs/{action}")
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return SuccessMessageResponse.model_validate(payload)


def _quote_path_value(value: str) -> str:
    return quote(value, safe="")


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
