from fastapi import WebSocketDisconnect, WebSocket
from app.dependencies.users import WSUserDep
from app.dependencies.rooms import RoomDep
from app.schemas.ws import WSRoomConnection
from app.ws.room_manager import room_manager

async def wsRoomEndpoint(ws: WebSocket, room: RoomDep, user: WSUserDep):
    await ws.accept()
    await room_manager.connect(room, WSRoomConnection(user=user, ws=ws))
    try:
        # receiving data
        while True:
            data = await ws.receive_json()
            await room_manager.handle(room, user, data)
    except WebSocketDisconnect:
        await room_manager.disconnect(room, WSRoomConnection(user=user, ws=ws))
