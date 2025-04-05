from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func

from db.base import Base


class Role(Base):
    """
    角色数据库模型
    
    表名: jishe.role
    字段:
    - role_id: 角色唯一标识
    - role_name: 角色名称
    """
    __tablename__ = "role"
    __table_args__ = {"schema": "jishe"}
    
    # 重命名主键，以匹配数据库
    id = None  # 移除基类中的id
    role_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
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
    
    # 关系
    users = relationship("UserRole", back_populates="role") 