from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class DirectorInMovie(BaseModel):
    """
    Director representation as embedded in movie responses.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None


class MovieBase(BaseModel):
    """
    Base fields shared by create & update operations.
    """

    title: str = Field(..., min_length=1)
    release_year: Optional[int] = None
    cast: Optional[str] = None


class MovieCreate(MovieBase):
    """
    Schema for creating a new movie.
    """

    director_id: int
    # List of genre IDs, as required in the spec:
    # "genres": [1, 5]
    genres: List[int] = Field(default_factory=list)


class MovieUpdate(MovieBase):
    """
    Schema for updating an existing movie.
    """

    # In update we will also send full list of genre IDs to sync.
    genres: List[int] = Field(default_factory=list)


class MovieListItem(BaseModel):
    """
    Representation of a movie in list endpoints (GET /movies).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    release_year: Optional[int] = None
    director: DirectorInMovie
    # In responses, genres are represented by their names:
    # "genres": ["Drama", "Crime"]
    genres: List[str]
    average_rating: Optional[float] = None
    ratings_count: int = 0


class MovieDetail(MovieListItem):
    """
    Detailed representation of a single movie (GET /movies/{id}).
    """

    cast: Optional[str] = None


class PaginatedMovies(BaseModel):
    """
    Pagination wrapper for movie list responses.
    Matches the shape in the project document.
    """

    page: int
    page_size: int
    total_items: int
    items: List[MovieListItem]
