from app.model.user import UserModel


class RoomModel():
    # Unique id
    room_code: str

    # Room props
    code: list[str] = list()
    stdin: list[str] = list()
    stdout: list[str] = list()
    connections: set[UserModel] = set()
    is_running: bool = False

    def __init__(self, room_code: str):
        self.room_code = room_code

    # Function to handle code/stdin changes
    def __diffsHandler__(arr: list[str], diffs: dict[int, str | None]):
        pass

    def setCode(self, diffs: dict[int, str | None]): 
        self.__diffsHandler__(self.code, diffs)

    def setStdin(self, diffs: dict[int, str | None]): 
        self.__diffsHandler__(self.stdin, diffs)

    def run(self) -> list[str]:
        self.is_running = True

        # Docker contianer code run

        self.is_running = False

        return self.stdout