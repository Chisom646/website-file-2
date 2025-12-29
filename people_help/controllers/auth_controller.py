from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import get_db
from ..schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    LoginResponse,
    RegisterResponse,
    UserProfile
)
from ..services.auth_service import AuthService
from ..utils.exceptions import InvalidCredentialsException
from ..dependencies.auth import get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    
    # Register user
    user = await auth_service.register_user(user_data)
    
    # Get user with roles
    user_with_roles = await auth_service.get_user_profile(user.id)
    
    # Prepare response
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        name=user_data.name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user_with_roles["roles"]]
    )
    
    return RegisterResponse(
        message="User registered successfully",
        user=user_response
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    
    # Authenticate user
    authenticated, user = await auth_service.authenticate_user(
        login_data.username,
        login_data.password
    )
    
    if not authenticated or not user:
        raise InvalidCredentialsException()
    
    # Create access token
    access_token = await auth_service.create_access_token(user)
    
    # Get user profile
    user_profile = await auth_service.get_user_profile(user.id)
    
    # Prepare response
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        name=user_profile["person"].name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user_profile["roles"]]
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    user_profile = await auth_service.get_user_profile(current_user.id)
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        name=user_profile["person"].name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        roles=[role.name for role in user_profile["roles"]]
    )


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    user_profile = await auth_service.get_user_profile(current_user.id)
    
    person = user_profile["person"]
    
    return UserProfile(
        name=person.name,
        birth=str(person.birth),
        sex=person.sex,
        phone_number=person.phone_number,
        profile=person.profile
    )


@router.post("/logout")
async def logout():
    # In JWT, logout is client-side by removing the token
    return {"message": "Successfully logged out"}


@router.get("/check-username/{username}")
async def check_username_availability(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    existing_user = await auth_service.user_repo.get_by_username(username)
    
    return {
        "available": existing_user is None,
        "username": username
    }


@router.get("/check-email/{email}")
async def check_email_availability(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    existing_user = await auth_service.user_repo.get_by_email(email)
    
    return {
        "available": existing_user is None,
        "email": email
    }