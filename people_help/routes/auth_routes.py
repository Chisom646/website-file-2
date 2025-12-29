from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, validator
from datetime import timedelta
import uuid
from ..config import get_db
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..models.user import User
from ..models.person import Person
from ..models.role import Role
from ..models.user_role import UserRole

router = APIRouter()

MAX_PASSWORD_BYTES = 72  # bcrypt and PostgreSQL max bytes

def truncate_password_to_bytes(password: str) -> str:
    """Truncate password to 72 bytes for bcrypt/PostgreSQL compatibility."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > MAX_PASSWORD_BYTES:
        # Truncate to 72 bytes
        password_bytes = password_bytes[:MAX_PASSWORD_BYTES]
        # Try to decode back, ignoring any incomplete characters
        return password_bytes.decode('utf-8', 'ignore')
    return password

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    name: str
    phone_number: str
    birth: str
    sex: str
    
    @validator('password')
    def validate_password_length(cls, v):
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > MAX_PASSWORD_BYTES:
            raise ValueError(
                f"Password is too long. Maximum is {MAX_PASSWORD_BYTES} bytes "
                f"(approx {MAX_PASSWORD_BYTES} ASCII characters or fewer for Unicode)"
            )
        return v
    
    @validator('username')
    def validate_username_length(cls, v):
        if len(v) > 50:  # Assuming your User model has VARCHAR(50)
            raise ValueError("Username must be 50 characters or less")
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Check if username exists
        result = await db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email exists
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Prepare person instance
        person = Person.from_dict({
            "name": data.name,
            "birth": data.birth,
            "sex": data.sex,
            "phone_number": data.phone_number
        })
        db.add(person)
        await db.flush()
        
        # Hash password (already validated to be ≤ 72 bytes)
        hashed_password = get_password_hash(data.password)
        
        # Create user
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hashed_password,
            person_id=person.id
        )
        db.add(user)
        await db.flush()
        
        # Get or create default role
        result = await db.execute(select(Role).where(Role.name == "user"))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(name="user", description="Regular user")
            db.add(role)
            await db.flush()
        
        # Assign role
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)
        
        await db.commit()
        
        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Find user
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Truncate password if necessary before verifying
    password_to_verify = truncate_password_to_bytes(data.password)
    if not verify_password(password_to_verify, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get user roles
    result = await db.execute(
        select(Role)
        .join(UserRole, Role.id == UserRole.role_id)
        .where(UserRole.user_id == user.id)
    )
    roles = result.scalars().all()
    
    # Create token
    token = create_access_token(
        data={
            "sub": user.id,
            "username": user.username,
            "roles": [role.name for role in roles]
        },
        expires_delta=timedelta(minutes=30)
    )
    
    # Get person info
    result = await db.execute(select(Person).where(Person.id == user.person_id))
    person = result.scalar_one_or_none()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "name": person.name if person else user.username,
        "roles": [role.name for role in roles]
    }