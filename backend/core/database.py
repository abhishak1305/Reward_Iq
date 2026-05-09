"""
Async SQLAlchemy database engine and session management.
Supports both SQLite (local dev) and PostgreSQL (production/Neon).
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, StaticPool
from typing import AsyncGenerator
from sqlalchemy import event
from sqlalchemy.engine import Engine

from backend.core.config import settings

# Detect SQLite vs PostgreSQL
_IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

if _IS_SQLITE:
    # SQLite: use StaticPool so the same in-memory or file connection is reused
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL / Neon: NullPool avoids connection leaks in serverless envs
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        poolclass=NullPool,
        connect_args={
            "server_settings": {"application_name": settings.APP_NAME},
        },
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session per request,
    rolling back on error and always closing the session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_all_tables() -> None:
    """Create all tables on startup (dev/test only). Use Alembic in production."""
    async with engine.begin() as conn:
        from backend.models import (  # noqa: F401 — import for side effects
            user, employee, attendance, reward, bonus, feedback,
            ai_prediction, notification,
        )
        await conn.run_sync(Base.metadata.create_all)
