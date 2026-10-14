"""
Historical-data module routes: HIST-001, HIST-002, HIST-003 — exact
paths, methods, and behavior per API Specification v1.0 Section 9/14.
All endpoints require Admin authorization.
"""

import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, build_pagination_meta
from app.database import get_db
from app.modules.historical_data import service
from app.modules.historical_data.models import ImportJob
from app.modules.historical_data.schemas import (
    ImportAcceptedResponse,
    ImportJobDetailResponse,
    ImportJobListResponse,
    ImportJobSummaryResponse,
    ImportRecordErrorResponse,
)
from app.modules.users.models import User

router = APIRouter(
    prefix="/historical-data",
    tags=["historical-data"],
    dependencies=[Depends(require_roles("administrator"))],
)


def _to_summary(job: ImportJob) -> ImportJobSummaryResponse:
    return ImportJobSummaryResponse(
        import_id=job.id,
        uploaded_by_user_id=job.uploaded_by_user_id,
        uploaded_at=job.uploaded_at,
        status=job.status,
        total_records=job.total_records,
        valid_records=job.valid_records,
        invalid_records=job.invalid_records,
    )


@router.post(
    "/imports", response_model=ImportAcceptedResponse, status_code=status.HTTP_201_CREATED
)
async def upload_historical_data(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("administrator")),
) -> ImportAcceptedResponse:
    """
    HIST-001. Admin only. Processed synchronously (see
    app/modules/historical_data/service.py's module docstring), so the
    returned status is always a terminal state ("completed" or "failed"),
    consistent with API Specification v1.0 Section 14's "201 if
    processed synchronously" allowance.
    """
    file_content = await file.read()
    job = service.process_import(db, current_user.id, file_content)
    return ImportAcceptedResponse(import_id=job.id, status=job.status, uploaded_at=job.uploaded_at)


@router.get("/imports", response_model=ImportJobListResponse, status_code=status.HTTP_200_OK)
def list_imports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
    db: Session = Depends(get_db),
) -> ImportJobListResponse:
    """
    HIST-002. No filters — per API Specification v1.0 Section 22, this
    endpoint's filters are explicitly documented as "none (all jobs)".
    """
    jobs, total_items = service.list_import_jobs(db, page, page_size)
    return ImportJobListResponse(
        data=[_to_summary(job) for job in jobs],
        pagination=build_pagination_meta(page, page_size, total_items),
    )


@router.get(
    "/imports/{import_id}", response_model=ImportJobDetailResponse, status_code=status.HTTP_200_OK
)
def get_import(import_id: uuid.UUID, db: Session = Depends(get_db)) -> ImportJobDetailResponse:
    """HIST-003."""
    job = service.get_import_job(db, import_id)
    errors = service.list_import_errors(db, import_id)
    summary = _to_summary(job)
    return ImportJobDetailResponse(
        **summary.model_dump(),
        errors=[
            ImportRecordErrorResponse(row_reference=e.row_reference, failure_reason=e.failure_reason)
            for e in errors
        ],
    )
