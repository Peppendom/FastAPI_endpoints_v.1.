# Third-party libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Modules
from app.db import models

# DATABASE_URL = "mysql+mysqlconnector://user:password@localhost/mydb"
DATABASE_URL = "mysql+mysqlconnector://user:password@mysql-db:3306/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)


def get_db():
    """
    Provides an SQLAlchemy session.

    - yields a database session for dependency injection;
    - ensures the session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all database tables based on SQLAlchemy models.
    """
    models.Base.metadata.create_all(bind = engine)
