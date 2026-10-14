"""
Users module routes: USR-001 through USR-005 — exact paths, methods, and
behavior per API Specification v1.0 Section 9 (Endpoint Inventory) and
Section 11 (User Management API). All endpoints require Admin authorization.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, build_pagination_meta
from app.database import get_db
from app.modules.users import service
from app.modules.users.models import User
from app.modules.users.schemas import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_roles("administrator"))],
)


def _to_response(db: Session, user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        role=service.role_name_for(db, user),
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("", response_model=UserListResponse, status_code=status.HTTP_200_OK)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
    db: Session = Depends(get_db),
) -> UserListResponse:
    """USR-001."""
    users, total_items = service.list_users(db, page, page_size)
    return UserListResponse(
        data=[_to_response(db, u) for u in users],
        pagination=build_pagination_meta(page, page_size, total_items),
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest, db: Session = Depends(get_db)) -> UserResponse:
    """USR-002."""
    user = service.create_user(db, payload.username, payload.password, payload.role)
    return _to_response(db, user)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> UserResponse:
    """USR-003."""
    user = service.get_user(db, user_id)
    return _to_response(db, user)


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(
    user_id: uuid.UUID, payload: UserUpdateRequest, db: Session = Depends(get_db)
) -> UserResponse:
    """USR-004."""
    user = service.update_user(db, user_id, payload.username, payload.role)
    return _to_response(db, user)


@router.post("/{user_id}/deactivate", response_model=UserResponse, status_code=status.HTTP_200_OK)
def deactivate_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> UserResponse:
    """USR-005. No hard-delete endpoint exists (Database Spec Section 18)."""
    user = service.deactivate_user(db, user_id)
    return _to_response(db, user)
