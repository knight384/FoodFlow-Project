"""
Classification module route: CLS-001 — exact path, method, and behavior
per API Specification v1.0 Section 9/18. Manager and Admin authorization
only (matches the API Specification's resolved authorization column).
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database import get_db
from app.modules.classification import service
from app.modules.classification.schemas import ClassificationListResponse, ClassificationResponseItem

router = APIRouter(
    prefix="/classifications",
    tags=["classifications"],
    dependencies=[Depends(require_roles("manager", "administrator"))],
)


@router.get("", response_model=ClassificationListResponse, status_code=status.HTTP_200_OK)
def get_classifications(
    location_id: uuid.UUID | None = Query(default=None, alias="locationId"),
    meal_type_id: uuid.UUID | None = Query(default=None, alias="mealTypeId"),
    single_date: date | None = Query(default=None, alias="date"),
    date_from: date | None = Query(default=None, alias="dateFrom"),
    date_to: date | None = Query(default=None, alias="dateTo"),
    db: Session = Depends(get_db),
) -> ClassificationListResponse:
    """CLS-001. Read-only, dynamically computed — no persisted table."""
    rows = service.compute_classifications(
        db,
        location_id=location_id,
        meal_type_id=meal_type_id,
        single_date=single_date,
        date_from=date_from,
        date_to=date_to,
    )
    return ClassificationListResponse(
        data=[
            ClassificationResponseItem(
                date=r.date,
                location_id=r.location_id,
                meal_type_id=r.meal_type_id,
                status=r.status,
                threshold_applied=r.threshold_applied,
            )
            for r in rows
        ]
    )
