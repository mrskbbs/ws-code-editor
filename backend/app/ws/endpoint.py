from fastapi import WebSocketDisconnect, WebSocket
from app.dependencies.users import WSUserDep
from app.dependencies.rooms import RoomDep
from app.schemas.ws import WSRoomConnection

async def wsRoomEndpoint(ws: WebSocket, room: RoomDep, user: WSUserDep):
    await ws.accept()
    conn = WSRoomConnection(user=user, ws=ws)
    await ws.app.state.room_manager.connect(room, conn)
    try:
        # receiving data
        while True:
            data = await ws.receive_json()
            await ws.app.state.room_manager.handle(room, conn, data)
    except WebSocketDisconnect:
        await ws.app.state.room_manager.disconnect(room, conn)
