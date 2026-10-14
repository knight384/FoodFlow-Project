"""
users module.

Administrator-managed user CRUD and role assignment. See TRD v1.0
Section 8, SRS-FR-004.

Phase 2 (Database Implementation) status: Role and User ORM models (see
models.py).

Phase 3 (Backend Foundation) status: implemented.
- schemas.py  — UserCreateRequest, UserUpdateRequest, UserResponse, UserListResponse
- service.py  — list/get/create/update/deactivate_user
- router.py   — GET/POST /users, GET/PATCH /users/{id}, POST /users/{id}/deactivate
  (USR-001..005, API Specification v1.0 Section 11) — all Admin-only,
  enforced via app.core.dependencies.require_roles.
"""
