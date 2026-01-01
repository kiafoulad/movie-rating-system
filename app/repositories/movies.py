from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.models import Director, Genre, Movie, MovieRating


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

    # Apply filters based on optional parameters.
    # If multiple filters are provided, they are combined with AND logic.
    if title:
        # Partial, case-insensitive match on movie title
        query = query.filter(Movie.title.ilike(f"%{title}%"))

    if release_year is not None:
        query = query.filter(Movie.release_year == release_year)

    if genre:
        # Partial, case-insensitive match on genre name
        query = query.filter(
            Movie.genres.any(Genre.name.ilike(f"%{genre}%"))
        )

    total_items = query.count()

    movies = (
        query.offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return movies, total_items


def get_movie_by_id(
    db: Session,
    movie_id: int,
) -> Optional[Movie]:
    """
    Return a single movie by its ID, or None if not found.
    """
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
    return movie


def get_director_by_id(
    db: Session,
    director_id: int,
) -> Optional[Director]:
    """
    Return a director by its ID, or None if not found.
    """
    return (
        db.query(Director)
        .filter(Director.id == director_id)
        .first()
    )


def get_genres_by_ids(
    db: Session,
    genre_ids: List[int],
) -> List[Genre]:
    """
    Return all genres that match the given list of IDs.

    If some IDs do not exist, they will simply be missing from the result.
    """
    if not genre_ids:
        return []

    return (
        db.query(Genre)
        .filter(Genre.id.in_(genre_ids))
        .all()
    )


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

    This function assumes that:
    - The movie instance already exists and is loaded from the database.
    - The genres list contains fully loaded Genre objects that have already
      been validated by the service layer.
    """
    movie.title = title
    movie.release_year = release_year
    movie.cast = cast
    movie.genres = genres

    db.add(movie)
    db.commit()
    db.refresh(movie)

    return movie


def delete_movie(
    db: Session,
    movie: Movie,
) -> None:
    """
    Delete the given movie from the database.

    Related records (e.g. genres_movie, movie_ratings) are expected to be
    handled by database-level cascade rules.
    """
    db.delete(movie)
    db.commit()


def create_movie_rating(
    db: Session,
    *,
    movie_id: int,
    score: int,
) -> MovieRating:
    """
    Create a new rating for the given movie.
    """
    rating = MovieRating(
        movie_id=movie_id,
        score=score,
    )

    db.add(rating)
    db.commit()
    db.refresh(rating)

    return rating
