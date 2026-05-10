"""
Async SQLAlchemy database engine and session management.
Supports SQLite (local dev) and PostgreSQL (production).
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


def _normalize_db_url(url: str) -> str:
    """
    Normalize any PostgreSQL URL variant to use the asyncpg driver.
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    
    # asyncpg is extremely sensitive to unsupported query parameters
    # (like sslmode, channel_binding, etc. used by Render/Neon/Heroku).
    # We strip them all for PostgreSQL URLs to prevent TypeErrors.
    if "postgresql" in url and "?" in url:
        url = url.split("?")[0]
        
    return url


_DB_URL = _normalize_db_url(settings.DATABASE_URL)
_IS_SQLITE = _DB_URL.startswith("sqlite")

if _IS_SQLITE:
    engine = create_async_engine(
        _DB_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_async_engine(
        _DB_URL,
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
    """Enable FK enforcement for SQLite only (no-op for PostgreSQL)."""
    if _IS_SQLITE:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_all_tables() -> None:
    """Create all tables. Safe to call repeatedly (IF NOT EXISTS)."""
    async with engine.begin() as conn:
        from backend.models import (  # noqa: F401
            user, employee, attendance, reward, bonus,
            feedback, ai_prediction, notification,
        )
        await conn.run_sync(Base.metadata.create_all)
