"""
Database connection management
"""

from sqlmodel import SQLModel, Session, create_engine
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


def init_db():
    """Initialize the database by creating all tables"""
    SQLModel.metadata.create_all(engine)
    print("Database initialized")


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session
