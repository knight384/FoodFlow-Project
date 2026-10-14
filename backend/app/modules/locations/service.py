"""
Locations module business logic (SRS-FR-005).

Authorization (Admin for create/update/delete; all roles for view) is
enforced at the router level via app.core.dependencies.require_roles —
this service layer assumes the caller has already been authorized.

=== PROVISIONAL DECISION: deletion behavior ===
The deletion-safety strategy is explicitly unresolved (Database
Specification v1.0 Section 8/18/29; API Specification v1.0 Section 12).
API Specification v1.0 Section 12 describes two API-contract-compatible
outcomes (soft delete/archive, or restricted hard delete) and states
either can be implemented later without changing the endpoint's
signature (`DELETE /locations/{id}` -> success or conflict).

This implementation chooses **soft delete/archive** (setting
`is_active = False`, never physically removing the row) because:
1. It is the Database Specification's own stated recommendation
   (Section 18), specifically because it can never lose or orphan
   historical data — the strongest "preserve historical referential
   integrity" guarantee available.
2. A location, once soft-archived, is automatically excluded from
   creation of *new* historical/planned/forecast/recommendation records
   that reference it only insofar as it no longer appears in "active"
   listings by default — but existing historical rows referencing it
   remain fully intact and queryable.

This is a PROVISIONAL / IMPLEMENTATION-LEVEL decision, not a confirmed
business requirement. It does not foreclose switching to a "restricted
delete" policy later — see API Specification v1.0 Section 12 for how
that would be implemented against the same endpoint signature.
"""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DuplicateResourceError, NotFoundError, ValidationError
from app.modules.locations.models import Location


def list_locations(
    db: Session, page: int, page_size: int, include_inactive: bool
) -> tuple[list[Location], int]:
    query = db.query(Location)
    if not include_inactive:
        query = query.filter(Location.is_active.is_(True))
    total_items = query.count()
    locations = (
        query.order_by(Location.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return locations, total_items


def get_location(db: Session, location_id: uuid.UUID) -> Location:
    location = db.get(Location, location_id)
    if location is None:
        raise NotFoundError(f"Location '{location_id}' not found.")
    return location


def create_location(db: Session, name: str) -> Location:
    name = name.strip()
    if not name:
        raise ValidationError("Location name must not be empty.")

    existing = db.query(Location).filter(Location.name == name).one_or_none()
    if existing is not None:
        raise DuplicateResourceError(f"Location '{name}' already exists.")

    location = Location(name=name)
    db.add(location)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateResourceError(f"Location '{name}' already exists.") from None
    db.refresh(location)
    return location


def update_location(db: Session, location_id: uuid.UUID, name: str) -> Location:
    location = get_location(db, location_id)
    name = name.strip()
    if not name:
        raise ValidationError("Location name must not be empty.")

    if name != location.name:
        existing = db.query(Location).filter(Location.name == name).one_or_none()
        if existing is not None:
            raise DuplicateResourceError(f"Location '{name}' already exists.")
        location.name = name

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateResourceError(f"Location '{name}' already exists.") from None
    db.refresh(location)
    return location


def archive_location(db: Session, location_id: uuid.UUID) -> Location:
    """
    Soft-archive a location (see module docstring for why this is the
    chosen, provisional behavior). Idempotent: archiving an
    already-archived location simply confirms its current state.
    """
    location = get_location(db, location_id)
    location.is_active = False
    db.commit()
    db.refresh(location)
    return location
