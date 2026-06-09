from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import getDb
from app.db.models.room_members import room_members
from app.db.models.room import Room
from app.db.models.user import User
from app.dependencies import isRoomMember, isRoomOwner, isRoomMember, getRoom as getRoomDep, getUser
from app.schemas.rooms import RoomCreate, RoomEdit
from uuid import uuid4

rooms_router = APIRouter(prefix="/rooms", dependencies=[Depends(getUser)])

@rooms_router.get("/")
async def getRooms(user: User = Depends(getUser), db: AsyncSession = Depends(getDb)):
    await db.refresh(user, ["rooms"])

    return user.rooms

@rooms_router.post("/")
async def createRoom(data: RoomCreate, db: AsyncSession = Depends(getDb), user: User = Depends(getUser)):
    room = Room(
        title=data.title,
        invite_token=str(uuid4()),
        owner_id=user.id,
        language_id=data.language_id,
    )

    db.add(room)
    await db.flush()

    await db.execute(
        insert(room_members)
        .values(
            user_id=user.id,
            room_id=room.id,
        )
    )

    await db.commit()
    await db.refresh(room, ["members", "owner", "language"])

    return room

@rooms_router.get("/invite/{invite_token}")
async def roomInvite(invite_token: str, db: AsyncSession = Depends(getDb), user: User = Depends(getUser)):
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


@rooms_router.get("/{room_id}", dependencies=[Depends(isRoomMember)])
async def getRoom(room: Room = Depends(getRoomDep), db: AsyncSession = Depends(getDb)):
    await db.refresh(room, ["members", "language", "owner"])

    return room

@rooms_router.put("/{room_id}", dependencies=[Depends(isRoomOwner)])
async def editRoom(data: RoomEdit, room: Room = Depends(getRoomDep), db: AsyncSession = Depends(getDb)):

    if data.title: room.title = data.title
    if data.language_id: room.language_id = data.language_id
    
    await db.commit()
    await db.refresh(room, ["members", "language", "owner"])

    return room

@rooms_router.delete("/{room_id}", dependencies=[Depends(isRoomOwner)])
async def deleteRoom(room: Room = Depends(getRoomDep), db: AsyncSession = Depends(getDb)):
    await db.delete(room)
    await db.commit()

    return { "message": "Succesfully deleted a room" }

# rooms_router.add_websocket_route("/{id}/ws", RoomsManagerWS)

