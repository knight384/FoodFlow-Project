"""
Comparison module business logic (SRS-FR-018–020).

Per Database Specification v1.0 Section 12 and API Specification v1.0
Section 17: Variance is computed dynamically from `forecasted_demand`
and `planned_quantity` rows for a matching period — there is NO
persisted `variance` table, and none is created by this module.

=== Zero-forecast edge case: NOT resolved, handled safely ===
When Forecasted Demand is exactly 0, a percentage-based variance is
mathematically undefined (division by zero). Per this phase's explicit
instruction ("do not produce division-by-zero, infinity, misleading
percentages... clearly document the unresolved behavior"), this
implementation returns `None` (JSON `null`) for `variance_percentage` in
that case, exactly as API Specification v1.0 Section 17 already commits
to ("this API will omit or null the field... pending confirmation of
the intended behavior"). This is not a resolution of the open question —
just a safe placeholder pending one.
"""

import uuid
from dataclasses import dataclass
from datetime import date as date_type

from sqlalchemy.orm import Session

from app.modules.forecasting.models import ForecastedDemand
from app.modules.planned_quantities.models import PlannedQuantity


@dataclass
class ComparisonRow:
    date: date_type
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    forecasted_demand: float | None
    planned_quantity: float | None
    potential_surplus: float | None
    potential_shortage: float | None
    variance_percentage: float | None


def _compute_row(
    key: tuple[date_type, uuid.UUID, uuid.UUID],
    forecasted_demand: float | None,
    planned_quantity: float | None,
) -> ComparisonRow:
    period_date, location_id, meal_type_id = key

    if forecasted_demand is None or planned_quantity is None:
        # Per API Specification v1.0 Section 17: if only one of the two
        # source values exists, potentialSurplus/potentialShortage/
        # variancePercentage are all null rather than a misleading 0.
        return ComparisonRow(
            period_date, location_id, meal_type_id, forecasted_demand, planned_quantity, None, None, None
        )

    raw_variance = planned_quantity - forecasted_demand
    potential_surplus = raw_variance if raw_variance > 0 else 0.0
    potential_shortage = -raw_variance if raw_variance < 0 else 0.0

    if forecasted_demand == 0:
        variance_percentage = None  # zero-forecast edge case — see module docstring
    else:
        variance_percentage = round((raw_variance / forecasted_demand) * 100, 2)

    return ComparisonRow(
        period_date,
        location_id,
        meal_type_id,
        forecasted_demand,
        planned_quantity,
        potential_surplus,
        potential_shortage,
        variance_percentage,
    )


def compute_comparisons(
    db: Session,
    location_id: uuid.UUID | None = None,
    meal_type_id: uuid.UUID | None = None,
    single_date: date_type | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
) -> list[ComparisonRow]:
    """
    Returns one ComparisonRow per (date, location, meal type) period that
    has at least a Forecasted Demand or a Planned Quantity matching the
    given filters.
    """
    forecast_query = db.query(ForecastedDemand)
    planned_query = db.query(PlannedQuantity)

    if location_id is not None:
        forecast_query = forecast_query.filter(ForecastedDemand.location_id == location_id)
        planned_query = planned_query.filter(PlannedQuantity.location_id == location_id)
    if meal_type_id is not None:
        forecast_query = forecast_query.filter(ForecastedDemand.meal_type_id == meal_type_id)
        planned_query = planned_query.filter(PlannedQuantity.meal_type_id == meal_type_id)
    if single_date is not None:
        forecast_query = forecast_query.filter(ForecastedDemand.forecast_date == single_date)
        planned_query = planned_query.filter(PlannedQuantity.plan_date == single_date)
    else:
        if date_from is not None:
            forecast_query = forecast_query.filter(ForecastedDemand.forecast_date >= date_from)
            planned_query = planned_query.filter(PlannedQuantity.plan_date >= date_from)
        if date_to is not None:
            forecast_query = forecast_query.filter(ForecastedDemand.forecast_date <= date_to)
            planned_query = planned_query.filter(PlannedQuantity.plan_date <= date_to)

    forecasts_by_key: dict[tuple[date_type, uuid.UUID, uuid.UUID], float] = {
        (f.forecast_date, f.location_id, f.meal_type_id): float(f.predicted_quantity)
        for f in forecast_query.all()
    }
    planned_by_key: dict[tuple[date_type, uuid.UUID, uuid.UUID], float] = {
        (p.plan_date, p.location_id, p.meal_type_id): float(p.quantity)
        for p in planned_query.all()
    }

    all_keys = set(forecasts_by_key.keys()) | set(planned_by_key.keys())
    rows = [
        _compute_row(key, forecasts_by_key.get(key), planned_by_key.get(key)) for key in all_keys
    ]
    rows.sort(key=lambda r: (r.date, str(r.location_id), str(r.meal_type_id)))
    return rows


def get_comparison_for_period(
    db: Session, location_id: uuid.UUID, meal_type_id: uuid.UUID, period_date: date_type
) -> ComparisonRow:
    """Single-period lookup, used by the classification and recommendations modules."""
    rows = compute_comparisons(
        db, location_id=location_id, meal_type_id=meal_type_id, single_date=period_date
    )
    if rows:
        return rows[0]
    return ComparisonRow(period_date, location_id, meal_type_id, None, None, None, None, None)
