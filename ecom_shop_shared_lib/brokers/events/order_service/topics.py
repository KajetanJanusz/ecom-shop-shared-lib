from brokers.events.base import BrokerTopics


class OrderServiceTopics(BrokerTopics):
    ORDER_CREATED = "order.created"
    ORDER_PAID = "order.paid"
    ORDER_COMPLETED = "order.completed"
