"""
Narrow prediction interface (TRD v1.0 Section 12): given a
(date, meal type, location), return a Forecasted Demand value, or a
clear "insufficient data" signal — never a fabricated value.

This is the ONLY place the selected algorithm (algorithm.recent_period_mean)
is invoked for actual forecast generation. Kept intentionally narrow so
the algorithm can be replaced later (e.g., once real operational data
justifies re-evaluating the model-selection decision documented in
algorithm.py) without touching the backend's other modules, the API
layer, or the database schema (TRD v1.0 Section 12's explicit design
goal).
"""

import uuid
from dataclasses import dataclass
from datetime import date as date_type

from sqlalchemy.orm import Session

from app.config import get_settings
from app.modules.forecasting.algorithm import recent_period_mean
from app.modules.forecasting.preprocessing import get_historical_series


@dataclass(frozen=True)
class ForecastResult:
    predicted_quantity: float
    model_version: str


class InsufficientHistoricalDataError(Exception):
    """
    Raised when there is not enough historical data to produce a
    reliable forecast for the requested period (SRS-FR-013).

    The minimum-data threshold is a PROVISIONAL configuration value
    (app.config.Settings.min_historical_records_for_forecast) — not a
    confirmed business decision (ML & Testing Plan v1.0 Section 12,
    item 3; carried forward from every prior planning document).
    """


# Identifies which algorithm produced a forecast — a lightweight
# traceability label only (Database Specification v1.0 Section 6.8:
# "not a full model registry"), not a version-management system.
MODEL_VERSION_LABEL = "recent-period-mean-v1"


def predict(
    db: Session, location_id: uuid.UUID, meal_type_id: uuid.UUID, forecast_date: date_type
) -> ForecastResult:
    """
    Produces a Forecasted Demand value for the requested period using
    the selected production algorithm (see algorithm.py's module
    docstring for the evidence-based selection rationale).

    Raises InsufficientHistoricalDataError if the (location, meal type)
    combination does not have at least
    `settings.min_historical_records_for_forecast` historical records
    strictly before `forecast_date`.
    """
    settings = get_settings()
    history = get_historical_series(db, location_id, meal_type_id, forecast_date)

    if len(history) < settings.min_historical_records_for_forecast:
        raise InsufficientHistoricalDataError(
            f"Only {len(history)} historical record(s) available for this location/meal "
            f"type before {forecast_date.isoformat()}; at least "
            f"{settings.min_historical_records_for_forecast} are required to generate a "
            f"reliable forecast."
        )

    predicted_quantity = recent_period_mean(history, settings.forecast_recent_window_size)
    return ForecastResult(predicted_quantity=predicted_quantity, model_version=MODEL_VERSION_LABEL)
