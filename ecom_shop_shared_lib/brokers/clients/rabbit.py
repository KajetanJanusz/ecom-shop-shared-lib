import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import Type

import aio_pika
import aio_pika.abc
from immutabledict import immutabledict
from pydantic import BaseModel

from brokers.clients.base import AsyncBaseClient, TopicEntry
from brokers.events.base import BrokerTopics

logger = logging.getLogger(__name__)


class AsyncRabbitClient(AsyncBaseClient):
    def __init__(self, broker_url: str):
        super().__init__(broker_url)
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.broker_url)
        self.channel = await self.connection.channel()

    async def disconnect(self) -> None:
        if not self.connection:
            return

        await self.connection.close()
        self.connection = None
        self.channel = None

    async def produce(self, topic: str, key: uuid.UUID, value: BaseModel) -> None:
        if self.channel is None:
            raise RuntimeError("Client not connected. Call connect() first.")

        await self.channel.declare_queue(topic, durable=True)
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=value.model_dump_json().encode(),
                message_id=str(key),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=topic,
        )

    async def consume(
        self,
        topic_handlers: immutabledict[BrokerTopics, TopicEntry],
    ) -> None:
        if self.channel is None:
            raise RuntimeError("Client not connected. Call connect() first.")

        await self.channel.set_qos(prefetch_count=1)
        exchange = await self.channel.declare_exchange(
            "events", aio_pika.ExchangeType.TOPIC, durable=True
        )

        tasks = []
        for topic, entry in topic_handlers.items():
            queue = await self.channel.declare_queue(topic, durable=True)
            await queue.bind(exchange=exchange, routing_key=topic)
            tasks.append(self._consume_queue(queue, entry.schema, entry.handler))

        await asyncio.gather(*tasks)

    async def _consume_queue(
        self,
        queue: aio_pika.abc.AbstractQueue,
        schema: Type[BaseModel],
        handler: Callable[[BaseModel], Awaitable[None]],
    ) -> None:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self._process_message(
                        topic=queue.name,
                        body=message.body,
                        schema=schema,
                        handler=handler,
                    )
