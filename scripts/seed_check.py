from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import engine


def verify_seeding() -> bool:
    """
    Check if the database has the expected number of records after seeding.

    Uses the same SQLAlchemy engine as the main application,
    so no password or connection string is hard-coded here.
    """
    try:
        with Session(engine) as session:
            # Check for ~1000 movies (as defined by the seed script)
            movie_count = session.execute(
                text("SELECT COUNT(*) FROM movies")
            ).scalar_one()

            # Check directors count (should be > 1000 in TMDB-based seeding)
            director_count = session.execute(
                text("SELECT COUNT(*) FROM directors")
            ).scalar_one()

        if movie_count == 1000 and director_count > 1000:
            print("Seeding Successful!")
            print(f" - Movies loaded: {movie_count}")
            print(f" - Directors loaded: {director_count}")
            return True

        print(
            "Seeding may be incomplete or inconsistent."
        )
        print(f" - Movies loaded: {movie_count}")
        print(f" - Directors loaded: {director_count}")
        return False

    except Exception as exc:
        print("Database connection or query failed during verification:")
        print(f"  {exc}")
        return False


if __name__ == "__main__":
    verify_seeding()
