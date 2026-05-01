from __future__ import annotations

import httpx

from ._json import decode_json_object
from .errors import raise_for_api_status
from .models.habits import AreaListResponse


class AreasResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self) -> AreaListResponse:
        response = self._client.get("/areas")
        raise_for_api_status(response)
        payload = decode_json_object(response)
        return AreaListResponse.model_validate(payload)
