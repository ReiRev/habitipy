from __future__ import annotations

from typing import Any

import httpx

from .errors import ResponseDecodeError, UnexpectedResponseShapeError


def decode_json_object(response: httpx.Response) -> dict[str, Any]:
    """Decode an HTTP response body as a JSON object.

    Args:
        response: HTTP response whose body should be parsed.

    Returns:
        The decoded JSON payload as a Python dict.

    Raises:
        ResponseDecodeError: When the body is not valid JSON.
        UnexpectedResponseShapeError: When the decoded value is not a dict.
    """
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
