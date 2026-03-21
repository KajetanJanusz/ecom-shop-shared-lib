import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock

import aio_pika
import pytest
from immutabledict import immutabledict
from pydantic import BaseModel

from brokers.clients.base import TopicEntry
from brokers.events.base import BrokerTopics


class Topic(BrokerTopics):
    ORDER = "test-topic"


class Message(BaseModel):
    message: str
    identifier: uuid.UUID


class TestAsyncKafkaClient:
    def _make_message(self, topic: str, data: BaseModel) -> MagicMock:
        msg = MagicMock()
        msg.error.return_value = None
        msg.topic.return_value = topic
        msg.value.return_value = data.model_dump_json().encode()
        return msg

    async def test_produce_serializes_and_sends_message(self, kafka_client):
        # Arrange
        key = uuid.uuid4()
        value = Message(message="hello", identifier=uuid.uuid4())

        # Act
        await kafka_client.produce(topic="test-topic", key=key, value=value)

        # Assert
        kafka_client.producer.produce.assert_called_once_with(
            topic="test-topic",
            key=str(key).encode(),
            value=value.model_dump_json().encode(),
        )

    async def test_consume_subscribes_to_provided_topics(self, kafka_client):
        # Arrange
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        kafka_client.consumer = AsyncMock()
        kafka_client.consumer.poll = AsyncMock(side_effect=asyncio.CancelledError())

        # Act
        with pytest.raises(asyncio.CancelledError):
            await kafka_client.consume(topic_handlers)

        # Assert
        kafka_client.consumer.subscribe.assert_called_once_with([Topic.ORDER])

    async def test_consume_calls_handler_with_validated_message(self, kafka_client):
        # Arrange
        payload = Message(message="test", identifier=uuid.uuid4())
        mock_msg = self._make_message(Topic.ORDER, payload)
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        kafka_client.consumer = AsyncMock()
        kafka_client.consumer.poll = AsyncMock(
            side_effect=[mock_msg, asyncio.CancelledError()]
        )

        # Act
        with pytest.raises(asyncio.CancelledError):
            await kafka_client.consume(topic_handlers)

        # Assert
        handler.assert_called_once()
        assert isinstance(handler.call_args[0][0], Message)
        assert handler.call_args[0][0].message == payload.message

    @pytest.mark.parametrize(
        ("topic", "body", "error"),
        [
            pytest.param(None, None, None, id="none_message"),
            pytest.param(Topic.ORDER, b"x", "broker error", id="errored_message"),
            pytest.param(
                "unknown-topic",
                b'{"message":"x","identifier":"00000000-0000-0000-0000-000000000000"}',
                None,
                id="unknown_topic",
            ),
            pytest.param(Topic.ORDER, b"not-json", None, id="invalid_json"),
            pytest.param(
                Topic.ORDER, b'{"wrong":"fields"}', None, id="schema_mismatch"
            ),
        ],
    )
    async def test_consume_handler_not_called_when_message_invalid(
        self, kafka_client, topic, body, error
    ):
        # Arrange
        if topic is None:
            poll_value = None
        else:
            poll_value = MagicMock()
            poll_value.error.return_value = error
            poll_value.topic.return_value = topic
            poll_value.value.return_value = body
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        kafka_client.consumer.poll = AsyncMock(
            side_effect=[poll_value, asyncio.CancelledError()]
        )

        # Act
        with pytest.raises(asyncio.CancelledError):
            await kafka_client.consume(topic_handlers)

        # Assert
        handler.assert_not_called()

    async def test_disconnect_closes_producer_and_consumer(self, kafka_client):
        # Arrange
        kafka_client.producer = AsyncMock()
        kafka_client.consumer = AsyncMock()

        # Act
        await kafka_client.disconnect()

        # Assert
        kafka_client.producer.close.assert_called_once()
        kafka_client.consumer.close.assert_called_once()


