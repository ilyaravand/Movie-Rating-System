from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select, func, delete, and_
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
        title_filter: str | None = None,
        release_year_filter: int | None = None,
        genre_filter: str | None = None,
    ) -> tuple[Sequence[Movie], int]:
        """
        Get paginated list of movies with optional filters.

        Returns tuple of (movies, total_count).
        Supports filtering by title (partial match), release_year, and genre name.
        All filters are combined with AND logic.
        """
        # Build filter conditions
        conditions = []
        if title_filter:
            conditions.append(Movie.title.ilike(f"%{title_filter}%"))
        if release_year_filter is not None:
            conditions.append(Movie.release_year == release_year_filter)
        if genre_filter:
            # Filter by genre name through the many-to-many relationship
            genre_subquery = (
                select(movie_genres.c.movie_id)
                .join(Genre, movie_genres.c.genre_id == Genre.id)
                .where(Genre.name.ilike(f"%{genre_filter}%"))
            )
            conditions.append(Movie.id.in_(genre_subquery))

        # Get total count before pagination
        count_stmt = select(func.count(Movie.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_count = db.execute(count_stmt).scalar_one()

        # Base query with joins and filters
        stmt = (
            select(Movie)
            .options(
                joinedload(Movie.director),
                selectinload(Movie.genres),
            )
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Order by id for consistent pagination
        stmt = stmt.order_by(Movie.id)

        movies = db.execute(stmt).scalars().unique().all()
        return movies, total_count

    @staticmethod
    def create_rating(db: Session, movie_id: int, score: int) -> MovieRating:
        """Create a new rating for a movie."""
        rating = MovieRating(movie_id=movie_id, score=score)
        db.add(rating)
        db.flush()
        db.refresh(rating)
        return rating
