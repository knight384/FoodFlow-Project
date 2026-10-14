"""
Shared/cross-cutting utilities.

Phase 3 (Backend Foundation) status: implemented.
- errors.py        — AppError and subclasses; the standard error envelope
                      shape used across all endpoints (API Specification
                      v1.0 Section 8).
- security.py       — password hashing (bcrypt) and JWT access-token
                       issuance/verification.
- schemas.py         — CamelModel, the shared Pydantic base enforcing the
                        camelCase JSON field-naming convention (API
                        Specification v1.0 Section 6).
- pagination.py       — shared page/pageSize pagination schema and helper
                         (API Specification v1.0 Section 22).
- dependencies.py      — get_current_user, get_current_user_role_name,
                          require_roles: the backend-authoritative
                          authentication/authorization layer (TRD v1.0
                          Section 15).
"""
