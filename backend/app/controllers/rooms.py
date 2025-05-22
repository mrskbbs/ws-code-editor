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
        room = self.rooms.get(room_code) 
        if room == None:
            self.rooms[room_code] = RoomModel(room_code)
            self.room = self.rooms[room_code]
        else:
            self.room = room
    
    def __formatListToJson__(self, arr) -> dict:
        d = dict()
        
        for i in range(len(arr)):
            d[i] = arr[i]

        return d

    def connect(self):
        join_room(room=self.room.room_code, sid=self.user.sid)
        self.room.connections.add(self.user)
        emit("code", self.__formatListToJson__(self.room.code), to=self.user.sid)
        emit("stdin", self.__formatListToJson__(self.room.stdin), to=self.user.sid)
        emit("stdout", self.__formatListToJson__(self.room.stdout), to=self.user.sid)
        emit(
            "connections", 
            list(map(str, self.room.connections)), 
            # broadcast=True, 
            to=self.room.room_code
        )

    def disconnect(self):
        leave_room(room=self.room.room_code, sid=self.user.sid)
        self.room.connections.remove(self.user)

        emit(
            "connections", 
            list(map(str, self.room.connections)), 
            # broadcast=True, 
            to=self.room.room_code
        )

        if len(self.room.connections) == 0:
            self.rooms.pop(self.room.room_code, None)

    def setCode(self, diffs: dict[int, str | None]):
        print("[diffs]", diffs)
        self.room.setCode(diffs)
        emit("code", diffs, to=self.room.room_code, include_self=False)
        print("[code]", self.room.code)

    def setStdin(self, diffs: dict[int, str | None]):
        self.room.setStdin(diffs)
        emit("stdin", diffs, to=self.room.room_code, include_self=False)

    def run(self):
        try:
            emit("run", True, to=self.room.room_code)
            stdout, stderr = self.room.run()
            emit("run", False, to=self.room.room_code)

            if len(stdout) > 0:
                emit("stdout", stdout, to=self.room.room_code)
            if len(stderr) > 0:
                emit("stderr", stderr, to=self.room.room_code)
        except Exception as e:
            print(e)
            emit("run", False, to=self.room.room_code)