"""
Planned-quantities module routes: PQ-001 through PQ-004 — exact paths,
methods, and behavior per API Specification v1.0 Section 9/16.
Create/Edit restricted to Operations Staff (confirmed); Admin/Manager
entry ability is a "pending permission confirmation" cell and is
therefore NOT implemented. View is open to all authenticated roles.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, build_pagination_meta
from app.database import get_db
from app.modules.planned_quantities import service
from app.modules.planned_quantities.schemas import (
    PlannedQuantityCreateRequest,
    PlannedQuantityListResponse,
    PlannedQuantityResponse,
    PlannedQuantityUpdateRequest,
)
from app.modules.users.models import User

router = APIRouter(prefix="/planned-quantities", tags=["planned-quantities"])


@router.get("", response_model=PlannedQuantityListResponse, status_code=status.HTTP_200_OK)
def list_planned_quantities(
    location_id: uuid.UUID | None = Query(default=None, alias="locationId"),
    meal_type_id: uuid.UUID | None = Query(default=None, alias="mealTypeId"),
    date_from: date | None = Query(default=None, alias="dateFrom"),
    date_to: date | None = Query(default=None, alias="dateTo"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> PlannedQuantityListResponse:
    """PQ-002. All authenticated roles may view."""
    entries, total_items = service.list_planned_quantities(
        db, page, page_size, location_id, meal_type_id, date_from, date_to
    )
    return PlannedQuantityListResponse(
        data=[PlannedQuantityResponse.model_validate(e) for e in entries],
        pagination=build_pagination_meta(page, page_size, total_items),
    )


@router.post(
    "", response_model=PlannedQuantityResponse, status_code=status.HTTP_201_CREATED
)
def create_planned_quantity(
    payload: PlannedQuantityCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("operations_staff")),
) -> PlannedQuantityResponse:
    """PQ-001. Operations Staff only (confirmed permission)."""
    entry = service.create_planned_quantity(
        db,
        payload.plan_date,
        payload.location_id,
        payload.meal_type_id,
        payload.quantity,
        current_user.id,
    )
    return PlannedQuantityResponse.model_validate(entry)


@router.get(
    "/{planned_quantity_id}",
    response_model=PlannedQuantityResponse,
    status_code=status.HTTP_200_OK,
)
def get_planned_quantity(
    planned_quantity_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> PlannedQuantityResponse:
    """PQ-003. All authenticated roles may view."""
    entry = service.get_planned_quantity(db, planned_quantity_id)
    return PlannedQuantityResponse.model_validate(entry)


@router.patch(
    "/{planned_quantity_id}",
    response_model=PlannedQuantityResponse,
    status_code=status.HTTP_200_OK,
)
def update_planned_quantity(
    planned_quantity_id: uuid.UUID,
    payload: PlannedQuantityUpdateRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles("operations_staff")),
) -> PlannedQuantityResponse:
    """
    PQ-004. Operations Staff only (confirmed permission). No edit-window
    restriction — see app/modules/planned_quantities/service.py.
    """
    entry = service.update_planned_quantity(db, planned_quantity_id, payload.quantity)
    return PlannedQuantityResponse.model_validate(entry)
