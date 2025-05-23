import datetime
from sqlalchemy import Integer, Interval, String
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base


class Transport(Base):
    """
    运输管理数据库模型 (运输线路表)
    """
    __tablename__ = "transport"
    __table_args__ = (
        {"schema": "jishe", "comment": "运输线路表"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='唯一id')
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment='线路名称')
    stock: Mapped[int] = mapped_column(Integer, nullable=False, comment='货物量')
    already_percent: Mapped[int] = mapped_column(Integer, nullable=False, comment='已送达')
    estimated_duration: Mapped[datetime.timedelta | None] = mapped_column(Interval, nullable=True, comment='预估时长')