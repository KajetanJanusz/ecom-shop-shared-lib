from typing import Any

from pydantic import BaseModel

from ecom_shop_shared_lib.brokers.events.base import BrokerTopics
from ecom_shop_shared_lib.models.outbox_mixin import EventStatus


class OutboxSchema(BaseModel):
    event_topic: BrokerTopics
    payload: dict[str, Any]
    status: EventStatus | None = None
