from typing import Any
from fastapi import WebSocketException, status
from app.db.models.room import Room
from app.schemas.ws import WSRoomConnection
from app.ws.room import WSRoom

class WSRoomManager():

    def __init__(self):
        self.rooms: dict[int, WSRoom] = dict()

    def removeRoom(self, room: Room):
        if room.id not in self.rooms.keys(): 
            raise WebSocketException(status.WS_1011_INTERNAL_ERROR)

        self.rooms.pop(room.id)

    async def connect(self, room: Room, conn: WSRoomConnection):
        if room.id not in self.rooms.keys(): 
            self.rooms[room.id] = WSRoom(room)

        await self.rooms[room.id].connect(conn)

    async def disconnect(self, room: Room, conn: WSRoomConnection):
        if room.id not in self.rooms.keys(): 
            raise WebSocketException(status.WS_1011_INTERNAL_ERROR)

        await self.rooms[room.id].disconnect(conn)

        if len(self.rooms[room.id].connections) == 0:
            self.removeRoom(room)

    async def handle(self, room: Room, conn: WSRoomConnection, data: Any):
        if room.id not in self.rooms.keys():
            raise WebSocketException(status.WS_1011_INTERNAL_ERROR)

        await self.rooms[room.id].handle(conn, data)


room_manager = WSRoomManager()
