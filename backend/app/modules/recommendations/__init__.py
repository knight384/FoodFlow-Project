"""
recommendations module.

Rule-based, advisory redistribution recommendation generation. See TRD v1.0 Section 9/17, SRS-FR-024-027.

Phase 2: RedistributionRecommendation ORM model (see models.py).

Phase 4 (Core Backend Business Features) status: implemented.
- schemas.py — RecommendationResponse, RecommendationListResponse (no create schema — see below)
- service.py — ensure_recommendation_for_period (idempotent upsert, Surplus-only), list/get_recommendation
- router.py — REC-001..002 (read-only). No POST endpoint — recommendations are generated automatically
  as a side effect of Planned Quantity create/update (see service.py's module docstring for the
  full trigger-point rationale, explicitly flagged as a proposed implementation decision).
"""
