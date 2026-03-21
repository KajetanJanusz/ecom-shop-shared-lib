from brokers.events.base import BrokerEvent
from brokers.events.product_service.schemas import (
    ProductCreatedSchema,
    ProductUpdatedSchema,
)
from brokers.events.product_service.topics import ProductServiceTopics


class ProductServiceEvents:
    PRODUCT_CREATED = BrokerEvent(
        topic=ProductServiceTopics.PRODUCT_CREATED, schema=ProductCreatedSchema
    )
    PRODUCT_UPDATED = BrokerEvent(
        topic=ProductServiceTopics.PRODUCT_UPDATED, schema=ProductUpdatedSchema
    )
