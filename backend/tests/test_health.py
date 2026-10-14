"""
Phase 1 verification test: confirms the FastAPI application boots and the
liveness health-check endpoint responds correctly.

This is NOT the detailed executable test suite described in ML & Testing
Plan v1.0 (Section 10) — that is explicitly out of scope for Phase 1.
This single test exists only to verify the foundation works, per the
Phase 1 task's "verify the foundation works" instruction.

Note: /health/db is intentionally not asserted against a live database
here, since Phase 1 does not require a running PostgreSQL instance to
be present in every environment (e.g., CI without a DB service). Run it
manually (see backend/README.md) to verify DB connectivity locally.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body
    assert "version" in body
