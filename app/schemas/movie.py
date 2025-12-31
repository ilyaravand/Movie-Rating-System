from __future__ import annotations

from collections.abc import Sequence
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.director import DirectorOut
from app.schemas.genre import GenreOut


# ---------- Inputs (Ilya owns create/update) ----------
class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    director_id: int
    release_year: int = Field(..., ge=1888, le=2100)
    cast: Optional[str] = None
    genre_ids: list[int] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    director_id: Optional[int] = None
    release_year: Optional[int] = Field(None, ge=1888, le=2100)
    cast: Optional[str] = None
    genre_ids: Optional[list[int]] = None  # if provided, replace genres


# ---------- Output for functionality #3 (movie details) ----------
class MovieDetailOut(BaseModel):
    id: int
    title: str
    director: DirectorOut
    release_year: int
    cast: Optional[str] = None
    genres: list[GenreOut] = Field(default_factory=list)

    # Part of functionality #8 but *on details side* (you own details, so include it here)
    average_rating: float | None = None
    ratings_count: int = 0


# ---------- Output for functionality #1 (movie list with pagination) ----------
class MovieListItemOut(BaseModel):
    """Schema for a movie item in the paginated list."""

    id: int
    title: str
    release_year: int
    director: DirectorOut
    genres: list[str] = Field(default_factory=list)  # Only genre names for list view
    average_rating: float | None = None
    ratings_count: int = 0


class PaginatedMoviesOut(BaseModel):
    """Schema for paginated movies list response."""

    page: int
    page_size: int
    total_items: int
    items: Sequence[MovieListItemOut]
