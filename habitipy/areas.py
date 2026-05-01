from __future__ import annotations

import httpx

from ._resource import quote_path_value, request_model, request_no_content
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

    def list(self) -> list[Area]:
        return request_model(self._client, "GET", "/areas", AreaListResponse).data

    def get(self, area_id: str) -> Area:
        return request_model(
            self._client,
            "GET",
            f"/areas/{quote_path_value(area_id)}",
            AreaResponse,
        ).data

    def create(self, request: AreaCreateRequest) -> Area:
        return request_model(
            self._client,
            "POST",
            "/areas",
            AreaResponse,
            json=request.to_request_body(),
        ).data

    def update(self, area_id: str, request: AreaUpdateRequest) -> Area:
        return request_model(
            self._client,
            "PUT",
            f"/areas/{quote_path_value(area_id)}",
            AreaResponse,
            json=request.to_request_body(),
        ).data

    def delete(self, area_id: str) -> None:
        request_no_content(
            self._client,
            "DELETE",
            f"/areas/{quote_path_value(area_id)}",
            success_label="area deletion",
        )
