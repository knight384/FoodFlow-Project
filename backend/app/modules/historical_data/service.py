"""
Historical-data module business logic (SRS-FR-007–010).

=== Accepted file format (implementation detail, not spec-mandated) ===
API Specification v1.0 Section 14 explicitly leaves the exact file
format unspecified ("an implementation detail not further specified
here"). This implementation accepts a UTF-8 CSV file with a header row
containing exactly these column names (case-insensitive):
    date, location, meal_type, actual_consumed_quantity
`location` and `meal_type` are matched by NAME against the existing
`locations`/`meal_types` reference tables (not by internal ID), since a
human- or spreadsheet-produced CSV is far more likely to contain names
than internal UUIDs.

=== Duplicate-record policy: NOT implemented ===
Per this phase's explicit instruction: no uniqueness constraint exists
on historical_consumption (Database Specification v1.0 Section 17/29,
item 1, deliberately left unresolved), and this service does NOT reject,
merge, or overwrite rows that duplicate an existing (location, meal
type, date) combination — every structurally/referentially valid row is
inserted as-is, exactly as the current schema allows.

=== Transaction integrity ===
All valid rows for a given upload are inserted, and the owning
import_job's summary counts are updated, in a single database
transaction (one `db.commit()` at the end) — so a valid row is never
"lost" due to a later invalid row, and the job's reported counts always
match what was actually persisted.
"""

import csv
import io
import uuid
from dataclasses import dataclass
from datetime import date as date_type

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.modules.historical_data.models import HistoricalConsumption, ImportJob, ImportRecordError
from app.modules.locations.models import Location
from app.modules.meal_types.models import MealType

REQUIRED_COLUMNS = {"date", "location", "meal_type", "actual_consumed_quantity"}


@dataclass
class _RowOutcome:
    row_reference: int
    valid: bool
    failure_reason: str | None = None
    record: HistoricalConsumption | None = None


def _normalize_header(fieldnames: list[str] | None) -> dict[str, str]:
    """Maps a lowercased/stripped column name back to its original header text."""
    if not fieldnames:
        return {}
    return {name.strip().lower(): name for name in fieldnames}


def _parse_row(
    row_reference: int,
    raw_row: dict[str, str],
    location_by_name: dict[str, Location],
    meal_type_by_name: dict[str, MealType],
) -> _RowOutcome:
    date_str = (raw_row.get("date") or "").strip()
    location_str = (raw_row.get("location") or "").strip()
    meal_type_str = (raw_row.get("meal_type") or "").strip()
    quantity_str = (raw_row.get("actual_consumed_quantity") or "").strip()

    missing = [
        name
        for name, value in (
            ("date", date_str),
            ("location", location_str),
            ("meal_type", meal_type_str),
            ("actual_consumed_quantity", quantity_str),
        )
        if not value
    ]
    if missing:
        return _RowOutcome(
            row_reference, False, f"Missing required field(s): {', '.join(missing)}."
        )

    try:
        record_date = date_type.fromisoformat(date_str)
    except ValueError:
        return _RowOutcome(
            row_reference, False, f"Invalid date '{date_str}' (expected YYYY-MM-DD)."
        )

    try:
        quantity = float(quantity_str)
    except ValueError:
        return _RowOutcome(
            row_reference, False, f"Actual Consumed Quantity '{quantity_str}' is not numeric."
        )
    if quantity < 0:
        return _RowOutcome(
            row_reference, False, f"Actual Consumed Quantity {quantity} must be >= 0."
        )

    location = location_by_name.get(location_str.lower())
    if location is None:
        return _RowOutcome(
            row_reference, False, f"Unrecognized location '{location_str}'."
        )

    meal_type = meal_type_by_name.get(meal_type_str.lower())
    if meal_type is None:
        return _RowOutcome(
            row_reference, False, f"Unrecognized meal type '{meal_type_str}'."
        )

    record = HistoricalConsumption(
        record_date=record_date,
        location_id=location.id,
        meal_type_id=meal_type.id,
        actual_consumed_quantity=quantity,
    )
    return _RowOutcome(row_reference, True, record=record)


def process_import(db: Session, uploaded_by_user_id: uuid.UUID, file_content: bytes) -> ImportJob:
    """
    Parses and validates the uploaded CSV synchronously (no background
    job queue — consistent with the "no unnecessary infrastructure"
    guardrail), then persists the job summary, valid records, and
    per-record errors in a single transaction.
    """
    try:
        text = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValidationError("File must be UTF-8 encoded text.") from None

    reader = csv.DictReader(io.StringIO(text))
    header_map = _normalize_header(reader.fieldnames)

    job = ImportJob(uploaded_by_user_id=uploaded_by_user_id, status="processing")
    db.add(job)
    db.flush()  # assign job.id without committing yet

    missing_columns = REQUIRED_COLUMNS - set(header_map.keys())
    if missing_columns:
        job.status = "failed"
        job.total_records = 0
        job.valid_records = 0
        job.invalid_records = 0
        db.add(
            ImportRecordError(
                import_job_id=job.id,
                row_reference=0,
                failure_reason=(
                    f"Missing required column(s) in file header: {', '.join(sorted(missing_columns))}."
                ),
            )
        )
        db.commit()
        db.refresh(job)
        return job

    # Preload reference data once, keyed by lowercased name, to avoid a
    # per-row database query for every location/meal-type lookup.
    locations = db.query(Location).filter(Location.is_active.is_(True)).all()
    meal_types = db.query(MealType).filter(MealType.is_active.is_(True)).all()
    location_by_name = {loc.name.lower(): loc for loc in locations}
    meal_type_by_name = {mt.name.lower(): mt for mt in meal_types}

    total = 0
    valid = 0
    invalid = 0
    for row_index, raw_row in enumerate(reader, start=1):
        total += 1
        # Translate the row's actual header casing back to our expected keys.
        normalized_row = {
            expected: raw_row.get(header_map.get(expected, ""), "")
            for expected in REQUIRED_COLUMNS
        }
        outcome = _parse_row(row_index, normalized_row, location_by_name, meal_type_by_name)
        if outcome.valid and outcome.record is not None:
            outcome.record.import_job_id = job.id
            db.add(outcome.record)
            valid += 1
        else:
            db.add(
                ImportRecordError(
                    import_job_id=job.id,
                    row_reference=outcome.row_reference,
                    failure_reason=outcome.failure_reason or "Unknown validation failure.",
                )
            )
            invalid += 1

    job.total_records = total
    job.valid_records = valid
    job.invalid_records = invalid
    job.status = "completed"

    db.commit()
    db.refresh(job)
    return job


def get_import_job(db: Session, import_id: uuid.UUID) -> ImportJob:
    job = db.get(ImportJob, import_id)
    if job is None:
        raise NotFoundError(f"Import job '{import_id}' not found.")
    return job


def list_import_errors(db: Session, import_id: uuid.UUID) -> list[ImportRecordError]:
    return (
        db.query(ImportRecordError)
        .filter(ImportRecordError.import_job_id == import_id)
        .order_by(ImportRecordError.row_reference.asc())
        .all()
    )


def list_import_jobs(db: Session, page: int, page_size: int) -> tuple[list[ImportJob], int]:
    """
    No filters, per the locked API Specification v1.0 Section 22, which
    explicitly lists this endpoint's filters as "none (all jobs)".
    """
    query = db.query(ImportJob)
    total_items = query.count()
    jobs = (
        query.order_by(ImportJob.uploaded_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return jobs, total_items
