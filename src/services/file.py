import json
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from redis import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import File as FileModel
from src.schemas.file import FileCreate, FileInDB, FileUpdate

from .base import ModelType, RepositoryDB


class RepositoryUser(RepositoryDB[FileModel, FileCreate, FileUpdate]):
    async def get_multi_for_user(
        self,
        *,
        db: AsyncSession,
        user_id: int,
        offset: int,
        limit: int,
    ) -> list[ModelType]:
        """
        Получение списка файлов пользователя
        """

        stmt = (
            select(self._model)
            .where(self._model.user_id == user_id)  # noqa: E712
            .offset(offset)
            .limit(limit)
        )
        results = await db.execute(statement=stmt)
        return results.scalars().all()

    async def get_for_user(
        self, db: AsyncSession, cache: Redis, id: UUID, user_id: int
    ) -> ModelType | FileInDB | None:
        """
        Получение фйла по id файла и id пользователя
        """

        cache_key = f'file_id:{str(id)}'
        cached_result = await cache.get(cache_key)
        if cached_result:
            file = FileInDB(**json.loads(cached_result))
            return file

        stmt = select(self._model).where(
            (self._model.id == id) & (self._model.user_id == user_id)
        )
        results = await db.execute(statement=stmt)
        file = results.scalar_one_or_none()
        if file:
            file_data = FileInDB.from_orm(file)
            await cache.set(cache_key, file_data.json())

        return file

    async def get_file_on_path(
        self, db: AsyncSession, cache: Redis, user_id: int, path: str
    ) -> ModelType | FileInDB | None:
        """
        Получение фйла по пути и id пользователя
        """

        cache_key = f'file_path:{str(path)}:{user_id}'
        cached_result = await cache.get(cache_key)
        if cached_result:
            file = FileInDB(**json.loads(cached_result))
            return file

        stmt = select(self._model).where(
            (self._model.user_id == user_id) & (self._model.path == path)
        )
        results = await db.execute(statement=stmt)
        file = results.scalar_one_or_none()
        if file:
            file_data = FileInDB.from_orm(file)
            await cache.set(cache_key, file_data.json())

        return file


file_crud = RepositoryUser(FileModel)


def set_file_name(path_str: str, file: UploadFile) -> str:
    """
    Задание имени файла
    """

    if path_str is None:
        return file.filename

    if path_str and path_str.endswith('/') or path_str.endswith('\\'):
        return file.filename

    path = Path(path_str)
    return path.parts[-1]


def set_file_path(path_str: str, file_name: str) -> str:
    """
    Задание пути к файлу
    """

    if path_str and (path_str.endswith('/') or path_str.endswith('\\')):
        return path_str + file_name

    if path_str:
        return path_str

    return file_name
