from hashlib import sha256
from app.config import CONTAINER_NAME, CONTAINER_USER, CONTAINER_WORKDIR, SALT
from app.model.base import Base
from app.model.user import UserModel
from app.docker import docker_client
from datetime import datetime
from base64 import b64encode

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, func

from app.model.base import Base

class AssociationRoomUser(Base):
    __tablename__ = "association_room_user"

    user_id_fk: Mapped[UUID] = mapped_column(ForeignKey("user_.id"), ondelete="CASCADE", onupdate="CASCADE")
    room_id_fk: Mapped[UUID] = mapped_column(ForeignKey("room.id"), ondelete="CASCADE", onupdate="CASCADE")

    room: Mapped["RoomModelNew"] = relationship(back_populates="users")
    user: Mapped["UserModelNew"] = relationship(back_populates="rooms")

class RoomModelNew(Base):
    __tablename__ = "room"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        unique=True, 
        server_default=func.gen_random_uuid()
    )
    
    invite_token: Mapped[str] = mapped_column(unique=True)
    
    users: Mapped[list["AssociationRoomUser"]] = relationship(back_populates="room")

    creator_id_fk: Mapped[UUID] = mapped_column(ForeignKey("user_.id", ondelete="CASCADE", onupdate="CASCADE"))
    creator: Mapped[UUID] = relationship()

    code: Mapped[str]
    stdin: Mapped[str]
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
class RoomModel():

    def __init__(self, room_code: str):
        # Unique id
        self.room_code = room_code

        # Room props
        self.code: list[str] = list()
        self.stdin: list[str] = list()
        self.stdout: list[str] = list()
        self.stderr: list[str] = list()
        self.code_location: dict[str, list[int]] = dict()
        self.stdin_location: dict[str, list[int]] = dict()
        self.connections: set[UserModel] = set()
        self.is_running: bool = False

    # Function to handle code/stdin changes
    def __diffsHandler__(self, arr: list[str], diffs: dict[str, str | None]):
        new_arr = arr.copy()
        for key in diffs:
            ind = int(key)

            if diffs[key] == None and ind >= len(new_arr):
                raise ValueError("NULL  values must be in range of the current list length")
            
            if ind >= len(new_arr):
                new_arr.extend("" for _ in range(len(new_arr)-1, ind))
            new_arr[ind] = diffs[key]
        
        cut_ind = len(new_arr) + 1

        for i in range(len(new_arr)-1):
            if new_arr[i] == None and new_arr[i+1] != None:
                raise ValueError("NULL values must be followed by another NULL value or end of the list")
            
            if new_arr[i] == None:
                cut_ind = min(cut_ind, i)
            if new_arr[i+1] == None:
                cut_ind = min(cut_ind, i+1)

        if cut_ind != len(new_arr) + 1:
            new_arr = new_arr[:cut_ind]
        
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
