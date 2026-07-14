from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from app.db import Base


class Language(Base):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    ext: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
