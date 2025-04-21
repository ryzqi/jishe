from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Rooms(Base):
    __tablename__ = "rooms"
    __table_args__ = {"schema": "jishe"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    num: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
