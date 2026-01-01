"""Script to verify database seeding was successful."""

from __future__ import annotations

import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Get DATABASE_URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://app_user:app_pass@localhost:5432/app_db",
)

engine = create_engine(DATABASE_URL)


def verify_seeding() -> bool:
    """
    Check if the database has the expected number of records after seeding.

    Returns True if seeding was successful, False otherwise.
    """
    try:
        with Session(engine) as session:
            # Check for 1000 movies
            movie_count = session.execute(
                text("SELECT COUNT(*) FROM movies")
            ).scalar_one()

            # Check for the number of directors (should be > 1000)
            director_count = session.execute(
                text("SELECT COUNT(*) FROM directors")
            ).scalar_one()

            # Check genres count
            genre_count = session.execute(
                text("SELECT COUNT(*) FROM genres")
            ).scalar_one()

            # Check ratings count
            rating_count = session.execute(
                text("SELECT COUNT(*) FROM movie_ratings")
            ).scalar_one()

            if movie_count == 1000 and director_count > 1000:
                print("Seeding Successful!")
                print(f"   - Movies loaded: {movie_count}")
                print(f"   - Directors loaded: {director_count}")
                print(f"   - Genres loaded: {genre_count}")
                print(f"   - Ratings loaded: {rating_count}")
                return True
            else:
                print("Seeding Failed!")
                print(f"   - Expected 1000 movies, found {movie_count}")
                print(f"   - Expected > 1000 directors, found {director_count}")
                return False

    except Exception as e:
        print(f"Database connection or query failed during verification: {e}")
        return False


if __name__ == "__main__":
    verify_seeding()

