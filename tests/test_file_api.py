import pytest
from fastapi import status

from .conftest import FILE_NAME, TEST_USER, URL_PREFIX_AUTH, URL_PREFIX_FILE

FILE_PATH = 'test_file_path/'
FILE_PATH_WITH_FILE_NAME = FILE_PATH + FILE_NAME


@pytest.mark.anyio
async def test_add_user(async_client):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/register', json=TEST_USER
    )
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    assert user == {'id': 1, 'login': TEST_USER['login']}


@pytest.mark.anyio
async def test_file_upload_with_path(async_client, headers, test_file, create_test_backet):
    params = {'path': FILE_PATH_WITH_FILE_NAME}
    response = await async_client.post(
        f'{URL_PREFIX_FILE}/upload',
        headers=headers,
        params=params,
        files=test_file,
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result['name'] == FILE_NAME
    assert result['path'] == FILE_PATH_WITH_FILE_NAME


@pytest.mark.anyio
async def test_file_upload_without_path(async_client, headers, test_file, create_test_backet):
    response = await async_client.post(
        f'{URL_PREFIX_FILE}/upload', headers=headers, files=test_file
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result['name'] == FILE_NAME
    assert result['path'] == FILE_NAME


@pytest.mark.anyio
async def test_file_upload_with_path_without_filename(
    async_client, headers, test_file, create_test_backet
):
    params = {'path': FILE_PATH}
    response = await async_client.post(
        f'{URL_PREFIX_FILE}/upload',
        headers=headers,
        params=params,
        files=test_file,
    )
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result['name'] == FILE_NAME
    assert result['path'] == FILE_PATH + FILE_NAME


@pytest.mark.anyio
async def test_file_download_for_path(async_client, headers, create_file):
    params = {'path': create_file['path']}
    response = await async_client.get(
        f'{URL_PREFIX_FILE}/download',
        headers=headers,
        params=params,
    )
    assert response.status_code == status.HTTP_200_OK
