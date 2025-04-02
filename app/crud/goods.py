from typing import Optional, List
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.models.goods import Goods
from app.schemas.goods import GoodsCreate, GoodsUpdate


async def create_goods(db: AsyncSession, goods: GoodsCreate) -> Goods:
    """
    创建货物
    
    Args:
        db: 数据库会话
        goods: 货物创建模型
        
    Returns:
        Goods: 创建的货物对象
    """
    try:
        db_goods = Goods(goods_name=goods.goods_name)
        db.add(db_goods)
        await db.commit()
        await db.refresh(db_goods)
        return db_goods
    except SQLAlchemyError as e:
        logger.error(f"创建货物失败: {str(e)}")
        await db.rollback()
        raise


async def get_goods(db: AsyncSession, goods_id: int) -> Optional[Goods]:
    """
    根据ID获取货物
    
    Args:
        db: 数据库会话
        goods_id: 货物ID
        
    Returns:
        Goods: 找到的货物或None
    """
    try:
        query = select(Goods).where(Goods.id == goods_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"查询货物(ID:{goods_id})失败: {str(e)}")
        raise


async def get_all_goods(db: AsyncSession) -> List[Goods]:
    """
    获取所有货物
    
    Args:
        db: 数据库会话
        
    Returns:
        List[Goods]: 货物列表
    """
    try:
        query = select(Goods)
        result = await db.execute(query)
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logger.error(f"查询所有货物失败: {str(e)}")
        raise


async def update_goods(db: AsyncSession, goods_id: int, goods: GoodsUpdate) -> Optional[Goods]:
    """
    更新货物信息
    
    Args:
        db: 数据库会话
        goods_id: 货物ID
        goods: 货物更新模型
        
    Returns:
        Goods: 更新后的货物对象或None
    """
    try:
        db_goods = await get_goods(db, goods_id)
        if not db_goods:
            return None
        
        for field, value in goods.dict(exclude_unset=True).items():
            setattr(db_goods, field, value)
        
        await db.commit()
        await db.refresh(db_goods)
        return db_goods
    except SQLAlchemyError as e:
        logger.error(f"更新货物(ID:{goods_id})失败: {str(e)}")
        await db.rollback()
        raise


async def delete_goods(db: AsyncSession, goods_id: int) -> bool:
    """
    删除货物
    
    Args:
        db: 数据库会话
        goods_id: 货物ID
        
    Returns:
        bool: 是否删除成功
    """
    try:
        db_goods = await get_goods(db, goods_id)
        if not db_goods:
            return False
        
        await db.delete(db_goods)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"删除货物(ID:{goods_id})失败: {str(e)}")
        await db.rollback()
        raise 