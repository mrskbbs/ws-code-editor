from hashlib import sha256
from venv import logger

from sqlalchemy_serializer import SerializerMixin
from app.config import CONTAINER_NAME, CONTAINER_USER, CONTAINER_WORKDIR, SALT
from app.models.base import Base
from app.docker import docker_client
from datetime import datetime
from base64 import b64encode

from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, Table, func

from app.models.base import Base
from app.models.associations import association_user_room
from app.types.auth import HashableAuthSessionInfo

class RoomModelNew(Base, SerializerMixin):
    __tablename__ = "room"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        unique=True, 
        server_default=func.gen_random_uuid()
    )
    name: Mapped[str]
    invite_token: Mapped[str] = mapped_column(unique=True)
    
    users: Mapped[list["UserModelNew"]] = relationship(
        secondary=association_user_room,
        back_populates="rooms"
    )

    creator_id_fk: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_.id", ondelete="CASCADE", onupdate="CASCADE"))
    creator: Mapped["UserModelNew"] = relationship()

    code: Mapped[str] = mapped_column(default="")
    stdin: Mapped[str] = mapped_column(default="")
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    


class RoomDynamicModel():
    """
    This model is used for realtime interactions 
    and it is created on first websocket connection.
    
    My reasoning is that extending SQLAlchemy model 
    could break some stuff, plus constant sql queries 
    that change the state of a table will be too much 
    of a load for db
    """
    def __init__(self, room: RoomModelNew):
        self.room_db = room

        self.id = str(self.room_db.id)
        self.name = self.room_db.name
        self.invite_token = self.room_db.invite_token
        
        # Room props
        db_code = self.room_db.code.splitlines()
        db_stdin = self.room_db.stdin.splitlines()
        self.code: list[str] = [""] if len(db_code) == 0 else db_code
        self.stdin: list[str] = [""] if len(db_stdin) == 0 else db_stdin
        self.stdout: list[str] = list()
        self.stderr: list[str] = list()
        self.code_location: dict[uuid.UUID, list[int]] = dict()
        self.stdin_location: dict[uuid.UUID, list[int]] = dict()
        self.connections: set[HashableAuthSessionInfo] = set()
        self.is_running: bool = False

    # Function to handle code/stdin changes
    def __diffsHandler__(self, arr: list[str], diffs_obj: dict[str, str | None]):
        diffs: dict[int, str] = dict()
        for key, val in diffs_obj.items():
            diffs[int(key)] = val
            
        diffs_len = max(diffs.keys())
        new_arr = arr.copy()

        if len(new_arr) < diffs_len:
            for _ in range(len(new_arr) - 1, diffs_len):
                new_arr.append("")

        cut_ind = len(new_arr) + 1

        for ind, val in diffs.items():
            if val == None:
                cut_ind = min(cut_ind, ind)
            else:
                new_arr[ind] = val

        return new_arr[0:cut_ind]

    def setCode(self, diffs: dict[int, str | None]):
        if self.is_running:
            return
        
        if type(diffs) is not dict:
            raise TypeError("Invalid diff input")
        try:
            self.code = self.__diffsHandler__(self.code, diffs)
        except Exception as exc:
            logger.error(exc)
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
