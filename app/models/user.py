from sqlalchemy import Column, String, Table, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """
    用户数据库模型
    
    表名: jishe.user
    字段:
    - id: 用户唯一标识
    - username: 用户名
    - email: 电子邮件
    - password: 用户密码
    - is_active: 是否激活
    - is_superuser: 是否为超级用户
    """
    __tablename__ = "user"
    __table_args__ = {"schema": "jishe"}
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    roles = relationship("UserRole", back_populates="user") 