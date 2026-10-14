"""
dashboard module.

Read-oriented aggregation of forecast/planned/variance/status/recommendation
data. See TRD v1.0 Section 8, SRS-FR-028-029.

Database note: this module owns no table of its own — it composes data
from forecasted_demand, planned_quantity, and redistribution_recommendation
via app.modules.classification.service.compute_classifications (Database
Specification v1.0 Section 18). No models.py file exists in this module.

Phase 6 (API Completion & System Integration) status: implemented.
- schemas.py — DashboardResponseItem, DashboardRecommendation, DashboardListResponse
- service.py — get_dashboard (default 14-day upcoming window when no
  date filter given; batch-fetches matching recommendations in one
  query to avoid N+1)
- router.py — DASH-001 (API Specification v1.0 Section 20). Manager/Admin only.
"""
