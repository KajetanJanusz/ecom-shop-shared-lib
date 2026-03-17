from events.base import BrokerEvent, BrokerEvents
from events.product_service.schemas import ProductCreatedSchema, ProductUpdatedSchema
from events.product_service.topics import ProductServiceTopics


class ProductServiceEvents(BrokerEvents):
    PRODUCT_CREATED = BrokerEvent(
        ProductServiceTopics.PRODUCT_CREATED, ProductCreatedSchema
    )
    PRODUCT_UPDATED = BrokerEvent(
        ProductServiceTopics.PRODUCT_UPDATED, ProductUpdatedSchema
    )
