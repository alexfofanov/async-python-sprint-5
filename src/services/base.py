from typing import Any, Generic, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

from sqlalchemy import select


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(
    Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(
            self, db: AsyncSession, *, offset: int, limit: int
    ) -> list[ModelType]:
        statement = select(self._model).offset(offset).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(
            self, db: AsyncSession, *, obj: CreateSchemaType
    ) -> ModelType:
        obj_data = jsonable_encoder(obj)
        db_obj = self._model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> ModelType | None:
        obj = await self.get(db=db, id=id)
        if not obj:
            return None

        await db.delete(obj)
        await db.commit()
        return obj

    async def patch(
            self, db: AsyncSession, id: Any, data: UpdateSchemaType
    ) -> ModelType | None:
        obj = await self.get(db=db, id=id)
        if not obj:
            return None

        obj_data = jsonable_encoder(data)
        for key, value in obj_data.items():
            setattr(obj, key, value)

        await db.commit()
        await db.refresh(obj)
        return obj
