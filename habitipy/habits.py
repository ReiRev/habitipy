from __future__ import annotations

import builtins
from datetime import date

import httpx

from ._resource import quote_path_value, request_json_object, request_model, request_no_content
from .errors import raise_for_api_status
from .models.habits import (
    Habit,
    HabitCreateRequest,
    HabitJournalEntry,
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
    HabitResponse,
    HabitStatistics,
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
        payload = request_json_object(self._client, "GET", f"/habits/{quote_path_value(habit_id)}")
        if isinstance(payload.get("data"), dict):
            return HabitResponse.model_validate(payload).data
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
        return request_model(
            self._client,
            "GET",
            "/habits",
            HabitListPage,
            params=params.to_query_params(),
        )

    def create(self, request: HabitCreateRequest) -> Habit:
        return request_model(
            self._client,
            "POST",
            "/habits",
            Habit,
            json=request.to_request_body(),
        )

    def archive(self, habit_id: str) -> None:
        request_no_content(
            self._client,
            "POST",
            f"/habits/{quote_path_value(habit_id)}/archive",
            success_label="habit archive",
        )

    def delete(self, habit_id: str) -> None:
        request_no_content(
            self._client,
            "DELETE",
            f"/habits/{quote_path_value(habit_id)}",
            success_label="habit deletion",
        )

    def create_log(self, habit_id: str, request: HabitLogRequest) -> HabitLogResponse:
        return request_model(
            self._client,
            "POST",
            f"/habits/{quote_path_value(habit_id)}/logs",
            HabitLogResponse,
            json=request.to_request_body(),
        )

    def delete_log(self, habit_id: str, log_id: str) -> SuccessMessageResponse:
        return request_model(
            self._client,
            "DELETE",
            f"/habits/{quote_path_value(habit_id)}/logs/{quote_path_value(log_id)}",
            SuccessMessageResponse,
        )

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

    def list_notes(self, habit_id: str) -> builtins.list[HabitNote]:
        return request_model(
            self._client,
            "GET",
            f"/habits/{quote_path_value(habit_id)}/notes",
            HabitNoteListResponse,
        ).data

    def create_note(self, habit_id: str, request: HabitNoteCreateRequest) -> HabitNote:
        return request_model(
            self._client,
            "POST",
            f"/habits/{quote_path_value(habit_id)}/notes",
            HabitNote,
            json=request.to_request_body(),
        )

    def update_note(
        self,
        habit_id: str,
        note_id: str,
        request: HabitNoteUpdateRequest,
    ) -> HabitNote:
        return request_model(
            self._client,
            "PUT",
            f"/habits/{quote_path_value(habit_id)}/notes/{quote_path_value(note_id)}",
            HabitNote,
            json=request.to_request_body(),
        )

    def delete_note(self, habit_id: str, note_id: str) -> None:
        request_no_content(
            self._client,
            "DELETE",
            f"/habits/{quote_path_value(habit_id)}/notes/{quote_path_value(note_id)}",
            success_label="habit note deletion",
        )

    def update(self, habit_id: str, request: HabitUpdateRequest) -> None:
        response = self._client.put(
            f"/habits/{quote_path_value(habit_id)}", json=request.to_request_body()
        )
        raise_for_api_status(response)

    def journal(self, *, date: date | None = None) -> builtins.list[HabitJournalEntry]:
        params = HabitJournalParams(journal_date=date)
        return request_model(
            self._client,
            "GET",
            "/habits/journal",
            HabitJournalPage,
            params=params.to_query_params(),
        ).data

    def statistics(
        self,
        habit_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> HabitStatistics:
        params = HabitStatisticsParams(start_date=start_date, end_date=end_date)
        return request_model(
            self._client,
            "GET",
            f"/habits/{quote_path_value(habit_id)}/statistics",
            HabitStatisticsResponse,
            params=params.to_query_params(),
        ).data

    def _post_log_action(
        self,
        habit_id: str,
        action: str,
        request: HabitLogActionRequest | None,
    ) -> SuccessMessageResponse:
        request_body = request.to_request_body() if request is not None else None
        if request_body:
            return request_model(
                self._client,
                "POST",
                f"/habits/{quote_path_value(habit_id)}/logs/{action}",
                SuccessMessageResponse,
                json=request_body,
            )
        return request_model(
            self._client,
            "POST",
            f"/habits/{quote_path_value(habit_id)}/logs/{action}",
            SuccessMessageResponse,
        )
