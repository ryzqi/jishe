from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.role import Role


async def get_role_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
    """
    根据ID获取角色
    
    Args:
        db: 数据库会话
        role_id: 角色ID
        
    Returns:
        Role: 角色对象或None
    """
    query = select(Role).where(Role.role_id == role_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_role_by_name(db: AsyncSession, role_name: str) -> Optional[Role]:
    """
    根据名称获取角色
    
    Args:
        db: 数据库会话
        role_name: 角色名称
        
    Returns:
        Role: 角色对象或None
    """
    query = select(Role).where(Role.role_name == role_name)
    result = await db.execute(query)
    return result.scalars().first()


async def get_all_roles(db: AsyncSession) -> List[Role]:
    """
    获取所有角色
    
    Args:
        db: 数据库会话
        
    Returns:
        List[Role]: 角色列表
    """
    query = select(Role)
    result = await db.execute(query)
    return list(result.scalars().all()) 