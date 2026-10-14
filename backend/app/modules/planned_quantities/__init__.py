"""
planned_quantities module.

Operations Staff entry/edit/view of Planned Quantity. See TRD v1.0 Section 8, SRS-FR-014-017.

Phase 2: PlannedQuantity ORM model (see models.py).

Phase 4 (Core Backend Business Features) status: implemented.
- schemas.py — PlannedQuantityCreate/UpdateRequest, PlannedQuantityResponse, PlannedQuantityListResponse
- service.py — list/get/create/update_planned_quantity (edit-window rule NOT implemented, per API Spec Section 16);
  create/update trigger a recommendation-refresh side effect (see recommendations/service.py)
- router.py — PQ-001..004 (API Specification v1.0 Section 16). Entry restricted to Operations Staff
  (confirmed); Admin/Manager entry remains a pending-confirmation cell and is NOT implemented.
"""
