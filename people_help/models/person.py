from datetime import date, datetime
from typing import Optional
from enum import Enum            # ✔ Correct Enum
from sqlmodel import SQLModel, Field
import uuid

class Sex(str, Enum):            # ✔ Python Enum (Pydantic compatible)
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class Person(SQLModel, table=True):
    __tablename__ = "person"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(nullable=False)
    birth: date = Field(nullable=False)
    sex: Sex = Field(nullable=False)
    profile: str = Field(default="default.png")
    phone_number: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


    @classmethod
    def from_dict(cls, data: dict):
        if isinstance(data.get("birth"), str):
            data["birth"] = datetime.strptime(data["birth"], "%Y-%m-%d").date()
        return cls(**data)