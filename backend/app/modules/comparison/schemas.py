"""
Response schema for the comparison module (read-only, computed — no
request/create schema exists, per API Specification v1.0 Section 17).
"""

import uuid
from datetime import date

from app.core.schemas import CamelModel


class ComparisonResponseItem(CamelModel):
    date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    forecasted_demand: float | None
    planned_quantity: float | None
    potential_surplus: float | None
    potential_shortage: float | None
    variance_percentage: float | None


class ComparisonListResponse(CamelModel):
    data: list[ComparisonResponseItem]
