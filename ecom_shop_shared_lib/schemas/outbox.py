from typing import Any

from pydantic import BaseModel

from ecom_shop_shared_lib.brokers.events.base import BrokerTopics
from ecom_shop_shared_lib.models.outbox_mixin import EventStatus


class OutboxSchema(BaseModel):
    event_type: BrokerTopics
    status: EventStatus
    payload: dict[str, Any]
