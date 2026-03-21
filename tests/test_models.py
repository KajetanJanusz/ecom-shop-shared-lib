import uuid
from datetime import datetime

import pytest
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.base_mixin import BaseDbModelMixin
from models.outbox_mixin import EventStatus, OutboxMixin


class MixinBase(DeclarativeBase):
    pass


class SampleItem(BaseDbModelMixin, MixinBase):
    __tablename__ = "sample_items"
    name: Mapped[str] = mapped_column(String(100))


TEST_EVENT = "test-event"


class SampleOutboxEvent(OutboxMixin, MixinBase):
    __tablename__ = "sample_outbox_events"


@pytest.fixture(scope="module")
async def mixin_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(MixinBase.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(MixinBase.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def mixin_session(mixin_engine):
    async with AsyncSession(mixin_engine, expire_on_commit=False) as session:
        await session.begin()
        yield session
        await session.rollback()


class TestBaseDbModelMixin:
    async def test_defaults_are_set_on_insert(self, mixin_session):
        # Arrange
        item = SampleItem(name="alpha")

        # Act
        mixin_session.add(item)
        await mixin_session.flush()
        await mixin_session.refresh(item)

        # Assert
        assert isinstance(item.id, uuid.UUID)
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)


class TestOutboxMixin:
    async def test_defaults_are_set_on_insert(self, mixin_session):
        # Arrange
        event = SampleOutboxEvent(
            event_type=TEST_EVENT,
            status=EventStatus.UNPROCESSED,
        )

        # Act
        mixin_session.add(event)
        await mixin_session.flush()
        await mixin_session.refresh(event)

        # Assert
        assert isinstance(event.id, uuid.UUID)
        assert isinstance(event.created_at, datetime)
        assert isinstance(event.updated_at, datetime)
        assert event.attempts == 1
        assert event.last_error is None

    async def test_fields_are_persisted(self, mixin_session):
        # Arrange
        event = SampleOutboxEvent(
            event_type=TEST_EVENT,
            status=EventStatus.FAILED,
            attempts=3,
            last_error="Connection timeout",
        )

        # Act
        mixin_session.add(event)
        await mixin_session.flush()
        await mixin_session.refresh(event)

        # Assert
        assert event.event_type == TEST_EVENT
        assert event.status == EventStatus.FAILED
        assert event.attempts == 3
        assert event.last_error == "Connection timeout"
