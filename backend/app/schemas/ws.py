from pydantic import BaseModel
from app.db.models.user import User
from fastapi import WebSocket
from typing import Literal

class WSRoomConnection(BaseModel):
    model_config = { "arbitrary_types_allowed": True }
    user: User
    ws: WebSocket

class WSRoomAction(BaseModel):
    action: Literal["stdin"] | Literal["code"] | Literal["stdout"] | Literal["connected"] | Literal["disconnected"]


