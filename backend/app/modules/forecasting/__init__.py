"""
forecasting module.

Interfaces with the internal Forecasting/ML module to produce Forecasted
Demand. See TRD v1.0 Section 8/12, SRS-FR-011-013.

Phase 2 (Database Implementation) status: ForecastedDemand ORM model
(see models.py).

Phase 5 (ML / Forecasting Implementation) status: implemented.
- preprocessing.py — historical series retrieval (no data leakage; day-of-
  week derived here, never persisted, per Database Spec Section 6.5)
- algorithm.py — baseline (recent-period mean) and candidate (day-of-week
  seasonal mean) approaches; documents the evidence-based selection of
  the baseline as the production model, per real evaluation against the
  seeded synthetic demo dataset (see that file's module docstring)
- evaluation.py — reusable MAE/MAPE evaluation harness (time-based
  train/holdout split), used both for the one-time selection exercise
  and as an ongoing regression check (tests/test_forecasting.py)
- interface.py — the narrow prediction interface (TRD v1.0 Section 12):
  (location, meal type, date) -> Forecasted Demand, or a clear
  InsufficientHistoricalDataError — never a fabricated value
- schemas.py — ForecastGenerateRequest, ForecastResponse, ForecastListResponse
- service.py — generate_or_get_forecast (single-active-forecast model,
  Database Spec Section 6.8/17), list/get_forecast
- router.py — FC-001..003 (API Specification v1.0 Section 15).
  Manager/Admin only — Operations Staff visibility remains a pending-
  confirmation cell and is NOT implemented.

No forecasting algorithm was pre-selected by any planning document —
the selection documented in algorithm.py is evidence-based, reproducible,
and explicitly open to revision once real (non-synthetic) operational
data is available.
"""
