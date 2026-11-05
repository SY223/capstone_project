from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
from app.core.base import Base



DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL or not DATABASE_URL.strip():
    raise ValueError(
        "DATABASE_URL is missing or empty. "
        "Check the Railway DATABASE_URL environment variable."
    )

engine = create_engine(
    DATABASE_URL,
    echo= settings.ENVIRONMENT == "DEBUG",
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


from app.models import *