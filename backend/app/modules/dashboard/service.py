"""
Dashboard module business logic (SRS-FR-028–029).

Per TRD v1.0 Section 18 and API Specification v1.0 Section 20: a single
aggregated endpoint composing data from the forecasting, planned-
quantities, comparison/classification, and recommendations modules —
this module owns NO table of its own and does NOT duplicate the
forecast/planned-quantity merge logic already implemented in
`app.modules.classification.service.compute_classifications` (which
itself reuses `app.modules.comparison.service.compute_comparisons`).
This is the same reuse pattern Phase 4 already established between
comparison and classification.

Default date window: API Specification v1.0 Section 20 leaves the exact
default window an implementation detail ("defaults to a sensible
near-term window, e.g., 'upcoming periods'"). This implementation
defaults to today through 13 days from today (a 14-day upcoming
window) when no date filter is supplied — a documented implementation
default, not a business decision.
"""

import uuid
from datetime import date as date_type
from datetime import timedelta

from sqlalchemy.orm import Session

from app.modules.classification.service import compute_classifications
from app.modules.recommendations.models import RedistributionRecommendation

DEFAULT_UPCOMING_WINDOW_DAYS = 14


def get_dashboard(
    db: Session,
    location_id: uuid.UUID | None = None,
    meal_type_id: uuid.UUID | None = None,
    single_date: date_type | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
) -> list[dict]:
    if single_date is None and date_from is None and date_to is None:
        today = date_type.today()
        date_from = today
        date_to = today + timedelta(days=DEFAULT_UPCOMING_WINDOW_DAYS - 1)

    classification_rows = compute_classifications(
        db,
        location_id=location_id,
        meal_type_id=meal_type_id,
        single_date=single_date,
        date_from=date_from,
        date_to=date_to,
    )

    # Batch-fetch matching recommendations in ONE query (not per-row) to
    # avoid N+1 - keyed by (location_id, meal_type_id, period_date) for
    # O(1) lookup while building the response.
    recommendation_query = db.query(RedistributionRecommendation)
    if location_id is not None:
        recommendation_query = recommendation_query.filter(
            RedistributionRecommendation.location_id == location_id
        )
    if meal_type_id is not None:
        recommendation_query = recommendation_query.filter(
            RedistributionRecommendation.meal_type_id == meal_type_id
        )
    if single_date is not None:
        recommendation_query = recommendation_query.filter(
            RedistributionRecommendation.period_date == single_date
        )
    else:
        if date_from is not None:
            recommendation_query = recommendation_query.filter(
                RedistributionRecommendation.period_date >= date_from
            )
        if date_to is not None:
            recommendation_query = recommendation_query.filter(
                RedistributionRecommendation.period_date <= date_to
            )

    recommendations_by_key = {
        (r.location_id, r.meal_type_id, r.period_date): r for r in recommendation_query.all()
    }

    results = []
    for row in classification_rows:
        recommendation = None
        if row.status == "surplus":
            match = recommendations_by_key.get((row.location_id, row.meal_type_id, row.date))
            if match is not None:
                recommendation = {
                    "id": match.id,
                    "estimated_surplus_quantity": float(match.estimated_surplus_quantity),
                    "recommendation_text": match.recommendation_text,
                    "is_advisory": match.is_advisory,
                }
        results.append(
            {
                "date": row.date,
                "location_id": row.location_id,
                "meal_type_id": row.meal_type_id,
                "forecasted_demand": row.comparison.forecasted_demand,
                "planned_quantity": row.comparison.planned_quantity,
                "potential_surplus": row.comparison.potential_surplus,
                "potential_shortage": row.comparison.potential_shortage,
                "variance_percentage": row.comparison.variance_percentage,
                "status": row.status,
                "recommendation": recommendation,
            }
        )
    results.sort(key=lambda r: (r["date"], str(r["location_id"]), str(r["meal_type_id"])))
    return results
