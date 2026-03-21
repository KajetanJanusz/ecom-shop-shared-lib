import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BasePaymentSchema(BaseModel):
    id: uuid.UUID


class PaymentPendingSchema(BasePaymentSchema):
    order_id: uuid.UUID
    amount: Decimal
    currency: str
    created_at: datetime


class PaymentStatusSchema(BasePaymentSchema):
    order_id: uuid.UUID
    status: str
    completed_at: datetime
