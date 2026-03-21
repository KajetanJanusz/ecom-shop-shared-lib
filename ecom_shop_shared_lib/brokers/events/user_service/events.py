from brokers.events.base import BrokerEvent
from brokers.events.user_service.schemas import (
    UserCreatedSchema,
    UserLoggedSchema,
)
from brokers.events.user_service.topics import UserServiceTopics


class UserServiceEvents:
    USER_CREATED = BrokerEvent(
        topic=UserServiceTopics.USER_CREATED, schema=UserCreatedSchema
    )
    USER_LOGGED = BrokerEvent(
        topic=UserServiceTopics.USER_LOGGED, schema=UserLoggedSchema
    )
