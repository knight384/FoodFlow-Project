"""
Seed mandatory reference data: the three approved roles.

Per Database Specification v1.0 Section 26: the `roles` rows
(administrator, manager, operations_staff) are genuinely part of the
approved system configuration — not "sample" or "demo" data — so this
script is separate from scripts/seed_demo_data.py, which seeds clearly
synthetic/demo data instead.

This script is idempotent: running it multiple times will not create
duplicate role rows.

Usage:
    cd backend
    python3 -m scripts.seed_reference_data
"""

from app.database import session_scope
from app.modules.users.models import APPROVED_ROLE_NAMES, Role


def seed_roles() -> None:
    with session_scope() as db:
        existing = {row.name for row in db.query(Role).all()}
        created = []
        for name in APPROVED_ROLE_NAMES:
            if name not in existing:
                db.add(Role(name=name))
                created.append(name)
        db.commit()

    if created:
        print(f"Seeded {len(created)} role(s): {', '.join(created)}")
    else:
        print("All approved roles already present — nothing to seed.")


if __name__ == "__main__":
    seed_roles()
