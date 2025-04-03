from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """
    用户数据库模型
    
    表名: jishe.user
    字段:
    - id: 用户唯一标识
    - username: 用户名
    - password: 用户密码
    - email: 用户电子邮件
    - is_active: 用户是否活跃
    - is_superuser: 是否为超级管理员
    - name: 用户姓名
    - phone: 用户电话号码
    - createtime: 账户创建时间
    """
    __tablename__ = "user"
    __table_args__ = {"schema": "jishe"}
    
    id = Column(Integer, primary_key=True, index=True, comment="用户唯一标识")
    username = Column(String(50), nullable=False, comment="用户名")
    password = Column(String(100), nullable=False, comment="用户密码")
    email = Column(String(100), nullable=False, default="default@example.com", comment="用户电子邮件")
    is_active = Column(Boolean, nullable=False, default=True, comment="用户是否活跃")
    is_superuser = Column(Boolean, nullable=False, default=False, comment="是否为超级管理员")
    name = Column(String(100), comment="用户姓名")
    phone = Column(String(15), comment="用户电话号码")
    createtime = Column(DateTime, nullable=False, server_default=func.now(), comment="账户创建时间")
    
    # 关系
    roles = relationship("UserRole", back_populates="user") 