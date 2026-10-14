"""
meal_types module.

Meal-type CRUD (configurable); consumed by other modules. See TRD v1.0 Section 8, SRS-FR-006.

Phase 2: MealType ORM model (see models.py).

Phase 4 (Core Backend Business Features) status: implemented.
- schemas.py — MealTypeCreate/UpdateRequest, MealTypeResponse, MealTypeListResponse
- service.py — list/get/create/update/archive_meal_type (PROVISIONAL soft-archive delete)
- router.py — MEAL-001..005 (API Specification v1.0 Section 13)
"""
