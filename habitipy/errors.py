from __future__ import annotations

from typing import Any

import httpx


class ResponseDecodeError(httpx.DecodingError):
    """Raised when a response body cannot be decoded as JSON."""


class UnexpectedResponseShapeError(ResponseDecodeError):
    """Raised when a response JSON payload does not match the expected top-level shape."""


class ApiError(httpx.HTTPStatusError):
    def __init__(
        self,
        message: str,
        *,
        request: httpx.Request,
        response: httpx.Response,
        payload: Any | None = None,
    ) -> None:
        super().__init__(message, request=request, response=response)
        self.payload = payload


class AuthenticationError(ApiError):
    """Raised when authentication is missing or invalid."""


class NotFoundError(ApiError):
    """Raised when the requested resource is missing."""


class RateLimitError(ApiError):
    """Raised when the Habitify API rate limit is exceeded."""


class ServerError(ApiError):
    """Raised when the Habitify API returns a server-side error."""


def raise_for_api_status(response: httpx.Response) -> None:
    payload: Any | None = None
    message = response.reason_phrase
    cause: httpx.HTTPStatusError | None = None

    try:
        response.raise_for_status()
        return
    except httpx.HTTPStatusError as exc:
        cause = exc
        request = exc.request
        response = exc.response

    try:
        payload = response.json()
    except ValueError:
        payload = response.text or None

    if isinstance(payload, dict):
        payload_message = payload.get("message") or payload.get("error")
        if isinstance(payload_message, str) and payload_message:
            message = payload_message
    elif isinstance(payload, str) and payload:
        message = payload

    error_cls: type[ApiError]
    if response.status_code == 400:
        error_cls = ApiError
    elif response.status_code == 401:
        error_cls = AuthenticationError
    elif response.status_code == 404:
        error_cls = NotFoundError
    elif response.status_code == 429:
        error_cls = RateLimitError
    elif response.status_code >= 500:
        error_cls = ServerError
    else:
        error_cls = ApiError

    raise error_cls(message, request=request, response=response, payload=payload) from cause
