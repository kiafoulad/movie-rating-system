from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


# Association table for many-to-many relation between movies and genres
genres_movie_table = Table(
    "genres_movie",
    Base.metadata,
    Column(
        "movie_id",
        ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Director(Base):
    """
    Represents a movie director.
    """

    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birth_year = Column(Integer, nullable=True)
    description = Column(String, nullable=True)

    # One-to-many: one director has many movies
    movies = relationship("Movie", back_populates="director")


class Genre(Base):
    """
    Represents a movie genre (e.g. Drama, Crime, Sci-Fi).
    """

    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    # Many-to-many: a genre can belong to many movies
    movies = relationship(
        "Movie",
        secondary=genres_movie_table,
        back_populates="genres",
    )


class Movie(Base):
    """
    Represents a movie entity.
    """

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    director_id = Column(
        Integer,
        ForeignKey("directors.id"),
        nullable=False,
    )
    release_year = Column(Integer, nullable=True)
    cast = Column(String, nullable=True)

    # Relations
    director = relationship("Director", back_populates="movies")

    genres = relationship(
        "Genre",
        secondary=genres_movie_table,
        back_populates="movies",
    )

    ratings = relationship(
        "MovieRating",
        back_populates="movie",
        cascade="all, delete-orphan",
    )


class MovieRating(Base):
    """
    Represents a rating for a movie (score 1-10).
    """

    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
    )
    score = Column(Integer, nullable=False)

    __table_args__ = (
        # Ensure score is always between 1 and 10 at database level
        CheckConstraint(
            "score BETWEEN 1 AND 10",
            name="ck_movie_ratings_score_range",
        ),
    )

    # Many-to-one: many ratings belong to one movie
    movie = relationship("Movie", back_populates="ratings")
