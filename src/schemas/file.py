from datetime import datetime
from typing import Optional
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


class SearchOptions(BaseModel):
    path: Optional[str] = None
    extension: Optional[str] = None
    order_by: Optional[str] = None
    limit: Optional[int] = None
    query: Optional[str] = None
