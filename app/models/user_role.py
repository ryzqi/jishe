from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func

from db.base import Base


class UserRole(Base):
    """
    用户角色关联数据库模型
    
    表名: jishe.user_role
    字段:
    - user_id: 用户唯一标识
    - role_id: 角色唯一标识
    """
    __tablename__ = "user_role"
    __table_args__ = {"schema": "jishe"}
    
    # 复合主键，覆盖基类中的id
    id = None  # 移除基类中的id
    user_id: Mapped[int] = mapped_column(ForeignKey("jishe.user.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("jishe.role.role_id", ondelete="CASCADE"), primary_key=True)
    
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
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users") 