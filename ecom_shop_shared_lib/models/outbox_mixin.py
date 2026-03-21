from enum import StrEnum

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ecom_shop_shared_lib.models.base_mixin import BaseDbModelMixin


class EventStatus(StrEnum):
    UNPROCESSED = "unprocessed"
    IN_PROGRESS = "in_progress"
    RETRY = "retry"
    COMPLETED = "completed"
    FAILED = "failed"


class OutboxMixin(BaseDbModelMixin):
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(Enum(EventStatus), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    last_error: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

