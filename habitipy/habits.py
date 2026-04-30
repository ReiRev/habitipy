from __future__ import annotations

from .models.habits import HabitListPage, HabitListParams, HabitType
from .transport import HabitipyTransport


class HabitsResource:
    def __init__(self, transport: HabitipyTransport) -> None:
        self._transport = transport

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
        payload = self._transport.request_json("GET", "/habits", params=params.to_query_params())
        return HabitListPage.model_validate(payload)