from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User as UserModel
from src.schemas.user import User, UserCreate, UserUpdate

from .base import RepositoryDB


class RepositoryUser(RepositoryDB[UserModel, UserCreate, UserUpdate]):
    async def get_user_by_login(
        self, db: AsyncSession, login: str
    ) -> User | None:
        """
        Получение пользователя по login
        """

        stmt = select(self._model).where(self._model.login == login)
        results = await db.execute(statement=stmt)
        return results.scalar_one_or_none()


user_crud = RepositoryUser(UserModel)
