from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRegisterResponse, UserResponse
from app.core.security import hash_password
from uuid import UUID
from app.core.exceptions import AppError
from app.resources import strings
from fastapi import status
from app.schemas.post import PostCreate, PostResponse, PostUpdate


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

    async def add_friend(self, current_user_id: UUID, friend_id: UUID):
        # Check if trying to add self
        if current_user_id == friend_id:
            raise AppError(
                strings.FRIEND_AND_USER_THE_SAME_ERROR_MSG, status.HTTP_400_BAD_REQUEST
            )

        # Check if friend exists
        friend = await self.repository.get_by_id_with_raw_sql(friend_id)
        if not friend:
            raise AppError(strings.NOT_FOUND_USER_ERROR_MSG, status.HTTP_404_NOT_FOUND)

        # Add friend (upsert handles existing friendships)
        await self.repository.add_friend(current_user_id, friend_id)

    async def delete_friend(self, current_user_id: UUID, friend_id: UUID):
        # Check if friendship exists
        existing_friendship = await self.repository.get_friendship_raw_sql(
            current_user_id, friend_id
        )
        if not existing_friendship:
            raise AppError(
                strings.NOT_FOUND_FRIEND_ERROR_MSG, status.HTTP_404_NOT_FOUND
            )

        # Delete friend
        await self.repository.delete_friend(current_user_id, friend_id)

    async def get_friends_list(self, user_id: UUID) -> list[UserResponse] | None:
        db_friends = await self.repository.get_friends_list(user_id)
        if db_friends:
            return [UserResponse.model_validate(friend) for friend in db_friends]
        return None

    async def create_post(self, post_data: PostCreate, user_id: UUID) -> UUID | None:
        user = await self.repository.get_by_id_with_raw_sql(user_id)
        if not user:
            raise AppError(strings.NOT_FOUND_USER_ERROR_MSG, status.HTTP_404_NOT_FOUND)

        return await self.repository.create_post(post_data, user_id)

    async def update_post(self, post_data: PostUpdate, user_id: UUID):
        post = await self.repository.get_post_by_id(post_data.id)

        if not post:
            raise AppError(strings.NOT_FOUND_POST_ERROR_MSG, status.HTTP_404_NOT_FOUND)

        if str(post["author_user_id"]) != user_id:
            raise AppError(strings.NOT_OWNER_POST_ERROR_MSG, status.HTTP_403_FORBIDDEN)

        await self.repository.update_post(post_data)

    async def delete_post(self, post_id: UUID, user_id: UUID):
        post = await self.repository.get_post_by_id(post_id)

        if not post:
            raise AppError(strings.NOT_FOUND_POST_ERROR_MSG, status.HTTP_404_NOT_FOUND)

        if str(post["author_user_id"]) != user_id:
            raise AppError(strings.NOT_OWNER_POST_ERROR_MSG, status.HTTP_403_FORBIDDEN)

        await self.repository.delete_post(post_id)

    async def get_post(self, post_id: UUID) -> PostResponse | None:
        post = await self.repository.get_post_by_id(post_id)

        if post:
            return PostResponse.model_validate(post)

        return None

    async def get_posts_feed(
        self, user_id: UUID, offset: int, limit: int
    ) -> list[PostResponse] | None:
        db_posts = await self.repository.get_posts_feed(user_id, offset, limit)
        if db_posts:
            return [PostResponse.model_validate(post) for post in db_posts]

        return None
