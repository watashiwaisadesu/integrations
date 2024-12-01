from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.core.config import ASYNC_DATABASE_URL, SYNC_DATABASE_URL

Base = declarative_base()

# Async engine and session
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# Sync engine and session
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(
    bind=sync_engine, autocommit=False, autoflush=False
)

# Dependency for async database session
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

# Dependency for sync database session
def get_sync_db():
    session = SessionLocal()
    return session
