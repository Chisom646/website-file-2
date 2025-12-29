from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import get_db
from ..services.auth_service import AuthService
from ..utils.exceptions import InvalidTokenException, InactiveUserException

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise InvalidTokenException()
    
    if not user.is_active:
        raise InactiveUserException()
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    return current_user


async def require_admin(current_user = Depends(get_current_user)):
    role_names = [role.name for role in current_user.roles]
    if "admin" not in role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user