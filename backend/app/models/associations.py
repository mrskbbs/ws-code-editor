import uuid
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

association_user_room = Table(
    "association_room_user",
    Base.metadata,
    Column(
        "user_id_fk", 
        UUID(as_uuid=True), 
        ForeignKey("user_.id", ondelete="CASCADE", onupdate="CASCADE"), 
        primary_key=True, 
        nullable=False
    ),
    Column(
        "room_id_fk", 
        UUID(as_uuid=True), 
        ForeignKey("room.id", ondelete="CASCADE", onupdate="CASCADE"), 
        primary_key=True, 
        nullable=False
    ),
)
