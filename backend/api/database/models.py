"""
Database models for the chat application
"""

from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field


class Message(SQLModel, table=True):
    """Message model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    content: str
    is_bot: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """Conversation model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
