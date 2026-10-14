"""
Reports module route: RPT-001 — exact path, method, and behavior per
API Specification v1.0 Section 9/21. Manager and Admin authorization
only — Operations Staff "limited" access remains a pending-confirmation
cell (API Specification v1.0 Section 9's RPT-001 row) and is therefore
NOT implemented, consistent with every other pending-confirmation cell
since Phase 3.

`dateFrom`/`dateTo` are required (no defaults) — API Specification v1.0
Section 21: "a report without a date range is not a defined use case."
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, build_pagination_meta
from app.database import get_db
from app.modules.reports import service
from app.modules.reports.schemas import ReportListResponse, ReportResponseItem

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(require_roles("manager", "administrator"))],
)


@router.get("", response_model=ReportListResponse, status_code=status.HTTP_200_OK)
def get_reports(
    date_from: date = Query(alias="dateFrom"),
    date_to: date = Query(alias="dateTo"),
    location_id: uuid.UUID | None = Query(default=None, alias="locationId"),
    meal_type_id: uuid.UUID | None = Query(default=None, alias="mealTypeId"),
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
    db: Session = Depends(get_db),
) -> ReportListResponse:
    """RPT-001."""
    rows, total_items = service.get_reports(
        db, date_from, date_to, location_id, meal_type_id, status_filter, page, page_size
    )
    return ReportListResponse(
        data=[ReportResponseItem(**r) for r in rows],
        pagination=build_pagination_meta(page, page_size, total_items),
    )
