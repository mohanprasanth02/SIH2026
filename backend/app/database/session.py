"""
SatQuery AI - Database Session Management
Supports both SQLite (dev) and PostgreSQL (production).
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, event
from app.config.settings import get_settings

settings = get_settings()

# Build engine kwargs based on database type
_is_sqlite = "sqlite" in settings.database_url

engine_kwargs = {
    "echo": settings.debug,
}
if not _is_sqlite:
    # Connection pooling only for non-SQLite
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })
else:
    # SQLite needs connect_args for async
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Async engine (FastAPI routes)
async_engine = create_async_engine(
    settings.database_url,
    **engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Sync engine (Alembic migrations only)
sync_engine_kwargs = {"echo": settings.debug}
if _is_sqlite:
    sync_engine_kwargs["connect_args"] = {"check_same_thread": False}

sync_engine = create_engine(
    settings.sync_database_url,
    **sync_engine_kwargs,
)


async def get_db() -> AsyncSession:
    """Dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables (for development; use Alembic in production)."""
    from app.database.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
