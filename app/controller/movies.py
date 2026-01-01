from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
import logging

from app.controller.deps import get_db
from app.schemas.movie import MovieCreate, MovieUpdate
from app.schemas.rating import RatingCreate
from app.services.movies_service import MoviesService

router = APIRouter(prefix="/movies", tags=["movies"])
logger = logging.getLogger("movie_rating")


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
    # Build filter info for logging
    filters = []
    if title:
        filters.append(f"title={title}")
    if release_year:
        filters.append(f"release_year={release_year}")
    if genre:
        filters.append(f"genre={genre}")
    filter_str = ", ".join(filters) if filters else "none"
    
    logger.info(
        f"Listing movies (page={page}, page_size={page_size}, filters={filter_str}, route=/api/v1/movies)"
    )
    
    try:
        result = MoviesService.get_movies_list(
            db=db,
            page=page,
            page_size=page_size,
            title=title,
            release_year=release_year,
            genre=genre,
        )
        # Use model_dump with exclude_none=False to ensure all fields are serialized
        data = result.model_dump(exclude_none=False)
        
        logger.info(
            f"Movies list retrieved successfully (page={page}, total_items={data['total_items']}, items_returned={len(data['items'])})"
        )
        
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(
            f"Failed to retrieve movies list (page={page}, page_size={page_size}, filters={filter_str})",
            exc_info=True
        )
        raise


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
    score = payload.score
    
    # Log the rating attempt
    logger.info(
        f"Rating movie (movie_id={movie_id}, rating={score}, route=/api/v1/movies/{movie_id}/ratings)"
    )
    
    # Validate score range (should be handled by Pydantic, but log warning if invalid)
    if score < 1 or score > 10:
        logger.warning(
            f"Invalid rating value (movie_id={movie_id}, rating={score}, route=/api/v1/movies/{movie_id}/ratings)"
        )
    
    try:
        rating_out = MoviesService.create_rating(db, movie_id, payload)
        
        # Get rating_id from the response data
        rating_data = rating_out.model_dump()
        rating_id = rating_data.get("rating_id", "unknown")
        
        logger.info(
            f"Rating saved successfully (movie_id={movie_id}, rating={score}, rating_id={rating_id})"
        )
        
        return {"status": "success", "data": rating_data}
    except Exception as e:
        logger.error(
            f"Failed to save rating (movie_id={movie_id}, rating={score})",
            exc_info=True
        )
        raise
