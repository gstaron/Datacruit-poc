"""SQLAlchemy access to the shared Postgres database.

The AI matching microservice is a separate deployable process from the
Django app, so it talks to Postgres through its own SQLAlchemy engine
rather than importing Django — but both read/write the *same* database
(the tables Django's migrations create), configured via the same
DATABASE_URL convention.
"""

import os
from functools import lru_cache

from sqlalchemy import Column, Integer, JSON, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()


class JobRow(Base):
    """Read-only mapping onto Django's jobs_job table."""

    __tablename__ = "jobs_job"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    must_have = Column(JSON)
    nice_to_have = Column(JSON)


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/datacruit")
    # SQLAlchemy's psycopg2 dialect wants "postgresql://", not "postgres://".
    return url.replace("postgres://", "postgresql://", 1)


@lru_cache
def get_engine():
    return create_engine(_database_url(), pool_pre_ping=True)


def get_db():
    session_factory = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    db: Session = session_factory()
    try:
        yield db
    finally:
        db.close()
