from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions.api_exceptions import NotFoundError, BadRequestError, UnprocessableEntityError
from app.models.movie import Movie
from app.repositories.movies_repository import MoviesRepository
from app.schemas.movie import (
    MovieCreate,
    MovieUpdate,
    MovieDetailOut,
    MovieListItemOut,
    PaginatedMoviesOut,
)
from app.schemas.director import DirectorOut
from app.schemas.genre import GenreOut
from app.schemas.rating import RatingCreate, RatingOut


class MoviesService:
    @staticmethod
    def get_movie_detail(db: Session, movie_id: int) -> MovieDetailOut:
        movie = MoviesRepository.get_movie_by_id(db, movie_id)
        if not movie:
            raise NotFoundError("Movie not found")

        avg_score, cnt = MoviesRepository.get_rating_stats(db, movie_id)
        avg_val = float(avg_score) if avg_score is not None else None

        return MovieDetailOut(
            id=movie.id,
            title=movie.title,
            director=DirectorOut(
                id=movie.director.id,
                name=movie.director.name,
                birth_year=movie.director.birth_year,
                description=movie.director.description,
            ),
            release_year=movie.release_year,
            cast=movie.cast,
            genres=[
                GenreOut(id=g.id, name=g.name, description=g.description)
                for g in movie.genres
            ],
            average_rating=avg_val,
            ratings_count=cnt,
        )

    @staticmethod
    def create_movie(db: Session, payload: MovieCreate) -> MovieDetailOut:
        # validate director exists
        if not MoviesRepository.director_exists(db, payload.director_id):
            raise BadRequestError("director_id does not exist")

        # validate genres exist
        unique_genre_ids = sorted(set(payload.genre_ids))
        genres = MoviesRepository.get_genres_by_ids(db, unique_genre_ids)
        if len(genres) != len(unique_genre_ids):
            raise BadRequestError("One or more genre_ids do not exist")

        movie = Movie(
            title=payload.title,
            director_id=payload.director_id,
            release_year=payload.release_year,
            cast=payload.cast,
        )
        MoviesRepository.create_movie(db, movie)

        # sync genres bridge
        MoviesRepository.replace_movie_genres(db, movie.id, unique_genre_ids)

        db.commit()
        return MoviesService.get_movie_detail(db, movie.id)

    @staticmethod
    def update_movie(db: Session, movie_id: int, payload: MovieUpdate) -> MovieDetailOut:
        movie = MoviesRepository.get_movie_by_id(db, movie_id)
        if not movie:
            raise NotFoundError("Movie not found")

        if payload.director_id is not None:
            if not MoviesRepository.director_exists(db, payload.director_id):
                raise BadRequestError("director_id does not exist")
            movie.director_id = payload.director_id

        if payload.title is not None:
            movie.title = payload.title

        if payload.release_year is not None:
            movie.release_year = payload.release_year

        if payload.cast is not None:
            movie.cast = payload.cast

        # genre replacement: only if provided
        if payload.genre_ids is not None:
            unique_genre_ids = sorted(set(payload.genre_ids))
            genres = MoviesRepository.get_genres_by_ids(db, unique_genre_ids)
            if len(genres) != len(unique_genre_ids):
                raise BadRequestError("One or more genre_ids do not exist")
            MoviesRepository.replace_movie_genres(db, movie.id, unique_genre_ids)

        db.commit()
        return MoviesService.get_movie_detail(db, movie.id)

    @staticmethod
    def delete_movie(db: Session, movie_id: int) -> None:
        movie = MoviesRepository.get_movie_by_id(db, movie_id)
        if not movie:
            raise NotFoundError("Movie not found")

        MoviesRepository.delete_movie(db, movie)
        db.commit()

    @staticmethod
    def get_movies_list(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        title: str | None = None,
        release_year: int | None = None,
        genre: str | None = None,
    ) -> PaginatedMoviesOut:
        """
        Get paginated list of movies with optional filters.

        Supports filtering by title (partial match), release_year, and genre name.
        All filters can be combined (AND logic).
        Returns paginated list with rating statistics for each movie.
        """
        # Validate pagination parameters
        if page < 1:
            raise UnprocessableEntityError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise UnprocessableEntityError("page_size must be between 1 and 100")

        # Validate release_year if provided
        if release_year is not None and (release_year < 1888 or release_year > 2100):
            raise UnprocessableEntityError("Invalid release_year")

        movies, total_count = MoviesRepository.get_movies_paginated(
            db=db,
            page=page,
            page_size=page_size,
            title_filter=title,
            release_year_filter=release_year,
            genre_filter=genre,
        )

        # Build list items with rating stats
        items = []
        for movie in movies:
            avg_rating, ratings_count = MoviesRepository.get_rating_stats(db, movie.id)
            # Convert Decimal to float for JSON serialization
            avg_val = float(avg_rating) if avg_rating is not None else None

            items.append(
                MovieListItemOut(
                    id=movie.id,
                    title=movie.title,
                    release_year=movie.release_year,
                    director=DirectorOut(
                        id=movie.director.id,
                        name=movie.director.name,
                        birth_year=movie.director.birth_year,
                        description=movie.director.description,
                    ),
                    genres=[g.name for g in movie.genres],
                    average_rating=avg_val,
                    ratings_count=ratings_count,
                )
            )

        return PaginatedMoviesOut(
            page=page,
            page_size=page_size,
            total_items=total_count,
            items=items,
        )

    @staticmethod
    def create_rating(db: Session, movie_id: int, payload: RatingCreate) -> RatingOut:
        """
        Create a new rating for a movie.

        Validates that the movie exists and score is within valid range (1-10).
        Score validation is handled by Pydantic schema.
        """
        # Validate movie exists
        movie = MoviesRepository.get_movie_by_id(db, movie_id)
        if not movie:
            raise NotFoundError("Movie not found")

        # Create rating (score is already validated by Pydantic schema)
        rating = MoviesRepository.create_rating(db, movie_id, payload.score)
        db.commit()

        return RatingOut(
            rating_id=rating.id,
            movie_id=rating.movie_id,
            score=rating.score,
            created_at=rating.created_at,
        )
