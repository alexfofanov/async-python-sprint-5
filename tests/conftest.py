from io import BytesIO

import asyncpg
import pytest
from fastapi import UploadFile, status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import app_settings
from src.db.db import get_session
from src.main import app
from src.models import Base
from src.services.minio import minio_handler

URL_PREFIX_AUTH = '/api/v1/users'
URL_PREFIX_FILE = '/api/v1/files'
TEST_USER = {'login': 'test_user', 'password': 'password'}
FILE_NAME = 'test_file.txt'
UPLOAD_FILE_NAME = 'test_upload_file.txt'
FILE_PATH = '/test_file_path/'
FILE_PATH_WITH_FILE_NAME = FILE_PATH + FILE_NAME
ROOT_PATH = '/'
EXTENSION = 'ext'
PATTERN = 'XXX'

FILES_SEARCH_IN_PATH = [
    {'path': ROOT_PATH, 'name': 'test_file_1.txt'},
    {'path': ROOT_PATH, 'name': 'test_file_2.txt'},
    {'path': ROOT_PATH, 'name': 'test_file_1.jpg'},
]

FILES_SEARCH_IN_EXTENSION = [
    {'path': '/dir1/', 'name': f'test_file_1.{EXTENSION}'},
    {'path': '/dir1/dir2/', 'name': f'test_file_2.{EXTENSION}'},
]

FILES_SEARCH_IN_QUERY = [
    {'path': '/dir1/', 'name': f'test_{PATTERN}_file_1.txt'},
    {'path': '/dir1/', 'name': f'test_{PATTERN}_file_2.txt'},
    {'path': f'/dir1_{PATTERN}/', 'name': 'test_file_3.txt'},
]

FILES_FOR_COMPARISON = (
    FILES_SEARCH_IN_PATH + FILES_SEARCH_IN_EXTENSION + FILES_SEARCH_IN_QUERY
)


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def create_test_backet():
    minio_handler.bucket_name = app_settings.minio_test_bucket_name
    await minio_handler.create_backet(app_settings.minio_test_bucket_name)

    yield

    await minio_handler.delete_bucket()


@pytest.fixture(scope='session')
async def create_test_database():
    conn = await asyncpg.connect(
        app_settings.dsn.replace('postgresql+asyncpg', 'postgresql')
    )

    await conn.execute(
        f'DROP DATABASE IF EXISTS {app_settings.postgres_test_db}'
    )
    await conn.execute(f'CREATE DATABASE {app_settings.postgres_test_db}')
    await conn.close()

    yield

    conn = await asyncpg.connect(
        app_settings.dsn.replace('postgresql+asyncpg', 'postgresql')
    )
    await conn.execute(
        f'DROP DATABASE IF EXISTS {app_settings.postgres_test_db}'
    )
    await conn.close()


@pytest.fixture(scope='module')
async def db_engine(create_test_database):
    engine = create_async_engine(
        app_settings.dsn_test, echo=False, future=True, poolclass=NullPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture()
async def db_session_factory(db_engine):
    return async_sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest.fixture()
async def db_session(db_session_factory):
    async with db_session_factory() as session:
        yield session


@pytest.fixture()
async def async_client(db_session_factory):
    async def override_get_session():
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture()
async def headers():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        response = await async_client.post(
            f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
        )
        token = response.json()
        headers = {'Authorization': f'Bearer {token["access_token"]}'}
        return headers


@pytest.fixture()
async def test_file():
    file_content = b'this is some test file content'
    return {'file': (UPLOAD_FILE_NAME, file_content, 'text/plain')}


@pytest.fixture()
def upload_file():
    file_content = b'this is some test file content'
    return UploadFile(filename=UPLOAD_FILE_NAME, file=BytesIO(file_content))


@pytest.fixture()
async def create_file(async_client, headers, test_file):
    response = await async_client.post(
        f'{URL_PREFIX_FILE}/upload', headers=headers, files=test_file
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture()
async def create_files(async_client, headers, test_file):
    for file in FILES_FOR_COMPARISON:
        params = {'path': file['path'] + file['name']}
        response = await async_client.post(
            f'{URL_PREFIX_FILE}/upload',
            headers=headers,
            files=test_file,
            params=params,
        )
        assert response.status_code == status.HTTP_201_CREATED


def filter_files_result(files_result):
    path_and_name = []
    files_result.sort(key=lambda x: (x['path'], x['name']))
    for file in files_result:
        path_and_name.append(
            {k: v for k, v in file.items() if k in ('path', 'name')}
        )

    return path_and_name
