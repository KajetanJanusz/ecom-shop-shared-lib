import uuid
from datetime import datetime

from pydantic import BaseModel


class BaseUserSchema(BaseModel):
    id: uuid.UUID


class UserCreatedSchema(BaseUserSchema):
    created_at: datetime


class UserLoggedSchema(BaseUserSchema):
    pass
