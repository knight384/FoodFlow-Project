"""
auth module.

Authentication and session/token issuance; resolves the current user's role.
See TRD v1.0 Section 8, SRS-FR-001-003.

Phase 3 (Backend Foundation) status: implemented.
- schemas.py  — LoginRequest, CurrentUserResponse, LoginResponse
- service.py  — authenticate_user (credential verification + token issuance)
- router.py   — POST /auth/login, POST /auth/logout, GET /auth/me
  (AUTH-001..003, API Specification v1.0 Section 10)

No models.py — auth has no table of its own; it authenticates against
User/Role, owned by the `users` module (Phase 2).
"""
