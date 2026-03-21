from brokers.events.base import BrokerEvent
from brokers.events.payment_service.schemas import (
    PaymentPendingSchema,
    PaymentStatusSchema,
)
from brokers.events.payment_service.topics import PaymentServiceTopics


class PaymentServiceEvents:
    PAYMENT_PENDING = BrokerEvent(
        topic=PaymentServiceTopics.PAYMENT_PENDING, schema=PaymentPendingSchema
    )
    PAYMENT_SUCCESS = BrokerEvent(
        topic=PaymentServiceTopics.PAYMENT_SUCCESS, schema=PaymentStatusSchema
    )
    PAYMENT_FAILED = BrokerEvent(
        topic=PaymentServiceTopics.PAYMENT_FAILED, schema=PaymentStatusSchema
    )
