from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FileBase(BaseModel):
    name: str


class FileCreate(BaseModel):
    user_id: int
    name: str
    path: str
    size: int


class FileInDB(FileCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileUpdate:
    pass
