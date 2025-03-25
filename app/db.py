import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator

# Retrieve the database URL from the environment variables. Use os.environ to ensure the type is str.
DATABASE_URL: str = os.environ["DB_URL"]

# Create the SQLAlchemy engine using the provided DB_URL.
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the ORM models.
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a SQLAlchemy database session.
    It creates a new session for each request and ensures the session is closed after the request is finished.
    
    Returns:
        A database session generator.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
