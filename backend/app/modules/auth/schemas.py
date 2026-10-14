"""
Request/response schemas for the auth module.

Field shapes match API Specification v1.0 Section 10 (AUTH-001, AUTH-003)
exactly.
"""

import uuid

from pydantic import Field

from app.core.schemas import CamelModel


class LoginRequest(CamelModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class CurrentUserResponse(CamelModel):
    """Also used as the `user` field of LoginResponse (API Spec Section 10)."""

    id: uuid.UUID
    username: str
    role: str


class LoginResponse(CamelModel):
    token: str
    user: CurrentUserResponse
