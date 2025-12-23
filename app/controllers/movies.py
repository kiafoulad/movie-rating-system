from typing import Optional

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
    title: Optional[str] = Query(
        None,
        description="Filter by movie title (partial, case-insensitive).",
    ),
    release_year: Optional[int] = Query(
        None,
        description="Filter by exact release year.",
    ),
    genre: Optional[str] = Query(
        None,
        description="Filter by genre name (partial, case-insensitive).",
    ),
    db: Session = Depends(get_db),
):
    """
    List movies with pagination and optional filters.

    Filters:
    - title: partial, case-insensitive match on movie title
    - release_year: exact match on release year
    - genre: partial, case-insensitive match on genre name
    """
    movies_page: PaginatedMovies = list_movies_service(
        db=db,
        page=page,
        page_size=page_size,
        title=title,
        release_year=release_year,
        genre=genre,
    )

    return APIResponse(
        status="success",
        data=movies_page,
    )
