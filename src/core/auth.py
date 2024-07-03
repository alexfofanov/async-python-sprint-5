from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import app_settings
from src.db.db import get_session
from src.schemas.user import User
from src.services.user import user_crud

ALGORITHM = 'HS256'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')


def hash_password(password: str) -> str:
    """
    Хеширование пароля
    """

    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Проверка пароля
    """

    return pwd_context.verify(password, hashed_password)


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """
    Создание токена
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, app_settings.secret_key, algorithm=ALGORITHM
    )

    return encoded_jwt


async def authenticate_user(
    db: AsyncSession,
    login: str,
    password: str,
) -> bool | User:
    """
    Аутентификация пользователя по имени и паролю
    """

    user = await user_crud.get_user_by_login(db=db, login=login)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> User:
    """
    Получение пользователя из токена
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, app_settings.secret_key, algorithms=[ALGORITHM]
        )
        login: str = payload.get('sub')
        if login is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await user_crud.get_user_by_login(db=db, login=login)

    if user is None:
        raise credentials_exception

    return user
