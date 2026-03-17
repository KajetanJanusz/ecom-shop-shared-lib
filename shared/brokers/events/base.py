from dataclasses import dataclass
from enum import StrEnum, Enum
from typing import Type

from pydantic import BaseModel


class BrokerTopics(StrEnum):
    pass


class BrokerEvents(Enum):
    pass


@dataclass(frozen=True)
class BrokerEvent:
    topic: BrokerTopics
    schema: Type[BaseModel]
