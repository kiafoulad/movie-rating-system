from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import APIResponse
from app.schemas.movies import PaginatedMovies
from app.services.movies import list_movies as list_movies_service

router = APIRouter(
    prefix="/api/v1/movies",
    tags=["Movies"],
)


@router.get(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
def list_movies_endpoint(
    page: int = Query(
        1,
        ge=1,
        description="Page number (starting from 1).",
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of items per page.",
    ),
    db: Session = Depends(get_db),
):
    """
    List movies with pagination.

    For now this endpoint only supports pagination.
    Filtering by title / release_year / genre will be added later
    in a separate step.
    """
    movies_page: PaginatedMovies = list_movies_service(
        db=db,
        page=page,
        page_size=page_size,
    )

    return APIResponse(
        status="success",
        data=movies_page,
    )
