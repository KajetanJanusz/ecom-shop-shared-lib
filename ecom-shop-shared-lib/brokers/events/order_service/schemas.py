import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BaseOrderSchema(BaseModel):
    id: uuid.UUID


class OrderCreatedSchema(BaseOrderSchema):
    created_at: datetime


class OrderPaidSchema(BaseOrderSchema):
    amount: Decimal
    currency: str
    paid_at: datetime


class OrderCompletedSchema(BaseOrderSchema):
    completed_at: datetime
