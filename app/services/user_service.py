from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRegisterResponse, UserResponse
from typing import Optional
from app.core.security import hash_password
from uuid import UUID


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, user_data: UserCreate) -> UserRegisterResponse:
        hashed_password = hash_password(user_data.password)
        user_id = await self.repository.create_with_raw_sql(user_data, hashed_password)
        return UserRegisterResponse(user_id=str(user_id))

    async def get_user_by_id(self, user_id: UUID) -> UserResponse | None:
        db_user = await self.repository.get_by_id_with_raw_sql(user_id)
        if db_user:
            return UserResponse.model_validate(db_user)

        return None

    async def search_users(
        self, first_name: str, second_name: str
    ) -> list[UserResponse] | None:
        db_users = await self.repository.search_users_with_raw_sql(
            first_name, second_name
        )
        if db_users:
            return [UserResponse.model_validate(user) for user in db_users]

        return None
