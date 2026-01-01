from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.controller.deps import get_db
from app.schemas.movie import MovieCreate, MovieUpdate
from app.schemas.rating import RatingCreate
from app.services.movies_service import MoviesService

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("")
def get_movies_list(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    title: str | None = Query(None, description="Filter by title (partial match)"),
    release_year: int | None = Query(None, ge=1888, le=2100, description="Filter by release year"),
    genre: str | None = Query(None, description="Filter by genre name (partial match)"),
    db: Session = Depends(get_db),
):
    """
    Functionality #1 and #2: Get paginated list of movies with optional filters.

    Supports filtering by title, release_year, and genre.
    All filters can be combined (AND logic).
    Each movie includes director info, genres, and rating statistics.
    """
    result = MoviesService.get_movies_list(
        db=db,
        page=page,
        page_size=page_size,
        title=title,
        release_year=release_year,
        genre=genre,
    )
    return {"status": "success", "data": result.model_dump()}


@router.get("/{movie_id}")
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """
    Functionality #3: Movie details (director + genres) + rating stats.
    """
    movie_out = MoviesService.get_movie_detail(db, movie_id)
    return {"status": "success", "data": movie_out.model_dump()}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_movie(payload: MovieCreate, db: Session = Depends(get_db)):
    """
    Functionality #4: Add a movie (validate director + genres).
    """
    movie_out = MoviesService.create_movie(db, payload)
    return {"status": "success", "data": movie_out.model_dump()}


@router.put("/{movie_id}")
def update_movie(movie_id: int, payload: MovieUpdate, db: Session = Depends(get_db)):
    """
    Functionality #5: Update a movie (+ sync genres if genre_ids provided).
    """
    movie_out = MoviesService.update_movie(db, movie_id, payload)
    return {"status": "success", "data": movie_out.model_dump()}


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Functionality #6: Delete a movie (cascade cleanup via FK/relationship).

    Returns 204 No Content on success (no response body).
    """
    MoviesService.delete_movie(db, movie_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{movie_id}/ratings", status_code=status.HTTP_201_CREATED)
def create_movie_rating(
    movie_id: int,
    payload: RatingCreate,
    db: Session = Depends(get_db),
):
    """
    Functionality #7: Create a new rating for a movie.

    Score must be an integer between 1 and 10.
    """
    rating_out = MoviesService.create_rating(db, movie_id, payload)
    return {"status": "success", "data": rating_out.model_dump()}
