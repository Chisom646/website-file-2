from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime
from typing import List
import logging
import json

from ..config import get_db
from ..models.user import User
from ..models.community import Community, CommunityMember, ChatMessage
from ..routes.auth_routes import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, community_id: str):
        await websocket.accept()
        if community_id not in self.active_connections:
            self.active_connections[community_id] = []
        self.active_connections[community_id].append(websocket)
        logger.info(f"WebSocket connected to community {community_id}")

    def disconnect(self, websocket: WebSocket, community_id: str):
        if community_id in self.active_connections:
            self.active_connections[community_id].remove(websocket)
            logger.info(f"WebSocket disconnected from community {community_id}")

    async def broadcast(self, message: dict, community_id: str):
        if community_id in self.active_connections:
            for connection in self.active_connections[community_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to websocket: {e}")

manager = ConnectionManager()


# Pydantic models
class CommunityCreate(BaseModel):
    name: str
    description: str


class MessageCreate(BaseModel):
    message: str


# Community endpoints
@router.get("/communities")
async def list_communities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all communities with user's membership status."""
    # Get all communities
    result = await db.execute(select(Community))
    communities = result.scalars().all()

    # Get user's memberships
    member_result = await db.execute(
        select(CommunityMember.community_id).where(CommunityMember.user_id == current_user.id)
    )
    user_communities = {row for row in member_result.scalars().all()}

    # Get member counts for each community
    community_list = []
    for community in communities:
        count_result = await db.execute(
            select(func.count(CommunityMember.id)).where(CommunityMember.community_id == community.id)
        )
        member_count = count_result.scalar()

        community_list.append({
            "id": community.id,
            "name": community.name,
            "description": community.description,
            "is_default": community.is_default,
            "member_count": member_count,
            "is_member": community.id in user_communities,
            "created_at": community.created_at.isoformat()
        })

    return {"communities": community_list}


@router.post("/communities/{community_id}/join")
async def join_community(
    community_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Join a community."""
    # Check if community exists
    result = await db.execute(select(Community).where(Community.id == community_id))
    community = result.scalar_one_or_none()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Check if already a member
    member_result = await db.execute(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == current_user.id
        )
    )
    existing_member = member_result.scalar_one_or_none()
    if existing_member:
        raise HTTPException(status_code=400, detail="Already a member of this community")

    # Create membership
    membership = CommunityMember(
        community_id=community_id,
        user_id=current_user.id
    )
    db.add(membership)
    await db.commit()

    logger.info(f"User {current_user.username} joined community {community.name}")

    return {"message": "Successfully joined community", "community_id": community_id}


@router.post("/communities/{community_id}/leave")
async def leave_community(
    community_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave a community."""
    # Find membership
    result = await db.execute(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == current_user.id
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=400, detail="Not a member of this community")

    # Delete membership
    await db.delete(membership)
    await db.commit()

    logger.info(f"User {current_user.username} left community {community_id}")

    return {"message": "Successfully left community"}


@router.get("/communities/{community_id}/messages")
async def get_messages(
    community_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent messages from a community."""
    # Check if user is a member
    member_result = await db.execute(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == current_user.id
        )
    )
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Must be a member to view messages")

    # Get messages with user info
    result = await db.execute(
        select(ChatMessage, User).join(User, ChatMessage.user_id == User.id)
        .where(ChatMessage.community_id == community_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    rows = result.all()

    messages = []
    for message, user in reversed(rows):  # Reverse to get chronological order
        messages.append({
            "id": message.id,
            "user_id": message.user_id,
            "username": user.username,
            "message": message.message,
            "created_at": message.created_at.isoformat()
        })

    return {"messages": messages}


@router.websocket("/communities/{community_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    community_id: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket, community_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Extract user_id and message from the payload
            user_id = message_data.get("user_id")
            message_text = message_data.get("message")

            if not user_id or not message_text:
                continue

            # Verify user is a member
            member_result = await db.execute(
                select(CommunityMember).where(
                    CommunityMember.community_id == community_id,
                    CommunityMember.user_id == user_id
                )
            )
            if not member_result.scalar_one_or_none():
                await websocket.send_json({"error": "Not a member of this community"})
                continue

            # Save message to database
            chat_message = ChatMessage(
                community_id=community_id,
                user_id=user_id,
                message=message_text
            )
            db.add(chat_message)
            await db.commit()
            await db.refresh(chat_message)

            # Get username
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()

            # Broadcast message to all connected clients
            broadcast_message = {
                "id": chat_message.id,
                "user_id": user_id,
                "username": user.username if user else "Unknown",
                "message": message_text,
                "created_at": chat_message.created_at.isoformat()
            }
            await manager.broadcast(broadcast_message, community_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, community_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, community_id)
