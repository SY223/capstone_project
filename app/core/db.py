from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings



DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in environment variables or fallback!")

engine = create_engine(
    DATABASE_URL,
    echo= True if settings.ENVIRONMENT == "DEBUG" else False, 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base class
class Base(DeclarativeBase):
    pass

from app.models import *