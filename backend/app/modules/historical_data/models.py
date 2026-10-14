"""
ORM models for the `historical_data` module: HistoricalConsumption,
ImportJob, ImportRecordError.

Maps to Database Specification v1.0:
- Section 6.5 (historical_consumption table)
- Section 6.6 (import_job table)
- Section 6.7 (import_record_error table)
- Section 9 (Historical Consumed Quantity Model)
- Section 15 (Import Job / Import Result Model)

Phase 2 scope: schema definition only. No upload/validation/import
service logic and no API routes are implemented here.

Note on day-of-week: per Database Specification v1.0 Section 6.5, day of
week is deliberately NOT persisted as a column — it is derived from
`record_date` at query/preprocessing time. No such column exists below.

Note on duplicates: per Database Specification v1.0 Section 17/29, a
unique constraint on (location_id, meal_type_id, record_date) for
`historical_consumption` is only a *recommended* option pending
confirmation of the duplicate-record handling policy — it is
deliberately NOT enforced here. Only a non-unique composite index exists
(Section 19), matching the spec's explicit "do not silently resolve"
instruction.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# Approved import_job status values (Database Specification v1.0 Section 6.6).
APPROVED_IMPORT_JOB_STATUSES = ("processing", "completed", "failed")


class ImportJob(Base):
    """
    A single historical-data upload event and its summary outcome.

    Database Specification v1.0 Section 6.6.
    """

    __tablename__ = "import_job"
    __table_args__ = (
        CheckConstraint("total_records >= 0", name="ck_import_job_total_records_nonneg"),
        CheckConstraint("valid_records >= 0", name="ck_import_job_valid_records_nonneg"),
        CheckConstraint("invalid_records >= 0", name="ck_import_job_invalid_records_nonneg"),
        CheckConstraint(
            "status IN ('processing', 'completed', 'failed')",
            name="ck_import_job_status_approved_values",
        ),
        Index("ix_import_job_uploaded_at", "uploaded_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invalid_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False)


class ImportRecordError(Base):
    """
    Per-record validation failure detail for an import job.

    Database Specification v1.0 Section 6.7 — supports SRS-FR-010.
    """

    __tablename__ = "import_record_error"
    __table_args__ = (
        Index("ix_import_record_error_import_job_id", "import_job_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    import_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_job.id"), nullable=False
    )
    row_reference: Mapped[int] = mapped_column(Integer, nullable=False)
    failure_reason: Mapped[str] = mapped_column(Text, nullable=False)
    # Optional snapshot of the offending row's raw values (Database Spec
    # Section 6.7) — nullable, since not every implementation may choose
    # to capture it.
    raw_data_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class HistoricalConsumption(Base):
    """
    A historical Actual Consumed Quantity record, used as forecasting
    input.

    Database Specification v1.0 Section 6.5.
    """

    __tablename__ = "historical_consumption"
    __table_args__ = (
        CheckConstraint(
            "actual_consumed_quantity >= 0",
            name="ck_historical_consumption_quantity_nonneg",
        ),
        # Non-unique composite index only (Section 19) — NOT a unique
        # constraint, since duplicate-record handling remains unresolved
        # (Database Specification v1.0 Section 17/29, item 1).
        Index(
            "ix_historical_consumption_date_location_mealtype",
            "record_date",
            "location_id",
            "meal_type_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    record_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    meal_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meal_types.id"), nullable=False
    )
    actual_consumed_quantity: Mapped[float] = mapped_column(Numeric, nullable=False)
    # Nullable: allows for a possible future non-upload data-entry path,
    # though none is built now (Database Spec Section 6.5).
    import_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_job.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
