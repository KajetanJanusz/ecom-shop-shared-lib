from events.base import BrokerEvent, BrokerEvents
from events.order_service.schemas import (
    OrderCreatedSchema,
    OrderPaidSchema,
    OrderCompletedSchema,
)
from events.order_service.topics import OrderServiceTopics


class OrderServiceEvents(BrokerEvents):
    ORDER_CREATED = BrokerEvent(OrderServiceTopics.ORDER_CREATED, OrderCreatedSchema)
    ORDER_PAID = BrokerEvent(OrderServiceTopics.ORDER_PAID, OrderPaidSchema)
    ORDER_COMPLETED = BrokerEvent(
        OrderServiceTopics.ORDER_COMPLETED, OrderCompletedSchema
    )
