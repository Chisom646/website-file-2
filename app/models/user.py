from typing import Optional
from sqlalchemy import Column, String
from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True, nullable=False))
    email: str = Field(sa_column=Column(String, unique=True, nullable=False))
    password_hash: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    person_id: Optional[str] = Field(default=None, foreign_key="person.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    