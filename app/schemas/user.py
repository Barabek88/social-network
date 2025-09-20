from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from app.models.enums import Gender


class UserCreate(BaseModel):
    password: str
    first_name: str
    second_name: str
    birthdate: datetime
    biography: str | None = None
    city: str | None = None
    gender: Gender | None = None

    @field_validator("gender", mode="before")
    @classmethod
    def convert_gender(cls, v):
        if isinstance(v, str):
            return Gender(v.upper())
        return v


class UserRegisterResponse(BaseModel):
    user_id: str


class UserResponse(BaseModel):
    id: UUID
    first_name: str
    second_name: str
    birthdate: date
    biography: str | None = None
    city: str | None = None

    class Config:
        from_attributes = True
