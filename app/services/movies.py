from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.movies import get_movies as repo_get_movies
from app.schemas.movies import PaginatedMovies, MovieListItem, DirectorInMovie
from app.models.models import Movie


def _compute_average_rating(movie: Movie) -> Optional[float]:
    """
    Compute the average rating of a movie based on its ratings.
    Returns None if there are no ratings.
    """
    if not movie.ratings:
        return None

    total = sum(r.score for r in movie.ratings)
    count = len(movie.ratings)
    return round(total / count, 1)


def _compute_ratings_count(movie: Movie) -> int:
    """
    Compute the number of ratings for a given movie.
    """
    return len(movie.ratings)


def _movie_to_list_item(movie: Movie) -> MovieListItem:
    """
    Map a Movie ORM object to a MovieListItem schema.
    """
    if movie.director is None:
        # This should not normally happen if data integrity is correct,
        # but we guard against it for safety.
        director_schema = DirectorInMovie(
            id=0,
            name="Unknown",
            birth_year=None,
            description=None,
        )
    else:
        director_schema = DirectorInMovie(
            id=movie.director.id,
            name=movie.director.name,
            birth_year=movie.director.birth_year,
            description=movie.director.description,
        )

    genre_names = [genre.name for genre in movie.genres]

    average_rating = _compute_average_rating(movie)
    ratings_count = _compute_ratings_count(movie)

    return MovieListItem(
        id=movie.id,
        title=movie.title,
        release_year=movie.release_year,
        director=director_schema,
        genres=genre_names,
        average_rating=average_rating,
        ratings_count=ratings_count,
    )


def list_movies(
    db: Session,
    page: int,
    page_size: int,
) -> PaginatedMovies:
    """
    List movies with pagination.

    For now this service only handles pagination.
    Filtering by title / release_year / genre will be added
    in a next step when wiring up the controller with query params.
    """
    movies, total_items = repo_get_movies(
        db=db,
        page=page,
        page_size=page_size,
    )

    items = [_movie_to_list_item(movie) for movie in movies]

    # Basic normalization of page & page_size, in sync with repository behavior
    if page < 1:
        page = 1
    if page_size <= 0:
        page_size = 10

    return PaginatedMovies(
        page=page,
        page_size=page_size,
        total_items=total_items,
        items=items,
    )
