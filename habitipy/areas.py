from __future__ import annotations

from urllib.parse import quote

import httpx

from ._json import decode_json_object
from .errors import raise_for_api_status
from .models.habits import (
    Area,
    AreaCreateRequest,
    AreaListResponse,
    AreaResponse,
    AreaUpdateRequest,
)


class AreasResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self) -> AreaListResponse:
        response = self._client.get("/areas")
        raise_for_api_status(response)
        payload = decode_json_object(response)
        return AreaListResponse.model_validate(payload)

    def get(self, area_id: str) -> Area:
        response = self._client.get(f"/areas/{_quote_path_value(area_id)}")
        raise_for_api_status(response)
        payload = decode_json_object(response)
        return AreaResponse.model_validate(payload).data

    def create(self, request: AreaCreateRequest) -> Area:
        response = self._client.post("/areas", json=request.to_request_body())
        raise_for_api_status(response)
        payload = decode_json_object(response)
        return AreaResponse.model_validate(payload).data

    def update(self, area_id: str, request: AreaUpdateRequest) -> Area:
        response = self._client.put(
            f"/areas/{_quote_path_value(area_id)}",
            json=request.to_request_body(),
        )
        raise_for_api_status(response)
        payload = decode_json_object(response)
        return AreaResponse.model_validate(payload).data

    def delete(self, area_id: str) -> None:
        response = self._client.delete(f"/areas/{_quote_path_value(area_id)}")
        raise_for_api_status(response)
        if response.status_code != 204:
            raise httpx.HTTPStatusError(
                f"Expected HTTP 204 No Content for area deletion, got {response.status_code}.",
                request=response.request,
                response=response,
            )


def _quote_path_value(value: str) -> str:
    return quote(value, safe="")
