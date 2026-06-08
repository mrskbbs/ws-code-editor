from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import getDb
from app.db.models.room_members import room_members_association_table as room_members
from app.db.models.room import Room
from app.middleware.auth import AuthMiddleware
from uuid import uuid4

rooms_router = APIRouter(prefix="/rooms", dependencies=[Depends(AuthMiddleware)])

@rooms_router.get("/")
async def getRooms(req: Request, res: Response):
    return req.state.user.rooms

@rooms_router.post("/")
async def createRoom(data, req: Request, res: Response, db: AsyncSession = Depends(getDb)):
    room = await db.scalar(
        insert(Room)
        .values(
            title=data.title,
            invite_token=str(uuid4()),
            owner_id=req.state.user.id,
            language_id=data.language_id,
        )
        .returning(Room)
    )
    
    if not room:
        await db.rollback()
        raise HTTPException(
            500,
            { "message": "Failed to create a room" }
        )

    await db.commit()

    await db.refresh(room, ["members", "owner", "language"])

    return room

@rooms_router.get("/invite/{invite_token}")
async def roomInvite(invite_token: str, req: Request, res: Response, db: AsyncSession = Depends(getDb)):
    room = (await db.execute(
        select(Room.id)
        .where(Room.invite_token == invite_token)
    )).one_or_none()
    
    if not room:
        raise HTTPException(
            404,
            { "message": "Invalid invite link" }
        )

    await db.execute(
        insert(room_members)
        .values(
            user_id=req.state.user.id,
            room_id=room.id,
        )
    )

    await db.commit()

    return { "message": f"Succesfully joined the room {room.id}" }


@rooms_router.get("/{id}")
async def getRoom(id: int, req: Request, res: Response, db: AsyncSession = Depends(getDb)):
    is_member = await db.scalar(select(
        select(room_members.c.room_id)
        .where(
            room_members.c.user_id == req.state.user.id,
            room_members.c.room_id == id,
        ).exists()
    ))

    if not is_member:
        raise HTTPException(
            403,
            { "message": "Forbiden" }
        )

    return await db.get(Room, id)

@rooms_router.put("/{id}")
async def editRoom(id: int, data, req: Request, res: Response, db: AsyncSession = Depends(getDb)):
    room = (await db.scalar(
        update(Room)
        .where(Room.id == id)
        .returning(Room)
    ))

    if not room:
        await db.rollback()
        raise HTTPException(
            500,
            { "message": "Failed to create a room" }
        )

    await db.commit()
    
    await db.refresh(room, ["members", "owner", "language"])

    return room

@rooms_router.delete("/{id}")
async def deleteRoom(id: int, req: Request, res: Response, db: AsyncSession = Depends(getDb)):
    await db.execute(
        delete(Room)
        .where(Room.id == id)
    )

    return { "message": "Succesfully deleted a room" }

# rooms_router.add_websocket_route("/{id}/ws", RoomsManagerWS)

