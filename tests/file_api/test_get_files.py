import pytest
from fastapi import status

from tests.conftest import (
    FILES_FOR_COMPARISON,
    FILES_SEARCH_IN_PATH,
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
async def test_get_files_no_files(async_client, headers):
    response = await async_client.get(f'{URL_PREFIX_FILE}/', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    files = response.json()
    assert files == []


@pytest.mark.anyio
async def test_get_files_in_folder_no_files(async_client, headers):
    response = await async_client.get(
        f'{URL_PREFIX_FILE}/folder',
        headers=headers,
        params={'path': ROOT_PATH},
    )
    assert response.status_code == status.HTTP_200_OK
    files = response.json()
    assert files == []


@pytest.mark.anyio
async def test_get_files(async_client, headers, create_files):
    response = await async_client.get(f'{URL_PREFIX_FILE}/', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    path_and_name = filter_files_result(response.json())
    assert path_and_name == sorted(
        FILES_FOR_COMPARISON, key=lambda x: (x['path'], x['name'])
    )


@pytest.mark.anyio
async def test_get_files_in_folder(async_client, headers, create_files):
    response = await async_client.get(
        f'{URL_PREFIX_FILE}/folder',
        headers=headers,
        params={'path': ROOT_PATH},
    )
    assert response.status_code == status.HTTP_200_OK
    path_and_name = filter_files_result(response.json())
    assert path_and_name == sorted(FILES_SEARCH_IN_PATH, key=lambda x: (x['path'], x['name']))
