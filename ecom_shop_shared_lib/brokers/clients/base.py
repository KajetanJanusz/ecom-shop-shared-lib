import logging
import uuid
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import NamedTuple, Type

import orjson
from immutabledict import immutabledict
from pydantic import BaseModel, ValidationError

from ecom_shop_shared_lib.brokers.events.base import BrokerTopics

logger = logging.getLogger(__name__)


class TopicEntry(NamedTuple):
    schema: Type[BaseModel]
    handler: Callable[[BaseModel], Awaitable[None]]


class AsyncBaseClient(ABC):
    def __init__(self, broker_url: str):
        self.broker_url = broker_url

    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def produce(self, topic: str, key: uuid.UUID, value: BaseModel) -> None:
        raise NotImplementedError

    @abstractmethod
    async def consume(
        self,
        topic_handlers: immutabledict[BrokerTopics, TopicEntry],
    ) -> None:
        raise NotImplementedError

    @staticmethod
    async def _process_message(
        topic: str,
        body: bytes,
        schema: Type[BaseModel],
        handler: Callable[[BaseModel], Awaitable[None]],
    ) -> None:
        try:
            parsed = orjson.loads(body)
        except orjson.JSONDecodeError:
            logger.error(
                "Failed to decode JSON. Topic: %s, payload: %s",
                topic,
                body,
                exc_info=True,
            )
            return

        try:
            validated = schema.model_validate(parsed)
        except ValidationError:
            logger.error(
                "Message failed validation. Topic: %s, payload: %s",
                topic,
                parsed,
                exc_info=True,
            )
            return

        await handler(validated)
