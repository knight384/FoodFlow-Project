"""
Request/response schemas for the forecasting module.

Field shapes match API Specification v1.0 Section 15 exactly.
"""

import uuid
from datetime import date, datetime

from app.core.pagination import PaginationMeta
from app.core.schemas import CamelModel


class ForecastGenerateRequest(CamelModel):
    forecast_date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID


class ForecastResponse(CamelModel):
    id: uuid.UUID
    forecast_date: date
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    forecasted_demand: float
    generated_at: datetime


class ForecastListResponse(CamelModel):
    data: list[ForecastResponse]
    pagination: PaginationMeta
