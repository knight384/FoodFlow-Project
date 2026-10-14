"""
ORM model for the `recommendations` module: RedistributionRecommendation.

Maps to Database Specification v1.0 Section 6.10 (redistribution_recommendation
table) and Section 14 (Redistribution Recommendation Model).

Phase 2 scope: schema definition only. No recommendation-generation
logic and no API routes are implemented here.

No columns/tables exist for routing, donor/recipient matching,
logistics, or external-partner references — consistent with TRD v1.0
Section 17 and Foundation v1.1 exclusions.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RedistributionRecommendation(Base):
    """
    A rule-based, advisory recommendation generated for a Surplus-
    classified period.

    Database Specification v1.0 Section 6.10. `secondary_location_id`
    reuses the existing `locations` table rather than introducing a new
    "destination" concept.
    """

    __tablename__ = "redistribution_recommendation"
    __table_args__ = (
        CheckConstraint(
            "estimated_surplus_quantity >= 0",
            name="ck_redistribution_recommendation_surplus_nonneg",
        ),
        # is_advisory must be true for MVP (Database Spec Section 6.10) —
        # the recommendation is always advisory/non-executing, never a
        # record of an executed action.
        CheckConstraint(
            "is_advisory = true", name="ck_redistribution_recommendation_is_advisory_true"
        ),
        Index(
            "ix_redistribution_recommendation_date_location_mealtype",
            "period_date",
            "location_id",
            "meal_type_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    period_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    meal_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meal_types.id"), nullable=False
    )
    estimated_surplus_quantity: Mapped[float] = mapped_column(Numeric, nullable=False)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Optional configured secondary/destination location, if applicable.
    secondary_location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True
    )
    is_advisory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
