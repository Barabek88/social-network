from fastapi import WebSocket
from typing import Dict, Set
from uuid import UUID
from app.logger import logger


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: UUID):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_post_to_user(self, user_id: UUID, post_data: dict):
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(post_data)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.add(connection)

            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast_post_to_friends(self, friend_ids: list[UUID], post_data: dict):
        for friend_id in friend_ids:
            await self.send_post_to_user(friend_id, post_data)


ws_manager = WebSocketManager()
