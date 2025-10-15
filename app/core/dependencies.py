"""FastAPI dependencies for database sessions."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_manager import db_manager
from fastapi import Request, status
from app.core.exceptions import AppError
from app.resources import strings
from app.settings import settings
from app.core.jwt_token import get_data_from_jwt_token


async def get_write_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for write operations (master database)."""
    async for session in db_manager.get_write_session():
        yield session


async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for read operations (replica database)."""
    async for session in db_manager.get_read_session():
        yield session


async def get_current_user(request: Request) -> dict | None:
    authorization = request.headers.get("authorization")

    if not authorization or not authorization.startswith("Bearer "):
        raise AppError(strings.TOKEN_MISSING, status.HTTP_401_UNAUTHORIZED)

    token_parts = authorization.split(" ")

    if len(token_parts) != 2:
        raise AppError(strings.TOKEN_MISSING, status.HTTP_401_UNAUTHORIZED)
    token = token_parts[1]

    payload = get_data_from_jwt_token(
        token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
    )

    if not payload:
        raise AppError(strings.TOKEN_MISSING, status.HTTP_401_UNAUTHORIZED)

    return payload
