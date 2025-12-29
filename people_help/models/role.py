from typing import Optional
from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime

class Role(SQLModel, table=True):
    __tablename__ = "role"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(unique=True, nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)