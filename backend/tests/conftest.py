"""
Shared pytest fixtures for tests that require a live database (Phase 4
business-logic tests) — as opposed to tests/test_health.py and
tests/test_auth_users_wiring.py, which are deliberately DB-free.

=== Testing-approach trade-off (documented, not hidden) ===
These fixtures run against the SAME database the app is configured to
use (DATABASE_URL — typically the local Postgres started via
`docker compose up -d`, per backend/README.md), rather than a fully
isolated, transactionally-rolled-back test database. This is a
deliberate simplification: a proper SAVEPOINT-based transactional
rollback fixture is the more rigorous approach, but this could not be
authored *and verified* without a live database available in the
authoring environment (see docs/phase-4-verification.md, Section 5).

To keep this safe on a shared dev database:
- All test-created data (users, locations, meal types, historical
  records, planned quantities) uses clearly-labeled, uniquely-suffixed
  names (e.g., "Test Location {uuid4}"), so it can never collide with
  or be mistaken for real seed/demo data (Database Specification v1.0
  Section 26).
- Nothing here ever touches or asserts against pre-existing rows from
  scripts/seed_demo_data.py.
- This is explicitly a development/test database per backend/README.md
  and data/README.md — never a production database.

A future phase should consider migrating to a dedicated test database
with transactional rollback per test, for full isolation and speed.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.database import SessionLocal, get_db
from app.main import app
from app.modules.users.models import APPROVED_ROLE_NAMES, Role, User
from scripts.seed_reference_data import seed_roles


@pytest.fixture(scope="session", autouse=True)
def _ensure_roles_seeded() -> None:
    """Roles are mandatory reference data (Database Spec v1.0 Section 26),
    not test pollution — safe and correct to seed once per test session
    using the same idempotent script used in real deployments."""
    seed_roles()


@pytest.fixture()
def db() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db: Session) -> TestClient:
    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


def _create_user_and_token(db: Session, role_name: str) -> tuple[User, str]:
    role = db.query(Role).filter_by(name=role_name).one()
    username = f"test_{role_name}_{uuid.uuid4().hex[:8]}"
    user = User(username=username, password_hash=hash_password("Test1234!"), role_id=role.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user_id=str(user.id), role_name=role_name)
    return user, token


@pytest.fixture()
def admin_user_and_token(db: Session) -> tuple[User, str]:
    assert "administrator" in APPROVED_ROLE_NAMES
    return _create_user_and_token(db, "administrator")


@pytest.fixture()
def manager_user_and_token(db: Session) -> tuple[User, str]:
    return _create_user_and_token(db, "manager")


@pytest.fixture()
def ops_staff_user_and_token(db: Session) -> tuple[User, str]:
    return _create_user_and_token(db, "operations_staff")


@pytest.fixture()
def admin_headers(admin_user_and_token: tuple[User, str]) -> dict:
    _, token = admin_user_and_token
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def manager_headers(manager_user_and_token: tuple[User, str]) -> dict:
    _, token = manager_user_and_token
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def ops_staff_headers(ops_staff_user_and_token: tuple[User, str]) -> dict:
    _, token = ops_staff_user_and_token
    return {"Authorization": f"Bearer {token}"}


def unique_name(prefix: str) -> str:
    """Generates a clearly-labeled, collision-free synthetic test name."""
    return f"Test {prefix} {uuid.uuid4().hex[:8]}"


def collection_contains_id(client: TestClient, url: str, headers: dict, target_id: str, params: dict | None = None) -> bool:
    """
    Searches every page of a paginated collection endpoint for `target_id`,
    rather than assuming it appears on the (arbitrary, default-sized)
    first page.

    Why this exists: `/locations` and `/meal-types` (and similar
    collection endpoints) are correctly, deliberately paginated per API
    Specification v1.0 Section 22 (default page size 20, ordered by
    name) — there is no guarantee, and the spec makes no promise, that
    a freshly created row appears on an unfiltered default-sized first
    page once the total row count exceeds one page. Because
    conftest.py's fixtures intentionally run against a shared,
    persistent dev database (see this module's docstring) rather than
    an isolated, rolled-back one, accumulated rows from many prior test
    runs can push a table's row count past 20 over time — at which
    point a plain `client.get(url)` followed by `any(row["id"] ==
    target_id ...)` becomes non-deterministic (it depends on where the
    new row's name happens to sort among however many rows already
    exist), not because of any defect in the list endpoint itself.

    This helper makes "is this item in the collection" a correct,
    deterministic check regardless of how large the table has grown, by
    walking every page using the response's own pagination metadata.
    Bounded by `totalPages` (with a hard safety cap) so it can never
    loop indefinitely even if pagination metadata were ever wrong.
    """
    page = 1
    max_pages_safety_cap = 1000  # guards against a pathological/incorrect totalPages value
    while page <= max_pages_safety_cap:
        query_params = dict(params or {})
        query_params["page"] = page
        query_params["pageSize"] = 100  # MAX_PAGE_SIZE — minimizes the number of requests needed
        response = client.get(url, params=query_params, headers=headers)
        assert response.status_code == 200, f"Unexpected status while paginating {url}: {response.status_code}"
        body = response.json()
        if any(row["id"] == target_id for row in body["data"]):
            return True
        total_pages = body.get("pagination", {}).get("totalPages", 0)
        if page >= total_pages:
            return False
        page += 1
    return False
