from __future__ import annotations

from typing import Any, Mapping

import httpx

from .errors import (
    NetworkError,
    ResponseDecodeError,
    TimeoutError,
    UnexpectedResponseShapeError,
    api_error_from_response,
)

DEFAULT_BASE_URL = "https://api.habitify.me/v2"
DEFAULT_TIMEOUT = 10.0


class HabitipyTransport:
    def __init__(self, *, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"X-API-Key": api_key},
        )

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = self._client.request(method, path, params=params)
        except httpx.TimeoutException as exc:
            raise TimeoutError("Habitify request timed out.") from exc
        except httpx.HTTPError as exc:
            raise NetworkError("Habitify request failed before receiving a response.") from exc

        if response.status_code >= 400:
            raise api_error_from_response(response)

        try:
            payload = response.json()
        except ValueError as exc:
            raise ResponseDecodeError("Habitify API returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise UnexpectedResponseShapeError("Habitify API response payload must be a JSON object.")
        return payload

    def close(self) -> None:
        self._client.close()