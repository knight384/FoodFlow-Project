"""
ORM models for the `users` module: Role and User.

Maps directly to Database Specification v1.0:
- Section 6.1 (roles table)
- Section 6.2 (users table)
- Section 7 (User and Role Data Model)

Phase 2 scope: schema definition only. No authentication logic, no
password-hashing implementation, no CRUD service functions, and no API
routes are implemented here — those remain deferred to a later phase
(explicitly excluded from this phase per the Phase 2 task boundary).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# The three approved roles (Foundation v1.1; SRS v1.0 Section 4).
# Used only for the CHECK constraint below and the roles seed script
# (scripts/seed_reference_data.py) — not enforced anywhere else in code.
APPROVED_ROLE_NAMES = ("administrator", "manager", "operations_staff")


class Role(Base):
    """
    Fixed reference list of the three approved roles.

    Database Specification v1.0 Section 6.1: a small reference table
    (rather than an inline enum on `users`) is used so role metadata can
    be extended later without a schema change to `users` — a proposed
    database decision, not a confirmed requirement.
    """

    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint(
            "name IN ('administrator', 'manager', 'operations_staff')",
            name="ck_roles_name_approved_values",
        ),
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)


class User(Base):
    """
    A system user with exactly one role (one-to-one, not many-to-many —
    Database Specification v1.0 Section 7, per SRS v1.0's explicit
    statement that each user has exactly one approved role).
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    # Securely hashed credential. Hashing algorithm/implementation is not
    # selected in Phase 2 (TRD v1.0 Section 20) — this column only defines
    # storage shape, never a plain-text password.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("roles.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
