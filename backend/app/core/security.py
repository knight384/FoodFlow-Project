"""
Password hashing and access-token issuance/verification.

Per TRD v1.0 Section 14 and API Specification v1.0 Section 10, the exact
authentication mechanism (server-side session vs. stateless token) was
left as an implementation decision compatible with either approach. This
implementation uses **stateless JWT access tokens**:

- Chosen because it requires no additional server-side session store
  (Redis and similar are explicitly excluded — TRD v1.0 Section 6/22),
  keeping the MVP simple.
- Trade-off, stated plainly: because there is no server-side token
  store, `POST /auth/logout` (see app/modules/auth/router.py) cannot
  truly invalidate a still-valid token early — it is effectively a
  client-side "discard the token" action. This is a proposed technical
  decision, not dictated by any source document; a future phase could
  add a token-blocklist table if early invalidation becomes a real
  requirement.

Passwords are hashed with bcrypt — never stored or transmitted in plain
text (TRD v1.0 Section 20).
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config import get_settings

settings = get_settings()


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password for storage in users.password_hash."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Malformed hash — treat as a verification failure, not a crash.
        return False


def create_access_token(user_id: str, role_name: str) -> str:
    """
    Issue a signed JWT access token carrying the user's id (`sub`) and
    role name, so app.core.dependencies.get_current_user can resolve
    identity and role without a database round-trip on every request
    beyond loading the user record itself.
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role_name,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Raises jwt.PyJWTError (or a subclass, e.g. ExpiredSignatureError,
    InvalidTokenError) on any invalid/expired/tampered token — callers
    (app.core.dependencies.get_current_user) are responsible for
    converting that into an AuthenticationError.
    """
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
