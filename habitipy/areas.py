from __future__ import annotations

from typing import Any

import httpx

from .errors import ResponseDecodeError, UnexpectedResponseShapeError, raise_for_api_status
from .models.habits import AreaListResponse


class AreasResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self) -> AreaListResponse:
        response = self._client.get("/areas")
        raise_for_api_status(response)
        payload = _decode_json_object(response)
        return AreaListResponse.model_validate(payload)


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
