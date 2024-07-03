import pytest
from fastapi import status

from .conftest import TEST_USER, URL_PREFIX_AUTH


@pytest.mark.anyio
async def test_add_user(async_client):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/register', json=TEST_USER
    )
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    assert user == {'id': 1, 'login': TEST_USER['login']}


@pytest.mark.anyio
async def test_add_user_exist(async_client):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/register', json=TEST_USER
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_user_auth_correct(async_client):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_user_auth_wrong_login(async_client):
    TEST_USER['login'] = 'wrong_login'
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_user_auth_wrong_password(async_client):
    TEST_USER['password'] = 'wrong_password'
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
