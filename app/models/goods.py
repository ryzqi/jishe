from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Goods(Base):
    """
    货物数据库模型
    
    表名: jishe.goods
    字段:
    - id: 货物种类唯一标识
    - goods_name: 货物种类名称
    """
    __tablename__ = "goods"
    __table_args__ = {"schema": "jishe"}
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    goods_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 关系
    stocks = relationship("Stock", back_populates="goods", cascade="all, delete-orphan") 