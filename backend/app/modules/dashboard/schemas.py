"""
Response schema for the dashboard module (read-only, aggregated — no
request/create schema exists, per API Specification v1.0 Section 20).
"""

import uuid
from datetime import date

from app.core.schemas import CamelModel


class DashboardRecommendation(CamelModel):
    id: uuid.UUID
    estimated_surplus_quantity: float
    recommendation_text: str
    is_advisory: bool


class DashboardResponseItem(CamelModel):
    date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    forecasted_demand: float | None
    planned_quantity: float | None
    potential_surplus: float | None
    potential_shortage: float | None
    variance_percentage: float | None
    status: str
    recommendation: DashboardRecommendation | None


class DashboardListResponse(CamelModel):
    """No pagination field — API Specification v1.0 Section 20's
    documented response is `{ data: [...] }` only, unlike Reports."""

    data: list[DashboardResponseItem]
