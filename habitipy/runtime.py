from __future__ import annotations

from .client import HabitipyClient
from .models.habits import HabitListPage, HabitType
from .transport import DEFAULT_BASE_URL, DEFAULT_TIMEOUT

_default_client: HabitipyClient | None = None


def configure(
    *,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
) -> HabitipyClient:
    global _default_client

    if _default_client is not None:
        _default_client.close()

    _default_client = HabitipyClient(api_key=api_key, base_url=base_url, timeout=timeout)
    return _default_client


def get_client() -> HabitipyClient:
    if _default_client is None:
        raise RuntimeError("habitipy is not configured. Call habitipy.configure(api_key=...) first.")
    return _default_client


def reset() -> None:
    global _default_client

    if _default_client is not None:
        _default_client.close()
    _default_client = None


class _HabitsNamespace:
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
        return get_client().habits.list(
            archived=archived,
            area_id=area_id,
            habit_type=habit_type,
            time_of_day=time_of_day,
            limit=limit,
            offset=offset,
        )


habits = _HabitsNamespace()