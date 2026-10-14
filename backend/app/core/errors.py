"""
Standard error model and application exception classes.

Implements the single consistent error envelope defined in API
Specification v1.0 Section 8:

    { "error": { "category": "...", "message": "...", "details": [...] } }

and the category-to-HTTP-status mapping from Section 28. Every
application-raised error in Phase 3 (and future phases) should raise one
of the AppError subclasses below rather than a raw FastAPI HTTPException,
so every endpoint produces a consistent response shape.
"""

from typing import Any


class AppError(Exception):
    """
    Base class for all application errors that should be converted into
    the standard error envelope (see app.main's exception handler).
    """

    category: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class AuthenticationError(AppError):
    """
    Invalid credentials or missing/invalid session token.

    Per SRS-FR-001 / API Specification v1.0 Section 10: never indicates
    which specific credential was wrong.
    """

    category = "AUTHENTICATION_ERROR"
    status_code = 401


class AuthorizationError(AppError):
    """Authenticated, but the user's role does not permit this action."""

    category = "FORBIDDEN"
    status_code = 403


class NotFoundError(AppError):
    """The requested resource does not exist."""

    category = "NOT_FOUND"
    status_code = 404


class ValidationError(AppError):
    """A well-formed request whose field values fail a business rule."""

    category = "VALIDATION_ERROR"
    status_code = 400


class DuplicateResourceError(AppError):
    """A uniqueness constraint (e.g., username) was violated."""

    category = "DUPLICATE_RESOURCE"
    status_code = 409


class BusinessRuleViolationError(AppError):
    """A well-formed, authorized request that violates a business rule."""

    category = "BUSINESS_RULE_VIOLATION"
    status_code = 409
