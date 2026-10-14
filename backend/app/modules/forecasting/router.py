"""
Forecasting module routes: FC-001, FC-002, FC-003 — exact paths,
methods, and behavior per API Specification v1.0 Section 9/15.

Authorization: Manager and Admin, per the API Specification's resolved
authorization column for FC-001. FC-002/FC-003 additionally list
"Operations Staff (pending confirmation)" — that cell is NOT
implemented here, consistent with how every other pending-confirmation
cell has been handled since Phase 3 (require_roles restricted to the
confirmed roles only).
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, build_pagination_meta
from app.database import get_db
from app.modules.forecasting import service
from app.modules.forecasting.models import ForecastedDemand
from app.modules.forecasting.schemas import (
    ForecastGenerateRequest,
    ForecastListResponse,
    ForecastResponse,
)

router = APIRouter(
    prefix="/forecasts",
    tags=["forecasts"],
    dependencies=[Depends(require_roles("manager", "administrator"))],
)


def _to_response(forecast: ForecastedDemand) -> ForecastResponse:
    return ForecastResponse(
        id=forecast.id,
        forecast_date=forecast.forecast_date,
        location_id=forecast.location_id,
        meal_type_id=forecast.meal_type_id,
        forecasted_demand=float(forecast.predicted_quantity),
        generated_at=forecast.generated_at,
    )


@router.post("", response_model=ForecastResponse)
def generate_forecast(
    payload: ForecastGenerateRequest, response: Response, db: Session = Depends(get_db)
) -> ForecastResponse:
    """
    FC-001. Returns 201 if a new forecast was generated, or 200 if an
    existing active forecast for this exact period was returned instead
    (single-active-forecast model — API Specification v1.0 Section 15).
    Raises FORECAST_UNAVAILABLE (422) if historical data is insufficient
    or generation otherwise fails — never a fabricated value.
    """
    forecast, was_created = service.generate_or_get_forecast(
        db, payload.location_id, payload.meal_type_id, payload.forecast_date
    )
    response.status_code = status.HTTP_201_CREATED if was_created else status.HTTP_200_OK
    return _to_response(forecast)


@router.get("", response_model=ForecastListResponse, status_code=status.HTTP_200_OK)
def list_forecasts(
    location_id: uuid.UUID | None = Query(default=None, alias="locationId"),
    meal_type_id: uuid.UUID | None = Query(default=None, alias="mealTypeId"),
    date_from: date | None = Query(default=None, alias="dateFrom"),
    date_to: date | None = Query(default=None, alias="dateTo"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
    db: Session = Depends(get_db),
) -> ForecastListResponse:
    """FC-002. Manager/Admin only (Operations Staff cell not implemented — see module docstring)."""
    forecasts, total_items = service.list_forecasts(
        db, page, page_size, location_id, meal_type_id, date_from, date_to
    )
    return ForecastListResponse(
        data=[_to_response(f) for f in forecasts],
        pagination=build_pagination_meta(page, page_size, total_items),
    )


@router.get("/{forecast_id}", response_model=ForecastResponse, status_code=status.HTTP_200_OK)
def get_forecast(forecast_id: uuid.UUID, db: Session = Depends(get_db)) -> ForecastResponse:
    """FC-003. Manager/Admin only."""
    forecast = service.get_forecast(db, forecast_id)
    return _to_response(forecast)
