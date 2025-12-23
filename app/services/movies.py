from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import Movie
from app.repositories.movies import (
    get_movies as repo_get_movies,
    get_movie_by_id as repo_get_movie_by_id,
)
from app.schemas.movies import (
    DirectorInMovie,
    MovieDetail,
    MovieListItem,
    PaginatedMovies,
)


def _compute_average_rating(movie: Movie) -> Optional[float]:
    """
    Compute the average rating of a movie based on its ratings.

    Returns None if the movie has no ratings.
    """
    if not movie.ratings:
        return None

    total = sum(rating.score for rating in movie.ratings)
    count = len(movie.ratings)
    return round(total / count, 1)


def _compute_ratings_count(movie: Movie) -> int:
    """
    Compute the number of ratings for a given movie.
    """
    return len(movie.ratings)


def _build_director_schema(movie: Movie) -> DirectorInMovie:
    """
    Build a DirectorInMovie schema for the given movie.

    Falls back to an 'Unknown' director if the relation is missing.
    """
    if movie.director is None:
        return DirectorInMovie(
            id=0,
            name="Unknown",
            birth_year=None,
            description=None,
        )

    return DirectorInMovie(
        id=movie.director.id,
        name=movie.director.name,
        birth_year=movie.director.birth_year,
        description=movie.director.description,
    )


def _movie_to_list_item(movie: Movie) -> MovieListItem:
    """
    Map a Movie ORM object to a MovieListItem schema.
    """
    director_schema = _build_director_schema(movie)
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


def _movie_to_detail(movie: Movie) -> MovieDetail:
    """
    Map a Movie ORM object to a MovieDetail schema.
    """
    list_item = _movie_to_list_item(movie)

    # Reuse list representation and extend it with the cast field
    return MovieDetail(
        **list_item.model_dump(),
        cast=movie.cast,
    )


def list_movies(
    db: Session,
    page: int,
    page_size: int,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None,
) -> PaginatedMovies:
    """
    List movies with pagination and optional filters.

    Filters:
    - title: partial, case-insensitive match on movie title
    - release_year: exact match on release year
    - genre: partial, case-insensitive match on genre name

    If multiple filters are provided, they are combined with AND logic.
    """
    movies, total_items = repo_get_movies(
        db=db,
        page=page,
        page_size=page_size,
        title=title,
        release_year=release_year,
        genre=genre,
    )

    # Normalize page and page_size to safe defaults
    if page < 1:
        page = 1
    if page_size <= 0:
        page_size = 10

    items = [_movie_to_list_item(movie) for movie in movies]

    return PaginatedMovies(
        page=page,
        page_size=page_size,
        total_items=total_items,
        items=items,
    )


def get_movie_detail(
    db: Session,
    movie_id: int,
) -> Optional[MovieDetail]:
    """
    Get detailed information about a single movie by its ID.

    Returns:
        - MovieDetail if the movie exists.
        - None if the movie does not exist.
    """
    movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        return None

    return _movie_to_detail(movie)
