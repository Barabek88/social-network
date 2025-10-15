"""Endpoint auth."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import LoginResponse, UserLogin
from app.core.dependencies import get_read_db
from app.services.auth_service import AuthService
from app.logger import logger
from app.core.exceptions import AppError
from app.resources import strings

router = APIRouter(tags=["Auth"])


async def get_auth_service(db: AsyncSession = Depends(get_read_db)) -> AuthService:
    return AuthService(db)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: UserLogin, service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    logger.info(f"user_id: {credentials.id}")

    login_response = await service.login(credentials)
    if not login_response:
        raise AppError(strings.PASS_OR_LOGIN_ERROR_MSG, status.HTTP_401_UNAUTHORIZED)
    return login_response
