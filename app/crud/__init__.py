"""
CRUD操作模块

包含所有数据库CRUD(创建、读取、更新、删除)操作
遵循资源隔离原则，每个资源对应一个独立模块
"""

from crud.user import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    update_user,
    delete_user,
    authenticate_user,
    get_user_roles
)

from crud.role import (
    get_role_by_id,
    get_role_by_name,
    get_all_roles
)

__all__ = [
    # 用户操作
    "create_user",
    "get_user_by_id", 
    "get_user_by_username", 
    "update_user",
    "delete_user",
    "authenticate_user",
    "get_user_roles",
    
    # 角色操作
    "get_role_by_id",
    "get_role_by_name",
    "get_all_roles"
]
