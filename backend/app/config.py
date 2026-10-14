"""
Application configuration.

Loads configuration from environment variables (never hardcoded secrets),
consistent with TRD v1.0 Section 21 (Configuration and Environment Strategy).

Phase 1 scope only: application metadata, environment name, and database
connection string. No business-specific configuration (e.g., thresholds)
is defined here yet — those remain open decisions per the approved
Deferred Decisions lists in prior documents.
"""

import os
from functools import lru_cache


class Settings:
    """
    Minimal settings object. Values are read from environment variables
    at process start. No secrets are hardcoded or committed to source
    control (see backend/.env.example for the expected variable names).
    """

    # General application metadata
    app_name: str = "FoodFlow Backend"
    app_version: str = "0.1.0-phase1"

    # Environment: "development" | "test" | "production" (TRD v1.0 Section 21)
    environment: str = os.getenv("APP_ENVIRONMENT", "development")

    # Database connection (PostgreSQL, per TRD v1.0 Section 6 / Database Spec v1.0)
    # Expected format: postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://foodflow_app:foodflow_app@localhost:5432/foodflow_dev",
    )

    # CORS: allow the local frontend dev server to call the backend during development.
    cors_allowed_origins: list[str] = os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")

    # --- Authentication (Phase 3) ---
    # Stateless JWT access tokens (see app/core/security.py docstring for
    # the rationale and stated trade-offs of this proposed technical
    # decision). JWT_SECRET_KEY MUST be overridden via a real environment
    # variable outside local development — the default below is only a
    # convenience for `docker compose`-based local dev and is
    # deliberately obvious/unsuitable for any shared environment.
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY", "dev-only-insecure-secret-change-me"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    # --- Classification threshold (Phase 4) ---
    # PROVISIONAL / TEST CONFIGURATION ONLY — NOT a confirmed business
    # decision. The numeric surplus/shortage threshold is explicitly
    # unresolved (SRS v1.0 Section 14; Database Specification v1.0
    # Section 13/29; API Specification v1.0 Section 18/24/29). This
    # value exists only so the classification logic (app/modules/
    # classification/service.py) is exercisable and testable in Phase 4.
    # It represents a percentage variance (relative to Forecasted
    # Demand) beyond which a period is classified Surplus/Shortage
    # rather than Balanced. It MUST be replaced with a confirmed
    # business value (and, per the Database Specification's proposed
    # design, likely moved into a proper configuration mechanism) before
    # this is treated as production-ready.
    provisional_classification_threshold_percentage: float = float(
        os.getenv("CLASSIFICATION_THRESHOLD_PERCENTAGE", "10.0")
    )

    # --- Forecasting (Phase 5) ---
    # PROVISIONAL / TEST CONFIGURATION ONLY — NOT a confirmed business
    # decision. The minimum historical-data sufficiency threshold is
    # explicitly unresolved (SRS v1.0 Section 11/13; TRD v1.0 Section 12;
    # ML & Testing Plan v1.0 Section 8/12 item 3). This value is the
    # minimum number of historical_consumption records required for a
    # given (location, meal type) before a forecast will be generated;
    # below it, the system returns FORECAST_UNAVAILABLE rather than a
    # fabricated value (SRS-FR-013). Must be replaced with a confirmed
    # business value before this is production-ready.
    min_historical_records_for_forecast: int = int(
        os.getenv("MIN_HISTORICAL_RECORDS_FOR_FORECAST", "7")
    )
    # The lookback window (in most-recent records) used by the selected
    # forecasting approach (recent-period mean — see
    # app/modules/forecasting/algorithm.py for the evaluation that
    # selected it). Not a business decision — an algorithm parameter.
    forecast_recent_window_size: int = int(
        os.getenv("FORECAST_RECENT_WINDOW_SIZE", "14")
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (avoids re-reading env vars repeatedly)."""
    return Settings()
