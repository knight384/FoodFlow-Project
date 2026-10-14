"""
Backend-authoritative authentication/authorization dependencies.

Per TRD v1.0 Section 15: "Backend authorization is authoritative. Even if
a UI element is hidden, the backend independently enforces the
permission on every request." This module is the single place that
enforcement happens — every protected route depends on `get_current_user`
(identity) and, where role-restricted, `require_roles(...)` (authorization).

Per SRS v1.0 Section 6 (permission matrix): only endpoints whose access
is fully resolved in the SRS/PRD are role-restricted here (Admin-only
user management). No "pending permission confirmation" cell from the
matrix is silently resolved by this phase — none of those cells are
exercised by the Auth/User endpoints implemented in Phase 3.
"""

from collections.abc import Callable

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.database import get_db
from app.modules.users.models import Role, User

# `auto_error=False` so a missing/malformed Authorization header produces
# our own AuthenticationError (and therefore our standard error envelope)
# rather than FastAPI's default 403 "Not authenticated" response.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the authenticated user from the request's Bearer token.

    Raises AuthenticationError (401) if the token is missing, malformed,
    expired, or refers to a user that no longer exists or has been
    deactivated (SRS-FR-004: a deactivated account cannot authenticate).
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing or invalid authentication credentials.")

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise AuthenticationError("Missing or invalid authentication credentials.") from None

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Missing or invalid authentication credentials.")

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("Missing or invalid authentication credentials.")

    return user


def get_current_user_role_name(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    """Resolve the current user's role name (e.g. "administrator")."""
    role = db.get(Role, current_user.role_id)
    # role_id is a NOT NULL foreign key to roles.id, so `role` should
    # always be found; the fallback below only guards against a
    # corrupted/partial database state, not a normal code path.
    if role is None:
        raise AuthenticationError("Missing or invalid authentication credentials.")
    return role.name


def require_roles(*allowed_role_names: str) -> Callable[..., User]:
    """
    Dependency factory: restricts an endpoint to one or more approved
    role names (e.g. `Depends(require_roles("administrator"))`).

    This is the authoritative authorization check (TRD v1.0 Section 15) —
    it always runs server-side regardless of what the frontend does or
    does not show.
    """

    def dependency(
        current_user: User = Depends(get_current_user),
        role_name: str = Depends(get_current_user_role_name),
    ) -> User:
        if role_name not in allowed_role_names:
            raise AuthorizationError("You do not have permission to perform this action.")
        return current_user

    return dependency
