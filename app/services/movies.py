from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import Movie
from app.repositories.movies import (
    create_movie as repo_create_movie,
    create_movie_rating as repo_create_movie_rating,
    delete_movie as repo_delete_movie,
    get_director_by_id as repo_get_director_by_id,
    get_genres_by_ids as repo_get_genres_by_ids,
    get_movie_by_id as repo_get_movie_by_id,
    get_movies as repo_get_movies,
    update_movie as repo_update_movie,
)
from app.schemas.movies import (
    DirectorInMovie,
    MovieCreate,
    MovieDetail,
    MovieListItem,
    MovieRatingCreate,
    MovieUpdate,
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

    The 'updated_at' field is optional and will be filled only if the
    Movie ORM model exposes such an attribute. Otherwise, it will be None.
    """
    list_item = _movie_to_list_item(movie)

    updated_at_value: Optional[str] = None
    # Some specs expect an 'updated_at' field. If the ORM model provides it,
    # we convert it to string; otherwise we keep it as None.
    if hasattr(movie, "updated_at"):
        raw_value = getattr(movie, "updated_at")
        if raw_value is not None:
            updated_at_value = str(raw_value)

    return MovieDetail(
        **list_item.model_dump(),
        cast=movie.cast,
        updated_at=updated_at_value,
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


def create_movie(
    db: Session,
    movie_in: MovieCreate,
) -> MovieDetail:
    """
    Create a new movie with the given data.

    Raises:
        ValueError: if the director_id or one of the genre IDs is invalid.
    """
    # Validate director existence
    director = repo_get_director_by_id(
        db=db,
        director_id=movie_in.director_id,
    )
    if director is None:
        raise ValueError("Director not found")

    # Load genres and validate all IDs exist
    genres = repo_get_genres_by_ids(
        db=db,
        genre_ids=movie_in.genres,
    )
    if len(genres) != len(set(movie_in.genres)):
        raise ValueError("One or more genres not found")

    movie = repo_create_movie(
        db=db,
        title=movie_in.title,
        director_id=movie_in.director_id,
        release_year=movie_in.release_year,
        cast=movie_in.cast,
        genres=genres,
    )

    return _movie_to_detail(movie)


def update_movie(
    db: Session,
    movie_id: int,
    movie_in: MovieUpdate,
) -> MovieDetail:
    """
    Update an existing movie with the given data.

    According to the spec:
    - Only title, release_year, cast, and genres are updated.
    - The director is not changed by this operation.

    Raises:
        ValueError: if the movie does not exist.
        ValueError: if one or more genre IDs are invalid.
    """
    # Ensure the movie exists
    movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    # Load genres and validate all IDs exist
    genres = repo_get_genres_by_ids(
        db=db,
        genre_ids=movie_in.genres,
    )
    if len(genres) != len(set(movie_in.genres)):
        raise ValueError("One or more genres not found")

    updated_movie = repo_update_movie(
        db=db,
        movie=movie,
        title=movie_in.title,
        release_year=movie_in.release_year,
        cast=movie_in.cast,
        genres=genres,
    )

    return _movie_to_detail(updated_movie)


def delete_movie(
    db: Session,
    movie_id: int,
) -> None:
    """
    Delete an existing movie by its ID.

    Raises:
        ValueError: if the movie does not exist.
    """
    movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    repo_delete_movie(db=db, movie=movie)


def add_movie_rating(
    db: Session,
    movie_id: int,
    rating_in: MovieRatingCreate,
) -> MovieDetail:
    """
    Add a new rating to the given movie and return updated movie details.

    Raises:
        ValueError: if the movie does not exist.
    """
    movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise ValueError("Movie not found")

    # Create rating
    repo_create_movie_rating(
        db=db,
        movie_id=movie_id,
        score=rating_in.score,
    )

    # Reload movie to include the new rating
    updated_movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    return _movie_to_detail(updated_movie)
