"""
Reports module business logic (SRS-FR-030-031).

Reuses `app.modules.classification.service.compute_classifications` for
the underlying forecast/planned-quantity merge and status computation -
does not duplicate that logic (same reuse pattern as the dashboard
module). Since `compute_classifications` already returns a fully
materialized, sorted list (there is no separate `variance`/
`classification` table to paginate at the database level - Database
Specification v1.0 Sections 12-13), pagination here is applied to the
in-memory result list, after any `status` filter, rather than via a
SQL OFFSET/LIMIT.
"""

import uuid
from datetime import date as date_type

from sqlalchemy.orm import Session

from app.modules.classification.service import compute_classifications


def get_reports(
    db: Session,
    date_from: date_type,
    date_to: date_type,
    location_id: uuid.UUID | None,
    meal_type_id: uuid.UUID | None,
    status_filter: str | None,
    page: int,
    page_size: int,
) -> tuple[list[dict], int]:
    rows = compute_classifications(
        db,
        location_id=location_id,
        meal_type_id=meal_type_id,
        date_from=date_from,
        date_to=date_to,
    )

    if status_filter is not None:
        rows = [r for r in rows if r.status == status_filter]

    total_items = len(rows)
    start = (page - 1) * page_size
    page_rows = rows[start : start + page_size]

    results = [
        {
            "date": r.date,
            "location_id": r.location_id,
            "meal_type_id": r.meal_type_id,
            "forecasted_demand": r.comparison.forecasted_demand,
            "planned_quantity": r.comparison.planned_quantity,
            "potential_surplus": r.comparison.potential_surplus,
            "potential_shortage": r.comparison.potential_shortage,
            "variance_percentage": r.comparison.variance_percentage,
            "status": r.status,
        }
        for r in page_rows
    ]
    return results, total_items
