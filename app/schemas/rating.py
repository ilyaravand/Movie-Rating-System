from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    """Schema for creating a new movie rating."""

    score: int = Field(..., ge=1, le=10, description="Rating score between 1 and 10")


class RatingOut(BaseModel):
    """Schema for rating output response."""

    rating_id: int
    movie_id: int
    score: int
    created_at: datetime

