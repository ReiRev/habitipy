from __future__ import annotations

from typing import Any, TypeVar
from urllib.parse import quote

import httpx
from pydantic import BaseModel

from ._json import decode_json_object
from .errors import ApiError, raise_for_api_status

ModelT = TypeVar("ModelT", bound=BaseModel)


def quote_path_value(value: str) -> str:
    """Percent-encode a path segment so it is safe for URL paths.

    Args:
        value: Raw path segment value.

    Returns:
        URL-encoded string with no safe characters preserved.
    """
    return quote(value, safe="")


def request_json_object(
    client: httpx.Client,
    method: str,
    path: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Send a request and return the decoded JSON object payload.

    Args:
        client: HTTP client to use.
        method: HTTP method (e.g. ``"GET"``, ``"POST"``).
        path: URL path relative to the client's base URL.
        **kwargs: Additional arguments forwarded to :meth:`httpx.Client.request`.

    Returns:
        The JSON response parsed as a dict.

    Raises:
        ApiError: When the response status is not successful.
        ResponseDecodeError: When the body is not valid JSON.
        UnexpectedResponseShapeError: When the body is not a JSON object.
    """
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
    """Send a request and validate the JSON response against a Pydantic model.

    Args:
        client: HTTP client to use.
        method: HTTP method.
        path: URL path relative to the client's base URL.
        model_type: Pydantic model class to validate the response against.
        **kwargs: Additional arguments forwarded to :meth:`httpx.Client.request`.

    Returns:
        An instance of *model_type* populated from the response.

    Raises:
        ApiError: When the response status is not successful.
        ResponseDecodeError: When the body is not valid JSON.
        UnexpectedResponseShapeError: When the body is not a JSON object.
        pydantic.ValidationError: When the payload does not match *model_type*.
    """
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
    """Send a request and expect an empty response with a specific status code.

    Args:
        client: HTTP client to use.
        method: HTTP method.
        path: URL path relative to the client's base URL.
        success_label: Human-readable label for the operation (used in error
            messages).
        expected_status: Expected HTTP status code. Defaults to ``204``.
        **kwargs: Additional arguments forwarded to :meth:`httpx.Client.request`.

    Raises:
        ApiError: When the response status is not successful or does not match
            *expected_status*.
    """
    response = client.request(method, path, **kwargs)
    raise_for_api_status(response)
    if response.status_code != expected_status:
        raise ApiError(
            (
                f"Expected HTTP {expected_status} No Content for {success_label}, "
                f"got {response.status_code}."
            ),
            request=response.request,
            response=response,
        )
