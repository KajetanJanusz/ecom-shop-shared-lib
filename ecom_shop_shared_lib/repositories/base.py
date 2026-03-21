from dataclasses import dataclass
from typing import Any, Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from ecom_shop_shared_lib.exceptions.custom import MultipleResultsError, NotFoundError
from sqlalchemy import delete, select, update
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, QueryableAttribute, joinedload

ModelType = TypeVar("ModelType")
T = TypeVar("T")


@dataclass(frozen=True)
class ModelFields(Generic[T]):
    field: InstrumentedAttribute[T]
    value: Any

    @property
    def as_statement(self):
        return self.field == self.value


class AsyncBaseRepository(Generic[ModelType]):
    def __init__(self, model_class: Type[ModelType], db_session: AsyncSession):
        self.db_session = db_session
        self.model_class: Type[ModelType] = model_class

    async def create(self, schema: BaseModel) -> ModelType:
        instance = self.model_class(**schema.model_dump())
        self.db_session.add(instance)
        await self.db_session.flush()
        await self.db_session.refresh(instance)
        return instance

    async def update_one(
        self, model: ModelType, update_fields: list[ModelFields]
    ) -> ModelType:
        for f in update_fields:
            setattr(model, f.field.key, f.value)
        await self.db_session.flush()
        await self.db_session.refresh(model)
        return model

    async def update_many(
        self,
        update_fields: list[ModelFields],
        filter_fields: list[ModelFields] | None = None,
    ) -> int:
        query = update(self.model_class)

        if filter_fields:
            query = query.where(*[f.as_statement for f in filter_fields])

        query = query.values({f.field: f.value for f in update_fields})

        result = await self.db_session.execute(query)

        if result.rowcount == 0:
            raise NotFoundError

        return result.rowcount

    async def delete_one(self, model: ModelType) -> None:
        await self.db_session.delete(model)

    async def delete_many(self, filter_fields: list[ModelFields]) -> int:
        query = delete(self.model_class).where(*[f.as_statement for f in filter_fields])
        result = await self.db_session.execute(query)

        if result.rowcount == 0:
            raise NotFoundError

        return result.rowcount

    async def exists(self, filter_fields: list[ModelFields]) -> bool:
        query = (
            select(self.model_class)
            .where(*[f.as_statement for f in filter_fields])
            .limit(1)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_one(
        self,
        filter_fields: list[ModelFields],
        joins: list[QueryableAttribute] | None = None,
    ) -> ModelType:
        query = select(self.model_class).where(*[f.as_statement for f in filter_fields])

        if joins is not None:
            query = query.options(*[joinedload(j) for j in joins])

        result = await self.db_session.execute(query)
        try:
            return result.scalar_one()
        except NoResultFound as e:
            raise NotFoundError from e
        except MultipleResultsFound as e:
            raise MultipleResultsError from e

    async def get_many(
        self,
        filter_fields: list[ModelFields] | None = None,
        limit: int | None = None,
        joins: list[QueryableAttribute] | None = None,
    ) -> Sequence[ModelType]:
        query = select(self.model_class)

        if filter_fields is not None:
            query = query.where(*[f.as_statement for f in filter_fields])

        if limit is not None:
            query = query.limit(limit)

        if joins is not None:
            query = query.options(*[joinedload(j) for j in joins])

        result = await self.db_session.execute(query)
        return result.unique().scalars().all()
