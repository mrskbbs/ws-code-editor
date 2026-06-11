from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.ws.room_manager import WSRoomManager

@asynccontextmanager
async def appLifespan(app: FastAPI):
    # start
    app.state.room_manager = WSRoomManager()
    yield
    # shutdown

    
