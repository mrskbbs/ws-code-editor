from typing import Optional
from pydantic import BaseModel

class RoomCreate(BaseModel):
    title: str
    language_id: int 

class RoomEdit(BaseModel):
    title: Optional[str] = None
    language_id: Optional[int] = None
