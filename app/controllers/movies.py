from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import APIResponse, ErrorDetail
from app.schemas.movies import PaginatedMovies
from app.services.movies import (
    get_movie_detail as get_movie_detail_service,
    list_movies as list_movies_service,
)

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


@router.get(
    "/{movie_id}",
    response_model=APIResponse,
)
def get_movie_detail_endpoint(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a single movie by its ID.

    Response on success:
    - status: "success"
    - data: MovieDetail

    Response on failure (not found):
    - status: "failure"
    - data: null
    - error: { code: 404, message: "Movie not found" }
    """
    movie_detail = get_movie_detail_service(
        db=db,
        movie_id=movie_id,
    )

    if movie_detail is None:
        api_response = APIResponse(
            status="failure",
            data=None,
            error=ErrorDetail(
                code=404,
                message="Movie not found",
            ),
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=api_response.model_dump(),
        )

    return APIResponse(
        status="success",
        data=movie_detail,
    )
