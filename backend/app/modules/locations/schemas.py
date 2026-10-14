"""
Request/response schemas for the locations module.

Field shapes match API Specification v1.0 Section 12 exactly.
"""

import uuid
from datetime import datetime

from pydantic import Field

from app.core.pagination import PaginationMeta
from app.core.schemas import CamelModel


class LocationCreateRequest(CamelModel):
    name: str = Field(min_length=1)


class LocationUpdateRequest(CamelModel):
    name: str = Field(min_length=1)


class LocationResponse(CamelModel):
    id: uuid.UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LocationListResponse(CamelModel):
    data: list[LocationResponse]
    pagination: PaginationMeta
