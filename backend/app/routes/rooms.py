from flask import request
from flask_socketio import Namespace, emit
from app.controllers.rooms import RoomController
from app.model.room import RoomModel

class RoomWS(Namespace):
    rooms: dict[str, RoomModel] = dict()

    def __init__(self, namespace = None):
        super().__init__(namespace)

    def on_connect(self):
        RoomController(request, self.rooms).connect()

    def on_disconnect(self):
        RoomController(request, self.rooms).disconnect()

    def on_code(self, data: dict[int, str | None]):
        RoomController(request, self.rooms).setCode(data)

    def on_stdin(self, data: dict[int, str | None]):
        RoomController(request, self.rooms).setStdin(data)

    def on_run(self):
        RoomController(request, self.rooms).run()