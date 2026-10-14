"""
Meal-types module routes: MEAL-001 through MEAL-005 — exact paths,
methods, and behavior per API Specification v1.0 Section 9/13.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, build_pagination_meta
from app.database import get_db
from app.modules.meal_types import service
from app.modules.meal_types.schemas import (
    MealTypeCreateRequest,
    MealTypeListResponse,
    MealTypeResponse,
    MealTypeUpdateRequest,
)

router = APIRouter(prefix="/meal-types", tags=["meal-types"])


@router.get("", response_model=MealTypeListResponse, status_code=status.HTTP_200_OK)
def list_meal_types(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
    include_inactive: bool = Query(default=False, alias="includeInactive"),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
) -> MealTypeListResponse:
    """MEAL-001. All authenticated roles may view."""
    meal_types, total_items = service.list_meal_types(db, page, page_size, include_inactive)
    return MealTypeListResponse(
        data=[MealTypeResponse.model_validate(mt) for mt in meal_types],
        pagination=build_pagination_meta(page, page_size, total_items),
    )


@router.post("", response_model=MealTypeResponse, status_code=status.HTTP_201_CREATED)
def create_meal_type(
    payload: MealTypeCreateRequest,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("administrator")),
) -> MealTypeResponse:
    """MEAL-002. Admin only."""
    meal_type = service.create_meal_type(db, payload.name)
    return MealTypeResponse.model_validate(meal_type)


@router.get("/{meal_type_id}", response_model=MealTypeResponse, status_code=status.HTTP_200_OK)
def get_meal_type(
    meal_type_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
) -> MealTypeResponse:
    """MEAL-003. All authenticated roles may view."""
    meal_type = service.get_meal_type(db, meal_type_id)
    return MealTypeResponse.model_validate(meal_type)


@router.patch("/{meal_type_id}", response_model=MealTypeResponse, status_code=status.HTTP_200_OK)
def update_meal_type(
    meal_type_id: uuid.UUID,
    payload: MealTypeUpdateRequest,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("administrator")),
) -> MealTypeResponse:
    """MEAL-004. Admin only."""
    meal_type = service.update_meal_type(db, meal_type_id, payload.name)
    return MealTypeResponse.model_validate(meal_type)


@router.delete("/{meal_type_id}", response_model=MealTypeResponse, status_code=status.HTTP_200_OK)
def delete_meal_type(
    meal_type_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin=Depends(require_roles("administrator")),
) -> MealTypeResponse:
    """
    MEAL-005. Admin only. Provisional soft-archive behavior — see
    app/modules/meal_types/service.py's module docstring.
    """
    meal_type = service.archive_meal_type(db, meal_type_id)
    return MealTypeResponse.model_validate(meal_type)
