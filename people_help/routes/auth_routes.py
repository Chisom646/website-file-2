from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, validator
from datetime import timedelta
import uuid
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..config import get_db
from ..utils.security import get_password_hash, verify_password, create_access_token, verify_token
from ..models.user import User
from ..models.person import Person
from ..models.role import Role
from ..models.user_role import UserRole

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Rate limiter for sensitive endpoints
limiter = Limiter(key_func=get_remote_address)

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
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
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
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Registration attempt for username: {data.username}")
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
        logger.info(f"User registered successfully: {user.username} (ID: {user.id})")

        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Registration error for {data.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    logger.info(f"Login attempt for username: {data.username}")

    # Find user
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Login failed: user not found - {data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Truncate password if necessary before verifying
    password_to_verify = truncate_password_to_bytes(data.password)
    if not verify_password(password_to_verify, user.password_hash):
        logger.warning(f"Login failed: invalid password - {data.username}")
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

    logger.info(f"Login successful for user: {user.username} (ID: {user.id})")

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "name": person.name if person else user.username,
        "roles": [role.name for role in roles]
    }
# Dependency to get current user from JWT token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and verify JWT token, return current user."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user

@router.get("/auth/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's profile with person details and roles."""
    # Get person details
    person_result = await db.execute(
        select(Person).where(Person.id == current_user.person_id)
    )
    person = person_result.scalar_one_or_none()
    
    # Get roles
    roles_result = await db.execute(
        select(Role)
        .join(UserRole, Role.id == UserRole.role_id)
        .where(UserRole.user_id == current_user.id)
    )
    roles = roles_result.scalars().all()
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "name": person.name if person else current_user.username,
        "birth": str(person.birth) if person else None,
        "sex": person.sex if person else None,
        "phone_number": person.phone_number if person else None,
        "created_at": current_user.created_at.isoformat(),
        "roles": [role.name for role in roles]
    }

@router.get("/auth/check-username/{username}")
async def check_username(username: str, db: AsyncSession = Depends(get_db)):
    """Check if username is available."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    return {"available": user is None}

@router.get("/auth/check-email/{email}")
async def check_email(email: str, db: AsyncSession = Depends(get_db)):
    """Check if email is available."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    return {"available": user is None}
