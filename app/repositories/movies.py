from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.models import Movie


def get_movies(
    db: Session,
    page: int,
    page_size: int,
) -> Tuple[List[Movie], int]:
    """
    Return a paginated list of movies and the total number of items.
    This function only handles database access; business logic such as
    computing average rating will be done in the service layer.
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
