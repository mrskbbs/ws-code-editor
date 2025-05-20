from app.model.user import UserModel
from app.docker import docker_client

class RoomModel():
    # Unique id
    room_code: str

    # Room props
    code: list[str] = list()
    stdin: list[str] = list()
    stdout: list[str] = list()
    stderr: list[str] = list()
    connections: set[UserModel] = set()
    is_running: bool = False

    def __init__(self, room_code: str):
        self.room_code = room_code

    # Function to handle code/stdin changes
    def __diffsHandler__(arr: list[str], diffs: dict[int, str | None]):
        new_arr = arr.copy()
        cut_ind = len(new_arr)

        for line_ind in diffs.keys():
            line = diffs[line_ind]
            new_arr[line_ind] = line

            if line == None:
                cut_ind = min(cut_ind, line_ind)

        new_arr = new_arr[:cut_ind]
        
        return new_arr

    def setCode(self, diffs: dict[int, str | None]): 
        self.code = self.__diffsHandler__(self.code, diffs)

    def setStdin(self, diffs: dict[int, str | None]): 
        self.stdin = self.__diffsHandler__(self.stdin, diffs)

    def run(self) -> tuple[list[str], list[str]]:
        # Dumb code bellow, might work better

        # output = docker_client.containers.run(
        #     "python:latest",
        #     command=f"echo {"\n".join(self.stdin)} | python -c {";".join(self.code)}",
        #     auto_remove=True,
        #     detach=False,
        # ).decode()

        
        # More tricky code, might be broken

        container = docker_client.containers.create(
            "python:latest",
            detach=False, # we will wait for the execution rather than do it in background
            privileged=False,
        )
        
        joined_stdin = "\n".join(self.stdin)
        joined_code = ";".join(self.code)

        # returns tuple[int, tuple[bytes, bytes]]
        exit_code, output = container.exec_run( 
            command=f"echo {joined_stdin} | python -c {joined_code}",
            demux=True,
        )
        stdout, stderr = output

        self.stdout = stdout.decode().split("\n")
        self.stderr = stderr.decode().split("\n")

        # KILL
        container.stop()
        container.remove()

        return self.stdout, self.stderr

