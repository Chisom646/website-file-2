from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
import re


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    phone_number: str
    birth: str  # Will be validated as date
    sex: str
    profile: Optional[str] = "default.png"
    
    @validator("phone_number")
    def validate_phone_number(cls, v):
        # Basic phone validation
        if not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError("Invalid phone number format")
        return v
    
    @validator("birth")
    def validate_birth(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Birth date must be in YYYY-MM-DD format")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []


class UserProfile(BaseModel):
    name: str
    birth: str
    sex: str
    phone_number: str
    profile: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse