import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./datapilot.db")

# Create engine with appropriate options for SQLite vs PostgreSQL
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_engine():
    """Returns the SQLAlchemy engine instance."""
    return engine


def init_db(target_engine=None):
    """Initializes the database by creating all tables."""
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)


def get_db() -> Generator[Session, None, None]:
    """Dependency generator for FastAPI / service layer to acquire DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
