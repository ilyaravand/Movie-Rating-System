from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    director_id: Mapped[int] = mapped_column(ForeignKey("directors.id"), nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    cast: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    director: Mapped["Director"] = relationship(back_populates="movies")

    genres: Mapped[list["Genre"]] = relationship(
        secondary="movie_genres",
        back_populates="movies",
    )

    ratings: Mapped[list["MovieRating"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
