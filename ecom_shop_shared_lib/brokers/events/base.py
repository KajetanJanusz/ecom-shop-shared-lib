from dataclasses import dataclass
from enum import StrEnum
from typing import Type

from pydantic import BaseModel


class BrokerTopics(StrEnum):
    pass


@dataclass(frozen=True, kw_only=True)
class BrokerEvent:
    topic: BrokerTopics
    schema: Type[BaseModel]
