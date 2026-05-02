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
    """Resource namespace for Habitify areas."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self) -> list[Area]:
        """List all areas.

        Returns:
            List of :class:`Area` objects.
        """
        return request_model(self._client, "GET", "/areas", AreaListResponse).data

    def get(self, area_id: str) -> Area:
        """Get a single area by ID.

        Args:
            area_id: Unique identifier of the area.

        Returns:
            The requested :class:`Area`.

        Raises:
            NotFoundError: If the area does not exist.
        """
        return request_model(
            self._client,
            "GET",
            f"/areas/{quote_path_value(area_id)}",
            AreaResponse,
        ).data

    def create(self, request: AreaCreateRequest) -> Area:
        """Create a new area.

        Args:
            request: Area creation payload.

        Returns:
            The newly created :class:`Area`.
        """
        return request_model(
            self._client,
            "POST",
            "/areas",
            AreaResponse,
            json=request.to_request_body(),
        ).data

    def update(self, area_id: str, request: AreaUpdateRequest) -> Area:
        """Update an existing area.

        Args:
            area_id: Unique identifier of the area to update.
            request: Area update payload.

        Returns:
            The updated :class:`Area`.

        Raises:
            NotFoundError: If the area does not exist.
        """
        return request_model(
            self._client,
            "PUT",
            f"/areas/{quote_path_value(area_id)}",
            AreaResponse,
            json=request.to_request_body(),
        ).data

    def delete(self, area_id: str) -> None:
        """Delete an area.

        Args:
            area_id: Unique identifier of the area to delete.

        Raises:
            NotFoundError: If the area does not exist.
        """
        request_no_content(
            self._client,
            "DELETE",
            f"/areas/{quote_path_value(area_id)}",
            success_label="area deletion",
        )
