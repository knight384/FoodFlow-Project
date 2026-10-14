"""
Classification module business logic (SRS-FR-021–023).

Per Database Specification v1.0 Section 13 and API Specification v1.0
Section 18: Classification is computed dynamically from the (also
dynamically computed — see app.modules.comparison.service) Variance —
there is NO persisted `classification` table, and none is created here.

=== PROVISIONAL THRESHOLD — NOT a confirmed business decision ===
The numeric surplus/shortage threshold is explicitly unresolved (SRS
v1.0 Section 14; Database Specification v1.0 Section 13/29; API
Specification v1.0 Section 18/24/29). To make classification testable in
Phase 4, this module applies a provisional percentage threshold sourced
from `app.config.get_settings().provisional_classification_threshold_percentage`
(default 10%, overridable via the `CLASSIFICATION_THRESHOLD_PERCENTAGE`
environment variable — see app/config.py and backend/.env.example).

This value IS returned in each response row's `thresholdApplied` field
(rather than left `null`) — a deliberate transparency choice: since a
real, non-null value IS being used internally to actually classify
periods, returning it lets a caller/tester see exactly what produced a
given status, rather than hiding it behind a `null` while secretly
applying a number. This does not make the value confirmed — it remains
provisional and must be replaced with a real business decision before
this is production-ready.

=== Zero-forecast edge case ===
When Forecasted Demand is 0, a percentage-based threshold comparison is
undefined (see app.modules.comparison.service's docstring). This module
treats that case as `status = "unavailable"` — reusing the same status
value the API Specification already defines for "one of the two source
values is missing" — rather than inventing a new status value or a
misleading classification. This is a safe placeholder, not a resolution
of the open edge case (see this phase's instruction #10).
"""

import uuid
from dataclasses import dataclass
from datetime import date as date_type

from sqlalchemy.orm import Session

from app.config import get_settings
from app.modules.comparison.service import ComparisonRow, compute_comparisons, get_comparison_for_period

VALID_STATUSES = ("surplus", "shortage", "balanced", "unavailable")


@dataclass
class ClassificationRow:
    date: date_type
    location_id: uuid.UUID
    meal_type_id: uuid.UUID
    status: str
    threshold_applied: float | None
    comparison: ComparisonRow


def classify_row(row: ComparisonRow) -> ClassificationRow:
    settings = get_settings()
    threshold = settings.provisional_classification_threshold_percentage

    if row.forecasted_demand is None or row.planned_quantity is None:
        return ClassificationRow(row.date, row.location_id, row.meal_type_id, "unavailable", None, row)

    if row.forecasted_demand == 0:
        # Zero-forecast edge case — see module docstring.
        return ClassificationRow(row.date, row.location_id, row.meal_type_id, "unavailable", None, row)

    percentage_variance = ((row.planned_quantity - row.forecasted_demand) / row.forecasted_demand) * 100

    if percentage_variance > threshold:
        status = "surplus"
    elif percentage_variance < -threshold:
        status = "shortage"
    else:
        status = "balanced"

    return ClassificationRow(row.date, row.location_id, row.meal_type_id, status, threshold, row)


def compute_classifications(
    db: Session,
    location_id: uuid.UUID | None = None,
    meal_type_id: uuid.UUID | None = None,
    single_date: date_type | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
) -> list[ClassificationRow]:
    comparison_rows = compute_comparisons(
        db,
        location_id=location_id,
        meal_type_id=meal_type_id,
        single_date=single_date,
        date_from=date_from,
        date_to=date_to,
    )
    return [classify_row(row) for row in comparison_rows]


def get_classification_for_period(
    db: Session, location_id: uuid.UUID, meal_type_id: uuid.UUID, period_date: date_type
) -> ClassificationRow:
    """Single-period lookup, used by the recommendations module."""
    row = get_comparison_for_period(db, location_id, meal_type_id, period_date)
    return classify_row(row)
