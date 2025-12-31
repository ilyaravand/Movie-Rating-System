from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions.api_exceptions import NotFoundError, BadRequestError
from app.models.movie import Movie
from app.repositories.movies_repository import MoviesRepository
from app.schemas.movie import MovieCreate, MovieUpdate, MovieDetailOut
from app.schemas.director import DirectorOut
from app.schemas.genre import GenreOut


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
