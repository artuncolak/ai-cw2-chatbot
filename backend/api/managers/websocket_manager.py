from uuid import UUID
from fastapi import WebSocket
from typing import Dict


class WebsocketManager:
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}

    async def connect(self, conversation_id: UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[conversation_id] = websocket

    async def disconnect(
        self,
        conversation_id: UUID,
        websocket: WebSocket,
        code: int = 1000,
        reason: str = "",
    ):
        self.active_connections.pop(conversation_id, None)
        await websocket.close(code=code, reason=reason)

    async def send_message(self, conversation_id: UUID, message: str):
        if conversation_id in self.active_connections:
            websocket = self.active_connections[conversation_id]
            await websocket.send_text(message)


websocket_manager = WebsocketManager()
