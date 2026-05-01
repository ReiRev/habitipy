from __future__ import annotations

import json

import httpx
import pytest
import respx

from habitipy import AreaCreateRequest, AreaUpdateRequest, HabitipyClient
from habitipy.errors import (
    AuthenticationError,
    NotFoundError,
    ResponseDecodeError,
    UnexpectedResponseShapeError,
)


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


def build_area_payload() -> dict[str, object]:
    return {"data": build_areas_payload()["data"][0]}


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
    assert isinstance(areas, list)
    assert areas[0].name == "Health"


@respx.mock
def test_client_areas_get_parses_response() -> None:
    route = respx.get("https://api.habitify.me/v2/areas/area_1").mock(
        return_value=httpx.Response(200, json=build_area_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        area = client.areas.get("area_1")
    finally:
        client.close()

    assert route.called
    assert area.id == "area_1"
    assert area.name == "Health"


@respx.mock
def test_client_areas_get_url_encodes_path_segment() -> None:
    route = respx.get("https://api.habitify.me/v2/areas/area%2Fwith%20spaces%3F%23").mock(
        return_value=httpx.Response(200, json=build_area_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        area = client.areas.get("area/with spaces?#")
    finally:
        client.close()

    assert route.called
    assert route.calls[0].request.url.raw_path == b"/v2/areas/area%2Fwith%20spaces%3F%23"
    assert area.id == "area_1"


@respx.mock
def test_client_areas_create_sends_expected_json_and_parses_response() -> None:
    route = respx.post("https://api.habitify.me/v2/areas").mock(
        return_value=httpx.Response(201, json=build_area_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        area = client.areas.create(
            AreaCreateRequest(name="Health", color_hex="#4ECDC4", icon="heart")
        )
    finally:
        client.close()

    assert route.called
    assert route.calls[0].request.headers["X-API-Key"] == "test-key"
    assert json.loads(route.calls[0].request.content.decode("utf-8")) == {
        "name": "Health",
        "colorHex": "#4ECDC4",
        "icon": "heart",
    }
    assert area.id == "area_1"


@respx.mock
def test_client_areas_update_sends_only_provided_fields_and_parses_response() -> None:
    route = respx.put("https://api.habitify.me/v2/areas/area_1").mock(
        return_value=httpx.Response(200, json=build_area_payload())
    )

    client = HabitipyClient(api_key="test-key")
    try:
        area = client.areas.update("area_1", AreaUpdateRequest(name="Wellness"))
    finally:
        client.close()

    assert route.called
    assert json.loads(route.calls[0].request.content.decode("utf-8")) == {"name": "Wellness"}
    assert area.name == "Health"


@respx.mock
def test_client_areas_delete_returns_none_on_204() -> None:
    route = respx.delete("https://api.habitify.me/v2/areas/area_1").mock(
        return_value=httpx.Response(204)
    )

    client = HabitipyClient(api_key="test-key")
    try:
        result = client.areas.delete("area_1")
    finally:
        client.close()

    assert route.called
    assert result is None


@respx.mock
def test_client_areas_delete_rejects_unexpected_success_status() -> None:
    respx.delete("https://api.habitify.me/v2/areas/area_1").mock(return_value=httpx.Response(200))

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(httpx.HTTPStatusError, match="Expected HTTP 204 No Content"):
            client.areas.delete("area_1")
    finally:
        client.close()


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
def test_client_areas_get_maps_not_found_error() -> None:
    respx.get("https://api.habitify.me/v2/areas/missing").mock(
        return_value=httpx.Response(404, json={"message": "Area not found"})
    )

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(NotFoundError, match="Area not found"):
            client.areas.get("missing")
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


@respx.mock
def test_client_areas_list_raises_unexpected_response_shape_error_for_non_object_json() -> None:
    respx.get("https://api.habitify.me/v2/areas").mock(return_value=httpx.Response(200, json=[]))

    client = HabitipyClient(api_key="test-key")
    try:
        with pytest.raises(UnexpectedResponseShapeError, match="must be a JSON object"):
            client.areas.list()
    finally:
        client.close()
