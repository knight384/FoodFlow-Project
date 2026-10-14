"""
Auth module business logic.

Per TRD v1.0 Section 8: "auth is the only module that issues sessions/
tokens and resolves the current user's role." The User/Role identity
data itself is owned and stored by the `users` module's models
(app/modules/users/models.py, from Phase 2) — this service imports those
models to authenticate against them, which is the one deliberate
exception to strict module-to-module independence, since authentication
inherently needs to read the identity store.
"""

from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.modules.users.models import Role, User


def authenticate_user(db: Session, username: str, password: str) -> tuple[User, str, str]:
    """
    Verify credentials and issue an access token.

    Returns (user, role_name, token) on success.

    Raises AuthenticationError (never revealing which credential was
    wrong, per SRS-FR-001) if:
    - no user exists with that username,
    - the password does not match, or
    - the account has been deactivated (SRS-FR-004).
    """
    user = db.query(User).filter(User.username == username).one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid username or password.")

    if not user.is_active:
        raise AuthenticationError("Invalid username or password.")

    role = db.get(Role, user.role_id)
    role_name = role.name if role else ""

    token = create_access_token(user_id=str(user.id), role_name=role_name)
    return user, role_name, token
