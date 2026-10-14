"""
Request/response schemas for the meal_types module.

Field shapes match API Specification v1.0 Section 13 exactly.
"""

import uuid
from datetime import datetime

from pydantic import Field

from app.core.pagination import PaginationMeta
from app.core.schemas import CamelModel


class MealTypeCreateRequest(CamelModel):
    name: str = Field(min_length=1)


class MealTypeUpdateRequest(CamelModel):
    name: str = Field(min_length=1)


class MealTypeResponse(CamelModel):
    id: uuid.UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MealTypeListResponse(CamelModel):
    data: list[MealTypeResponse]
    pagination: PaginationMeta
