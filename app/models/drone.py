from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Drone(Base):
    """
    无人机数据库模型
    
    表名: jishe.drone
    字段:
    - id: 无人机编号
    - drone_type: 机型
    - states: 无人机状态: 1->正常工作, 0->未工作
    """
    __tablename__ = "drone"
    __table_args__ = {"schema": "jishe"}
    
    # 覆盖基类中的id定义，确保使用SERIAL类型
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    drone_type: Mapped[str] = mapped_column(String(255), nullable=False)
    states: Mapped[str] = mapped_column(String(1), nullable=False)
    
    # 关系
    patrols = relationship("Patrol", back_populates="drone", cascade="all, delete-orphan") 