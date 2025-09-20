from sqlalchemy import String, DateTime, Boolean, text as sa_text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.core.database import Base
from uuid import uuid4, UUID as PyUUID
from enum import Enum as PyEnum
from sqlalchemy import Enum
from app.models.enums import Gender


class User(Base):
    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    password: Mapped[str] = mapped_column(String(200))
    first_name: Mapped[str] = mapped_column(String)
    second_name: Mapped[str] = mapped_column(String)
    birthdate: Mapped[datetime] = mapped_column(DateTime)
    biography: Mapped[Optional[str]] = mapped_column(String)
    city: Mapped[Optional[str]] = mapped_column(String)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=sa_text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
