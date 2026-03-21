import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BaseProductSchema(BaseModel):
    id: uuid.UUID
    name: str
    price: Decimal
    stock: int


class ProductCreatedSchema(BaseProductSchema):
    created_at: datetime


class ProductUpdatedSchema(BaseProductSchema):
    updated_at: datetime
