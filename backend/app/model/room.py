from hashlib import sha256
from app.config import CONTAINER_NAME, CONTAINER_USER, CONTAINER_WORKDIR, SALT
from app.model.user import UserModel
from app.docker import docker_client
from datetime import datetime
from base64 import b64encode
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
        max_ind = max(map(int, (x for x in diffs.keys() if diffs[x] != None)))

        if (len(new_arr) <= max_ind):
            new_arr.extend("" for _ in range(len(new_arr)-1, max_ind)) 
        
        orig_len = len(new_arr)
        cut_ind = orig_len + 1
        
        for key, value in diffs.items():
            line_ind = int(key)
            if(value == None):
                cut_ind = min(cut_ind, line_ind)
            new_arr[line_ind] = value

        if(cut_ind != orig_len + 1):
            cut_ind + 1 < len(new_arr) and new_arr
            new_arr = new_arr[:cut_ind]
        
        if any(x == None for x in new_arr):
            raise ValueError("None value exists in output array")

        return new_arr
    
    def setCode(self, diffs: dict[int, str | None]):
        if self.is_running:
            return
        
        if type(diffs) is not dict:
            raise TypeError("Invalid diff input")
        
        self.code = self.__diffsHandler__(self.code, diffs)

    def setStdin(self, diffs: dict[int, str | None]): 
        if self.is_running:
            return
        
        if type(diffs) is not dict:
            raise TypeError("Invalid diff input")
        
        self.stdin = self.__diffsHandler__(self.stdin, diffs)

    def setStderr(self, text: list[str]):
        self.stderr = text

    def run(self) -> tuple[list[str], list[str]]:
        self.stdout = []
        self.stderr = []

        hashed_file_name = sha256(
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f").encode() +
            SALT.encode()
        ).hexdigest()
        
        encoded_stdin = b64encode("\n".join(self.stdin).encode("utf-8")).decode("utf-8")
        encoded_code = b64encode("\n".join(self.code).encode("utf-8")).decode("utf-8")

        commands_create = [
            f"echo '{encoded_stdin}' | base64 -d > stdin_{hashed_file_name}", 
            f"echo '{encoded_code}' | base64 -d > code_{hashed_file_name}.py",  
        ]

        commands_run = [
            f'python code_{hashed_file_name}.py < stdin_{hashed_file_name}', 
        ]

        commands_cleanup = [
            f'rm code_{hashed_file_name}.py',
            f'rm stdin_{hashed_file_name}'
        ]

        joined_commands = " && ".join(commands_create + commands_run) + "; " + "; ".join(commands_cleanup)

        container = docker_client.containers.get(CONTAINER_NAME)
        exit_code, output = container.exec_run( 
            cmd=f"bash -c '{joined_commands}'",
            demux=True,
            user=CONTAINER_USER,
            workdir=CONTAINER_WORKDIR
        )

        stdout, stderr = output

        self.stdout = (
            stdout
                .decode()
                .strip()
                .replace(hashed_file_name, "")
                .replace(CONTAINER_WORKDIR, "/workdir/")
                .split("\n")
        ) if stdout else []
        self.stderr = (
            stderr
                .decode()
                .strip()
                .replace(hashed_file_name, "")
                .replace(CONTAINER_WORKDIR, "")
                .split("\n")
        ) if stderr else []
    
        return self.stdout, self.stderr
