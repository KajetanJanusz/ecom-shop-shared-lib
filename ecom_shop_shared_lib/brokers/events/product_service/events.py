from ecom_shop_shared_lib.brokers.events.base import BrokerEvent
from ecom_shop_shared_lib.brokers.events.product_service.schemas import (
    ProductCreatedSchema,
    ProductUpdatedSchema,
)
from ecom_shop_shared_lib.brokers.events.product_service.topics import (
    ProductServiceTopics,
)


class ProductServiceEvents:
    PRODUCT_CREATED = BrokerEvent(
        topic=ProductServiceTopics.PRODUCT_CREATED, schema=ProductCreatedSchema
    )
    PRODUCT_UPDATED = BrokerEvent(
        topic=ProductServiceTopics.PRODUCT_UPDATED, schema=ProductUpdatedSchema
    )
