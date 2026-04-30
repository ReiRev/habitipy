from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Pagination(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total: int
    limit: int
    offset: int