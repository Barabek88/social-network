"""Base exception class for the app."""

from fastapi import status


class AppError(Exception):
    def __init__(self, name: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.description = name
        self.status_code = status_code
