from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

from app.db.base import Base


class Error(Base):
    """
    巡查发现的问题数据库模型
    
    表名: jishe.error
    字段:
    - error_id: 问题编号
    - error_content: 问题内容
    - error_found_time: 问题发现时间
    - states: 问题状态: 0->待解决, 1->正在解决
    """
    __tablename__ = "error"
    __table_args__ = {"schema": "jishe"}
    
    # 重命名主键，以匹配数据库
    id = None  # 移除基类中的id
    error_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    error_content: Mapped[str] = mapped_column(Text, nullable=False)
    error_found_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    states: Mapped[str] = mapped_column(String(1), nullable=False)
    
    # 覆盖基类中的通用字段，因为我们已经移除了id
    @declared_attr.directive
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
        
    @declared_attr.directive
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True), 
            server_default=func.now(), 
            onupdate=func.now(), 
            nullable=False
        ) 