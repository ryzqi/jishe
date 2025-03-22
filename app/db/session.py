from typing import AsyncGenerator, Callable, TypeVar, Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Select
from sqlalchemy.engine.result import Result
from sqlalchemy import delete, update, insert, func
from loguru import logger

from app.db.database import get_db_session, get_db_context

T = TypeVar('T')


async def execute_query(
    query: Select, 
    session: AsyncSession, 
    scalar: bool = False, 
    first: bool = False
) -> Any:
    """
    执行查询并返回结果
    
    Args:
        query: SQLAlchemy select查询对象
        session: 数据库会话
        scalar: 是否返回单个值
        first: 是否只返回第一条结果
        
    Returns:
        查询结果
    """
    try:
        result: Result = await session.execute(query)
        
        if scalar and first:
            return result.scalar_one_or_none()
        elif scalar:
            return result.scalars().all()
        elif first:
            return result.first()
        else:
            return result.all()
    except Exception as e:
        logger.error(f"查询执行失败: {str(e)}")
        raise


async def get_object_by_id(
    model_class: Any, 
    object_id: Any, 
    session: AsyncSession
) -> Any:
    """
    根据ID获取数据库对象
    
    Args:
        model_class: 模型类
        object_id: 对象ID
        session: 数据库会话
        
    Returns:
        数据库对象或None
    """
    query = select(model_class).where(model_class.id == object_id)
    return await execute_query(query, session, scalar=True, first=True)


async def count_objects(
    model_class: Any, 
    session: AsyncSession, 
    filters: list = None
) -> int:
    """
    计算符合条件的对象数量
    
    Args:
        model_class: 模型类
        session: 数据库会话
        filters: 过滤条件列表
        
    Returns:
        对象计数
    """
    query = select(func.count()).select_from(model_class)
    if filters:
        for filter_condition in filters:
            query = query.where(filter_condition)
    
    result = await session.execute(query)
    return result.scalar_one()


async def execute_transaction(
    session: AsyncSession, 
    operation: Callable[[AsyncSession], Awaitable[T]]
) -> T:
    """
    执行数据库事务
    
    Args:
        session: 数据库会话
        operation: 在事务中要执行的操作函数
        
    Returns:
        操作结果
    """
    async with session.begin():
        try:
            result = await operation(session)
            return result
        except Exception as e:
            await session.rollback()
            logger.error(f"事务执行失败: {str(e)}")
            raise 