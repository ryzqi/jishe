from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class StreamConfig(Base):
    __tablename__ = "stream_config"
    __table_args__ = {"schema": "jishe"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    stream_url: Mapped[str] = mapped_column(nullable=False)