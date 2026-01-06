import httpx
from typing import List, Dict, Any
from uuid import UUID
from app.settings import settings
from app.logger import logger


class MessagesClient:
    def __init__(self):
        self.base_url = settings.MESSAGES_SERVICE_URL
        self.timeout = httpx.Timeout(10.0, connect=5.0)
    
    async def send_message(
        self, 
        user_id: UUID, 
        text: str, 
        token: str, 
        request_id: str
    ) -> Dict[str, Any]:
        """Send message to user via messages-service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/dialog/{user_id}/send",
                    json={"text": text},
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Request-ID": request_id
                    }
                )
                response.raise_for_status()
                logger.info(
                    f"request_id={request_id} | Message sent to {user_id} via messages-service"
                )
                return response.json()
            except httpx.HTTPError as e:
                logger.error(
                    f"request_id={request_id} | Failed to send message: {e}"
                )
                raise
    
    async def get_messages(
        self, 
        user_id: UUID, 
        token: str, 
        request_id: str
    ) -> List[Dict[str, Any]]:
        """Get conversation with user via messages-service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/dialog/{user_id}/list",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Request-ID": request_id
                    }
                )
                response.raise_for_status()
                logger.info(
                    f"request_id={request_id} | Retrieved messages from {user_id} via messages-service"
                )
                return response.json()
            except httpx.HTTPError as e:
                logger.error(
                    f"request_id={request_id} | Failed to get messages: {e}"
                )
                raise
