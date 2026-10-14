"""
Users module business logic (SRS-FR-004).

Authorization (Admin-only) is enforced at the router level via
app.core.dependencies.require_roles — this service layer assumes the
caller has already been authorized and focuses only on data operations
and validation.
"""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DuplicateResourceError, NotFoundError, ValidationError
from app.core.security import hash_password
from app.modules.users.models import Role, User


def _get_role_by_name(db: Session, role_name: str) -> Role:
    role = db.query(Role).filter(Role.name == role_name).one_or_none()
    if role is None:
        # Should not normally happen (role names are validated by the
        # request schema against APPROVED_ROLE_NAMES first), but guards
        # against the roles reference table being unseeded.
        raise ValidationError(
            f"Role '{role_name}' is not configured in the database. "
            "Has scripts/seed_reference_data.py been run?"
        )
    return role


def list_users(db: Session, page: int, page_size: int) -> tuple[list[User], int]:
    total_items = db.query(User).count()
    users = (
        db.query(User)
        .order_by(User.username.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return users, total_items


def get_user(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User '{user_id}' not found.")
    return user


def create_user(db: Session, username: str, password: str, role_name: str) -> User:
    role = _get_role_by_name(db, role_name)

    existing = db.query(User).filter(User.username == username).one_or_none()
    if existing is not None:
        raise DuplicateResourceError(f"Username '{username}' already exists.")

    user = User(username=username, password_hash=hash_password(password), role_id=role.id)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Race condition fallback: another request created the same
        # username between our pre-check and commit.
        db.rollback()
        raise DuplicateResourceError(f"Username '{username}' already exists.") from None
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user_id: uuid.UUID,
    username: str | None,
    role_name: str | None,
) -> User:
    user = get_user(db, user_id)

    if username is not None and username != user.username:
        existing = db.query(User).filter(User.username == username).one_or_none()
        if existing is not None:
            raise DuplicateResourceError(f"Username '{username}' already exists.")
        user.username = username

    if role_name is not None:
        role = _get_role_by_name(db, role_name)
        user.role_id = role.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateResourceError(f"Username '{username}' already exists.") from None
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: uuid.UUID) -> User:
    user = get_user(db, user_id)
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def role_name_for(db: Session, user: User) -> str:
    role = db.get(Role, user.role_id)
    return role.name if role else ""
