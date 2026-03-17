from events.base import BrokerTopics


class ProductServiceTopics(BrokerTopics):
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
