"""
Locations module routes: LOC-001 through LOC-005 — exact paths, methods,
and behavior per API Specification v1.0 Section 9/12. Create/Update/
Delete require Admin authorization; List/Retrieve are available to all
authenticated roles (view).
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, build_pagination_meta
from app.database import get_db
from app.modules.locations import service
from app.modules.locations.schemas import (
    LocationCreateRequest,
    LocationListResponse,
    LocationResponse,
    LocationUpdateRequest,
)

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=LocationListResponse, status_code=status.HTTP_200_OK)
def list_locations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
    include_inactive: bool = Query(default=False, alias="includeInactive"),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
) -> LocationListResponse:
    """LOC-001. All authenticated roles may view."""
    locations, total_items = service.list_locations(db, page, page_size, include_inactive)
    return LocationListResponse(
        data=[LocationResponse.model_validate(loc) for loc in locations],
        pagination=build_pagination_meta(page, page_size, total_items),
    )


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreateRequest,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("administrator")),
) -> LocationResponse:
    """LOC-002. Admin only."""
    location = service.create_location(db, payload.name)
    return LocationResponse.model_validate(location)


@router.get("/{location_id}", response_model=LocationResponse, status_code=status.HTTP_200_OK)
def get_location(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
) -> LocationResponse:
    """LOC-003. All authenticated roles may view."""
    location = service.get_location(db, location_id)
    return LocationResponse.model_validate(location)


@router.patch("/{location_id}", response_model=LocationResponse, status_code=status.HTTP_200_OK)
def update_location(
    location_id: uuid.UUID,
    payload: LocationUpdateRequest,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("administrator")),
) -> LocationResponse:
    """LOC-004. Admin only."""
    location = service.update_location(db, location_id, payload.name)
    return LocationResponse.model_validate(location)


@router.delete("/{location_id}", response_model=LocationResponse, status_code=status.HTTP_200_OK)
def delete_location(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("administrator")),
) -> LocationResponse:
    """
    LOC-005. Admin only.

    Implements the PROVISIONAL soft-delete/archive behavior described in
    app/modules/locations/service.py's module docstring — sets
    `isActive = false` and returns 200 with the updated resource, per
    API Specification v1.0 Section 12's "if soft-delete is confirmed"
    branch. This is NOT a confirmed final business decision.
    """
    location = service.archive_location(db, location_id)
    return LocationResponse.model_validate(location)
