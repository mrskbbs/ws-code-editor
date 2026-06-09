from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import getDb
from app.db.models.room_members import room_members_association_table as room_members
from app.db.models.room import Room
from app.db.models.user import User
from app.middleware.auth import authMiddleware
from app.schemas.rooms import RoomCreate, RoomEdit
from uuid import uuid4

rooms_router = APIRouter(prefix="/rooms", dependencies=[Depends(authMiddleware)])

@rooms_router.get("/")
async def getRooms(user: User = Depends(authMiddleware), db: AsyncSession = Depends(getDb)):
    await db.refresh(user, ["rooms"])
    return user.rooms

@rooms_router.post("/")
async def createRoom(data: RoomCreate, db: AsyncSession = Depends(getDb), user: User = Depends(authMiddleware)):
    room = await db.scalar(
        insert(Room)
        .values(
            title=data.title,
            invite_token=str(uuid4()),
            owner_id=user.id,
            language_id=data.language_id,
        )
        .returning(Room)
    )

    if not room:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            { "message": "Failed to create a room" }
        )

    await db.execute(
        insert(room_members)
        .values(
            room_id=room.id,
            user_id=user.id
        )
    )

    await db.commit()

    await db.refresh(room, ["members", "owner", "language"])

    return room

@rooms_router.get("/invite/{invite_token}")
async def roomInvite(invite_token: str, db: AsyncSession = Depends(getDb), user: User = Depends(authMiddleware)):
    room = (await db.execute(
        select(Room.id)
        .where(Room.invite_token == invite_token)
    )).one_or_none()
    
    if not room:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            { "message": "Invalid invite link" }
        )

    await db.execute(
        insert(room_members)
        .values(
            user_id=user.id,
            room_id=room.id,
        )
    )

    await db.commit()

    return { "message": f"Succesfully joined the room {room.id}" }


@rooms_router.get("/{id}")
async def getRoom(id: int, db: AsyncSession = Depends(getDb), user: User = Depends(authMiddleware)):
    is_member = await db.scalar(select(
        select(room_members.c.room_id)
        .where(
            room_members.c.user_id == user.id,
            room_members.c.room_id == id,
        ).exists()
    ))

    if not is_member:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            { "message": "Forbiden" }
        )

    room = await db.get(Room, id)

    if not room:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            { "message": "Room not found" }
        )

    return room

@rooms_router.put("/{id}")
async def editRoom(id: int, data: RoomEdit, db: AsyncSession = Depends(getDb)):
    edit_data: dict[str, str | int] = dict()
    if data.title: edit_data["title"] = data.title
    if data.language_id: edit_data["language_id"] = data.language_id

    if len(edit_data.values()) == 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            { "message": "Invalid payload" }
        )

    room = (await db.scalar(
        update(Room)
        .values(**edit_data)
        .where(Room.id == id)
        .returning(Room)
    ))

    if not room:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            { "message": "Failed to create a room" }
        )

    await db.commit()
    
    await db.refresh(room, ["members", "owner", "language"])

    return room

@rooms_router.delete("/{id}")
async def deleteRoom(id: int, user: User = Depends(authMiddleware), db: AsyncSession = Depends(getDb)):
    room = await db.get(Room, id)

    if not room:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND
        )

    await db.execute(
        delete(Room)
        .where(Room.id == id)
    )

    await db.commit()

    return { "message": "Succesfully deleted a room" }

# rooms_router.add_websocket_route("/{id}/ws", RoomsManagerWS)

