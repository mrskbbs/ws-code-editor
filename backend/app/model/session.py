from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, func

from app.model.base import Base

class SessionModel(Base):
    __tablename__ = "session"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        unique=True, 
        server_default=func.gen_random_uuid()
    )

    # We ONUPDATE SET NULL cause we are preventing a case 
    # where db admin changes the user id and it messes up our tokens
    user_id_fk: Mapped[UUID] = mapped_column(ForeignKey("user_.id", ondelete="CASCADE", onupdate="SET NULL")) 
    user: Mapped["UserModelNew"] = relationship(back_populates="sessions")
    
    token: Mapped[str] = mapped_column(unique=True)
    user_agent: Mapped[Optional(str)]
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    