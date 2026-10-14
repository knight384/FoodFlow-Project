"""
Request/response schemas for the recommendations module.

Field shapes match API Specification v1.0 Section 19 exactly. No create
schema exists — recommendations are generated automatically by backend
logic (see service.py), never via a direct API write.
"""

import uuid
from datetime import date, datetime

from app.core.pagination import PaginationMeta
from app.core.schemas import CamelModel


class RecommendationResponse(CamelModel):
    id: uuid.UUID
    period_date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    estimated_surplus_quantity: float
    recommendation_text: str
    secondary_location_id: uuid.UUID | None
    is_advisory: bool
    generated_at: datetime


class RecommendationListResponse(CamelModel):
    data: list[RecommendationResponse]
    pagination: PaginationMeta
