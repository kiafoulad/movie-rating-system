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
    MovieRatingResponse,
    MovieUpdate,
    PaginatedMovies,
)
from app.core.logging import get_logger

# Initialize logger
logger = get_logger()

def _compute_average_rating(movie: Movie) -> Optional[float]:
    """
    Compute the average rating of a movie based on its ratings.

    Returns None if the movie has no ratings.
    """
    if not movie.ratings:
        logger.info(f"Movie '{movie.title}' has no ratings.")
        return None

    total = sum(rating.score for rating in movie.ratings)
    count = len(movie.ratings)
    logger.info(f"Computed average rating for movie '{movie.title}': {round(total / count, 1)}")
    return round(total / count, 1)

def _compute_ratings_count(movie: Movie) -> int:
    """
    Compute the number of ratings for a given movie.
    """
    count = len(movie.ratings)
    logger.info(f"Movie '{movie.title}' has {count} ratings.")
    return count

def _build_director_schema(movie: Movie) -> DirectorInMovie:
    """
    Build a DirectorInMovie schema for the given movie.

    Falls back to an 'Unknown' director if the relation is missing.
    """
    if movie.director is None:
        logger.warning(f"Movie '{movie.title}' has no director.")
        return DirectorInMovie(
            id=0,
            name="Unknown",
            birth_year=None,
            description=None,
        )

    logger.info(f"Director for movie '{movie.title}' is {movie.director.name}.")
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

    logger.info(f"Mapping movie '{movie.title}' to list item.")
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
    if hasattr(movie, "updated_at"):
        raw_value = getattr(movie, "updated_at")
        if raw_value is not None:
            updated_at_value = str(raw_value)

    logger.info(f"Mapping movie '{movie.title}' to detailed information.")
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
    """
    logger.info(f"Fetching movies list with filters - title: {title}, release_year: {release_year}, genre: {genre}")
    
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

    logger.info(f"Fetched {len(items)} movies successfully.")
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
    """
    logger.info(f"Fetching details for movie with ID {movie_id}")

    movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.error(f"Movie with ID {movie_id} not found.")
        return None

    logger.info(f"Fetched movie details for movie ID {movie_id}")
    return _movie_to_detail(movie)

def create_movie(
    db: Session,
    movie_in: MovieCreate,
) -> MovieDetail:
    """
    Create a new movie with the given data.
    """
    logger.info(f"Creating movie: {movie_in.title}")

    director = repo_get_director_by_id(
        db=db,
        director_id=movie_in.director_id,
    )
    logger.info(f"Director found: {director.name}" if director else "Director not found.")

    genres = repo_get_genres_by_ids(
        db=db,
        genre_ids=movie_in.genres,
    )
    logger.info(f"Genres found: {[genre.name for genre in genres]}")

    if director is None or len(genres) != len(set(movie_in.genres)):
        logger.error("Invalid director_id or genres")
        raise ValueError("Invalid director_id or genres")

    movie = repo_create_movie(
        db=db,
        title=movie_in.title,
        director_id=movie_in.director_id,
        release_year=movie_in.release_year,
        cast=movie_in.cast,
        genres=genres,
    )

    logger.info(f"Movie {movie.title} created successfully")
    return _movie_to_detail(movie)

def update_movie(
    db: Session,
    movie_id: int,
    movie_in: MovieUpdate,
) -> MovieDetail:
    """
    Update an existing movie with the given data.
    """
    logger.info(f"Updating movie with ID {movie_id}")

    movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.error(f"Movie with ID {movie_id} not found.")
        raise ValueError("Movie not found")

    genres = repo_get_genres_by_ids(
        db=db,
        genre_ids=movie_in.genres,
    )
    if len(genres) != len(set(movie_in.genres)):
        logger.error("One or more genres not found")
        raise ValueError("One or more genres not found")

    updated_movie = repo_update_movie(
        db=db,
        movie=movie,
        title=movie_in.title,
        release_year=movie_in.release_year,
        cast=movie_in.cast,
        genres=genres,
    )

    logger.info(f"Movie with ID {movie_id} updated successfully")
    return _movie_to_detail(updated_movie)

def delete_movie(
    db: Session,
    movie_id: int,
) -> None:
    """
    Delete an existing movie by its ID.
    """
    logger.info(f"Deleting movie with ID {movie_id}")

    movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.error(f"Movie with ID {movie_id} not found.")
        raise ValueError("Movie not found")

    repo_delete_movie(db=db, movie=movie)
    logger.info(f"Movie with ID {movie_id} deleted successfully")

def add_movie_rating(
    db: Session,
    movie_id: int,
    rating_in: MovieRatingCreate,
) -> MovieRatingResponse:
    """
    Add a new rating to the given movie and return the created rating.
    """
    logger.info(f"Adding rating for movie with ID {movie_id} and score {rating_in.score}")

    movie = repo_get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.error(f"Movie with ID {movie_id} not found.")
        raise ValueError("Movie not found")

    if rating_in.score < 1 or rating_in.score > 10:
        logger.error("Score must be an integer between 1 and 10")
        raise ValueError("Score must be an integer between 1 and 10")

    rating = repo_create_movie_rating(
        db=db,
        movie_id=movie_id,
        score=rating_in.score,
    )

    logger.info(f"Rating for movie with ID {movie_id} added successfully")
    return MovieRatingResponse(
        rating_id=rating.id,
        movie_id=rating.movie_id,
        score=rating.score,
        created_at=str(rating.created_at) if rating.created_at else None,
    )
