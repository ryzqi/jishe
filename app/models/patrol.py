from datetime import datetime, time
from sqlalchemy import Column, ForeignKey, String, DateTime, Time, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Patrol(Base):
    """
    巡查记录数据库模型
    
    表名: jishe.patrol
    字段:
    - id: 巡查记录唯一标识
    - drone_id: 无人机编号
    - address: 在寻路段
    - predict_fly_time: 预计飞行时长
    - fly_start_datetime: 开始飞行时间
    - update_time: 更新时间
    - error_id: 错误ID
    """
    __tablename__ = "patrol"
    __table_args__ = {"schema": "jishe"}
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    drone_id: Mapped[int] = mapped_column(ForeignKey("jishe.drone.id", ondelete="CASCADE"), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    predict_fly_time: Mapped[time] = mapped_column(Time, nullable=False)
    fly_start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    update_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")
    error_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 关系
    drone = relationship("Drone", back_populates="patrols") 