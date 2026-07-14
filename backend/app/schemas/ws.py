from pydantic import BaseModel
from app.db.models.user import User
from fastapi import WebSocket
from typing import Any, Literal

class WSRoomConnection(BaseModel):
    model_config = { "arbitrary_types_allowed": True }
    user: User
    ws: WebSocket

class WSRoomAction(BaseModel):
    action: Literal["run_code", "update_code", "output", "connect", "disconnect"]
    payload: Any

class WSRoomCodeActions(BaseModel):
    action: Literal["insert", "delete"]
    payload: Any

class WSRoomCodeInsert(BaseModel):
    position: int
    code: str
