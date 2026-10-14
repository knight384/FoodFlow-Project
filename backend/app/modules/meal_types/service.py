"""
Meal-types module business logic (SRS-FR-006).

Meal types remain fully configurable — no enum, no hardcoded
Breakfast/Lunch/Dinner values anywhere in this module.

=== PROVISIONAL DECISION: deletion behavior ===
Identical reasoning and choice as app/modules/locations/service.py's
module docstring: soft-archive via `is_active = False`, chosen as the
safest, historical-integrity-preserving option, explicitly provisional
and not a confirmed business decision. See that module's docstring for
the full rationale (not duplicated here to avoid redundant logic per
the modular-monolith module-boundary design — the two modules'
implementations remain independent, but the design reasoning is shared).
"""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DuplicateResourceError, NotFoundError, ValidationError
from app.modules.meal_types.models import MealType


def list_meal_types(
    db: Session, page: int, page_size: int, include_inactive: bool
) -> tuple[list[MealType], int]:
    query = db.query(MealType)
    if not include_inactive:
        query = query.filter(MealType.is_active.is_(True))
    total_items = query.count()
    meal_types = (
        query.order_by(MealType.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return meal_types, total_items


def get_meal_type(db: Session, meal_type_id: uuid.UUID) -> MealType:
    meal_type = db.get(MealType, meal_type_id)
    if meal_type is None:
        raise NotFoundError(f"Meal type '{meal_type_id}' not found.")
    return meal_type


def create_meal_type(db: Session, name: str) -> MealType:
    name = name.strip()
    if not name:
        raise ValidationError("Meal type name must not be empty.")

    existing = db.query(MealType).filter(MealType.name == name).one_or_none()
    if existing is not None:
        raise DuplicateResourceError(f"Meal type '{name}' already exists.")

    meal_type = MealType(name=name)
    db.add(meal_type)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateResourceError(f"Meal type '{name}' already exists.") from None
    db.refresh(meal_type)
    return meal_type


def update_meal_type(db: Session, meal_type_id: uuid.UUID, name: str) -> MealType:
    meal_type = get_meal_type(db, meal_type_id)
    name = name.strip()
    if not name:
        raise ValidationError("Meal type name must not be empty.")

    if name != meal_type.name:
        existing = db.query(MealType).filter(MealType.name == name).one_or_none()
        if existing is not None:
            raise DuplicateResourceError(f"Meal type '{name}' already exists.")
        meal_type.name = name

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateResourceError(f"Meal type '{name}' already exists.") from None
    db.refresh(meal_type)
    return meal_type


def archive_meal_type(db: Session, meal_type_id: uuid.UUID) -> MealType:
    """Soft-archive a meal type — see module docstring for rationale."""
    meal_type = get_meal_type(db, meal_type_id)
    meal_type.is_active = False
    db.commit()
    db.refresh(meal_type)
    return meal_type
