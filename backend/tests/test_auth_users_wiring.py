"""
Phase 3 verification tests: confirm the auth/users routers are wired
correctly and the standard error envelope is produced, WITHOUT requiring
a live PostgreSQL connection.

Why these specific tests don't need a database: creating a SQLAlchemy
Session (app.database.SessionLocal()) does not open a network connection
by itself — a connection is only opened when a query actually executes.
Both cases below are rejected before any query runs:
- A missing Authorization header fails in app.core.dependencies.get_current_user
  before it ever calls db.get(...).
- A malformed request body fails Pydantic validation before the route
  handler body (and therefore any query) executes.

This is NOT the full test suite described in ML & Testing Plan v1.0
Section 10 — those (e.g., actually logging in, actually creating a user)
require a live, seeded database and should be run in an environment with
one (see docs/phase-3-verification.md).
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_protected_endpoint_without_token_returns_401_envelope() -> None:
    response = client.get("/api/v1/users")
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["category"] == "AUTHENTICATION_ERROR"
    assert "message" in body["error"]


def test_protected_endpoint_with_garbage_token_returns_401_envelope() -> None:
    response = client.get(
        "/api/v1/users", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["category"] == "AUTHENTICATION_ERROR"


def test_login_with_missing_password_returns_validation_envelope() -> None:
    response = client.post("/api/v1/auth/login", json={"username": "someone"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["category"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)
    assert len(body["error"]["details"]) >= 1


def test_current_user_endpoint_requires_auth() -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["category"] == "AUTHENTICATION_ERROR"
