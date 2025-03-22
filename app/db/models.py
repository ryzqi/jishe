"""
SQLAlchemy 模型导入文件
此文件用于方便在一个地方导入所有模型，主要用于数据库迁移
"""

# 导入基类
from app.db.base import Base

# 导入所有模型，确保它们被 SQLAlchemy 注册
from app.models.drone import Drone
from app.models.error import Error
from app.models.goods import Goods
from app.models.patrol import Patrol
from app.models.role import Role
from app.models.warehouse import Warehouse
from app.models.stock import Stock
from app.models.user import User
from app.models.user_role import UserRole

# 所有模型列表
__all__ = [
    "Base",
    "Drone",
    "Error",
    "Goods",
    "Patrol",
    "Role",
    "Warehouse",
    "Stock",
    "User",
    "UserRole"
] 