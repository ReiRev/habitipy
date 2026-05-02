from __future__ import annotations

import builtins
from datetime import date

import httpx

from ._resource import quote_path_value, request_model, request_no_content
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
    """Resource namespace for Habitify habits."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def get(self, habit_id: str) -> Habit:
        """Get a single habit by ID.

        Args:
            habit_id: Unique identifier of the habit.

        Returns:
            The requested :class:`Habit`.

        Raises:
            NotFoundError: If the habit does not exist.
        """
        return request_model(
            self._client,
            "GET",
            f"/habits/{quote_path_value(habit_id)}",
            HabitResponse,
        ).data

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
        """List habits with optional filtering and pagination.

        Args:
            archived: Filter by archived status.
            area_id: Filter by area ID.
            habit_type: Filter by habit type (``good`` or ``bad``).
            time_of_day: Filter by time-of-day ID.
            limit: Maximum number of items to return (1–100).
            offset: Number of items to skip.

        Returns:
            A :class:`HabitListPage` containing the habits and pagination info.
        """
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
        """Create a new habit.

        Args:
            request: Habit creation payload.

        Returns:
            The newly created :class:`Habit`.
        """
        return request_model(
            self._client,
            "POST",
            "/habits",
            HabitResponse,
            json=request.to_request_body(),
        ).data

    def archive(self, habit_id: str) -> None:
        """Archive a habit.

        Args:
            habit_id: Unique identifier of the habit to archive.

        Raises:
            NotFoundError: If the habit does not exist.
            ApiError: If the habit is already archived.
        """
        request_no_content(
            self._client,
            "POST",
            f"/habits/{quote_path_value(habit_id)}/archive",
            success_label="habit archive",
        )

    def delete(self, habit_id: str) -> None:
        """Delete a habit.

        Args:
            habit_id: Unique identifier of the habit to delete.

        Raises:
            NotFoundError: If the habit does not exist.
        """
        request_no_content(
            self._client,
            "DELETE",
            f"/habits/{quote_path_value(habit_id)}",
            success_label="habit deletion",
        )

    def create_log(self, habit_id: str, request: HabitLogRequest) -> HabitLogResponse:
        """Create a log entry for a habit.

        Args:
            habit_id: Unique identifier of the habit.
            request: Log creation payload.

        Returns:
            A :class:`HabitLogResponse` confirming the log was created.

        Raises:
            NotFoundError: If the habit does not exist.
            ApiError: If the request payload is invalid.
        """
        return request_model(
            self._client,
            "POST",
            f"/habits/{quote_path_value(habit_id)}/logs",
            HabitLogResponse,
            json=request.to_request_body(),
        )

    def delete_log(self, habit_id: str, log_id: str) -> SuccessMessageResponse:
        """Delete a log entry.

        Args:
            habit_id: Unique identifier of the habit.
            log_id: Unique identifier of the log entry.

        Returns:
            A :class:`SuccessMessageResponse` confirming the deletion.

        Raises:
            NotFoundError: If the habit or log entry does not exist.
        """
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
        """Mark a habit as completed for a given date.

        Args:
            habit_id: Unique identifier of the habit.
            request: Optional payload with the target date.

        Returns:
            A :class:`SuccessMessageResponse` confirming the action.
        """
        return self._post_log_action(habit_id, "complete", request)

    def fail_log(
        self,
        habit_id: str,
        request: HabitLogActionRequest | None = None,
    ) -> SuccessMessageResponse:
        """Mark a habit as failed for a given date.

        Args:
            habit_id: Unique identifier of the habit.
            request: Optional payload with the target date.

        Returns:
            A :class:`SuccessMessageResponse` confirming the action.
        """
        return self._post_log_action(habit_id, "failed", request)

    def skip_log(
        self,
        habit_id: str,
        request: HabitLogActionRequest | None = None,
    ) -> SuccessMessageResponse:
        """Mark a habit as skipped for a given date.

        Args:
            habit_id: Unique identifier of the habit.
            request: Optional payload with the target date.

        Returns:
            A :class:`SuccessMessageResponse` confirming the action.
        """
        return self._post_log_action(habit_id, "skipped", request)

    def undo_log(
        self,
        habit_id: str,
        request: HabitLogActionRequest | None = None,
    ) -> SuccessMessageResponse:
        """Undo the most recent log action for a habit.

        Args:
            habit_id: Unique identifier of the habit.
            request: Optional payload with the target date.

        Returns:
            A :class:`SuccessMessageResponse` confirming the action.
        """
        return self._post_log_action(habit_id, "undo", request)

    def list_notes(self, habit_id: str) -> builtins.list[HabitNote]:
        """List all notes for a habit.

        Args:
            habit_id: Unique identifier of the habit.

        Returns:
            List of :class:`HabitNote` objects.

        Raises:
            NotFoundError: If the habit does not exist.
        """
        return request_model(
            self._client,
            "GET",
            f"/habits/{quote_path_value(habit_id)}/notes",
            HabitNoteListResponse,
        ).data

    def create_note(self, habit_id: str, request: HabitNoteCreateRequest) -> HabitNote:
        """Create a note for a habit.

        Args:
            habit_id: Unique identifier of the habit.
            request: Note creation payload.

        Returns:
            The newly created :class:`HabitNote`.

        Raises:
            NotFoundError: If the habit does not exist.
        """
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
        """Update an existing note.

        Args:
            habit_id: Unique identifier of the habit.
            note_id: Unique identifier of the note.
            request: Note update payload.

        Returns:
            The updated :class:`HabitNote`.

        Raises:
            NotFoundError: If the habit or note does not exist.
        """
        return request_model(
            self._client,
            "PUT",
            f"/habits/{quote_path_value(habit_id)}/notes/{quote_path_value(note_id)}",
            HabitNote,
            json=request.to_request_body(),
        )

    def delete_note(self, habit_id: str, note_id: str) -> None:
        """Delete a note.

        Args:
            habit_id: Unique identifier of the habit.
            note_id: Unique identifier of the note.

        Raises:
            NotFoundError: If the habit or note does not exist.
        """
        request_no_content(
            self._client,
            "DELETE",
            f"/habits/{quote_path_value(habit_id)}/notes/{quote_path_value(note_id)}",
            success_label="habit note deletion",
        )

    def update(self, habit_id: str, request: HabitUpdateRequest) -> Habit:
        """Update an existing habit.

        Args:
            habit_id: Unique identifier of the habit to update.
            request: Habit update payload.

        Returns:
            The updated :class:`Habit`.

        Raises:
            NotFoundError: If the habit does not exist.
            ApiError: If the request payload is invalid.
        """
        return request_model(
            self._client,
            "PUT",
            f"/habits/{quote_path_value(habit_id)}",
            HabitResponse,
            json=request.to_request_body(),
        ).data

    def journal(self, *, journal_date: date | None = None) -> builtins.list[HabitJournalEntry]:
        """Fetch the habit journal for a specific date.

        Args:
            journal_date: Date to fetch the journal for. Defaults to today.

        Returns:
            List of :class:`HabitJournalEntry` objects.
        """
        params = HabitJournalParams(journal_date=journal_date)
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
        """Fetch statistics for a habit.

        Args:
            habit_id: Unique identifier of the habit.
            start_date: Start of the date range (inclusive).
            end_date: End of the date range (inclusive).

        Returns:
            A :class:`HabitStatistics` object.

        Raises:
            NotFoundError: If the habit does not exist.
            ApiError: If the date range is invalid.
        """
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
        """Internal helper to POST a log action endpoint."""
        request_body = request.to_request_body() if request is not None else None
        return request_model(
            self._client,
            "POST",
            f"/habits/{quote_path_value(habit_id)}/logs/{action}",
            SuccessMessageResponse,
            json=request_body,
        )
