"""
SQLAlchemy 模型导入文件
此文件用于方便在一个地方导入所有模型，主要用于数据库迁移
"""

# 导入基类
from db.base import Base

# 导入所有模型，确保它们被 SQLAlchemy 注册
from models.drone import Drone
from models.error import Error
from models.goods import Goods
from models.patrol import Patrol
from models.role import Role
from models.warehouse import Warehouse
from models.stock import Stock
from models.user import User
from models.user_role import UserRole

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