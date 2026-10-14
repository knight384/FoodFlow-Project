"""
ORM model for the `forecasting` module: ForecastedDemand.

Maps to Database Specification v1.0 Section 6.8 (forecasted_demand
table) and Section 10 (Forecasted Demand Model).

Phase 2 scope: schema definition only. No forecast-generation logic, no
ML model integration, and no API routes are implemented here — those
remain out of scope for this phase (and for the ML module generally,
per TRD v1.0 Section 12 / ML & Testing Plan v1.0, which explicitly defer
algorithm selection).

Versioning note: per Database Specification v1.0 Section 6.8/17, a
unique constraint on (location_id, meal_type_id, forecast_date) is a
*proposed* decision (single active forecast per period), not a
company-confirmed requirement. It is implemented here as the schema
default because the spec recommends it, but it remains flagged as
open/pending confirmation (Section 29 of the Database Specification).
"""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ForecastedDemand(Base):
    """
    A system-generated Forecasted Demand value for a future period.

    Database Specification v1.0 Section 6.8.
    """

    __tablename__ = "forecasted_demand"
    __table_args__ = (
        CheckConstraint(
            "predicted_quantity >= 0", name="ck_forecasted_demand_quantity_nonneg"
        ),
        # Proposed decision (Database Spec Section 6.8/17/29): one active
        # forecast per (location, meal type, date). Flagged as pending
        # confirmation, not a confirmed business requirement.
        UniqueConstraint(
            "location_id",
            "meal_type_id",
            "forecast_date",
            name="uq_forecasted_demand_location_mealtype_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    forecast_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    meal_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meal_types.id"), nullable=False
    )
    predicted_quantity: Mapped[float] = mapped_column(Numeric, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # Optional lightweight traceability reference only — NOT a model
    # registry (TRD v1.0 Section 12 explicitly avoids that).
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
