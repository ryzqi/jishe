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
    - password: 用户密码
    """
    __tablename__ = "user"
    __table_args__ = {"schema": "jishe"}
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 关系
    roles = relationship("UserRole", back_populates="user") 