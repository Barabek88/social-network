from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse, UserLogin
from app.core.security import verify_password
from app.core.jwt_token import generate_jwt_token
from app.settings import settings
from app.core.security import hash_password


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)

    async def login(self, credentials: UserLogin) -> LoginResponse | None:
        user = await self.user_repository.get_by_id_for_auth(credentials.id)

        password_valid = verify_password(
            credentials.password,
            (
                user["password"]
                if user
                else hash_password("dummy_password")  # for(prevents timing attacks)
            ),
        )

        if not user or not password_valid:
            return None

        token = generate_jwt_token(
            dict(
                user_id=str(user["id"]),
                first_name=user["first_name"],
                second_name=user["second_name"],
            ),
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
            settings.JWT_EXPIRATION_TIME,
        )

        return LoginResponse(token=token)
