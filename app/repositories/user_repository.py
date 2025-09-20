from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.user import User
from app.schemas.user import UserCreate
from typing import Optional, List
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
            select id, first_name, second_name, birthdate, biography, city from users where id = :user_id
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
