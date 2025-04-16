from fastapi import Query
from app.core.config import pagination_settings


def PaginationParams(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        pagination_settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=pagination_settings.MAX_PAGE_SIZE,
        description=f"Items per page (max {pagination_settings.MAX_PAGE_SIZE})"
    )
):
    return {"page": page, "size": size}
