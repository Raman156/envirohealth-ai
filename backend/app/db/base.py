import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Use SQLite for local dev (no PostgreSQL required)
# Override with DATABASE_URL env var for production PostgreSQL
_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "envirohealth.db")
_DEFAULT_URL = f"sqlite+aiosqlite:///{os.path.abspath(_DB_PATH)}"
DATABASE_URL = os.environ.get("DATABASE_URL", _DEFAULT_URL)

# Normalise postgres+asyncpg → sqlite for local dev when no pg available
if DATABASE_URL.startswith("postgresql"):
    DATABASE_URL = _DEFAULT_URL


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        is_sqlite = DATABASE_URL.startswith("sqlite")
        kwargs = {"echo": False}
        if is_sqlite:
            kwargs["connect_args"] = {"check_same_thread": False}
        _engine = create_async_engine(DATABASE_URL, **kwargs)
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _session_factory


async def get_db():
    async with get_session_factory()() as session:
        try:
            yield session
        finally:
            await session.close()
