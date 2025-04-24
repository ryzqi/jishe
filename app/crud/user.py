from typing import Optional, List, Dict, Any, Union
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from models.user import User
from models.user_role import UserRole
from models.role import Role
from core.password import verify_password, get_password_hash
from schemas.user import UserCreate, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    根据ID获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        User: 找到的用户或None
    """
    try:
        query = select(User).where(User.id == user_id).options(joinedload(User.roles))
        result = await db.execute(query)
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"查询用户(ID:{user_id})失败: {str(e)}")
        raise


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    根据用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        User: 找到的用户或None
    """
    try:
        query = select(User).where(User.username == username).options(joinedload(User.roles))
        result = await db.execute(query)
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"查询用户(用户名:{username})失败: {str(e)}")
        raise


async def get_user_roles(db: AsyncSession, user_id: int) -> List[Role]:
    """
    获取用户的所有角色
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        List[Role]: 角色列表
    """
    try:
        query = select(Role).join(UserRole).where(UserRole.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logger.error(f"获取用户(ID:{user_id})角色失败: {str(e)}")
        raise


async def create_user(db: AsyncSession, user_create: UserCreate, role_ids: List[int] = None) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        user_create: 用户创建模型
        role_ids: 角色ID列表
        
    Returns:
        User: 创建的用户
    """
    try:
        # 先检查用户名是否存在
        existing_user = await get_user_by_username(db, user_create.username)
        if existing_user:
            logger.warning(f"创建用户失败: 用户名'{user_create.username}'已存在")
            raise ValueError(f"Username '{user_create.username}' already exists")
            
        # 创建用户数据
        user_data = {
            "username": user_create.username,
            "password": get_password_hash(user_create.password),
            "email": user_create.email or "default@example.com",
            "name": user_create.name or user_create.username,
            "phone": user_create.phone or "未设置"
        }
        
        # 创建用户
        db_user = User(**user_data)
        db.add(db_user)
        await db.flush()  # 获取自动生成的ID
        
        # 分配角色
        if role_ids:
            for role_id in role_ids:
                user_role = UserRole(user_id=db_user.id, role_id=role_id)
                db.add(user_role)
        
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"用户创建成功: {db_user.username} (ID: {db_user.id})")
        return db_user
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"创建用户失败: {str(e)}")
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"创建用户时发生错误: {str(e)}")
        raise


async def update_user(
    db: AsyncSession, 
    user_id: int, 
    user_update: UserUpdate, 
    role_ids: List[int] = None
) -> Optional[User]:
    """
    更新用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        user_update: 用户更新模型
        role_ids: 角色ID列表
        
    Returns:
        User: 更新后的用户或None
    """
    try:
        # 检查用户是否存在
        user = await get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"更新用户失败: 用户ID:{user_id}不存在")
            return None
        
        # 准备更新数据
        update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
        
        # 如果更新包含密码，需要进行哈希处理
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])
        
        # 更新用户信息
        if update_data:
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
        
        # 如果提供了角色，更新角色关联
        if role_ids is not None:
            # 删除当前所有角色
            await db.execute(
                delete(UserRole)
                .where(UserRole.user_id == user_id)
            )
            
            # 添加新角色
            for role_id in role_ids:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                db.add(user_role)
        
        await db.commit()
        updated_user = await get_user_by_id(db, user_id)
        logger.info(f"用户更新成功: {updated_user.username} (ID: {updated_user.id})")
        return updated_user
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"更新用户(ID:{user_id})失败: {str(e)}")
        raise


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    删除用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        bool: 是否成功删除
    """
    try:
        # 检查用户是否存在
        user = await get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"删除用户失败: 用户ID:{user_id}不存在")
            return False
        
        # 删除用户
        await db.execute(
            delete(User)
            .where(User.id == user_id)
        )
        await db.commit()
        logger.info(f"用户删除成功: {user.username} (ID: {user_id})")
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"删除用户(ID:{user_id})失败: {str(e)}")
        raise


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    用户认证
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
        
    Returns:
        User: 认证成功的用户或None
    """
    try:
        user = await get_user_by_username(db, username)
        if not user:
            logger.warning(f"认证失败: 用户名'{username}'不存在")
            return None
        
        # 验证密码
        if not verify_password(password, user.password):
            logger.warning(f"认证失败: 用户'{username}'密码错误")
            return None
        
        logger.debug(f"认证成功: 用户'{username}'")
        return user
    except SQLAlchemyError as e:
        logger.error(f"认证用户(用户名:{username})时数据库错误: {str(e)}")
        # 不在这里处理异常，将其传递给调用者
        raise
    except Exception as e:
        logger.error(f"认证用户(用户名:{username})时未知错误: {str(e)}")
        raise 