"""
Request/response schemas for the users module.

Field shapes match API Specification v1.0 Section 11 exactly.
Password hashes are never included in any response schema below.
"""

import uuid
from datetime import datetime

from pydantic import Field, field_validator

from app.core.pagination import PaginationMeta
from app.core.schemas import CamelModel
from app.modules.users.models import APPROVED_ROLE_NAMES


class UserCreateRequest(CamelModel):
    username: str = Field(min_length=1)
    # Minimum length is an implementation-level engineering default, not
    # a confirmed business/security policy (API Specification v1.0
    # Section 11 explicitly leaves "minimum handling" unspecified by the
    # source documents).
    password: str = Field(min_length=8)
    role: str

    @field_validator("role")
    @classmethod
    def role_must_be_approved(cls, value: str) -> str:
        if value not in APPROVED_ROLE_NAMES:
            raise ValueError(f"role must be one of {APPROVED_ROLE_NAMES}")
        return value


class UserUpdateRequest(CamelModel):
    username: str | None = Field(default=None, min_length=1)
    role: str | None = None

    @field_validator("role")
    @classmethod
    def role_must_be_approved(cls, value: str | None) -> str | None:
        if value is not None and value not in APPROVED_ROLE_NAMES:
            raise ValueError(f"role must be one of {APPROVED_ROLE_NAMES}")
        return value


class UserResponse(CamelModel):
    id: uuid.UUID
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(CamelModel):
    data: list[UserResponse]
    pagination: PaginationMeta
