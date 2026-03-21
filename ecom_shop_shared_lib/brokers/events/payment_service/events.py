from ecom_shop_shared_lib.brokers.events.base import BrokerEvent, BrokerEvents
from ecom_shop_shared_lib.brokers.events.payment_service.schemas import (
    PaymentPendingSchema,
    PaymentStatusSchema,
)
from ecom_shop_shared_lib.brokers.events.payment_service.topics import (
    PaymentServiceTopics,
)


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
