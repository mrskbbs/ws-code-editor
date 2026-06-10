from typing import Annotated
from fastapi import APIRouter, Depends

from app.dependencies.rooms import isRoomMember, isRoomOwner, isRoomMember, RoomDep 
from app.dependencies.users import getUser, UserDep
from app.services.rooms import *
from app.schemas.rooms import RoomCreate, RoomEdit
from app.ws.endpoint import wsRoomEndpoint

rooms_router = APIRouter(prefix="/rooms")

ServiceDep = Annotated[RoomService, Depends(getRoomService)]

@rooms_router.get("/", dependencies=[Depends(getUser)])
async def getRooms(user: UserDep, service: ServiceDep):
    return await service.getRooms(user)

@rooms_router.post("/", dependencies=[Depends(getUser)])
async def createRoom(data: RoomCreate, user: UserDep, service: ServiceDep):
    return await service.createRoom(data, user)

@rooms_router.get("/invite/{invite_token}", dependencies=[Depends(getUser)])
async def roomInvite(invite_token: str, user: UserDep, service: ServiceDep):
    return await service.roomInvite(invite_token, user)

@rooms_router.get("/{room_id}", dependencies=[Depends(isRoomMember), Depends(getUser)])
async def getRoom(room: RoomDep, service: ServiceDep):
    return await service.getRoom(room)

@rooms_router.put("/{room_id}", dependencies=[Depends(isRoomOwner), Depends(getUser)])
async def editRoom(data: RoomEdit, room: RoomDep, service: ServiceDep):
    return await service.editRoom(data, room)

@rooms_router.delete("/{room_id}", dependencies=[Depends(isRoomOwner), Depends(getUser)])
async def deleteRoom(room: RoomDep, service: ServiceDep):
    return await service.deleteRoom(room)

rooms_router.add_api_websocket_route("/{id}/ws", wsRoomEndpoint)
