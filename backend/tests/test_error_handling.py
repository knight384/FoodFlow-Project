"""
Phase 6 test: confirms the global catch-all exception handler
(app.main.handle_unexpected_error) converts a genuinely unexpected
exception into the standard error envelope, rather than leaking a raw
traceback or falling back to FastAPI's default error response.

DB-free, following the same pattern as tests/test_auth_users_wiring.py
(Phase 3): patches app.modules.auth.service.authenticate_user to raise
BEFORE it touches the database, so this test needs no live PostgreSQL
connection -- constructing a SQLAlchemy Session (via the get_db
dependency) does not itself open a network connection; only an actual
query would, and the patched function never issues one.
"""

from fastapi.testclient import TestClient

import app.modules.auth.router as auth_router_module
from app.main import app


def test_unexpected_exception_returns_standard_internal_error_envelope(monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError("simulated unexpected failure -- must never leak to the client")

    monkeypatch.setattr(auth_router_module, "authenticate_user", _boom)

    # raise_server_exceptions=False: get the actual HTTP response our
    # exception handler produced, instead of TestClient re-raising the
    # exception (its default behavior, which would defeat the point of
    # this test -- we want to see what a real client would receive).
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/api/v1/auth/login", json={"username": "irrelevant", "password": "irrelevant"}
    )

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["category"] == "INTERNAL_ERROR"
    assert "message" in body["error"]

    # Never leaks internals: the raised exception's own text must not
    # appear anywhere in the response body.
    assert "simulated unexpected failure" not in response.text
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text
