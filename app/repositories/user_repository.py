from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User
from ..repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.get_by_field("username", username)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_by_field("email", email)
    
    async def get_with_roles(self, user_id: str) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        # Eager load roles
        if user and user.roles:
            _ = user.roles
        return user
    
    async def create_user(self, **kwargs) -> User:
        return await self.create(**kwargs)