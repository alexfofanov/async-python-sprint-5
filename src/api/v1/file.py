from typing import Any
from uuid import UUID

from aiohttp import ClientConnectorError
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from miniopy_async import S3Error
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.config import logger
from src.core.utils import is_uuid
from src.db.db import get_session
from src.db.redis import get_redis
from src.models import User
from src.schemas.file import FileCreate, FileInDB, SearchOptions
from src.services.file import (
    file_crud,
    set_file_name,
    set_file_path,
    split_path_and_name,
)
from src.services.minio import minio_handler

file_router = APIRouter()


@file_router.get(
    '/',
    response_model=list[FileInDB],
    summary='Получение файлов',
    description='Получение списка загруженных пользователем файлов',
)
async def get_files(
    request: Request,
    *,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    offset: int = 0,
    limit: int = 10,
) -> Any:
    """
    Список загруженных файлов
    """

    files = await file_crud.get_multi_for_path(
        db=db, user_id=user.id, offset=offset, limit=limit
    )

    return files


@file_router.get(
    '/folder',
    response_model=list[FileInDB],
    summary='Получение файлов из папки',
    description='Получение списка файлов в папке',
)
async def get_files_in_folder(
    request: Request,
    *,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    path: str,
    offset: int = 0,
    limit: int = 10,
) -> Any:
    """
    Получение списка файлов в папке
    """

    files = await file_crud.get_multi_for_path(
        db=db, user_id=user.id, path=path, offset=offset, limit=limit
    )

    return files


@file_router.post(
    '/upload',
    response_model=FileInDB,
    status_code=status.HTTP_201_CREATED,
    summary='Сохранение файла',
    description='Сохранение файла в хранилище',
)
async def upload(
    request: Request,
    *,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    cache: Redis = Depends(get_redis),
    file: UploadFile,
    path: str | None = None,
) -> Any:
    """
    Сохранение файла в хранилище
    """

    file_name = set_file_name(path, file)
    file_path = set_file_path(path)

    file_in_db = await file_crud.get_file_on_path(
        db=db, cache=cache, user_id=user.id, path=file_path, name=file_name
    )

    if not file_in_db:
        obj = FileCreate(
            user_id=user.id, name=file_name, path=file_path, size=file.size
        )
        file_in_db = await file_crud.create(db=db, obj=obj)

    file_data = await file.read()

    try:
        await minio_handler.write(
            file_in_db.id, file_data, file.size, file_name
        )
    except (S3Error, ClientConnectorError) as e:
        error_msg = f'Minio error occurred: {e}'
        logger.error(error_msg)

        await file_crud.delete(db=db, id=file_in_db.id)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        )

    return file_in_db


@file_router.get(
    '/download',
    summary='Получение файла',
    description='Получение файла из хранилища',
)
async def download(
    request: Request,
    *,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    cache: Redis = Depends(get_redis),
    path: str | UUID,
) -> Any:
    """
    Получение файла из хранилища
    """

    if is_uuid(path):
        file = await file_crud.get_for_user(
            db=db, cache=cache, id=path, user_id=user.id
        )
    else:
        file_path, file_name = split_path_and_name(path)
        file = await file_crud.get_file_on_path(
            db=db, cache=cache, user_id=user.id, path=file_path, name=file_name
        )

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='File not found',
        )

    try:
        response = await minio_handler.read(file.id)
    except S3Error as e:
        error_msg = f'Minio error occurred: {e}'
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg,
        )

    async def file_iterator():
        async for chunk in response.content.iter_chunked(32 * 1024):
            yield chunk

    content_disposition = f'attachment; filename="{file.name}"'
    return StreamingResponse(
        file_iterator(),
        media_type='application/octet-stream',
        headers={'Content-Disposition': content_disposition},
    )


@file_router.post(
    '/search',
    response_model=list[FileInDB],
    summary='Поиск файлов',
    description='Поиск файлов по заданным параметрам',
)
async def search_files(
    request: Request,
    *,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    options: SearchOptions,
) -> Any:
    """
    Поиск файлов по заданным параметрам
    """

    files = await file_crud.search_files(
        db=db, user_id=user.id, options=options
    )

    return files
