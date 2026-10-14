"""
ORM model for the `meal_types` module: MealType.

Maps to Database Specification v1.0 Section 6.4 (meal_types table),
Section 8 (Location and Meal-Type Data Model), and Section 18
(soft-delete/archive recommendation).

Phase 2 scope: schema definition only. No CRUD service functions or API
routes are implemented here.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MealType(Base):
    """
    A configurable meal category (e.g., Breakfast, Lunch, Dinner, or
    others as configured — Foundation v1.1 Working Assumption: meal
    types are not hardcoded).

    `is_active` supports the same soft-delete/archive recommendation as
    Location (Database Specification v1.0 Section 18) — proposed, not
    yet confirmed.
    """

    __tablename__ = "meal_types"
    __table_args__ = (
        CheckConstraint("name <> ''", name="ck_meal_types_name_non_empty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
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
