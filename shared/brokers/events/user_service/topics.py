from events.base import BrokerTopics


class UserServiceTopics(BrokerTopics):
    USER_CREATED = "user.created"
    USER_LOGGED = "user.logged"
