"""
Dashboard module route: DASH-001 — exact path, method, and behavior per
API Specification v1.0 Section 9/20. Manager and Admin authorization
only (matches the API Specification's resolved authorization column).
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database import get_db
from app.modules.dashboard import service
from app.modules.dashboard.schemas import (
    DashboardListResponse,
    DashboardRecommendation,
    DashboardResponseItem,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_roles("manager", "administrator"))],
)


@router.get("", response_model=DashboardListResponse, status_code=status.HTTP_200_OK)
def get_dashboard(
    location_id: uuid.UUID | None = Query(default=None, alias="locationId"),
    meal_type_id: uuid.UUID | None = Query(default=None, alias="mealTypeId"),
    single_date: date | None = Query(default=None, alias="date"),
    date_from: date | None = Query(default=None, alias="dateFrom"),
    date_to: date | None = Query(default=None, alias="dateTo"),
    db: Session = Depends(get_db),
) -> DashboardListResponse:
    """DASH-001. Aggregates forecasting/planned-quantities/comparison/
    classification/recommendations — read-only, no table of its own."""
    rows = service.get_dashboard(
        db,
        location_id=location_id,
        meal_type_id=meal_type_id,
        single_date=single_date,
        date_from=date_from,
        date_to=date_to,
    )
    return DashboardListResponse(
        data=[
            DashboardResponseItem(
                date=r["date"],
                location_id=r["location_id"],
                meal_type_id=r["meal_type_id"],
                forecasted_demand=r["forecasted_demand"],
                planned_quantity=r["planned_quantity"],
                potential_surplus=r["potential_surplus"],
                potential_shortage=r["potential_shortage"],
                variance_percentage=r["variance_percentage"],
                status=r["status"],
                recommendation=(
                    DashboardRecommendation(**r["recommendation"]) if r["recommendation"] else None
                ),
            )
            for r in rows
        ]
    )
