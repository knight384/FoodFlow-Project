"""
Forecasting module business logic (SRS-FR-011–013).

Implements the "single active forecast per period" model — a PROPOSED,
not company-confirmed, decision from Database Specification v1.0
Section 6.8/17: one Forecasted Demand row per (location, meal type,
date), enforced by that table's unique constraint (already in place
since Phase 2 — no migration change needed here).
"""

import uuid
from datetime import date as date_type

from sqlalchemy.orm import Session

from app.core.errors import AppError, NotFoundError, ValidationError
from app.modules.forecasting import interface
from app.modules.forecasting.models import ForecastedDemand
from app.modules.locations.models import Location
from app.modules.meal_types.models import MealType


class ForecastUnavailableError(AppError):
    """
    Maps to API Specification v1.0 Section 15/28's FORECAST_UNAVAILABLE
    category (422) — covers both documented cases: insufficient
    historical data, and a technical generation failure. The `message`
    text distinguishes which one occurred, per the two example messages
    in API Specification v1.0 Section 15.
    """

    category = "FORECAST_UNAVAILABLE"
    status_code = 422


def _validate_references(db: Session, location_id: uuid.UUID, meal_type_id: uuid.UUID) -> None:
    location = db.get(Location, location_id)
    if location is None or not location.is_active:
        raise ValidationError(f"Location '{location_id}' does not exist or is not active.")
    meal_type = db.get(MealType, meal_type_id)
    if meal_type is None or not meal_type.is_active:
        raise ValidationError(f"Meal type '{meal_type_id}' does not exist or is not active.")


def generate_or_get_forecast(
    db: Session, location_id: uuid.UUID, meal_type_id: uuid.UUID, forecast_date: date_type
) -> tuple[ForecastedDemand, bool]:
    """
    Returns (forecast, was_created). If an active forecast already
    exists for this exact period (single-active-forecast model), it is
    returned as-is (was_created=False) rather than regenerated — this
    implementation does not re-run prediction for a period that already
    has a stored forecast; regeneration/versioning policy is an open
    item (see app/modules/forecasting/interface.py's module docstring
    and Database Specification v1.0 Section 29, item 7).
    """
    _validate_references(db, location_id, meal_type_id)

    existing = (
        db.query(ForecastedDemand)
        .filter_by(location_id=location_id, meal_type_id=meal_type_id, forecast_date=forecast_date)
        .one_or_none()
    )
    if existing is not None:
        return existing, False

    try:
        result = interface.predict(db, location_id, meal_type_id, forecast_date)
    except interface.InsufficientHistoricalDataError as exc:
        raise ForecastUnavailableError(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - deliberate: any other failure is a technical
        # generation failure, per API Specification v1.0 Section 15's
        # second documented FORECAST_UNAVAILABLE message variant.
        raise ForecastUnavailableError(
            "Forecast is temporarily unavailable. Please try again shortly."
        ) from exc

    forecast = ForecastedDemand(
        forecast_date=forecast_date,
        location_id=location_id,
        meal_type_id=meal_type_id,
        predicted_quantity=result.predicted_quantity,
        model_version=result.model_version,
    )
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    return forecast, True


def list_forecasts(
    db: Session,
    page: int,
    page_size: int,
    location_id: uuid.UUID | None = None,
    meal_type_id: uuid.UUID | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
) -> tuple[list[ForecastedDemand], int]:
    query = db.query(ForecastedDemand)
    if location_id is not None:
        query = query.filter(ForecastedDemand.location_id == location_id)
    if meal_type_id is not None:
        query = query.filter(ForecastedDemand.meal_type_id == meal_type_id)
    if date_from is not None:
        query = query.filter(ForecastedDemand.forecast_date >= date_from)
    if date_to is not None:
        query = query.filter(ForecastedDemand.forecast_date <= date_to)

    total_items = query.count()
    forecasts = (
        query.order_by(ForecastedDemand.forecast_date.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return forecasts, total_items


def get_forecast(db: Session, forecast_id: uuid.UUID) -> ForecastedDemand:
    forecast = db.get(ForecastedDemand, forecast_id)
    if forecast is None:
        raise NotFoundError(f"Forecast '{forecast_id}' not found.")
    return forecast
