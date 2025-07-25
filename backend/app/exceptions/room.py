from app.exceptions.base import HTTPBaseException


class RoomNotFound(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "Room was not found"
        self.status_code = 404

class RoomStateNotSaved(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "Room state was not saved"
        self.status_code = 500

class NotAllowedToRoom(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "You are not allowed to enter this room"
        self.status_code = 403

class AlreadyRoomMember(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "You are already a room member"
        self.status_code = 400

class NotRoomCreator(HTTPBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "This action is available only for room creator"
        self.status_code = 403
