"""
Response schema for the reports module (read-only, historical — no
request/create schema exists, per API Specification v1.0 Section 21).

No `recommendation` field — unlike Dashboard, the Reports API's
documented response shape explicitly lists only "date, forecastedDemand,
plannedQuantity, variance figures, status."
"""

import uuid
from datetime import date

from app.core.pagination import PaginationMeta
from app.core.schemas import CamelModel


class ReportResponseItem(CamelModel):
    date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    forecasted_demand: float | None
    planned_quantity: float | None
    potential_surplus: float | None
    potential_shortage: float | None
    variance_percentage: float | None
    status: str


class ReportListResponse(CamelModel):
    data: list[ReportResponseItem]
    pagination: PaginationMeta
