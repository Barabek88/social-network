"""Helper with jwt."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from fastapi import status

from app.core.exceptions import AppError
from app.resources import strings


def generate_jwt_token(
    token_data: dict, secret_key: str, algorithm: str, expiration_time: int = 3600
) -> str:
    """
    Generate a JWT token with the provided login and expiration time.

    Args:
        token_data: The token payload.
        algorithm: hash algorithm
        secret_key: The secret key used to sign the token.
        expiration_time: The expiration time of the token in seconds \
            (default is 1 hour).

    Returns:
        str: The generated JWT token.
    """

    payload = token_data.copy()
    payload.update(
        {"exp": datetime.now(timezone.utc) + timedelta(seconds=expiration_time)}
    )

    return jwt.encode(payload, secret_key, algorithm=algorithm)


def get_data_from_jwt_token(
    token: str, secret_key: str, algorithm: str
) -> Dict[str, Any]:
    """
    Decode data from a JWT token.

    Args:
        token: The token.
        algorithm: hash algorithm
        secret_key: The secret key used to sign the token.

    Raises:
        AppError: If token is expired or invalid.

    Returns:
        doct: The dict of the token data.
    """

    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise AppError(strings.TOKEN_EXPIRED, status.HTTP_401_UNAUTHORIZED)
    except jwt.PyJWTError:
        raise AppError(strings.TOKEN_INVALID, status.HTTP_401_UNAUTHORIZED)
