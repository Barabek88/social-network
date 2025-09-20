"""Provides dependency for service."""

from fastapi import Depends, Request, status

from app.core.exceptions import AppError
from app.resources import strings
from app.settings import settings
from app.core.jwt_token import get_data_from_jwt_token


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
