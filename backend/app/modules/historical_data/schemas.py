"""
Request/response schemas for the historical_data module.

Field shapes match API Specification v1.0 Section 14 exactly. There is
no request body schema for the upload endpoint — it accepts
`multipart/form-data` with a file field, handled directly in the router.
"""

import uuid
from datetime import datetime

from app.core.pagination import PaginationMeta
from app.core.schemas import CamelModel


class ImportAcceptedResponse(CamelModel):
    """Returned immediately by POST /historical-data/imports."""

    import_id: uuid.UUID
    status: str
    uploaded_at: datetime


class ImportRecordErrorResponse(CamelModel):
    row_reference: int
    failure_reason: str


class ImportJobSummaryResponse(CamelModel):
    """Used in the GET /historical-data/imports list (no error detail)."""

    import_id: uuid.UUID
    uploaded_by_user_id: uuid.UUID
    uploaded_at: datetime
    status: str
    total_records: int
    valid_records: int
    invalid_records: int


class ImportJobDetailResponse(ImportJobSummaryResponse):
    """Used in GET /historical-data/imports/{importId} — includes error detail."""

    errors: list[ImportRecordErrorResponse]


class ImportJobListResponse(CamelModel):
    data: list[ImportJobSummaryResponse]
    pagination: PaginationMeta
