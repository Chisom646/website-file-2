from sqlmodel import SQLModel, Field
from datetime import datetime

class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    
    user_id: str = Field(primary_key=True, foreign_key="users.id")
    role_id: str = Field(primary_key=True, foreign_key="role.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    