from app.db.session import Base, engine
from app.models import models as models_module  # noqa: F401


def init_db() -> None:
    """
    Create all database tables based on SQLAlchemy models.
    """
    # Importing models is enough because they are registered in Base.metadata
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created (or already exist).")
