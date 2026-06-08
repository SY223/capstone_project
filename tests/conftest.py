import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import NullPool
from app.main import app
from app.core.deps import get_async_db
from app.core.db import Base
import app.core.cache as cache_module
from tests.utils.mock_redis import mock_redis

TEST_DATABASE_URL = (
    "postgresql+asyncpg://test_user:test_password@postgres_test:5432/test_db"
)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def SessionLocal(engine):
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest.fixture(scope="function", autouse=True)
async def prepare_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def db_session(SessionLocal):
    async with SessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session):
    app.dependency_overrides[get_async_db] = lambda: db_session

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture(autouse=True)
def mock_redis_dependency():
    original = cache_module.redis_client
    cache_module.redis_client = mock_redis
    yield
    cache_module.redis_client = original