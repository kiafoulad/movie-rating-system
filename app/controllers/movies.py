from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import APIResponse, ErrorDetail
from app.schemas.movies import (
    MovieCreate,
    MovieRatingCreate,
    MovieUpdate,
    PaginatedMovies,
)
from app.services.movies import (
    add_movie_rating as add_movie_rating_service,
    create_movie as create_movie_service,
    delete_movie as delete_movie_service,
    get_movie_detail as get_movie_detail_service,
    list_movies as list_movies_service,
    update_movie as update_movie_service,
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


@router.put(
    "/{movie_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
def update_movie_endpoint(
    movie_id: int,
    movie_in: MovieUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing movie by its ID.

    According to the spec, this operation:
    - Updates title, release_year, cast, and genres.
    - Does NOT change the director.

    On success:
    - HTTP 200
    - status: "success"
    - data: MovieDetail

    On failure:
    - Movie not found:
      - HTTP 404
      - status: "failure"
      - error: { code: 404, message: "Movie not found" }
    - Invalid genres:
      - HTTP 422
      - status: "failure"
      - error: { code: 422, message: "One or more genres not found" }
    """
    try:
        movie_detail = update_movie_service(
            db=db,
            movie_id=movie_id,
            movie_in=movie_in,
        )
    except ValueError as exc:
        message = str(exc)

        if message == "Movie not found":
            status_code = status.HTTP_404_NOT_FOUND
            error_code = status.HTTP_404_NOT_FOUND
        else:
            # All other ValueError cases are treated as invalid input
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            error_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        api_response = APIResponse(
            status="failure",
            data=None,
            error=ErrorDetail(
                code=error_code,
                message=message,
            ),
        )
        return JSONResponse(
            status_code=status_code,
            content=api_response.model_dump(),
        )

    return APIResponse(
        status="success",
        data=movie_detail,
    )


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_movie_endpoint(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete an existing movie by its ID.

    On success:
    - HTTP 204 (no content)

    On failure (movie not found):
    - HTTP 404
    - status: "failure"
    - data: null
    - error: { code: 404, message: "Movie not found" }
    """
    try:
        delete_movie_service(
            db=db,
            movie_id=movie_id,
        )
    except ValueError as exc:
        api_response = APIResponse(
            status="failure",
            data=None,
            error=ErrorDetail(
                code=status.HTTP_404_NOT_FOUND,
                message=str(exc),
            ),
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=api_response.model_dump(),
        )

    # Spec: 204 No Content, so we return an empty response.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_movie_endpoint(
    movie_in: MovieCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new movie.

    On success:
    - HTTP 201
    - status: "success"
    - data: MovieDetail

    On failure (invalid director/genres):
    - HTTP 422
    - status: "failure"
    - data: null
    - error: { code: 422, message: <reason> }
    """
    try:
        movie_detail = create_movie_service(
            db=db,
            movie_in=movie_in,
        )
    except ValueError as exc:
        api_response = APIResponse(
            status="failure",
            data=None,
            error=ErrorDetail(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message=str(exc),
            ),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=api_response.model_dump(),
        )

    return APIResponse(
        status="success",
        data=movie_detail,
    )


@router.post(
    "/{movie_id}/ratings",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_movie_rating_endpoint(
    movie_id: int,
    rating_in: MovieRatingCreate,
    db: Session = Depends(get_db),
):
    """
    Add a new rating to the given movie.

    On success:
    - HTTP 201
    - status: "success"
    - data: MovieRatingResponse
      (rating_id, movie_id, score, created_at)

    On failure:
    - Movie not found:
      - HTTP 404
      - status: "failure"
      - error: { code: 404, message: "Movie not found" }
    - Invalid score:
      - HTTP 422
      - status: "failure"
      - error: {
          code: 422,
          message: "Score must be an integer between 1 and 10"
        }
    """
    try:
        rating = add_movie_rating_service(
            db=db,
            movie_id=movie_id,
            rating_in=rating_in,
        )
    except ValueError as exc:
        message = str(exc)

        if message == "Movie not found":
            status_code = status.HTTP_404_NOT_FOUND
            error_code = status.HTTP_404_NOT_FOUND
        elif message == "Score must be an integer between 1 and 10":
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            error_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            # Fallback for any unexpected ValueError
            status_code = status.HTTP_400_BAD_REQUEST
            error_code = status.HTTP_400_BAD_REQUEST

        api_response = APIResponse(
            status="failure",
            data=None,
            error=ErrorDetail(
                code=error_code,
                message=message,
            ),
        )
        return JSONResponse(
            status_code=status_code,
            content=api_response.model_dump(),
        )

    return APIResponse(
        status="success",
        data=rating,
    )
