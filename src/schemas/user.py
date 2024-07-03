from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class UserLogin(UserCreate):
    pass


class UserUpdate(BaseModel):
    password: str


class UserInDB(UserCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: int


class AccessToken(BaseModel):
    access_token: str
    token_type: str
