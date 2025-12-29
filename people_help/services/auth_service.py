from datetime import timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..models.role import Role
from ..models.user_role import UserRole
from ..repositories.user_repository import UserRepository
from ..repositories.person_repository import PersonRepository
from ..schemas.auth import UserCreate, UserLogin
from ..utils.security import password_hasher, jwt_manager
from ..utils.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    InactiveUserException,
    UserNotFoundException
)
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.person_repo = PersonRepository(session)
    
    async def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[User]]:
        user = await self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            return False, None
        
        if not password_hasher.verify_password(password, user.password_hash):
            return False, None
        
        return True, user
    
    async def register_user(self, user_data: UserCreate) -> User:
        # Check if username exists
        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise UserAlreadyExistsException("username")
        
        # Check if email exists
        existing_email = await self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise UserAlreadyExistsException("email")
        
        try:
            # Create person
            person = await self.person_repo.create_person(
                name=user_data.name,
                birth=user_data.birth,
                sex=user_data.sex,
                phone_number=user_data.phone_number,
                profile=user_data.profile
            )
            
            # Create user with hashed password
            password_hash = password_hasher.get_password_hash(user_data.password)
            user = await self.user_repo.create_user(
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                person_id=person.id
            )
            
            # Assign default "user" role
            role_query = select(Role).where(Role.name == "user")
            result = await self.session.execute(role_query)
            default_role = result.scalar_one_or_none()
            
            if default_role:
                user_role = UserRole(user_id=user.id, role_id=default_role.id)
                self.session.add(user_role)
            
            await self.session.commit()
            return user
            
        except Exception:
            await self.session.rollback()
            raise
    
    async def create_access_token(self, user: User) -> str:
        token_data = {"sub": user.id, "username": user.username}
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt_manager.create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        return access_token
    
    async def get_current_user(self, token: str) -> Optional[User]:
        payload = jwt_manager.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await self.user_repo.get_with_roles(user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    async def get_user_profile(self, user_id: str) -> dict:
        user = await self.user_repo.get_with_roles(user_id)
        if not user:
            raise UserNotFoundException()
        
        return {
            "user": user,
            "person": user.person,
            "roles": user.roles
        }


async def initialize_default_roles(session: AsyncSession):
    """Initialize default roles in the database"""
    default_roles = [
        {"name": "admin", "description": "Administrator with full access"},
        {"name": "user", "description": "Regular user"},
        {"name": "moderator", "description": "Content moderator"}
    ]
    
    for role_data in default_roles:
        result = await session.execute(
            select(Role).where(Role.name == role_data["name"])
        )
        existing_role = result.scalar_one_or_none()
        
        if not existing_role:
            role = Role(**role_data)
            session.add(role)
    
    await session.commit()