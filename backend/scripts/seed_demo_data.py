"""
Seed OPTIONAL synthetic/demo data: a couple of sample locations, meal
types, and a small synthetic historical_consumption dataset.

Per Database Specification v1.0 Section 26 (Seed / Demo Data Strategy):
this data supports local development and mentor demonstrations without
requiring real SensorSpine operational data (whose availability remains
an open Must-Clarify question across every prior planning document).

IMPORTANT: everything created by this script is clearly synthetic/demo
data, not real SensorSpine data, per the explicit instruction in every
prior planning document. Do not treat any value here as a real
operational figure.

This script is separate from scripts/seed_reference_data.py (roles),
which seeds mandatory reference data rather than demo data — running
this script is optional.

This script performs direct database inserts for seeding purposes only.
It does NOT go through (and does not simulate) the historical-data
upload/validation workflow described in SRS-FR-007-010 / API
Specification v1.0 Section 14 — that workflow is not implemented until
a later phase. Records inserted here have no `import_job_id` (it is
nullable, per Database Specification v1.0 Section 6.5).

Usage:
    cd backend
    python3 -m scripts.seed_demo_data
"""

import random
from datetime import date, timedelta

from app.database import session_scope
from app.modules.historical_data.models import HistoricalConsumption
from app.modules.locations.models import Location
from app.modules.meal_types.models import MealType

# Fixed seed for reproducible demo output across runs.
_RNG = random.Random(42)

DEMO_LOCATION_NAMES = ["Main Cafeteria (Demo)", "North Campus Dining (Demo)"]
DEMO_MEAL_TYPE_NAMES = ["Breakfast", "Lunch", "Dinner"]

# A modest, illustrative historical window — not a claim about the
# minimum data-sufficiency threshold, which remains unresolved (ML &
# Testing Plan v1.0 Section 12, item 3).
DEMO_HISTORY_DAYS = 60
# Plausible baseline quantity per meal type, with randomized daily
# variation — synthetic, not derived from any real dataset.
BASE_QUANTITY_BY_MEAL_TYPE = {"Breakfast": 120, "Lunch": 260, "Dinner": 190}


def _get_or_create_locations(db) -> list[Location]:
    locations = []
    for name in DEMO_LOCATION_NAMES:
        existing = db.query(Location).filter_by(name=name).one_or_none()
        if existing is None:
            existing = Location(name=name)
            db.add(existing)
            db.flush()
        locations.append(existing)
    return locations


def _get_or_create_meal_types(db) -> list[MealType]:
    meal_types = []
    for name in DEMO_MEAL_TYPE_NAMES:
        existing = db.query(MealType).filter_by(name=name).one_or_none()
        if existing is None:
            existing = MealType(name=name)
            db.add(existing)
            db.flush()
        meal_types.append(existing)
    return meal_types


def seed_demo_data() -> None:
    with session_scope() as db:
        locations = _get_or_create_locations(db)
        meal_types = _get_or_create_meal_types(db)
        db.commit()

        # Only generate historical records if none exist yet for these
        # demo locations, to keep the script safely re-runnable.
        already_seeded = (
            db.query(HistoricalConsumption)
            .filter(HistoricalConsumption.location_id.in_([loc.id for loc in locations]))
            .first()
        )
        if already_seeded is not None:
            print(
                "Demo historical_consumption records already exist for the "
                "demo locations — skipping generation to avoid duplicates "
                "(duplicate-record policy is unresolved; see Database "
                "Specification v1.0 Section 29, item 1)."
            )
            return

        today = date.today()
        records_created = 0
        for day_offset in range(DEMO_HISTORY_DAYS, 0, -1):
            record_date = today - timedelta(days=day_offset)
            for location in locations:
                for meal_type in meal_types:
                    base = BASE_QUANTITY_BY_MEAL_TYPE.get(meal_type.name, 150)
                    # +/- 15% synthetic daily variation.
                    quantity = round(base * _RNG.uniform(0.85, 1.15))
                    db.add(
                        HistoricalConsumption(
                            record_date=record_date,
                            location_id=location.id,
                            meal_type_id=meal_type.id,
                            actual_consumed_quantity=quantity,
                        )
                    )
                    records_created += 1
        db.commit()
        print(
            f"Seeded {len(locations)} demo location(s), "
            f"{len(meal_types)} meal type(s), and {records_created} "
            f"synthetic historical_consumption record(s) "
            f"({DEMO_HISTORY_DAYS} days)."
        )


if __name__ == "__main__":
    seed_demo_data()
