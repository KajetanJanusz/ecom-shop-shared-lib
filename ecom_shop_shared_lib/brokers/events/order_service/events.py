from brokers.events.base import BrokerEvent
from brokers.events.order_service.schemas import (
    OrderCreatedSchema,
    OrderPaidSchema,
    OrderCompletedSchema,
)
from brokers.events.order_service.topics import OrderServiceTopics


class OrderServiceEvents:
    ORDER_CREATED = BrokerEvent(
        topic=OrderServiceTopics.ORDER_CREATED, schema=OrderCreatedSchema
    )
    ORDER_PAID = BrokerEvent(
        topic=OrderServiceTopics.ORDER_PAID, schema=OrderPaidSchema
    )
    ORDER_COMPLETED = BrokerEvent(
        topic=OrderServiceTopics.ORDER_COMPLETED, schema=OrderCompletedSchema
    )
