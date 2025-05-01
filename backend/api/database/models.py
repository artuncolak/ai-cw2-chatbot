"""
Database models for the chat application
"""

from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field, Column, String
from typing import Optional


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


class Station(SQLModel, table=True):
    """Station model representing railway stations data"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    longname: Optional[str] = Field(default=None)
    alpha: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    code: str = Field(index=True)
    code_two: Optional[str] = Field(default=None)
    my_train_code: Optional[str] = Field(default=None)
    anglia_code: Optional[str] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
    national_rail_code: Optional[str] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
