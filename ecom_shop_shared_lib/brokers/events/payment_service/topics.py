from brokers.events.base import BrokerTopics


class PaymentServiceTopics(BrokerTopics):
    PAYMENT_PENDING = "payment.pending"
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