class TestAsyncRabbitClient:
    def _make_rabbit_message(self, body: bytes) -> AsyncMock:
        msg = AsyncMock()
        msg.body = body
        process_ctx = AsyncMock()
        process_ctx.__aenter__ = AsyncMock(return_value=None)
        process_ctx.__aexit__ = AsyncMock(return_value=False)
        msg.process = MagicMock(return_value=process_ctx)
        return msg

    def _make_mock_queue(self, name: str, messages: list) -> AsyncMock:
        async def _aiter():
            for msg in messages:
                yield msg

        iter_ctx = AsyncMock()
        iter_ctx.__aenter__ = AsyncMock(return_value=_aiter())
        iter_ctx.__aexit__ = AsyncMock(return_value=False)

        queue = AsyncMock()
        queue.name = name
        queue.iterator = MagicMock(return_value=iter_ctx)
        return queue

    async def test_produce_serializes_and_sends_message(self, rabbit_client):
        # Arrange
        key = uuid.uuid4()
        value = Message(message="hello", identifier=uuid.uuid4())

        # Act
        await rabbit_client.produce(topic="test-topic", key=key, value=value)

        # Assert
        rabbit_client.channel.declare_queue.assert_called_once_with(
            "test-topic", durable=True
        )
        published_msg = rabbit_client.channel.default_exchange.publish.call_args[0][0]
        assert published_msg.body == value.model_dump_json().encode()
        assert published_msg.message_id == str(key)
        assert (
            rabbit_client.channel.default_exchange.publish.call_args.kwargs[
                "routing_key"
            ]
            == "test-topic"
        )

    async def test_consume_sets_qos(self, rabbit_client):
        # Arrange
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        mock_queue = self._make_mock_queue(Topic.ORDER, [])
        rabbit_client.channel.declare_queue = AsyncMock(return_value=mock_queue)

        # Act
        await rabbit_client.consume(topic_handlers)

        # Assert
        rabbit_client.channel.set_qos.assert_called_once_with(prefetch_count=1)

    async def test_consume_declares_exchange(self, rabbit_client):
        # Arrange
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        mock_queue = self._make_mock_queue(Topic.ORDER, [])
        rabbit_client.channel.declare_queue = AsyncMock(return_value=mock_queue)

        # Act
        await rabbit_client.consume(topic_handlers)

        # Assert
        rabbit_client.channel.declare_exchange.assert_called_once_with(
            "events", aio_pika.ExchangeType.TOPIC, durable=True
        )

    async def test_consume_declares_queue_per_topic(self, rabbit_client):
        # Arrange
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        mock_queue = self._make_mock_queue(Topic.ORDER, [])
        rabbit_client.channel.declare_queue = AsyncMock(return_value=mock_queue)

        # Act
        await rabbit_client.consume(topic_handlers)

        # Assert
        rabbit_client.channel.declare_queue.assert_called_once_with(
            Topic.ORDER, durable=True
        )

    async def test_consume_binds_queue_to_exchange(self, rabbit_client):
        # Arrange
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        mock_queue = self._make_mock_queue(Topic.ORDER, [])
        mock_exchange = AsyncMock()
        rabbit_client.channel.declare_queue = AsyncMock(return_value=mock_queue)
        rabbit_client.channel.declare_exchange = AsyncMock(return_value=mock_exchange)

        # Act
        await rabbit_client.consume(topic_handlers)

        # Assert
        mock_queue.bind.assert_called_once_with(
            exchange=mock_exchange, routing_key=Topic.ORDER
        )

    async def test_consume_calls_handler_with_validated_message(self, rabbit_client):
        # Arrange
        payload = Message(message="test", identifier=uuid.uuid4())
        msg = self._make_rabbit_message(payload.model_dump_json().encode())
        mock_queue = self._make_mock_queue(Topic.ORDER, [msg])
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        rabbit_client.channel.declare_queue = AsyncMock(return_value=mock_queue)

        # Act
        await rabbit_client.consume(topic_handlers)

        # Assert
        handler.assert_called_once()
        assert isinstance(handler.call_args[0][0], Message)
        assert handler.call_args[0][0].message == payload.message

    @pytest.mark.parametrize(
        "body",
        [
            pytest.param(b"not-json", id="invalid_json"),
            pytest.param(b'{"wrong":"fields"}', id="schema_mismatch"),
        ],
    )
    async def test_consume_handler_not_called_for_invalid_body(
        self, rabbit_client, body
    ):
        # Arrange
        msg = self._make_rabbit_message(body)
        mock_queue = self._make_mock_queue(Topic.ORDER, [msg])
        handler = AsyncMock()
        topic_handlers = immutabledict(
            {Topic.ORDER: TopicEntry(schema=Message, handler=handler)}
        )
        rabbit_client.channel.declare_queue = AsyncMock(return_value=mock_queue)

        # Act
        await rabbit_client.consume(topic_handlers)

        # Assert
        handler.assert_not_called()

    async def test_disconnect_clears_connection_and_channel(self, rabbit_client):
        # Arrange
        connection = rabbit_client.connection

        # Act
        await rabbit_client.disconnect()

        # Assert
        connection.close.assert_called_once()
        assert rabbit_client.connection is None
        assert rabbit_client.channel is None
