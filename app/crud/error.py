from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from models.error import Error
from schemas.error import ErrorCreate, ErrorUpdate


async def get_error_by_id(db: AsyncSession, error_id: int) -> Optional[Error]:
    """
    根据 ID 获取问题记录
    """
    try:
        result = await db.execute(select(Error).where(Error.error_id == error_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"查询问题(ID:{error_id})失败: {str(e)}")
        raise


async def get_errors_by_user_id(db: AsyncSession, user_id: int) -> List[Error]:
    """
    获取某个用户下的所有问题记录
    """
    try:
        result = await db.execute(select(Error).where(Error.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"查询用户(ID:{user_id})的问题记录失败: {str(e)}")
        raise


async def get_all_errors(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    获取所有错误信息并添加发送者信息
    
    Args:
        db: 数据库会话
        
    Returns:
        List[Dict[str, Any]]: 包含用户信息的错误列表
    """
    try:
        # 创建SQL查询语句
        query = """
        SELECT e.error_id AS id, 
               u.username AS sender, 
               u.id AS user_id,
               e.title, 
               e.error_content AS content, 
               e.error_found_time::text AS "createTime",
               CASE 
                   WHEN e.states = '0' THEN '待处理' 
                   WHEN e.states = '1' THEN '已处理' 
                   ELSE '未知状态' 
               END AS status
        FROM jishe.error e
        LEFT JOIN jishe.user u ON e.user_id = u.id
        ORDER BY e.error_found_time DESC
        """
        
        # 执行原生SQL查询
        result = await db.execute(text(query))
        rows = result.mappings().all()
        
        # 转换结果为字典列表
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"获取错误列表失败: {str(e)}")
        raise


async def create_error(db: AsyncSession, error_create: ErrorCreate) -> Error:
    """
    创建问题记录
    """
    try:
        # 准备数据前先获取所有字段
        data = error_create.model_dump()
        
        # 确保设置时间和用户ID
        if data.get("error_found_time") is None:
            data["error_found_time"] = datetime.now()  # 使用不带时区的时间
        elif data["error_found_time"].tzinfo:
            # 如果时间有时区信息，移除时区信息
            data["error_found_time"] = data["error_found_time"].replace(tzinfo=None)
            
        # 创建Error实例
        new_error = Error(**data)
        db.add(new_error)
        await db.commit()
        await db.refresh(new_error)
        logger.info(f"创建问题成功: ID={new_error.error_id}")
        return new_error
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"创建问题失败: {str(e)}")
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"创建问题时发生未知错误: {str(e)}")
        raise


async def update_error(db: AsyncSession, error_id: int, error_update: ErrorUpdate) -> Optional[Error]:
    """
    更新问题记录
    """
    try:
        result = await db.execute(select(Error).where(Error.error_id == error_id))
        db_error = result.scalars().first()
        if not db_error:
            logger.warning(f"问题(ID:{error_id})不存在，无法更新")
            return None

        update_data = error_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_error, key, value)

        await db.commit()
        await db.refresh(db_error)
        logger.info(f"问题(ID:{error_id})更新成功")
        return db_error
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"更新问题(ID:{error_id})失败: {str(e)}")
        raise


async def delete_error(db: AsyncSession, error_id: int) -> bool:
    """
    删除问题记录
    """
    try:
        result = await db.execute(select(Error).where(Error.error_id == error_id))
        db_error = result.scalars().first()
        if not db_error:
            logger.warning(f"问题(ID:{error_id})不存在，无法删除")
            return False

        await db.delete(db_error)
        await db.commit()
        logger.info(f"问题(ID:{error_id})已删除")
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"删除问题(ID:{error_id})失败: {str(e)}")
        raise
