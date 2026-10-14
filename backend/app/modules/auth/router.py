"""
Auth module routes: AUTH-001 (login), AUTH-002 (logout), AUTH-003 (current
user) — exact paths, methods, and behavior per API Specification v1.0
Section 9 (Endpoint Inventory) and Section 10 (Authentication API).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_current_user_role_name
from app.database import get_db
from app.modules.auth.schemas import CurrentUserResponse, LoginRequest, LoginResponse
from app.modules.auth.service import authenticate_user
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """AUTH-001. No authentication required — this is the entry point."""
    user, role_name, token = authenticate_user(db, payload.username, payload.password)
    return LoginResponse(
        token=token,
        user=CurrentUserResponse(id=user.id, username=user.username, role=role_name),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)) -> None:
    """
    AUTH-002. Requires authentication (a valid token must be presented).

    See app.core.security's module docstring for the stated trade-off:
    with stateless JWTs and no server-side token store, this endpoint
    confirms the request is authenticated but cannot forcibly invalidate
    the presented token before its natural expiry. The client is
    expected to discard the token after calling this endpoint.
    """
    return None


@router.get("/me", response_model=CurrentUserResponse, status_code=status.HTTP_200_OK)
def get_current_user_identity(
    current_user: User = Depends(get_current_user),
    role_name: str = Depends(get_current_user_role_name),
) -> CurrentUserResponse:
    """AUTH-003. Requires authentication."""
    return CurrentUserResponse(id=current_user.id, username=current_user.username, role=role_name)
