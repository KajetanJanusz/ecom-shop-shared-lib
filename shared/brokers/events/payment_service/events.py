from events.base import BrokerEvent, BrokerEvents
from events.payment_service.schemas import PaymentPendingSchema, PaymentStatusSchema
from events.payment_service.topics import PaymentServiceTopics


class PaymentServiceEvents(BrokerEvents):
    PAYMENT_PENDING = BrokerEvent(
        PaymentServiceTopics.PAYMENT_PENDING, PaymentPendingSchema
    )
    PAYMENT_SUCCESS = BrokerEvent(
        PaymentServiceTopics.PAYMENT_SUCCESS, PaymentStatusSchema
    )
    PAYMENT_FAILED = BrokerEvent(
        PaymentServiceTopics.PAYMENT_FAILED, PaymentStatusSchema
    )
