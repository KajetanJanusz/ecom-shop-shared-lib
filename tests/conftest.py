from unittest.mock import AsyncMock

import pytest
from ecom_shop_shared_lib.brokers.clients.kafka import AsyncKafkaClient
from ecom_shop_shared_lib.brokers.clients.rabbit import AsyncRabbitClient
from db_models import Base, User
from repositories import AsyncBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine):
    """Function-scoped session; all changes are rolled back after each test."""
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest.fixture
async def user_repository(db_session) -> AsyncBaseRepository:
    return AsyncBaseRepository(User, db_session)


@pytest.fixture
async def kafka_client():
    client = AsyncKafkaClient(broker_url="123", group_id="123")
    client.producer = AsyncMock()
    client.consumer = AsyncMock()
    return client


@pytest.fixture
def rabbit_client():
    client = AsyncRabbitClient(broker_url="amqp://guest:guest@localhost/")
    client.connection = AsyncMock()
    client.channel = AsyncMock()
    return client
