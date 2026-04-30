from __future__ import annotations

from typing import Any

import httpx


class HabitipyError(Exception):
    """Base exception for habitipy."""


class NetworkError(HabitipyError):
    """Raised when an HTTP transport failure prevents a response from being received."""


class TimeoutError(NetworkError):
    """Raised when an HTTP request times out."""


class ResponseDecodeError(HabitipyError):
    """Raised when a response body cannot be decoded as JSON."""


class UnexpectedResponseShapeError(HabitipyError):
    """Raised when a response JSON payload does not match the expected top-level shape."""


class ApiError(HabitipyError):
    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        payload: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class BadRequestError(ApiError):
    """Raised when the API rejects request parameters or body data."""


class AuthenticationError(ApiError):
    """Raised when authentication is missing or invalid."""


class NotFoundError(ApiError):
    """Raised when the requested resource is missing."""


class RateLimitError(ApiError):
    """Raised when the Habitify API rate limit is exceeded."""


class ServerError(ApiError):
    """Raised when the Habitify API returns a server-side error."""


def api_error_from_response(response: httpx.Response) -> ApiError:
    payload: Any | None = None
    message = response.reason_phrase

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
        error_cls = BadRequestError
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

    return error_cls(response.status_code, message, payload=payload)