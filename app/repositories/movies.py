from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.models import Movie, Genre


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
