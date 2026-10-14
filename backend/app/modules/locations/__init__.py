"""
locations module.

Location (cafeteria/food-service site) CRUD; consumed by other modules. See TRD v1.0 Section 8, SRS-FR-005.

Phase 2: Location ORM model (see models.py).

Phase 4 (Core Backend Business Features) status: implemented.
- schemas.py — LocationCreate/UpdateRequest, LocationResponse, LocationListResponse
- service.py — list/get/create/update/archive_location (PROVISIONAL soft-archive delete — see service.py docstring)
- router.py — LOC-001..005 (API Specification v1.0 Section 12)
"""
