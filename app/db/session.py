import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("URL_DATABASE")


if not DATABASE_URL:
    # Fail fast if DATABASE_URL is not configured
    raise ValueError("DATABASE_URL (or URL_DATABASE) is not set in the environment variables.")

# Create SQLAlchemy engine
# echo=True is useful during development to see generated SQL queries
engine = create_engine(DATABASE_URL, echo=True, future=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Dependency-style generator for getting a database session.
    It will be used later in FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
