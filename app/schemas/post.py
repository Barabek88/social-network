from pydantic import BaseModel
from uuid import UUID


class PostCreate(BaseModel):
    text: str


class PostUpdate(BaseModel):
    id: str
    text: str


class PostResponse(BaseModel):
    id: UUID
    text: str
    author_user_id: UUID

    class Config:
        from_attributes = True
