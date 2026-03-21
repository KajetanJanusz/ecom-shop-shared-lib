from ecom_shop_shared_lib.brokers.events.base import BrokerEvent, BrokerEvents
from ecom_shop_shared_lib.brokers.events.product_service.schemas import (
    ProductCreatedSchema,
    ProductUpdatedSchema,
)
from ecom_shop_shared_lib.brokers.events.product_service.topics import ProductServiceTopics


class ProductServiceEvents(BrokerEvents):
    PRODUCT_CREATED = BrokerEvent(
        ProductServiceTopics.PRODUCT_CREATED, ProductCreatedSchema
    )
    PRODUCT_UPDATED = BrokerEvent(
        ProductServiceTopics.PRODUCT_UPDATED, ProductUpdatedSchema
    )
