"""
Response schema for the classification module (read-only, computed — no
request/create schema exists, per API Specification v1.0 Section 18).
"""

import uuid
from datetime import date

from app.core.schemas import CamelModel


class ClassificationResponseItem(CamelModel):
    date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    status: str
    threshold_applied: float | None


class ClassificationListResponse(CamelModel):
    data: list[ClassificationResponseItem]
