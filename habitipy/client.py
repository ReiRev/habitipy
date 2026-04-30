from __future__ import annotations

from .habits import HabitsResource
from .transport import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, HabitipyTransport


class HabitipyClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._transport = HabitipyTransport(api_key=api_key, base_url=base_url, timeout=timeout)
        self.habits = HabitsResource(self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "HabitipyClient":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()