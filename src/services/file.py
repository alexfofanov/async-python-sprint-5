import json
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from redis import Redis
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import File as FileModel
from src.schemas.file import FileCreate, FileInDB, FileUpdate, SearchOptions
from src.schemas.user import Status

from .base import ModelType, RepositoryDB


class RepositoryFile(RepositoryDB[FileModel, FileCreate, FileUpdate]):
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

        # Включить кэш
        # cache_key = f'file_id:{str(id)}'
        # cached_result = await cache.get(cache_key)
        # if cached_result:
        #     file = FileInDB(**json.loads(cached_result))
        #     return file

        stmt = select(self._model).where(
            (self._model.id == id) & (self._model.user_id == user_id)
        )
        results = await db.execute(statement=stmt)
        file = results.scalar_one_or_none()
        if file:
            file_data = FileInDB.from_orm(file)
            # await cache.set(cache_key, file_data.json())

        return file

    async def get_file_on_path(
        self,
        db: AsyncSession,
        cache: Redis,
        user_id: int,
        path: str,
        name: str,
    ) -> ModelType | FileInDB | None:
        """
        Получение фйла по пути, имени и id пользователя
        """

        # todo: Включить кэш
        # cache_key = f'file_path:{str(path)}:{user_id}'
        # cached_result = await cache.get(cache_key)
        # if cached_result:
        #     file = FileInDB(**json.loads(cached_result))
        #     return file

        stmt = select(self._model).where(
            (self._model.user_id == user_id)
            & (self._model.path == path)
            & (self._model.name == name)
        )
        results = await db.execute(statement=stmt)
        file = results.scalar_one_or_none()
        if file:
            file_data = FileInDB.from_orm(file)
            # await cache.set(cache_key, file_data.json())

        return file

    async def get_status_for_user(
        self, db: AsyncSession, user_id: int
    ) -> ModelType | Status | None:
        """
        Получение статуса использования дискового пространства пользователем
        """

        stmt = (
            select(
                self._model.path,
                func.sum(self._model.size).label('used'),
                func.count().label('files'),
            )
            .where(self._model.user_id == user_id)
            .group_by(self._model.path)
        )

        results = await db.execute(statement=stmt)
        return results.all()

    async def search_files(
        self, db: AsyncSession, user_id: int, options: SearchOptions
    ) -> ModelType | Status | None:
        """
        Получение файлов пользователя по заданным параметрам
        """

        filters = []
        if options.path:
            filters.append(self._model.path == options.path)

        if options.extension:
            filters.append(self._model.name.endswith(options.extension))

        if options.query:
            filters.append(
                or_(
                    self._model.name.like(options.query),
                    self._model.path.like(options.query),
                )
            )

        stmt = (
            select(self._model)
            .where(and_(*filters))
            .limit(options.limit)
            .order_by(options.order_by)
        )
        results = await db.execute(statement=stmt)

        return results.scalars().all()


file_crud = RepositoryFile(FileModel)


def set_file_name(path_str: str, file: UploadFile) -> str:
    """
    Задание имени файла
    """

    if path_str is None:
        return file.filename

    if path_str and path_str.endswith('/') or path_str.endswith('\\'):
        return file.filename

    path = Path(path_str)
    return str(path.name)


def set_file_path(path_str: str | None) -> str:
    """
    Задание пути к файлу
    """

    if path_str is None:
        return '/'

    path = Path(path_str)
    if path_str and (path_str.endswith('/') or path_str.endswith('\\')):
        if str(path) == '/':
            return '/'

        path_str = str(Path(path_str)) + '/'

        if path_str[0] != '/':
            path_str = '/' + path_str

        return path_str

    if path_str:
        path_str = str(path.parent)
        if path_str[0] != '/':
            path_str = '/' + path_str

        if path_str[-1] != '/':
            path_str = path_str + '/'

        return path_str

    return '/'


def split_path_and_name(file_path: str) -> tuple[str, str]:
    """
    Получение пути и имени файла из полного пути
    """

    if file_path[0] != '/':
        file_path = '/' + file_path

    path = Path(file_path)
    path_str = str(path.parent)
    if path_str[-1] != '/':
        path_str = path_str + '/'
    name_str = str(path.name)

    return path_str, name_str
