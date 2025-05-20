from flask import Request
from flask_socketio import emit, join_room, leave_room
from app.model.room import RoomModel
from app.model.user import UserModel


class RoomController():
    request: Request
    rooms: dict[str, RoomModel]
    room: RoomModel
    user: UserModel

    def __init__(self, request: Request, rooms: dict[str, RoomModel]):
        self.request = request
        self.user = UserModel(self.request)

        self.rooms = rooms
        # TODO: not that secure, room creation and join can be improved
        room_code = request.args.get("room_code")
        room = rooms.get(room_code) 
        if room == None:
            rooms[room_code] = RoomModel(room_code)
            self.room = rooms[room_code]
        else:
            self.room = room
    
    def connect(self):
        join_room(room=self.room.room_code, sid=self.user.sid)
        self.room.connections.add(self.user)

    def disconnect(self):
        self.room.connections.remove(self.user)

        if len(self.room.connections) == 0:
            self.rooms.pop(self.room.room_code, None)
        else:
            leave_room(room=self.room.room_code, sid=self.user.sid)
            emit(
                "connections", 
                list(
                    map(str, self.room.connections)
                ), 
                broadcast=True, 
                to=self.room.room_code
            )

    def setCode(self, diffs: dict[int, str | None]):
        self.room.setCode(diffs)
        emit("code", diffs, broadcast=True, to=self.room.room_code)

    def setStdin(self, diffs: dict[int, str | None]):
        self.room.setStdin(diffs)
        emit("stdin", diffs, broadcast=True, to=self.room.room_code)

    def run(self):
        pass