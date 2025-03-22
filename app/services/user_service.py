from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud import user as user_crud


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        user_in: 用户创建模型
        
    Returns:
        User: 创建的用户对象
    """
    return await user_crud.create_user(db, user_in)


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    通过ID获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        Optional[User]: 找到的用户对象，如果未找到则为None
    """
    return await user_crud.get_user_by_id(db, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    通过用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        Optional[User]: 找到的用户对象，如果未找到则为None
    """
    return await user_crud.get_user_by_username(db, username)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    通过电子邮件获取用户
    
    Args:
        db: 数据库会话
        email: 电子邮件
        
    Returns:
        Optional[User]: 找到的用户对象，如果未找到则为None
    """
    return await user_crud.get_user_by_email(db, email)


async def update_user(
    db: AsyncSession, user: User, user_in: UserUpdate
) -> User:
    """
    更新用户信息
    
    Args:
        db: 数据库会话
        user: 现有用户对象
        user_in: 用户更新模型
        
    Returns:
        User: 更新后的用户对象
    """
    return await user_crud.update_user(db, user, user_in)


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    删除用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        bool: 删除是否成功
    """
    return await user_crud.delete_user(db, user_id) 