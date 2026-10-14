"""
Request/response schemas for the planned_quantities module.

Field shapes match API Specification v1.0 Section 16 exactly.
"""

import uuid
from datetime import date, datetime

from pydantic import Field

from app.core.pagination import PaginationMeta
from app.core.schemas import CamelModel


class PlannedQuantityCreateRequest(CamelModel):
    plan_date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    quantity: float = Field(ge=0)


class PlannedQuantityUpdateRequest(CamelModel):
    quantity: float = Field(ge=0)


class PlannedQuantityResponse(CamelModel):
    id: uuid.UUID
    plan_date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    quantity: float
    entered_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PlannedQuantityListResponse(CamelModel):
    data: list[PlannedQuantityResponse]
    pagination: PaginationMeta
