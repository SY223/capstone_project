# tests/conftest.py

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from typing import AsyncGenerator

from app.main import app
from app.core.deps import get_async_db
from app.core.db import Base
import app.core.cache as cache_module
from tests.utils.mock_redis import mock_redis


TEST_DATABASE_URL = (
    "postgresql+asyncpg://test_user:test_password@postgres_test:5432/test_db"
)

# ---------------------------
# SESSION-SCOPED ENGINE
# ---------------------------
@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    yield engine

    import asyncio
    asyncio.get_event_loop().run_until_complete(engine.dispose())


# ---------------------------
# SESSION-SCOPED SESSIONMAKER
# ---------------------------
@pytest.fixture(scope="session")
def SessionLocal(engine):
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


# ---------------------------
# CREATE/DROP TABLES ONCE
# ---------------------------
@pytest.fixture(scope="session", autouse=True)
async def prepare_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# ---------------------------
# FUNCTION-SCOPED DB SESSION
# ---------------------------
@pytest.fixture(scope="function")
async def db_session(SessionLocal):
    async with SessionLocal() as session:
        yield session


# ---------------------------
# HTTP CLIENT WITH DB OVERRIDE
# ---------------------------
@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_async_db] = lambda: db_session

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ---------------------------
# REDIS MOCK
# ---------------------------
@pytest.fixture(autouse=True)
def mock_redis_dependency():
    original = cache_module.redis_client
    cache_module.redis_client = mock_redis
    yield
    cache_module.redis_client = original
