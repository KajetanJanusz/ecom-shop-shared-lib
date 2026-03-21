from shared.brokers.events.base import BrokerEvent, BrokerEvents
from shared.brokers.events.user_service.schemas import UserCreatedSchema, UserLoggedSchema
from shared.brokers.events.user_service.topics import UserServiceTopics


class UserServiceEvents(BrokerEvents):
    USER_CREATED = BrokerEvent(UserServiceTopics.USER_CREATED, UserCreatedSchema)
    USER_LOGGED = BrokerEvent(UserServiceTopics.USER_LOGGED, UserLoggedSchema)
