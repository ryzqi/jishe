from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Stock(Base):
    """
    库存数据库模型
    
    表名: jishe.stock
    字段:
    - id: 库存唯一标识
    - warehouse_id: 仓库唯一标识
    - goods_id: 货物种类唯一标识
    - all_count: 总库存量
    - last_add_count: 新增库存量
    - last_add_date: 新增库存时间
    """
    __tablename__ = "stock"
    __table_args__ = {"schema": "jishe"}
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("jishe.warehouse.id", ondelete="CASCADE"), nullable=False)
    goods_id: Mapped[int] = mapped_column(ForeignKey("jishe.goods.id", ondelete="CASCADE"), nullable=False)
    all_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_add_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_add_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # 关系
    warehouse = relationship("Warehouse", back_populates="stocks")
    goods = relationship("Goods", back_populates="stocks") 