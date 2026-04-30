from __future__ import annotations

import httpx
import pytest
import respx

from habitipy import AreaListResponse, HabitipyClient
from habitipy.errors import AuthenticationError, ResponseDecodeError


def build_areas_payload() -> dict[str, object]:
    return {
        "data": [
            {
                "id": "area_1",
                "name": "Health",
                "colorHex": "#4ECDC4",
                "icon": "heart",
                "createdAt": "2024-01-01T06:00:00Z",
                "description": "Health habits",
            }
        ]
    }


@respx.mock
def test_client_areas_list_parses_response() -> None:
    route = respx.get("https://api.habitify.me/v2/areas").mock(
        return_value=httpx.Response(200, json=build_areas_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        areas = client.areas.list()
    finally:
        client.close()

    assert route.called
    assert isinstance(areas, AreaListResponse)
    assert areas.data[0].name == "Health"


@respx.mock
def test_client_areas_list_maps_authentication_error() -> None:
    respx.get("https://api.habitify.me/v2/areas").mock(
        return_value=httpx.Response(401, json={"message": "Missing API key"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(AuthenticationError, match="Missing API key"):
            client.areas.list()
    finally:
        client.close()


@respx.mock
def test_client_areas_list_raises_response_decode_error_for_invalid_json() -> None:
    respx.get("https://api.habitify.me/v2/areas").mock(
        return_value=httpx.Response(
            200,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(ResponseDecodeError, match="invalid JSON"):
            client.areas.list()
    finally:
        client.close()
