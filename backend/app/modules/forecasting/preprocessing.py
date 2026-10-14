"""
Forecasting data preparation (ML & Testing Plan v1.0 Section 5).

Retrieves already-validated historical_consumption records (validation
happened at import time — SRS-FR-008, Phase 4) for a given (location,
meal type), strictly ordered and strictly BEFORE the requested forecast
date, to avoid data leakage (using data from the forecast date itself or
later would defeat the purpose of a forecast).

Day-of-week derivation: per Database Specification v1.0 Section 6.5,
day-of-week is deliberately NOT persisted — it is derived here, at
preprocessing time, from each record's date (`date.weekday()`), exactly
as that design decision anticipated.
"""

import uuid
from datetime import date as date_type

from sqlalchemy.orm import Session

from app.modules.historical_data.models import HistoricalConsumption


def get_historical_series(
    db: Session,
    location_id: uuid.UUID,
    meal_type_id: uuid.UUID,
    before_date: date_type,
) -> list[tuple[date_type, float]]:
    """
    Returns (date, actual_consumed_quantity) pairs for the given
    (location, meal type), strictly before `before_date`, ordered
    chronologically (oldest first). Only draws from already-validated
    historical_consumption rows (Phase 4's import validation, SRS-FR-008)
    — no additional validation is re-applied here.
    """
    rows = (
        db.query(HistoricalConsumption)
        .filter(
            HistoricalConsumption.location_id == location_id,
            HistoricalConsumption.meal_type_id == meal_type_id,
            HistoricalConsumption.record_date < before_date,
        )
        .order_by(HistoricalConsumption.record_date.asc())
        .all()
    )
    return [(row.record_date, float(row.actual_consumed_quantity)) for row in rows]


def day_of_week(target_date: date_type) -> int:
    """0=Monday ... 6=Sunday, per Python's date.weekday() convention."""
    return target_date.weekday()
