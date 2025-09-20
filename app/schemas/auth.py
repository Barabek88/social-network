from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from app.models.enums import Gender


class UserLogin(BaseModel):
    id: UUID
    password: str


class LoginResponse(BaseModel):
    token: str
