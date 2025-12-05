from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.websocket_manager import ws_manager
from app.core.jwt_token import get_data_from_jwt_token
from app.logger import logger
from uuid import UUID
from app.settings import settings

router = APIRouter(tags=["WebSocket"])


@router.websocket("/post/feed/posted")
async def websocket_post_feed(websocket: WebSocket, token: str = Query(...)):
    user_id = None
    try:
        payload = get_data_from_jwt_token(
            token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
        user_id = UUID(payload["user_id"])

        await ws_manager.connect(websocket, user_id)

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        if user_id:
            ws_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user_id:
            ws_manager.disconnect(websocket, user_id)
