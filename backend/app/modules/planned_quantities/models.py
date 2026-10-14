"""
ORM model for the `planned_quantities` module: PlannedQuantity.

Maps to Database Specification v1.0 Section 6.9 (planned_quantity table)
and Section 11 (Planned Quantity Model).

Phase 2 scope: schema definition only. No entry/edit service logic and
no API routes are implemented here.

Edit-window note: per Database Specification v1.0 Section 11, the
Planned Quantity edit-window rule (whether editing is restricted after
the meal period passes) is explicitly unresolved and is NOT implemented
as a schema constraint here — this table supports in-place updates with
no time-based restriction.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PlannedQuantity(Base):
    """
    The quantity Operations Staff intend to prepare for a period.

    Database Specification v1.0 Section 6.9.
    """

    __tablename__ = "planned_quantity"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_planned_quantity_quantity_nonneg"),
        # Recommended (Database Spec Section 17): one Planned Quantity
        # per period, edited in place rather than duplicated.
        UniqueConstraint(
            "location_id",
            "meal_type_id",
            "plan_date",
            name="uq_planned_quantity_location_mealtype_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    meal_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meal_types.id"), nullable=False
    )
    quantity: Mapped[float] = mapped_column(Numeric, nullable=False)
    entered_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
