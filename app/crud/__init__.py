"""
CRUD操作模块

包含所有数据库CRUD(创建、读取、更新、删除)操作
遵循资源隔离原则，每个资源对应一个独立模块
"""

from app.crud.user import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    update_user,
    delete_user
)

__all__ = [
    "create_user",
    "get_user_by_id", 
    "get_user_by_username", 
    "get_user_by_email",
    "update_user",
    "delete_user"
]
