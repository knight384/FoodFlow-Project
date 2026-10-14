"""
FastAPI application entrypoint.

PHASE 1 (repository & environment setup): application boot, CORS, and
two infrastructure health-check endpoints:
    GET /health      -> application process is up
    GET /health/db   -> application can reach PostgreSQL

PHASE 3 (backend foundation: authentication + authorization + user
foundation) added, under the `/api/v1` prefix (API Specification v1.0
Section 4):
    /api/v1/auth/*    -> login, logout, current-user identity (AUTH-001..003)
    /api/v1/users/*    -> Admin-only user management (USR-001..005)

PHASE 4 (core backend business features) adds:
    /api/v1/locations/*            -> LOC-001..005
    /api/v1/meal-types/*            -> MEAL-001..005
    /api/v1/historical-data/*        -> HIST-001..003
    /api/v1/planned-quantities/*      -> PQ-001..004
    /api/v1/comparisons               -> CMP-001 (read-only, dynamically computed)
    /api/v1/classifications            -> CLS-001 (read-only, dynamically computed)
    /api/v1/recommendations             -> REC-001..002 (read-only; generated
                                            automatically by backend logic, see
                                            app/modules/recommendations/service.py)

PHASE 5 (ML / forecasting implementation) adds:
    /api/v1/forecasts/*                  -> FC-001..003 (generate/list/retrieve
                                            Forecasted Demand; see
                                            app/modules/forecasting/algorithm.py
                                            for the evidence-based model selection)

PHASE 6 (API completion & system integration) adds:
    /api/v1/dashboard                      -> DASH-001 (aggregated summary;
                                              reuses classification/comparison/
                                              recommendations, no new table)
    /api/v1/reports                          -> RPT-001 (historical, filterable
                                                report; reuses classification)
and a global catch-all exception handler (see handle_unexpected_error
below) guaranteeing the standard error envelope for genuinely
unexpected errors too, not just the two previously-handled categories.

and a global exception-handling layer that converts every application
error (app.core.errors.AppError subclasses) and FastAPI's own request-
validation errors into the single standard error envelope defined in
API Specification v1.0 Section 8.

All 34 endpoints in API Specification v1.0's inventory are now
registered. Business frontend UI remains out of scope (Phase 7).
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.errors import AppError
from app.database import check_database_connection
from app.modules.auth.router import router as auth_router
from app.modules.classification.router import router as classification_router
from app.modules.comparison.router import router as comparison_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.forecasting.router import router as forecasting_router
from app.modules.historical_data.router import router as historical_data_router
from app.modules.locations.router import router as locations_router
from app.modules.meal_types.router import router as meal_types_router
from app.modules.planned_quantities.router import router as planned_quantities_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.reports.router import router as reports_router
from app.modules.users.router import router as users_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "FoodFlow API — Phase 6 (API completion & system integration). "
        "All 34 endpoints from API Specification v1.0's inventory are "
        "implemented: authentication/RBAC, users, locations, meal types, "
        "historical data import, planned quantities, forecasting (baseline "
        "model, evidence-based selection), dynamic comparison/"
        "classification, rule-based recommendations, an aggregated "
        "dashboard, and filterable historical reports. Frontend business "
        "UI remains out of scope (Phase 7)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_V1_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(users_router, prefix=API_V1_PREFIX)
app.include_router(locations_router, prefix=API_V1_PREFIX)
app.include_router(meal_types_router, prefix=API_V1_PREFIX)
app.include_router(historical_data_router, prefix=API_V1_PREFIX)
app.include_router(planned_quantities_router, prefix=API_V1_PREFIX)
app.include_router(forecasting_router, prefix=API_V1_PREFIX)
app.include_router(comparison_router, prefix=API_V1_PREFIX)
app.include_router(classification_router, prefix=API_V1_PREFIX)
app.include_router(recommendations_router, prefix=API_V1_PREFIX)
app.include_router(dashboard_router, prefix=API_V1_PREFIX)
app.include_router(reports_router, prefix=API_V1_PREFIX)


# --------------------------------------------------------------------------
# Standard error envelope (API Specification v1.0 Section 8)
# --------------------------------------------------------------------------


@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    """Converts every application-raised error into the standard envelope."""
    body: dict = {"error": {"category": exc.category, "message": exc.message}}
    if exc.details:
        body["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Converts FastAPI/Pydantic's default validation-error shape into the
    same standard envelope used by application-raised ValidationErrors,
    so the frontend only ever has to handle one error shape (API
    Specification v1.0 Section 8/23).
    """
    details = [
        {"field": ".".join(str(p) for p in err["loc"] if p != "body"), "issue": err["msg"]}
        for err in exc.errors()
    ]
    body = {
        "error": {
            "category": "VALIDATION_ERROR",
            "message": "The request could not be validated.",
            "details": details,
        }
    }
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body)


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """
    Phase 6 addition: catch-all for any exception NOT already handled by
    the two handlers above (i.e., a genuine bug, not an anticipated
    business/validation error).

    Why added now: Phase 4's verification pass (docs/phase-4-verification-
    pass-2.md, Section 2.3) identified that without this handler, an
    unexpected error would fall through to FastAPI's default handling
    and NOT produce the standard envelope — silently violating this
    project's own "Do not introduce a second error format" rule (API
    Specification v1.0 Section 8) the moment any uncaught bug occurred.
    Phase 6's explicit integration-testing work (Journeys A-G,
    tests/test_integration_e2e.py) exercises substantially more of the
    codebase's cross-module call paths than any single prior phase did,
    which is exactly the situation where an unanticipated exception in
    integrated code becomes more likely to actually occur — closing
    this gap now, rather than continuing to defer it, keeps the "API
    Contract Consistency" audit's claim (Section 7 of this phase's
    instructions) actually true for every response, not just the two
    previously-handled categories.

    Never leaks internals: the response body contains only a fixed,
    generic message — no exception text, no stack trace, no file paths.
    The real exception is logged server-side (not returned to the
    client) so it remains debuggable without exposing anything.
    """
    logging.getLogger("foodflow.unhandled").exception(
        "Unhandled exception while processing %s %s", request.method, request.url.path
    )
    body = {
        "error": {
            "category": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again shortly.",
        }
    }
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)


# --------------------------------------------------------------------------
# Health checks (Phase 1 — unchanged)
# --------------------------------------------------------------------------


@app.get("/health", tags=["health"])
def health() -> dict:
    """
    Basic liveness check: confirms the FastAPI process is running.
    Does not touch the database — see /health/db for that.
    """
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health/db", tags=["health"])
def health_db() -> dict:
    """
    Database connectivity check: attempts a minimal round-trip query
    against PostgreSQL (see app.database.check_database_connection).
    """
    is_connected, error = check_database_connection()
    if is_connected:
        return {"status": "ok", "database": "reachable"}
    return {"status": "error", "database": "unreachable", "detail": error}
