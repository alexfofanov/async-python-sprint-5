from sqlalchemy import Column, DateTime, Integer, String

from src.core.utils import naive_utcnow

from .base import Base


class User(Base):
    """
    Пользователь
    """

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        DateTime, nullable=False, index=True, default=naive_utcnow()
    )
