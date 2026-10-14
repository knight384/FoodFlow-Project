"""
Recommendations module routes: REC-001, REC-002 — exact paths, methods,
and behavior per API Specification v1.0 Section 9/19. Manager and Admin
authorization only. No POST endpoint exists, per the API Specification's
explicit design (recommendations are generated automatically by backend
logic — see app/modules/recommendations/service.py — never via a direct
API write).
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, build_pagination_meta
from app.database import get_db
from app.modules.recommendations import service
from app.modules.recommendations.schemas import RecommendationListResponse, RecommendationResponse

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    dependencies=[Depends(require_roles("manager", "administrator"))],
)


@router.get("", response_model=RecommendationListResponse, status_code=status.HTTP_200_OK)
def list_recommendations(
    location_id: uuid.UUID | None = Query(default=None, alias="locationId"),
    meal_type_id: uuid.UUID | None = Query(default=None, alias="mealTypeId"),
    date_from: date | None = Query(default=None, alias="dateFrom"),
    date_to: date | None = Query(default=None, alias="dateTo"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias="pageSize"),
    db: Session = Depends(get_db),
) -> RecommendationListResponse:
    """REC-001."""
    recommendations, total_items = service.list_recommendations(
        db, page, page_size, location_id, meal_type_id, date_from, date_to
    )
    return RecommendationListResponse(
        data=[RecommendationResponse.model_validate(r) for r in recommendations],
        pagination=build_pagination_meta(page, page_size, total_items),
    )


@router.get(
    "/{recommendation_id}", response_model=RecommendationResponse, status_code=status.HTTP_200_OK
)
def get_recommendation(
    recommendation_id: uuid.UUID, db: Session = Depends(get_db)
) -> RecommendationResponse:
    """REC-002."""
    recommendation = service.get_recommendation(db, recommendation_id)
    return RecommendationResponse.model_validate(recommendation)
