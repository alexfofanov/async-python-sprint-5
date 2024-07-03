from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import authenticate_user, create_access_token, hash_password
from src.core.config import app_settings
from src.db.db import get_session
from src.schemas.user import AccessToken, User, UserCreate, UserLogin
from src.services.user import user_crud

user_router = APIRouter()


@user_router.post(
    '/register',
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация',
    description='Создание нового пользователя',
)
async def register(
    *,
    db: AsyncSession = Depends(get_session),
    obj: UserCreate,
) -> Any:
    """
    Регистрация пользователя
    """

    user = await user_crud.get_user_by_login(db=db, login=obj.login)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists',
        )

    obj.password = hash_password(obj.password)
    user = await user_crud.create(db=db, obj=obj)
    return user


@user_router.post(
    '/auth',
    response_model=AccessToken,
    status_code=status.HTTP_200_OK,
    summary='Авторизация',
    description='Авторизация пользователя',
)
async def auth(
    *,
    db: AsyncSession = Depends(get_session),
    obj: UserLogin,
) -> Any:
    """
    Авторизация пользователя
    """

    user = await authenticate_user(
        db=db, login=obj.login, password=obj.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        seconds=app_settings.access_token_expire_seconds
    )
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return AccessToken(access_token=access_token, token_type="bearer")
