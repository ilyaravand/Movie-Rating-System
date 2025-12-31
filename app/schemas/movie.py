from pydantic import BaseModel, Field
from typing import List, Optional

from app.schemas.director import DirectorOut
from app.schemas.genre import GenreOut


# ---------- Inputs (Ilya owns create/update) ----------
class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    director_id: int
    release_year: int = Field(..., ge=1888, le=2100)
    cast: Optional[str] = None
    genre_ids: List[int] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    director_id: Optional[int] = None
    release_year: Optional[int] = Field(None, ge=1888, le=2100)
    cast: Optional[str] = None
    genre_ids: Optional[List[int]] = None  # if provided, replace genres


# ---------- Output for functionality #3 (movie details) ----------
class MovieDetailOut(BaseModel):
    id: int
    title: str
    director: DirectorOut
    release_year: int
    cast: Optional[str] = None
    genres: List[GenreOut] = Field(default_factory=list)

    # Part of functionality #8 but *on details side* (you own details, so include it here)
    average_rating: float | None = None
    ratings_count: int = 0
