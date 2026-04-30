from __future__ import annotations

import httpx

from .habits import HabitsResource

DEFAULT_BASE_URL = "https://api.habitify.me/v2"
DEFAULT_TIMEOUT = 10.0


class HabitipyClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        client: httpx.Client | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"X-API-Key": api_key} if api_key is not None else None,
        )

        if client is not None and api_key is not None and "X-API-Key" not in self._client.headers:
            self._client.headers["X-API-Key"] = api_key

        self.habits = HabitsResource(self._client)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> HabitipyClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
