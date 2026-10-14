"""
comparison module.

Variance calculation (Forecasted Demand vs Planned Quantity), computed
dynamically. See TRD v1.0 Section 9, SRS-FR-018-020.

Database note: per Database Specification v1.0 Section 12, Variance is
deliberately NOT a persisted table — it is computed dynamically at query
time from `forecasted_demand` and `planned_quantity` rows for a matching
period. No models.py file exists in this module for that reason.

Phase 4 (Core Backend Business Features) status: implemented.
- schemas.py — ComparisonResponseItem, ComparisonListResponse (read-only,
  no request/create schema)
- service.py — compute_comparisons, get_comparison_for_period (also used
  internally by the classification module)
- router.py — CMP-001 (API Specification v1.0 Section 17). Manager/Admin
  authorization only.
"""
