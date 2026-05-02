from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Pagination(BaseModel):
    """Pagination metadata returned by list endpoints.

    Attributes:
        total: Total number of items available across all pages.
        limit: Maximum number of items returned in the current page.
        offset: Number of items skipped before the current page.
    """

    model_config = ConfigDict(extra="ignore")

    total: int
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
