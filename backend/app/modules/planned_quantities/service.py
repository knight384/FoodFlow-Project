"""
Planned-quantities module business logic (SRS-FR-014–017).

Authorization: create/edit is restricted to Operations Staff (confirmed
by SRS/PRD/API Specification); Admin/Manager entry ability remains
"pending permission confirmation" and is therefore NOT implemented here
(enforced at the router level). View is open to all authenticated
roles — this is not one of the unresolved permission-matrix cells.

Edit-window rule: NOT implemented, per API Specification v1.0 Section 16
("This API allows editing at any time until the rule is confirmed").

Side effect: creating or updating a Planned Quantity triggers a
recommendation recomputation for that period — see
app/modules/recommendations/service.py's module docstring for the full
rationale of why this specific trigger point was chosen.
"""

import uuid
from datetime import date as date_type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DuplicateResourceError, NotFoundError, ValidationError
from app.modules.locations.models import Location
from app.modules.meal_types.models import MealType
from app.modules.planned_quantities.models import PlannedQuantity


def _validate_references(db: Session, location_id: uuid.UUID, meal_type_id: uuid.UUID) -> None:
    location = db.get(Location, location_id)
    if location is None or not location.is_active:
        raise ValidationError(f"Location '{location_id}' does not exist or is not active.")
    meal_type = db.get(MealType, meal_type_id)
    if meal_type is None or not meal_type.is_active:
        raise ValidationError(f"Meal type '{meal_type_id}' does not exist or is not active.")


def list_planned_quantities(
    db: Session,
    page: int,
    page_size: int,
    location_id: uuid.UUID | None = None,
    meal_type_id: uuid.UUID | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
) -> tuple[list[PlannedQuantity], int]:
    query = db.query(PlannedQuantity)
    if location_id is not None:
        query = query.filter(PlannedQuantity.location_id == location_id)
    if meal_type_id is not None:
        query = query.filter(PlannedQuantity.meal_type_id == meal_type_id)
    if date_from is not None:
        query = query.filter(PlannedQuantity.plan_date >= date_from)
    if date_to is not None:
        query = query.filter(PlannedQuantity.plan_date <= date_to)

    total_items = query.count()
    entries = (
        query.order_by(PlannedQuantity.plan_date.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return entries, total_items


def get_planned_quantity(db: Session, planned_quantity_id: uuid.UUID) -> PlannedQuantity:
    entry = db.get(PlannedQuantity, planned_quantity_id)
    if entry is None:
        raise NotFoundError(f"Planned Quantity '{planned_quantity_id}' not found.")
    return entry


def create_planned_quantity(
    db: Session,
    plan_date: date_type,
    location_id: uuid.UUID,
    meal_type_id: uuid.UUID,
    quantity: float,
    entered_by_user_id: uuid.UUID,
) -> PlannedQuantity:
    _validate_references(db, location_id, meal_type_id)

    existing = (
        db.query(PlannedQuantity)
        .filter_by(plan_date=plan_date, location_id=location_id, meal_type_id=meal_type_id)
        .one_or_none()
    )
    if existing is not None:
        raise DuplicateResourceError(
            "A Planned Quantity already exists for this date/location/meal type. "
            "Use PATCH to edit it instead."
        )

    entry = PlannedQuantity(
        plan_date=plan_date,
        location_id=location_id,
        meal_type_id=meal_type_id,
        quantity=quantity,
        entered_by_user_id=entered_by_user_id,
    )
    db.add(entry)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateResourceError(
            "A Planned Quantity already exists for this date/location/meal type. "
            "Use PATCH to edit it instead."
        ) from None
    db.refresh(entry)

    _refresh_recommendation(db, entry)
    return entry


def update_planned_quantity(
    db: Session, planned_quantity_id: uuid.UUID, quantity: float
) -> PlannedQuantity:
    entry = get_planned_quantity(db, planned_quantity_id)
    entry.quantity = quantity
    db.commit()
    db.refresh(entry)

    _refresh_recommendation(db, entry)
    return entry


def _refresh_recommendation(db: Session, entry: PlannedQuantity) -> None:
    """
    Best-effort recommendation recomputation side effect (see module
    docstring). Import is deferred to function scope to avoid a
    module-level circular import: recommendations.service imports
    classification.service, which imports comparison.service, which
    imports planned_quantities.models (not this service module) — so
    there is no true cycle, but keeping the import local here makes the
    one-directional dependency (planned_quantities -> recommendations)
    explicit and easy to spot during review.
    """
    from app.modules.recommendations.service import ensure_recommendation_for_period

    ensure_recommendation_for_period(db, entry.location_id, entry.meal_type_id, entry.plan_date)
