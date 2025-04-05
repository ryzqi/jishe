from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Warehouse(Base):
    """
    仓库数据库模型
    
    表名: jishe.warehouse
    字段:
    - id: 仓库唯一标识
    - warehouse_name: 仓库名称
    - states: 仓库状态
    """
    __tablename__ = "warehouse"
    __table_args__ = {"schema": "jishe"}
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    warehouse_name: Mapped[str] = mapped_column(String(255), nullable=False)
    states: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 关系
    stocks = relationship("Stock", back_populates="warehouse", cascade="all, delete-orphan") 