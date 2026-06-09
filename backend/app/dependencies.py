from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request, status
import jwt
from starlette.status import HTTP_404_NOT_FOUND
from app.config import JWT_KEY, JWT_ALGO
from app.db import getDb
from app.db.models.user import User
from app.db.models.room import Room
from app.db.models.room_members import room_members


async def getUser(req: Request, db: AsyncSession = Depends(getDb)):
    auth_token = req.cookies.get("auth_token")
    if not auth_token:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, 
            { "message": "Unauhtorized" }, 
        )

    try:
        payload = jwt.decode(
            auth_token, 
            JWT_KEY, 
            algorithms=[JWT_ALGO],
        )
    except:
        raise HTTPException(
           status.HTTP_401_UNAUTHORIZED, 
           { "message": "Unauhtorized, invalid token" }
        )

    user = await db.scalar(
        select(User)
        .where(User.id == payload.get("id"))
    )

    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            { "message": "Failed to authorize" },
        )

    return user

async def getRoom(room_id: int, db: AsyncSession = Depends(getDb)):
    room = await db.get(Room, room_id)

    if not room:
        raise HTTPException(HTTP_404_NOT_FOUND)

    return room

async def isRoomMember(room_id: int, user: User = Depends(getUser), db: AsyncSession = Depends(getDb)):
    is_member = await db.scalar(select(
        select(room_members.c.room_id)
        .where(
            room_members.c.user_id == user.id,
            room_members.c.room_id == room_id,
        ).exists()
    ))

    if not is_member:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            { "message": "Forbiden" }
        )

async def isRoomOwner(room: Room = Depends(getRoom), user: User = Depends(getUser)):
    if room.owner_id != user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            { "message": "Forbiden" }
        )
