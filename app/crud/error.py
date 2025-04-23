from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from models.error import Error
from schemas.error import ErrorCreate, ErrorUpdate  # 需要你自己定义 Pydantic 模型


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


async def create_error(db: AsyncSession, error_create: ErrorCreate) -> Error:
    """
    创建问题记录
    """
    try:
        # 覆盖 error_found_time 为当前系统时间
        error_data = error_create.copy(update={"error_found_time": datetime.utcnow()})
        new_error = Error(**error_data.dict())
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

        for key, value in error_update.dict(exclude_unset=True).items():
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
