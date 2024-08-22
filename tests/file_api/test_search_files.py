import pytest
from fastapi import status

from src.schemas.file import SearchOptions
from tests.conftest import (
    ROOT_PATH,
    TEST_USER,
    URL_PREFIX_AUTH,
    URL_PREFIX_FILE,
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
async def test_search_files(async_client, headers):
    options = SearchOptions(path=ROOT_PATH).dict()

    response = await async_client.post(
        f'{URL_PREFIX_FILE}/search',
        headers=headers,
        json=options,
    )
    files = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert files == []
