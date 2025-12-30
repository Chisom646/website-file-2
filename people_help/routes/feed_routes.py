from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
import logging

from ..config import get_db
from ..models.user import User
from ..models.post import Post
from ..models.community import CommunityMember
from ..routes.auth_routes import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class PostCreate(BaseModel):
    content: str
    community_id: Optional[str] = None


class PostResponse(BaseModel):
    id: str
    user_id: str
    username: str
    content: str
    community_id: Optional[str]
    created_at: str
    can_delete: bool


# Feed endpoints
@router.post("/posts")
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new post."""
    # If posting to a community, verify membership
    if data.community_id:
        member_result = await db.execute(
            select(CommunityMember).where(
                CommunityMember.community_id == data.community_id,
                CommunityMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(
                status_code=403,
                detail="Must be a member to post in this community"
            )

    # Create post
    post = Post(
        user_id=current_user.id,
        content=data.content,
        community_id=data.community_id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)

    logger.info(f"Post created by {current_user.username} (ID: {post.id})")

    return {
        "id": post.id,
        "user_id": post.user_id,
        "username": current_user.username,
        "content": post.content,
        "community_id": post.community_id,
        "created_at": post.created_at.isoformat(),
        "can_delete": True  # User just created it
    }


@router.get("/posts")
async def get_feed(
    community_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get feed posts (general or community-specific)."""
    # Build query
    query = select(Post, User).join(User, Post.user_id == User.id)

    if community_id:
        # Community feed - verify membership
        member_result = await db.execute(
            select(CommunityMember).where(
                CommunityMember.community_id == community_id,
                CommunityMember.user_id == current_user.id
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(
                status_code=403,
                detail="Must be a member to view community posts"
            )
        query = query.where(Post.community_id == community_id)
    else:
        # General feed - only posts without community_id
        query = query.where(Post.community_id.is_(None))

    # Execute query with pagination
    query = query.order_by(Post.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    rows = result.all()

    # Format response
    posts = []
    for post, user in rows:
        posts.append({
            "id": post.id,
            "user_id": post.user_id,
            "username": user.username,
            "content": post.content,
            "community_id": post.community_id,
            "created_at": post.created_at.isoformat(),
            "can_delete": post.user_id == current_user.id  # Only author can delete
        })

    return {"posts": posts, "count": len(posts)}


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a post (only author or admin can delete)."""
    # Find post
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check permissions - only author can delete (admin check can be added later)
    if post.user_id != current_user.id:
        # Check if user is admin
        from ..models.role import Role
        from ..models.user_role import UserRole

        role_result = await db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == current_user.id, Role.name == "admin")
        )
        is_admin = role_result.scalar_one_or_none() is not None

        if not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Only the post author or admins can delete posts"
            )

    # Delete post
    await db.delete(post)
    await db.commit()

    logger.info(f"Post {post_id} deleted by {current_user.username}")

    return {"message": "Post deleted successfully"}
