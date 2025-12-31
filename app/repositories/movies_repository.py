from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session, selectinload, joinedload

from app.models.movie import Movie
from app.models.director import Director
from app.models.genre import Genre
from app.models.movie_genres import movie_genres
from app.models.movie_rating import MovieRating


class MoviesRepository:
    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int) -> Movie | None:
        stmt = (
            select(Movie)
            .where(Movie.id == movie_id)
            .options(
                joinedload(Movie.director),
                selectinload(Movie.genres),
            )
        )
        return db.execute(stmt).scalars().first()

    @staticmethod
    def get_rating_stats(db: Session, movie_id: int) -> tuple[float | None, int]:
        stmt = (
            select(func.avg(MovieRating.score), func.count(MovieRating.id))
            .where(MovieRating.movie_id == movie_id)
        )
        avg_, cnt_ = db.execute(stmt).one()
        # avg_ may be Decimal depending on dialect; convert safely later in service
        return avg_, int(cnt_)

    @staticmethod
    def director_exists(db: Session, director_id: int) -> bool:
        stmt = select(func.count(Director.id)).where(Director.id == director_id)
        return db.execute(stmt).scalar_one() > 0

    @staticmethod
    def get_genres_by_ids(db: Session, genre_ids: list[int]) -> list[Genre]:
        if not genre_ids:
            return []
        stmt = select(Genre).where(Genre.id.in_(genre_ids))
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create_movie(db: Session, movie: Movie) -> Movie:
        db.add(movie)
        db.flush()  # get movie.id
        db.refresh(movie)
        return movie

    @staticmethod
    def delete_movie(db: Session, movie: Movie) -> None:
        db.delete(movie)

    @staticmethod
    def replace_movie_genres(db: Session, movie_id: int, genre_ids: list[int]) -> None:
        # remove existing
        db.execute(delete(movie_genres).where(movie_genres.c.movie_id == movie_id))
        # add new
        if genre_ids:
            rows = [{"movie_id": movie_id, "genre_id": gid} for gid in genre_ids]
            db.execute(movie_genres.insert(), rows)

    @staticmethod
    def get_movies_paginated(
        db: Session,
        page: int,
        page_size: int,
    ) -> tuple[Sequence[Movie], int]:
        """
        Get paginated list of movies.

        Returns tuple of (movies, total_count).
        """
        # Get total count
        count_stmt = select(func.count(Movie.id))
        total_count = db.execute(count_stmt).scalar_one()

        # Base query with joins
        stmt = (
            select(Movie)
            .options(
                joinedload(Movie.director),
                selectinload(Movie.genres),
            )
        )

        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Order by id for consistent pagination
        stmt = stmt.order_by(Movie.id)

        movies = db.execute(stmt).scalars().unique().all()
        return movies, total_count
