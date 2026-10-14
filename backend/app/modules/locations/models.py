"""
ORM model for the `locations` module: Location.

Maps to Database Specification v1.0 Section 6.3 (locations table),
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


class Location(Base):
    """
    A cafeteria/food-service site.

    `is_active` supports the Database Specification's recommended
    soft-delete/archive strategy (Section 18) — a proposed decision,
    flagged there as requiring confirmation, not yet final.
    """

    __tablename__ = "locations"
    __table_args__ = (
        CheckConstraint("name <> ''", name="ck_locations_name_non_empty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
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
