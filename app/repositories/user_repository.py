from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.user import User
from app.schemas.user import UserCreate
from typing import List
from uuid import uuid4, UUID


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_with_raw_sql(
        self, user_data: UserCreate, hashed_password: str
    ) -> UUID:
        user_id = uuid4()

        query = text(
            """
            INSERT INTO users (id, password, first_name, second_name, birthdate, biography, city, gender)
            VALUES (:id, :password, :first_name, :second_name, :birthdate, :biography, :city, :gender)
            RETURNING id
        """
        )

        result = await self.db.execute(
            query,
            {
                "id": user_id,
                "password": hashed_password,
                "first_name": user_data.first_name,
                "second_name": user_data.second_name,
                "birthdate": user_data.birthdate,
                "biography": user_data.biography,
                "city": user_data.city,
                "gender": user_data.gender.value if user_data.gender else None,
            },
        )

        await self.db.commit()
        return result.scalar_one()

    async def get_by_id_with_raw_sql(self, user_id: UUID) -> dict | None:
        query = text(
            """
            select id, first_name, second_name, birthdate::date as birthdate, biography, city from users where id = :user_id
            """
        )
        result = await self.db.execute(query, {"user_id": user_id})
        row = result.mappings().fetchone()

        return dict(row) if row else None

    async def get_by_id_for_auth(self, user_id: UUID) -> dict | None:
        query = text(
            """
            SELECT id, password, first_name, second_name
            FROM users WHERE id = :user_id
            """
        )
        result = await self.db.execute(query, {"user_id": user_id})
        row = result.mappings().fetchone()
        return dict(row) if row else None

    async def search_users_with_raw_sql(
        self, first_name: str, second_name: str
    ) -> List[dict] | None:
        query = text(
            """
            SELECT id, first_name, second_name, birthdate::date as birthdate, biography, city
            FROM users
            WHERE lower(first_name) LIKE lower(:first_name) || '%' and lower(second_name) LIKE lower(:second_name) || '%'
            order by id
            """
        )

        result = await self.db.execute(
            query, {"first_name": first_name, "second_name": second_name}
        )

        rows = result.mappings().fetchall()
        return [dict(row) for row in rows] if rows else None

    async def get_friendship_raw_sql(
        self, current_user_id: UUID, friend_id: UUID
    ) -> dict | None:
        query = text(
            """
            SELECT user_id, friend_id, created_at
            FROM friends WHERE user_id = :user_id and friend_id = :friend_id and is_active = true
            """
        )
        result = await self.db.execute(
            query, {"user_id": current_user_id, "friend_id": friend_id}
        )
        row = result.mappings().fetchone()
        return dict(row) if row else None

    async def add_friend(self, current_user_id: UUID, friend_id: UUID):
        query = text(
            """
            INSERT INTO friends (user_id, friend_id, is_active, created_at)
            VALUES (:user_id, :friend_id, true, NOW())
            ON CONFLICT (user_id, friend_id) 
            DO UPDATE SET is_active = true, updated_at = NOW()
            """
        )

        await self.db.execute(
            query,
            {
                "user_id": current_user_id,
                "friend_id": friend_id,
            },
        )

        await self.db.commit()

    async def delete_friend(self, current_user_id: UUID, friend_id: UUID):
        query = text(
            """
            UPDATE friends 
            SET is_active = false, updated_at = NOW()
            WHERE user_id = :user_id AND friend_id = :friend_id
            """
        )

        await self.db.execute(
            query,
            {
                "user_id": current_user_id,
                "friend_id": friend_id,
            },
        )

        await self.db.commit()

    async def get_friends_list(self, user_id: UUID) -> List[dict] | None:
        query = text(
            """
            SELECT u.id, u.first_name, u.second_name, u.birthdate::date as birthdate, u.biography, u.city
            FROM friends f
            JOIN users u ON f.friend_id = u.id
            WHERE f.user_id = :user_id AND f.is_active = true
            ORDER BY u.first_name, u.second_name
            """
        )
        
        result = await self.db.execute(query, {"user_id": user_id})
        rows = result.mappings().fetchall()
        return [dict(row) for row in rows] if rows else None