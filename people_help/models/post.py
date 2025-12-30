from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    content: str = Field(nullable=False)
    community_id: Optional[str] = Field(default=None, foreign_key="communities.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
