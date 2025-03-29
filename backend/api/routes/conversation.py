"""
Conversation routes
"""

from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlmodel import Session, delete, select
from websockets.exceptions import ConnectionClosedError

from ..database import Message, Conversation, get_session

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("")
def create_conversation(session: Session = Depends(get_session)) -> Conversation:
    """Create a new conversation"""
    conversation = Conversation()
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@router.get("")
def get_conversations(session: Session = Depends(get_session)):
    """Get all conversations"""
    return session.exec(select(Conversation)).all()


@router.get("/{conversation_id}")
def get_conversation(conversation_id: UUID, session: Session = Depends(get_session)):
    """Get all messages in a conversation"""

    conversation = session.exec(
        select(Conversation).where(Conversation.id == conversation_id)
    ).first()

    if not conversation:
        return {"message": "Conversation not found"}

    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
    ).all()


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: UUID, session: Session = Depends(get_session)):
    """Delete a conversation and its messages"""

    # Delete the conversation
    conversation = session.exec(
        select(Conversation).where(Conversation.id == conversation_id)
    ).first()

    if not conversation:
        return {"message": "Conversation not found"}

    # Delete all messages in the conversation
    session.exec(delete(Message).where(Message.conversation_id == conversation_id))

    session.delete(conversation)
    session.commit()
    return {"message": "Conversation deleted successfully"}


@router.websocket("/{conversation_id}")
async def conversation_websocket(websocket: WebSocket, conversation_id: UUID):
    """Handle WebSocket connections for chat functionality.

    The endpoint accepts WebSocket connections and maintains a persistent connection
    for real-time chat interaction with the AI chatbot.

    Args:
        websocket (WebSocket): The WebSocket connection instance
        conversation_id (UUID): The ID of the conversation to connect to
    """
    print(f"Attempting to connect with conversation_id: {conversation_id}")
    await websocket.accept()

    # Get existing conversation
    session = next(get_session())
    conversation = session.get(Conversation, conversation_id)

    if not conversation:
        await websocket.close(code=4004, reason="Conversation not found")
        return

    try:
        while True:
            message = await websocket.receive_text()

            # Store user message
            user_message = Message(
                conversation_id=conversation.id, content=message, is_bot=False
            )
            session.add(user_message)

            # Get chatbot response
            chatbot = websocket.app.state.chatbot
            response = chatbot.get_response(message)

            # Store bot response
            bot_message = Message(
                conversation_id=conversation.id, content=str(response), is_bot=True
            )
            session.add(bot_message)
            session.commit()

            await websocket.send_text(str(response))

    except WebSocketDisconnect:
        session.commit()
        return
    except ConnectionClosedError:
        session.commit()
        return
    except Exception as e:
        print(f"Unexpected error in websocket: {str(e)}")
        raise
    finally:
        session.close()
        try:
            await websocket.close()
        except RuntimeError:
            pass
