"""
reports module.

Read-oriented historical, filterable reporting queries. See TRD v1.0
Section 8, SRS-FR-030-031.

Database note: this module owns no table of its own — it composes data
from historical_consumption (indirectly), forecasted_demand, and
planned_quantity via app.modules.classification.service.compute_classifications
(Database Specification v1.0 Section 18). No models.py file exists here.

Phase 6 (API Completion & System Integration) status: implemented.
- schemas.py — ReportResponseItem, ReportListResponse (no recommendation
  field, unlike Dashboard — matches API Specification v1.0 Section 21's
  documented response shape exactly)
- service.py — get_reports (in-memory pagination over the classification
  result list, after any status filter)
- router.py — RPT-001 (API Specification v1.0 Section 21). Manager/Admin
  only — Operations Staff "limited" access is a pending-confirmation
  cell, NOT implemented. dateFrom/dateTo are required query parameters.
"""
