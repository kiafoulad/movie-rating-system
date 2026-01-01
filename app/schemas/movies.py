from typing import List, Optional

from pydantic import BaseModel, Field


class DirectorInMovie(BaseModel):
    """
    Lightweight director representation used inside movie responses.
    """
    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None


class MovieListItem(BaseModel):
    """
    Representation of a movie item in listing responses.
    """
    id: int
    title: str
    release_year: Optional[int] = None
    director: DirectorInMovie
    genres: List[str]
    average_rating: Optional[float] = None
    ratings_count: int


class MovieDetail(MovieListItem):
    """
    Detailed representation of a movie, extending the list item with cast.
    """
    cast: Optional[str] = None


class PaginatedMovies(BaseModel):
    """
    Paginated response wrapper for movie lists.
    """
    page: int
    page_size: int
    total_items: int
    items: List[MovieListItem]


class MovieCreate(BaseModel):
    """
    Payload used to create a new movie.
    """
    title: str = Field(..., description="Movie title.")
    director_id: int = Field(..., description="ID of the director.")
    release_year: Optional[int] = Field(
        None,
        description="Release year of the movie.",
    )
    cast: Optional[str] = Field(
        None,
        description="Cast information for the movie.",
    )
    genres: List[int] = Field(
        ...,
        description="List of genre IDs associated with the movie.",
    )


class MovieRatingCreate(BaseModel):
    """
    Payload used to add a rating to a movie.
    Score must be between 1 and 10 (inclusive).
    """
    score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Rating score between 1 and 10.",
    )
