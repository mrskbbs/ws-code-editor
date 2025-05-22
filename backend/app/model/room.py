from hashlib import sha256
from app.config import CONTAINER_NAME, SALT
from app.model.user import UserModel
from app.docker import docker_client
from datetime import datetime

class RoomModel():

    def __init__(self, room_code: str):
        # Unique id
        self.room_code = room_code

        # Room props
        self.code: list[str] = list()
        self.stdin: list[str] = list()
        self.stdout: list[str] = list()
        self.stderr: list[str] = list()
        self.connections: set[UserModel] = set()
        self.is_running: bool = False

    # Function to handle code/stdin changes
    def __diffsHandler__(self, arr: list[str], diffs: dict[str, str | None]):
        new_arr = arr.copy()
        max_ind = max(map(int, diffs.keys()))
        cut_ind = len(new_arr) + 1

        if (len(new_arr) <= max_ind):
            new_arr.extend("" for _ in range(len(new_arr)-1, max_ind+1)) 

        for key, value in diffs.items():
            line_ind = int(key)
            if(value == None):
                cut_ind = min(cut_ind, line_ind)
                continue
            new_arr[line_ind] = value

        if(cut_ind != len(new_arr) + 1):
            return new_arr[:cut_ind]

        return new_arr
    
    def setCode(self, diffs: dict[int, str | None]): 
        self.code = self.__diffsHandler__(self.code, diffs)

    def setStdin(self, diffs: dict[int, str | None]): 
        self.stdin = self.__diffsHandler__(self.stdin, diffs)

    def run(self) -> tuple[list[str], list[str]]:
        # try:
        #     # Dumb code bellow, might work better

        #     # output = docker_client.containers.run(
        #     #     "python:latest",
        #     #     command=f"echo {"\n".join(self.stdin)} | python -c {";".join(self.code)}",
        #     #     auto_remove=True,
        #     #     detach=False,
        #     # ).decode()

            
        #     # More tricky code, might be broken

        #     container = docker_client.containers.create(
        #         "python:latest",
        #         detach=False, # we will wait for the execution rather than do it in background
        #         privileged=False,
        #     )
        #     container.start()
        #     joined_stdin = "\n".join(self.stdin)
        #     joined_code = ";".join(self.code)

        #     # returns tuple[int, tuple[bytes, bytes]]
        #     exit_code, output = container.exec_run( 
        #         cmd=f"echo {joined_stdin} | python -c {joined_code}",
        #         demux=True,
        #     )
        #     print(exit_code, output)
        #     stdout, stderr = output

        #     self.stdout = stdout.decode() if stdout else ''
        #     self.stderr = stderr.decode() if stderr else ''

        #     # KILL
        #     container.stop()
        #     container.remove()

        # finally:
        #     container.remove.force()


        container = docker_client.containers.get(CONTAINER_NAME)

        joined_stdin = "\n".join(self.stdin).strip()
        joined_code = "\n".join(self.code)

        hashed_file_name = sha256(
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f").encode() +
            SALT.encode()
        ).hexdigest()


        exit_code, output = container.exec_run( 
            cmd=f"echo '{joined_stdin}' > 'stdin_{hashed_file_name}' &  echo '{joined_code}' > 'code_{hashed_file_name}.py' & python 'code_{hashed_file_name}.py' < 'stdin_{hashed_file_name}' & rm 'code_{hashed_file_name}.py' & 'stdin_{hashed_file_name}.py'",
            demux=True,
        )

        print(exit_code, output)
        stdout, stderr = output

        self.stdout = stdout.decode() if stdout else ''
        self.stderr = stderr.decode() if stderr else ''
    
        return self.stdout, self.stderr
