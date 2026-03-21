from ecom_shop_shared_lib.brokers.events.base import BrokerEvent, BrokerEvents
from ecom_shop_shared_lib.brokers.events.user_service.schemas import (
    UserCreatedSchema,
    UserLoggedSchema,
)
from ecom_shop_shared_lib.brokers.events.user_service.topics import UserServiceTopics


class UserServiceEvents(BrokerEvents):
    USER_CREATED = BrokerEvent(
        topic=UserServiceTopics.USER_CREATED, schema=UserCreatedSchema
    )
    USER_LOGGED = BrokerEvent(
        topic=UserServiceTopics.USER_LOGGED, schema=UserLoggedSchema
    )
