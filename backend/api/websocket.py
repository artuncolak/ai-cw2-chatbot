"""
WebSocket
"""

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from websockets.exceptions import ConnectionClosedError

router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for chat functionality.

    The endpoint accepts WebSocket connections and maintains a persistent connection
    for real-time chat interaction with the AI chatbot.

    Args:
        websocket (WebSocket): The WebSocket connection instance
    """
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()

            chatbot = websocket.app.state.chatbot
            response = chatbot.get_response(message)

            await websocket.send_text(str(response))
    except WebSocketDisconnect:
        return
    except ConnectionClosedError:
        return
    except Exception as e:
        print(f"Unexpected error in websocket: {str(e)}")
        raise  # Re-raise unexpected exceptions for proper logging
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass
