import pytest
from fastapi import status

from src.schemas.file import SearchOptions
from tests.conftest import (
    EXTENSION,
    FILES_SEARCH_IN_EXTENSION,
    FILES_SEARCH_IN_PATH,
    FILES_SEARCH_IN_QUERY,
    PATTERN,
    ROOT_PATH,
    TEST_USER,
    URL_PREFIX_AUTH,
    URL_PREFIX_FILE,
    filter_files_result,
)


@pytest.mark.anyio
async def test_add_user(async_client):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/register', json=TEST_USER
    )
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    assert user == {'id': 1, 'login': TEST_USER['login']}


@pytest.mark.anyio
async def test_search_files_in_path(async_client, headers, create_files):
    options = SearchOptions(path=ROOT_PATH).model_dump()

    response = await async_client.post(
        f'{URL_PREFIX_FILE}/search',
        headers=headers,
        json=options,
    )
    assert response.status_code == status.HTTP_200_OK
    path_and_name = filter_files_result(response.json())
    assert path_and_name == FILES_SEARCH_IN_PATH


@pytest.mark.anyio
async def test_search_files_in_extension(async_client, headers, create_files):
    options = SearchOptions(extension=EXTENSION).model_dump()

    response = await async_client.post(
        f'{URL_PREFIX_FILE}/search',
        headers=headers,
        json=options,
    )
    assert response.status_code == status.HTTP_200_OK
    path_and_name = filter_files_result(response.json())
    assert path_and_name == FILES_SEARCH_IN_EXTENSION


@pytest.mark.anyio
async def test_search_files_in_query(async_client, headers, create_files):
    options = SearchOptions(query=f'%{PATTERN}%').model_dump()

    response = await async_client.post(
        f'{URL_PREFIX_FILE}/search',
        headers=headers,
        json=options,
    )
    assert response.status_code == status.HTTP_200_OK
    path_and_name = filter_files_result(response.json())
    assert path_and_name == FILES_SEARCH_IN_QUERY
