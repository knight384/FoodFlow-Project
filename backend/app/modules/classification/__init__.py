"""
classification module.

Surplus/Shortage/Balanced threshold classification, computed
dynamically. See TRD v1.0 Section 9, SRS-FR-021-023.

Database note: per Database Specification v1.0 Section 13, Classification
is deliberately NOT a standalone persisted table — it is computed
dynamically from the dynamically-computed Variance (see the `comparison`
module) plus a configurable threshold. The only durable trace of a
Surplus classification is the existence of a `redistribution_recommendation`
row (see the `recommendations` module). No models.py file exists here.

Phase 4 (Core Backend Business Features) status: implemented.
- schemas.py — ClassificationResponseItem, ClassificationListResponse
- service.py — classify_row, compute_classifications, get_classification_for_period.
  Uses a PROVISIONAL, clearly-labeled percentage threshold (see service.py
  docstring and app/config.py) — the real numeric threshold remains
  unresolved (SRS v1.0 Section 14). Zero-forecast periods are classified
  "unavailable" (a safe placeholder, not a resolution of that open edge case).
- router.py — CLS-001 (API Specification v1.0 Section 18). Manager/Admin
  authorization only.
"""
