import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from src.core.utils import naive_utcnow

from .base import Base


class File(Base):
    """
    Файл
    """

    __tablename__ = 'file'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    name = Column(String, nullable=False)

    path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=naive_utcnow()
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'path', 'name', name='_user_path_name_uc'),
    )
