from fastapi import APIRouter, Depends, Request
from uuid import UUID
from pydantic import BaseModel
from app.core.messages_client import MessagesClient
from app.core.dependencies import get_current_user
from app.core.jwt_token import get_token_from_request
from app.logger import logger


router = APIRouter(prefix="/dialog", tags=["Messages"])


class MessageCreate(BaseModel):
    text: str


def get_messages_client() -> MessagesClient:
    return MessagesClient()


@router.post("/{user_id}/send")
async def send_message(
    user_id: UUID,
    message: MessageCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    client: MessagesClient = Depends(get_messages_client),
):
    """Send message to user (proxied to messages-service)"""
    request_id = getattr(request.state, "request_id", "unknown")
    token = get_token_from_request(request)

    logger.info(
        f"request_id={request_id} | Proxying send message from {current_user['user_id']} to {user_id}"
    )

    return await client.send_message(user_id, message.text, token, request_id)


@router.get("/{user_id}/list")
async def get_messages(
    user_id: UUID,
    request: Request,
    current_user: dict = Depends(get_current_user),
    client: MessagesClient = Depends(get_messages_client),
):
    """Get conversation with user (proxied to messages-service)"""
    request_id = getattr(request.state, "request_id", "unknown")
    token = get_token_from_request(request)

    logger.info(
        f"request_id={request_id} | Proxying get messages for {current_user['user_id']} with {user_id}"
    )

    return await client.get_messages(user_id, token, request_id)
