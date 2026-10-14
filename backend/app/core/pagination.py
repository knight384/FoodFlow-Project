"""
Shared pagination schema, per API Specification v1.0 Section 7/22:
a `{ data, pagination }` envelope for collection endpoints, using a
basic page/pageSize (offset-based) strategy — no cursor pagination.
"""

from app.core.schemas import CamelModel

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginationMeta(CamelModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


def build_pagination_meta(page: int, page_size: int, total_items: int) -> PaginationMeta:
    total_pages = (total_items + page_size - 1) // page_size if page_size else 0
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=max(total_pages, 1) if total_items > 0 else 0,
    )
