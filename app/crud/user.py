from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        user_in: 用户创建模型
        
    Returns:
        User: 创建的用户对象
    """
    # 创建用户对象，并哈希密码
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password=get_password_hash(user_in.password)
    )
    
    # 保存到数据库
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    通过ID获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        Optional[User]: 找到的用户对象，如果未找到则为None
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    通过用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        Optional[User]: 找到的用户对象，如果未找到则为None
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    通过电子邮件获取用户
    
    Args:
        db: 数据库会话
        email: 电子邮件
        
    Returns:
        Optional[User]: 找到的用户对象，如果未找到则为None
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


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
    # 更新基本属性
    if user_in.username is not None:
        user.username = user_in.username
    if user_in.email is not None:
        user.email = user_in.email
        
    # 更新密码（如果提供）
    if user_in.password is not None:
        user.password = get_password_hash(user_in.password)
    
    # 保存到数据库
    await db.commit()
    await db.refresh(user)
    
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    删除用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        bool: 删除是否成功
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    await db.delete(user)
    await db.commit()
    
    return True 