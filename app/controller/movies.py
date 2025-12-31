from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controller.deps import get_db
from app.schemas.movie import MovieCreate, MovieUpdate
from app.services.movies_service import MoviesService

router = APIRouter(prefix="/movies", tags=["movies"])


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


@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Functionality #6: Delete a movie (cascade cleanup via FK/relationship).
    """
    MoviesService.delete_movie(db, movie_id)
    return {"status": "success", "data": {"deleted": True, "movie_id": movie_id}}
