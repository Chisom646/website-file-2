from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class Community(SQLModel, table=True):
    __tablename__ = "communities"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False, index=True)
    description: str = Field(nullable=False)
    is_default: bool = Field(default=False)  # True for the 3 default communities
    created_by: Optional[str] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CommunityMember(SQLModel, table=True):
    __tablename__ = "community_members"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    community_id: str = Field(foreign_key="communities.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # Unique constraint on community_id + user_id
        table_args = ({"postgresql_unique_constraint": ("community_id", "user_id")},)


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    community_id: str = Field(foreign_key="communities.id", nullable=False, index=True)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    message: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
