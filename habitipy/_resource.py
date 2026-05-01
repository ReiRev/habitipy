from __future__ import annotations

from typing import Any, TypeVar
from urllib.parse import quote

import httpx
from pydantic import BaseModel

from ._json import decode_json_object
from .errors import raise_for_api_status

ModelT = TypeVar("ModelT", bound=BaseModel)


def quote_path_value(value: str) -> str:
    return quote(value, safe="")


def request_json_object(
    client: httpx.Client,
    method: str,
    path: str,
    **kwargs: Any,
) -> dict[str, Any]:
    response = client.request(method, path, **kwargs)
    raise_for_api_status(response)
    return decode_json_object(response)


def request_model(
    client: httpx.Client,
    method: str,
    path: str,
    model_type: type[ModelT],
    **kwargs: Any,
) -> ModelT:
    payload = request_json_object(client, method, path, **kwargs)
    return model_type.model_validate(payload)


def request_no_content(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    success_label: str,
    expected_status: int = 204,
    **kwargs: Any,
) -> None:
    response = client.request(method, path, **kwargs)
    raise_for_api_status(response)
    if response.status_code != expected_status:
        raise httpx.HTTPStatusError(
            (
                f"Expected HTTP {expected_status} No Content for {success_label}, "
                f"got {response.status_code}."
            ),
            request=response.request,
            response=response,
        )
