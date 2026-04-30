from __future__ import annotations

import httpx

from .habits import HabitsResource

DEFAULT_BASE_URL = "https://api.habitify.me/v2"
DEFAULT_TIMEOUT = 10.0
API_KEY_HEADER = "X-API-Key"


class HabitipyClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        client: httpx.Client | None = None,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        if client is None and api_key is None:
            raise ValueError("api_key is required when client is not provided.")

        self._owns_client = client is None
        default_headers: dict[str, str] | None = None
        if client is None:
            assert api_key is not None
            default_headers = {API_KEY_HEADER: api_key}

        self._client = client or httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=DEFAULT_TIMEOUT,
            headers=default_headers,
        )

        if client is not None:
            if not str(self._client.base_url):
                self._client.base_url = httpx.URL(base_url.rstrip("/"))

            if api_key is not None:
                self._client.headers[API_KEY_HEADER] = api_key

            if API_KEY_HEADER not in self._client.headers:
                raise ValueError(
                    "api_key is required unless the provided client already has "
                    "an X-API-Key header."
                )

        self.habits = HabitsResource(self._client)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> HabitipyClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
