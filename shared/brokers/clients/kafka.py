import logging
import uuid

from confluent_kafka import Message
from immutabledict import immutabledict

from confluent_kafka.aio import AIOProducer, AIOConsumer
from pydantic import BaseModel

from clients.base import AsyncBaseClient, TopicEntry
from events.base import BrokerTopics

logger = logging.getLogger(__name__)


class AsyncKafkaClient(AsyncBaseClient):
    def __init__(self, broker_url: str, group_id: str):
        super().__init__(broker_url)
        self.group_id = group_id
        self.producer: AIOProducer | None = None
        self.consumer: AIOConsumer | None = None

    async def connect(self) -> None:
        self.producer = AIOProducer(
            producer_conf={
                "bootstrap.servers": self.broker_url,
            }
        )
        self.consumer = AIOConsumer(
            {
                "bootstrap.servers": self.broker_url,
                "group_id": self.group_id,
                "auto.offset.reset": "earliest",
            }
        )

    async def disconnect(self) -> None:
        if self.producer:
            await self.producer.close()

        if self.consumer:
            await self.consumer.close()

    async def produce(self, topic: str, key: uuid.UUID, value: BaseModel) -> None:
        if self.producer is None:
            raise RuntimeError("Client not connected. Call connect() first.")

        await self.producer.produce(
            topic=topic,
            key=str(key).encode(),
            value=value.model_dump_json().encode(),
        )

    async def consume(
        self,
        topic_handlers: immutabledict[BrokerTopics, TopicEntry],
    ) -> None:
        if self.consumer is None:
            raise RuntimeError("Client not connected. Call connect() first.")

        await self.consumer.subscribe(list(topic_handlers.keys()))

        while True:
            message: Message = await self.consumer.poll(timeout=1.0)

            if message is None or message.error():
                logger.error("Consumer error: %s", message.error() if message else None)
                continue

            entry = topic_handlers.get(message.topic())

            if entry is None:
                logger.error(
                    "Topic not found. Topic: %s, payload: %s",
                    message.topic(),
                    message.value(),
                )
                continue

            await self._process_message(
                topic=message.topic(),
                body=message.value(),
                schema=entry.schema,
                handler=entry.handler,
            )
