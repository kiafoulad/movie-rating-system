from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.models import Director, Genre, Movie, MovieRating
from app.core.logging import get_logger

# Initialize logger
logger = get_logger()

def get_movies(
    db: Session,
    page: int,
    page_size: int,
    title: Optional[str] = None,
    release_year: Optional[int] = None,
    genre: Optional[str] = None,
) -> Tuple[List[Movie], int]:
    """
    Return a paginated list of movies and the total number of items.
    This function handles database access and basic filtering.
    """
    logger.info(f"Fetching movies - page: {page}, page_size: {page_size}, title: {title}, release_year: {release_year}, genre: {genre}")
    
    if page < 1:
        page = 1
    if page_size <= 0:
        page_size = 10

    query = (
        db.query(Movie)
        .options(
            joinedload(Movie.director),
            joinedload(Movie.genres),
            joinedload(Movie.ratings),
        )
        .order_by(Movie.id)
    )

    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))

    if release_year is not None:
        query = query.filter(Movie.release_year == release_year)

    if genre:
        query = query.filter(Movie.genres.any(Genre.name.ilike(f"%{genre}%")))

    total_items = query.count()

    movies = (
        query.offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    logger.info(f"Fetched {len(movies)} movies out of {total_items} total items.")
    return movies, total_items


def get_movie_by_id(
    db: Session,
    movie_id: int,
) -> Optional[Movie]:
    """
    Return a single movie by its ID, or None if not found.
    """
    logger.info(f"Fetching movie with ID: {movie_id}")

    movie = (
        db.query(Movie)
        .options(
            joinedload(Movie.director),
            joinedload(Movie.genres),
            joinedload(Movie.ratings),
        )
        .filter(Movie.id == movie_id)
        .first()
    )

    if movie is None:
        logger.warning(f"Movie with ID {movie_id} not found.")
    else:
        logger.info(f"Movie with ID {movie_id} found: {movie.title}")

    return movie


def get_director_by_id(
    db: Session,
    director_id: int,
) -> Optional[Director]:
    """
    Return a director by its ID, or None if not found.
    """
    logger.info(f"Fetching director with ID: {director_id}")

    director = db.query(Director).filter(Director.id == director_id).first()
    
    if director is None:
        logger.warning(f"Director with ID {director_id} not found.")
    else:
        logger.info(f"Director with ID {director_id} found: {director.name}")
    
    return director


def get_genres_by_ids(
    db: Session,
    genre_ids: List[int],
) -> List[Genre]:
    """
    Return all genres that match the given list of IDs.

    If some IDs do not exist, they will simply be missing from the result.
    """
    logger.info(f"Fetching genres for IDs: {genre_ids}")
    
    if not genre_ids:
        return []

    genres = db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
    logger.info(f"Found {len(genres)} genres for the given IDs.")
    return genres


def create_movie(
    db: Session,
    *,
    title: str,
    director_id: int,
    release_year: Optional[int],
    cast: Optional[str],
    genres: List[Genre],
) -> Movie:
    """
    Create a new movie with the given data and persist it to the database.
    """
    logger.info(f"Creating movie: {title}")

    movie = Movie(
        title=title,
        director_id=director_id,
        release_year=release_year,
        cast=cast,
    )

    if genres:
        movie.genres = genres

    db.add(movie)
    db.commit()
    db.refresh(movie)

    logger.info(f"Movie created successfully: {movie.title} with ID {movie.id}")
    return movie


def update_movie(
    db: Session,
    movie: Movie,
    *,
    title: str,
    release_year: Optional[int],
    cast: Optional[str],
    genres: List[Genre],
) -> Movie:
    """
    Update an existing movie with the given data and persist changes.
    """
    logger.info(f"Updating movie with ID {movie.id}: {title}")

    movie.title = title
    movie.release_year = release_year
    movie.cast = cast
    movie.genres = genres

    db.add(movie)
    db.commit()
    db.refresh(movie)

    logger.info(f"Movie with ID {movie.id} updated successfully")
    return movie


def delete_movie(
    db: Session,
    movie: Movie,
) -> None:
    """
    Delete the given movie from the database.
    """
    logger.info(f"Deleting movie with ID {movie.id}: {movie.title}")

    db.delete(movie)
    db.commit()

    logger.info(f"Movie with ID {movie.id} deleted successfully")


def create_movie_rating(
    db: Session,
    *,
    movie_id: int,
    score: int,
) -> MovieRating:
    """
    Create a new rating for the given movie.
    """
    logger.info(f"Creating movie rating for movie ID {movie_id} with score {score}")

    rating = MovieRating(
        movie_id=movie_id,
        score=score,
    )

    db.add(rating)
    db.commit()
    db.refresh(rating)

    logger.info(f"Movie rating created for movie ID {movie_id} with rating ID {rating.id}")
    return rating
