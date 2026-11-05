from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from app.core.base import Base



DATABASE_URL = settings.DATABASE_URL_ASYNC

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.ENVIRONMENT == "DEBUG",
    pool_pre_ping=True,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


from app.models import *